from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_cors import CORS
from processing import fit_on_dummy # Connects to your image logic
import os

app = Flask(__name__)
CORS(app) # Allows your frontend to communicate with this backend

# In-memory "database" for demonstration
users = {}

# ------------------ NAVIGATION & AUTH ROUTES ------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/closet")
def closet():
    return render_template("closet.html")

@app.route("/auth", methods=["GET", "POST"])
def auth():
    mode = request.args.get('mode', 'login')
    is_login_mode = (mode == 'login')
    error_msg = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        action = request.form.get("action")

        if not username or not password:
            error_msg = "Please fill both fields."
        elif action == "login":
            if username in users and users[username] == password:
                return redirect(url_for("menu"))
            else:
                error_msg = "Invalid username or password."
        elif action == "signup":
            if username in users:
                error_msg = "Username already taken!"
            else:
                users[username] = password
                return redirect(url_for("auth", mode="login"))

    return render_template(
        "auth.html",
        is_login_mode=is_login_mode,
        error_msg=error_msg
    )

# ------------------ IMAGE PROCESSING ROUTE ------------------

@app.route('/upload', methods=['POST'])
def upload_file():
    # 1. Get the image and garment type from the request
    if 'image' not in request.files:
        return "No image part", 400
        
    file = request.files['image']
    g_type = request.form.get('type') # Expecting 'top', 'bottom', or 'dress'
    
    if file.filename == '':
        return "No selected file", 400

    # 2. Save the user's upload temporarily
    temp_path = "user_upload.jpg"
    file.save(temp_path)
    
    # 3. Run your magic processing code from processing.py
    # This returns the path to the final image (e.g., 'final_look_top.png')
    result_image_path = fit_on_dummy(temp_path, g_type)
    
    if result_image_path and os.path.exists(result_image_path):
        # 4. Send the final "dressed dummy" back to the website
        return send_file(result_image_path, mimetype='image/png')
    else:
        return "Error processing image", 500

# ------------------ RUN APP ------------------

if __name__ == "__main__":
    # debug=True allows you to see errors in the browser
    app.run(port=5000, debug=True)