import cv2
import numpy as np
from rembg import remove
from PIL import Image

def fit_on_dummy(input_path, garment_type):
    dummy = cv2.imread('dummy.png', cv2.IMREAD_UNCHANGED)
    if dummy is None:
        print("Error: Could not find 'dummy.png'")
        return None

    # Process garment
    input_img = Image.open(input_path)
    no_bg = remove(input_img)
    cv_garment = cv2.cvtColor(np.array(no_bg), cv2.COLOR_RGBA2BGRA)
    
    # Crop to content
    alpha = cv_garment[:,:,3]
    y, x = np.where(alpha > 0)
    cropped = cv_garment[np.min(y):np.max(y), np.min(x):np.max(x)]
    h, w = cropped.shape[:2]

    # --- COORDINATE FIXES FOR 561x998 DUMMY ---
    # Center X is 280
    if garment_type == "top" or garment_type == "dress":
        # Anchoring to the top of the shoulders/base of neck
        target_width = 240  # Increased to actually cover the dummy's shoulders
        scale = target_width / w
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        anchor_x = (561 - new_w) // 2
        anchor_y = 285 # Moved down from your original to sit on the shoulders

    elif garment_type == "bottom":
        target_width = 160 # Waist width
        scale = target_width / w
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        anchor_x = (561 - new_w) // 2
        anchor_y = 480 # Hip/Waist line
    
    resized = cv2.resize(cropped, (new_w, new_h))

    # Overlay with alpha blending
    end_y = min(anchor_y + resized.shape[0], 998)
    end_x = min(anchor_x + resized.shape[1], 561)
    overlay_part = resized[:end_y-anchor_y, :end_x-anchor_x]

    for c in range(0, 3):
        alpha_s = overlay_part[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        dummy[anchor_y:end_y, anchor_x:end_x, c] = \
            (alpha_s * overlay_part[:, :, c] + 
             alpha_l * dummy[anchor_y:end_y, anchor_x:end_x, c])

    # Final result
    result_path = f"final_look_{garment_type}.png"
    cv2.imwrite(result_path, dummy)
    return result_path