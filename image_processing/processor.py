import cv2
import numpy as np
from rembg import remove
from PIL import Image
import os

def fit_on_dummy(input_path, garment_type):
    # 1. LOAD THE DUMMY (The base layer)
    # Make sure 'dummy.png' is in your folder!
    dummy = cv2.imread('dummy.png', cv2.IMREAD_UNCHANGED)
    
    # 2. PROCESS THE CLOTHES (Remove BG and Crop)
    input_img = Image.open(input_path)
    no_bg = remove(input_img)
    cv_garment = cv2.cvtColor(np.array(no_bg), cv2.COLOR_RGBA2BGRA)
    
    # Auto-crop logic
    alpha = cv_garment[:,:,3]
    y, x = np.where(alpha > 0)
    cropped = cv_garment[np.min(y):np.max(y), np.min(x):np.max(x)]
    
    # 3. SCALE & POSITION (Updated for your dummy)
    if garment_type == "top" or garment_type == "dress":
        target_w = 340  # Made it wider to cover shoulders
        anchor_x = 110  # Centered it based on new width
        anchor_y = 230  # Moved it down from the face to the neck
    else: # bottoms
        target_w = 260
        anchor_x = 150
        anchor_y = 480

    # Resize garment
    h, w = cropped.shape[:2]
    new_h = int(target_w * (h/w))
    resized = cv2.resize(cropped, (target_w, new_h))

    # 4. OVERLAY (The "Paper Doll" part)
    # This places the garment onto the dummy image
    for c in range(0, 3):
        alpha_s = resized[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        dummy[anchor_y:anchor_y+new_h, anchor_x:anchor_x+target_w, c] = \
            (alpha_s * resized[:, :, c] + alpha_l * dummy[anchor_y:anchor_y+new_h, anchor_x:anchor_x+target_w, c])

    # 5. SAVE RESULT
    result_path = f"final_look_{garment_type}.png"
    cv2.imwrite(result_path, dummy)
    print(f"Success! Check {result_path}")
    return result_path

# --- TO RUN THIS FOR ANY USER FILE ---
# You can change these two lines to whatever the user provides!
fit_on_dummy('red.jpg', 'top')