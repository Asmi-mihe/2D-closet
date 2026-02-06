import cv2
import numpy as np
from rembg import remove
from PIL import Image

def fit_on_dummy(input_path, garment_type):
    # Load dummy (561x998)
    dummy = cv2.imread('dummy.png', cv2.IMREAD_UNCHANGED)
    
    if dummy is None:
        print("Error: Could not find 'dummy.png'. Make sure it's in the same folder as your script!")
        return None
    
    # Process garment
    try:
        input_img = Image.open(input_path)
    except FileNotFoundError:
        print(f"Error: Could not find '{input_path}'. Check the file path!")
        return None
    
    no_bg = remove(input_img)
    cv_garment = cv2.cvtColor(np.array(no_bg), cv2.COLOR_RGBA2BGRA)
    
    # Crop to content
    alpha = cv_garment[:,:,3]
    y, x = np.where(alpha > 0)
    if len(y) == 0 or len(x) == 0:
        print("Error: No visible content found in the image after background removal!")
        return None
    
    cropped = cv_garment[np.min(y):np.max(y), np.min(x):np.max(x)]
    
    # Key measurements for 561x998 dummy
    if garment_type == "dress":
        shoulder_width = 200
        neck_y = 240
        max_length = 350
        
        h, w = cropped.shape[:2]
        target_w = shoulder_width
        target_h = int(target_w * (h/w))
        
        if target_h > max_length:
            target_h = max_length
            target_w = int(target_h * (w/h))
        
        resized = cv2.resize(cropped, (target_w, target_h))
        anchor_x = (561 - target_w) // 2
        anchor_y = neck_y
        
    elif garment_type == "top":
        shoulder_width = 400
        neck_y = 400 
        max_length = 400
        
        h, w = cropped.shape[:2]
        target_w = shoulder_width
        target_h = int(target_w * (h/w))
        
        if target_h > max_length:
            target_h = max_length
            target_w = int(target_h * (w/h))
        
        resized = cv2.resize(cropped, (target_w, target_h))
        anchor_x = (561 - target_w) // 2
        anchor_y = neck_y
        
    else:  # bottoms
        waist_width = 180
        waist_y = 440
        max_length = 400
        
        h, w = cropped.shape[:2]
        target_w = waist_width
        target_h = int(target_w * (h/w))
        
        if target_h > max_length:
            target_h = max_length
            target_w = int(target_h * (w/h))
        
        resized = cv2.resize(cropped, (target_w, target_h))
        anchor_x = (561 - target_w) // 2
        anchor_y = waist_y
    
    # Ensure we don't go out of bounds
    end_y = min(anchor_y + resized.shape[0], 998)
    end_x = min(anchor_x + resized.shape[1], 561)
    resized_crop = resized[:end_y-anchor_y, :end_x-anchor_x]
    
    # Overlay with alpha blending
    for c in range(0, 3):
        alpha_s = resized_crop[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        dummy[anchor_y:end_y, anchor_x:end_x, c] = \
            (alpha_s * resized_crop[:, :, c] + 
             alpha_l * dummy[anchor_y:end_y, anchor_x:end_x, c])
    
    # Update alpha channel
    dummy[anchor_y:end_y, anchor_x:end_x, 3] = np.maximum(
        dummy[anchor_y:end_y, anchor_x:end_x, 3],
        resized_crop[:, :, 3]
    )
    
    # Save
    result_path = f"final_look_{garment_type}.png"
    cv2.imwrite(result_path, dummy)
    print(f"✓ Saved to {result_path}")
    return result_path

# === HOW TO USE ===
# Make sure these files are in the same folder as your script:
# 1. dummy.png (import cv2
import numpy as np
from rembg import remove
from PIL import Image

def fit_on_dummy(input_path, garment_type):
    # Load dummy (561x998)
    dummy = cv2.imread('dummy.png', cv2.IMREAD_UNCHANGED)
    
    if dummy is None:
        print("Error: Could not find 'dummy.png'")
        return None
    
    # Process garment
    try:
        input_img = Image.open(input_path)
    except FileNotFoundError:
        print(f"Error: Could not find '{input_path}'")
        return None
    
    print("Removing background...")
    no_bg = remove(input_img)
    cv_garment = cv2.cvtColor(np.array(no_bg), cv2.COLOR_RGBA2BGRA)
    
    # Crop to content
    alpha = cv_garment[:,:,3]
    y, x = np.where(alpha > 0)
    if len(y) == 0 or len(x) == 0:
        print("Error: No visible content found!")
        return None
    
    cropped = cv_garment[np.min(y):np.max(y), np.min(x):np.max(x)]
    garment_h, garment_w = cropped.shape[:2]
    
    # EXACT MEASUREMENTS FROM YOUR DUMMY (all in pixels)
    HAIR_TOP = 228  # Calculated from 998 - 770
    NECK_Y = HAIR_TOP + 159  # = 387 (from hair to neck)
    SHOULDER_WIDTH = 160
    CHEST_WIDTH = 109
    WAIST_WIDTH = 74
    BUST_WIDTH = 108
    WAIST_Y = HAIR_TOP + 303  # = 531 (from hair to waist/pant point)
    PANTS_START_Y = WAIST_Y
    PANTS_LENGTH = 404
    TOTAL_HEIGHT = 770  # From hair to bottom
    
    if garment_type == "dress":
        # Analyze garment neckline (top 5%)
        neckline_sample = cropped[0:max(1, int(garment_h*0.05)), :]
        neckline_alpha = neckline_sample[:, :, 3]
        
        neck_widths = []
        for row in neckline_alpha:
            non_zero = np.where(row > 0)[0]
            if len(non_zero) > 10:
                neck_widths.append(non_zero[-1] - non_zero[0])
        
        if neck_widths:
            garment_neck_width = np.median(neck_widths)
        else:
            garment_neck_width = garment_w * 0.4
        
        # Analyze garment shoulder area (5-15% from top)
        shoulder_sample = cropped[int(garment_h*0.05):int(garment_h*0.15), :]
        shoulder_alpha = shoulder_sample[:, :, 3]
        
        shoulder_widths = []
        for row in shoulder_alpha:
            non_zero = np.where(row > 0)[0]
            if len(non_zero) > 20:
                shoulder_widths.append(non_zero[-1] - non_zero[0])
        
        if shoulder_widths:
            garment_shoulder_width = np.median(shoulder_widths)
            # Scale based on shoulders for better fit
            scale = SHOULDER_WIDTH / garment_shoulder_width
        else:
            # Fallback to neck scaling
            scale = CHEST_WIDTH / garment_neck_width
        
        new_w = int(garment_w * scale)
        new_h = int(garment_h * scale)
        
        # Limit to reasonable dress size
        max_width = SHOULDER_WIDTH + 20  # 180px
        max_height = WAIST_Y - NECK_Y + 150  # Neck to below waist (~294px)
        
        if new_w > max_width:
            scale_down = max_width / new_w
            new_w = max_width
            new_h = int(new_h * scale_down)
        
        if new_h > max_height:
            scale_down = max_height / new_h
            new_h = max_height
            new_w = int(new_w * scale_down)
        
        resized = cv2.resize(cropped, (new_w, new_h))
        anchor_x = (561 - new_w) // 2
        anchor_y = NECK_Y
        
    elif garment_type == "top":
        # Analyze neckline
        neckline_sample = cropped[0:max(1, int(garment_h*0.05)), :]
        neckline_alpha = neckline_sample[:, :, 3]
        
        neck_widths = []
        for row in neckline_alpha:
            non_zero = np.where(row > 0)[0]
            if len(non_zero) > 10:
                neck_widths.append(non_zero[-1] - non_zero[0])
        
        if neck_widths:
            garment_neck_width = np.median(neck_widths)
        else:
            garment_neck_width = garment_w * 0.4
        
        # Analyze shoulder area
        shoulder_sample = cropped[int(garment_h*0.05):int(garment_h*0.15), :]
        shoulder_alpha = shoulder_sample[:, :, 3]
        
        shoulder_widths = []
        for row in shoulder_alpha:
            non_zero = np.where(row > 0)[0]
            if len(non_zero) > 20:
                shoulder_widths.append(non_zero[-1] - non_zero[0])
        
        if shoulder_widths:
            garment_shoulder_width = np.median(shoulder_widths)
            scale = SHOULDER_WIDTH / garment_shoulder_width
        else:
            scale = CHEST_WIDTH / garment_neck_width
        
        new_w = int(garment_w * scale)
        new_h = int(garment_h * scale)
        
        # Tops should fit from neck to waist/slightly below
        max_width = SHOULDER_WIDTH + 20  # 180px
        max_height = WAIST_Y - NECK_Y + 20  # Neck to just past waist (~164px)
        
        if new_w > max_width:
            scale_down = max_width / new_w
            new_w = max_width
            new_h = int(new_h * scale_down)
        
        if new_h > max_height:
            scale_down = max_height / new_h
            new_h = max_height
            new_w = int(new_w * scale_down)
        
        resized = cv2.resize(cropped, (new_w, new_h))
        anchor_x = (561 - new_w) // 2
        anchor_y = NECK_Y
        
    else:  # bottoms (skirts, pants, shorts)
        # Analyze waistband (top 5%)
        waist_sample = cropped[0:max(1, int(garment_h*0.05)), :]
        waist_alpha = waist_sample[:, :, 3]
        
        waist_widths = []
        for row in waist_alpha:
            non_zero = np.where(row > 0)[0]
            if len(non_zero) > 10:
                waist_widths.append(non_zero[-1] - non_zero[0])
        
        if waist_widths:
            garment_waist_width = np.median(waist_widths)
        else:
            garment_waist_width = garment_w * 0.8
        
        # Scale based on waist width
        scale = WAIST_WIDTH / garment_waist_width
        
        new_w = int(garment_w * scale)
        new_h = int(garment_h * scale)
        
        # Bottoms can use full pants length
        max_width = WAIST_WIDTH + 40  # 114px
        max_height = PANTS_LENGTH  # 404px (full pant length)
        
        if new_w > max_width:
            scale_down = max_width / new_w
            new_w = max_width
            new_h = int(new_h * scale_down)
        
        if new_h > max_height:
            scale_down = max_height / new_h
            new_h = max_height
            new_w = int(new_w * scale_down)
        
        resized = cv2.resize(cropped, (new_w, new_h))
        anchor_x = (561 - new_w) // 2
        anchor_y = PANTS_START_Y
    
    # Ensure bounds
    end_y = min(anchor_y + resized.shape[0], 998)
    end_x = min(anchor_x + resized.shape[1], 561)
    
    if anchor_y < 0:
        resized = resized[-anchor_y:, :]
        anchor_y = 0
    if anchor_x < 0:
        resized = resized[:, -anchor_x:]
        anchor_x = 0
    
    resized_crop = resized[:end_y-anchor_y, :end_x-anchor_x]
    
    print(f"Garment size: {resized_crop.shape[1]}x{resized_crop.shape[0]}px")
    print(f"Position: ({anchor_x}, {anchor_y})")
    print(f"Type: {garment_type}")
    
    # Overlay with alpha blending
    for c in range(0, 3):
        alpha_s = resized_crop[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        dummy[anchor_y:end_y, anchor_x:end_x, c] = \
            (alpha_s * resized_crop[:, :, c] + 
             alpha_l * dummy[anchor_y:end_y, anchor_x:end_x, c])
    
    # Update alpha channel
    dummy[anchor_y:end_y, anchor_x:end_x, 3] = np.maximum(
        dummy[anchor_y:end_y, anchor_x:end_x, 3],
        resized_crop[:, :, 3]
    )
    
    # Save
    result_path = f"final_look_{garment_type}.png"
    cv2.imwrite(result_path, dummy)
    print(f"✓ Success! Saved to {result_path}")
    return result_path


# === MAIN EXECUTION ===
if __name__ == "__main__":
    # For the pink top/dress
    fit_on_dummy('test_pants.png', 'bottom')
    
    # Or try as dress:
    # fit_on_dummy('test_top.png', 'dress')the base model image you uploaded)
# 2. Your garment image (the pink dress)

# Then run with the correct filename:
fit_on_dummy('test_pants.png', 'bottom')  # If your bottom image is named 'test_bottoms.png'

# OR use the full path:
# fit_on_dummy(r'C:\Users\Acer\Desktop\project\2D-closet\image_processing\your_bottom.png', 'bottom')