import os
from flask import request, jsonify
from PIL import Image
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/wardrobe"

def handle_upload():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Secure the filename
    filename = secure_filename(file.filename)

    # Save temporarily
    temp_path = os.path.join("static/uploads", filename)
    os.makedirs("static/uploads", exist_ok=True)
    file.save(temp_path)

    # Convert to PNG
    img = Image.open(temp_path)
    png_filename = os.path.splitext(filename)[0] + ".png"
    final_path = os.path.join(UPLOAD_FOLDER, png_filename)

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    img.convert("RGBA").save(final_path, "PNG")

    # Delete temp file
    os.remove(temp_path)

    return jsonify({
        "message": "Uploaded successfully",
        "file_path": f"/static/wardrobe/{png_filename}"
    })
