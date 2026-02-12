# 2D Closet – Virtual Outfit Builder

2D Closet is a web-based virtual wardrobe application that allows users to upload clothing items, organize them digitally, and create outfits by layering garments on a 2D avatar.

The system performs background removal, automatic garment detection, intelligent scaling, and layered outfit composition using computer vision techniques.

## Features

* User authentication (Sign up / Login)    
* Upload and store clothing items      
* Automatic garment type detection (top, bottom, skirt, dress)    
* AI-based background removal     
* 2D virtual try-on using image layering     
* Multi-garment outfit building    
* Session-based outfit tracking     
* Clothing image validation (prevents face/body uploads)     
* Delete and manage wardrobe items    

## Technologies Used

* **Python**
* **Flask**
* **MySQL**
* **OpenCV**
* **Rembg**
* **NumPy**
* **Pillow (PIL)**
* **Werkzeug Security**
* **HTML, CSS, JavaScript**

## System Architecture

The application follows a client–server architecture:

* The frontend allows users to upload and select clothing items.     
* The Flask backend processes images using OpenCV and Rembg.      
* Clothing images are layered on a base avatar dynamically.     
* User authentication data is stored in a MySQL database.     
* Processed outfit images are returned to the frontend for display.
  
##  Project Structure
```
2D-Closet/
│
├── app.py                     # Main Flask application
├── processing.py              # Image processing & outfit building logic
├── upload.py                  # Upload handling utilities
├── .gitignore
│
├── database/
│   ├── 2D_closet.sql          # Database schema
│   ├── theUltimateConnector.py
│   └── users.json
│
├── image_processing/
│   └── test_pants.png
│
├── static/
│   ├── style.css
│   ├── menu.css
│   ├── images/
│   │   ├── avatar.png
│   │   ├── logo.png
│   │   └── other UI assets
│   └── uploads/               # Uploaded & processed clothing images
│
├── templates/
│   ├── index.html
│   ├── auth.html
│   ├── menu.html
│   └── closet.html
│
├── frontend/                  # Frontend-related files (if expanded)
├── backend/                   # Backend modules (if expanded)
└── README.md
```

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/2D-Closet.git
cd 2D-Closet
```

### 2️. Install dependencies

```bash
pip install flask flask-cors mysql-connector-python opencv-python numpy pillow rembg
```

### 3️. Configure MySQL

* Create a database (e.g., `closet_asmi`)
* Create a `users` table:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```

* Update database credentials inside `app.py`

### 4️. Run the application

```bash
python app.py
```

Then open:

```
http://127.0.0.1:5000
```

---

##  How It Works

1. User uploads a clothing image.
2. The system validates the image.
3. Background is removed using Rembg.
4. The garment is resized and positioned proportionally.
5. Multiple garments are layered in correct order.
6. Final outfit image is generated and displayed.

## Limitations

* 2D overlay only (no 3D body mapping)
* Basic garment detection logic
* Local storage (not cloud-based yet)
  
## License

This project is developed for academic purposes.
