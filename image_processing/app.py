from flask import Flask, request, send_file
from flask_cors import CORS
from processing import fit_on_dummy 
import os

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return "No image part", 400
        
    file = request.files['image']
    g_type = request.form.get('type', 'top') 
    
    # Use a generic name for the temp file
    temp_path = "temp_garment.png"
    file.save(temp_path)
    
    # Run the fit function
    result_path = fit_on_dummy(temp_path, g_type)
    
    if result_path and os.path.exists(result_path):
        return send_file(result_path, mimetype='image/png')
    else:
        return "Processing Failed", 500

if __name__ == '__main__':
    app.run(port=5000, debug=True) # Added debug=True to see errors in console