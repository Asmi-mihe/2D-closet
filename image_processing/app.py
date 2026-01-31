from flask import Flask, request, send_file
from flask_cors import CORS
from processing import fit_on_dummy # This connects to your script!
import os

app = Flask(__name__)
CORS(app) # This lets the website talk to the python code

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['image']
    g_type = request.form.get('type') # 'top', 'bottom', or 'dress'
    
    # Save the user's upload temporarily
    temp_path = "user_upload.jpg"
    file.save(temp_path)
    
    # Run your magic processing code
    result_image = fit_on_dummy(temp_path, g_type)
    
    # Send the final "dressed dummy" back to the website
    return send_file(result_image, mimetype='image/png')

if __name__ == '__main__':
    app.run(port=5000)