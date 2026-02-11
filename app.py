from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_cors import CORS
from PIL import Image
import os
import uuid
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import numpy as np

from processing import fit_on_dummy, build_outfit

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # Required for sessions
CORS(app)

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Track current outfit per session
outfit_tracker = {}

# ------------------ DATABASE CONFIG ------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "closet_asmi"
}

# ------------------ HELPER: Validate if image is clothing ------------------
def is_valid_clothing_image(image_path):
    """
    Basic validation to check if the uploaded image looks like clothing.
    Returns (is_valid, reason)
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False, "Unable to read image"
        
        # Convert to HSV for color analysis
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Check for skin tones (faces/body parts)
        # Skin tone range in HSV: H: 0-20, S: 20-150, V: 80-255
        lower_skin = np.array([0, 20, 80], dtype=np.uint8)
        upper_skin = np.array([20, 150, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        skin_percentage = (np.count_nonzero(skin_mask) / skin_mask.size) * 100
        
        # If more than 30% of image is skin tone, likely not clothing
        if skin_percentage > 30:
            return False, "Image appears to contain a person's face or body. Please upload clothing items only."
        
        # Check if image is too uniform (likely not clothing with texture/patterns)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # If variance is too low, image might be too plain (screenshot, solid color, etc.)
        if variance < 10:
            return False, "Image appears too uniform. Please upload a clear photo of a clothing item."
        
        # Passed basic checks
        return True, "Valid clothing image"
        
    except Exception as e:
        return False, f"Error validating image: {str(e)}"

# ------------------ NAVIGATION ------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/closet")
def closet():
    images = []

    for filename in os.listdir(UPLOAD_FOLDER):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        if filename.startswith("final_"):
            continue

        try:
            g_type = filename.split("_")[0]
        except:
            g_type = "top"

        images.append({
            "url": url_for("static", filename=f"uploads/{filename}"),
            "type": g_type,
            "filename": filename
        })

    return render_template("closet.html", images=images)

# ------------------ UPLOAD WITH VALIDATION ------------------
@app.route("/upload", methods=["POST"])
def upload_file():
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image part"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"}), 400

    # Save temporarily for validation
    temp_filename = f"temp_{uuid.uuid4().hex}.png"
    temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
    
    try:
        img = Image.open(file).convert("RGBA")
        img.save(temp_path, "PNG")
        
        # Validate if it's a clothing item
        is_valid, validation_message = is_valid_clothing_image(temp_path)
        
        if not is_valid:
            os.remove(temp_path)  # Clean up temp file
            return jsonify({
                "success": False, 
                "error": validation_message
            }), 400
        
        # Determine garment type from filename
        name = file.filename.lower()
        
        # FIXED: More specific matching with priority order
        if any(x in name for x in ["skirt", "skrt"]):
            g_type = "skirt"
        elif any(x in name for x in ["dress", "gown", "frock"]):
            g_type = "dress"
        elif any(x in name for x in ["top", "shirt", "tshirt", "t-shirt", "blouse", "sweater", "hoodie", "jacket"]):
            g_type = "top"
        elif any(x in name for x in ["pant", "pants", "trouser", "jeans", "bottom", "shorts"]):
            g_type = "bottom"
        else:
            # Fallback: use aspect ratio
            w, h = img.size
            if h / w > 1.5:
                g_type = "dress"  # Tall and narrow
            elif h / w < 0.8:
                g_type = "bottom"  # Short and wide
            else:
                g_type = "top"  # Default
        
        # Rename with proper type prefix
        final_filename = f"{g_type}_{uuid.uuid4().hex}.png"
        final_path = os.path.join(UPLOAD_FOLDER, final_filename)
        
        # Move temp file to final location
        os.rename(temp_path, final_path)
        
        image_url = url_for("static", filename=f"uploads/{final_filename}")

        return jsonify({
            "success": True,
            "url": image_url,
            "type": g_type,
            "message": f"Successfully uploaded as {g_type}"
        })
        
    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }), 500

# ------------------ TRY-ON (WITH OUTFIT TRACKING) ------------------
@app.route("/tryon", methods=["POST"])
def tryon():
    try:
        data = request.json
        image_url = data.get("image")
        garment_type = data.get("type", "top")

        if not image_url:
            return jsonify({"success": False, "error": "No image URL provided"}), 400

        # Get session ID
        if 'user_id' not in session:
            session['user_id'] = str(uuid.uuid4())
        session_id = session['user_id']

        # Initialize outfit tracker for this session
        if session_id not in outfit_tracker:
            outfit_tracker[session_id] = {}

        filename = os.path.basename(image_url)
        garment_path = os.path.join(UPLOAD_FOLDER, filename)

        # Normalize garment type (skirt is separate, not bottom)
        if garment_type in ["skirts"]:
            normalized_type = "skirt"
        else:
            normalized_type = garment_type

        # Update outfit tracker
        if normalized_type == "dress":
            # Dress replaces everything
            outfit_tracker[session_id] = {"dress": garment_path}
        else:
            # Remove dress if adding top or bottom or skirt
            if "dress" in outfit_tracker[session_id]:
                del outfit_tracker[session_id]["dress"]
            
            # If adding skirt or bottom, remove the other (can't wear both)
            if normalized_type in ["skirt", "bottom"]:
                if "skirt" in outfit_tracker[session_id]:
                    del outfit_tracker[session_id]["skirt"]
                if "bottom" in outfit_tracker[session_id]:
                    del outfit_tracker[session_id]["bottom"]
            
            # Add/update the garment
            outfit_tracker[session_id][normalized_type] = garment_path

        print(f"Current outfit for session {session_id}: {outfit_tracker[session_id]}")

        # Build the complete outfit
        result_url = build_outfit(outfit_tracker[session_id], session_id)

        if result_url:
            return jsonify({
                "success": True,
                "url": result_url,
                "type": normalized_type,
                "current_outfit": list(outfit_tracker[session_id].keys()),
                "worn_items": {k: os.path.basename(v) for k, v in outfit_tracker[session_id].items()}
            })

        return jsonify({"success": False, "error": "Image processing failed"}), 500

    except Exception as e:
        print("Server Error:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------ CLEAR OUTFIT ------------------
@app.route("/clear_outfit", methods=["POST"])
def clear_outfit_endpoint():
    try:
        if 'user_id' in session:
            session_id = session['user_id']
            if session_id in outfit_tracker:
                outfit_tracker[session_id] = {}
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------ DELETE ITEM ------------------
@app.route("/delete_item", methods=["POST"])
def delete_item():
    try:
        data = request.json
        image_url = data.get("image_url")
        
        if not image_url:
            return jsonify({"success": False, "error": "No image URL provided"}), 400
        
        # Extract filename and construct path
        filename = os.path.basename(image_url)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Delete the file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "File not found"}), 404
            
    except Exception as e:
        print("Delete error:", e)
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------ AUTH ------------------
@app.route("/auth", methods=["GET", "POST"])
def auth():
    mode = request.args.get("mode", "login")
    is_login_mode = (mode == "login")
    error_msg = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        action = request.form.get("action")

        if not username or not password:
            error_msg = "Please fill both fields."
        else:
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)

                if action == "signup":
                    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
                    if cursor.fetchone():
                        error_msg = "Username already taken!"
                    else:
                        hashed_password = generate_password_hash(password)
                        cursor.execute(
                            "INSERT INTO users (username, password) VALUES (%s, %s)",
                            (username, hashed_password)
                        )
                        conn.commit()
                        return redirect(url_for("auth", mode="login"))

                elif action == "login":
                    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
                    user = cursor.fetchone()
                    if user and check_password_hash(user['password'], password):
                        session['username'] = username
                        return redirect(url_for("menu"))
                    else:
                        error_msg = "Invalid username or password."

            except mysql.connector.Error as e:
                error_msg = f"Database error: {e}"

            finally:
                if cursor:
                    cursor.close()
                if conn and conn.is_connected():
                    conn.close()

    return render_template(
        "auth.html",
        is_login_mode=is_login_mode,
        error_msg=error_msg
    )

# ------------------ RUN APP ------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)