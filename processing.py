import cv2
import numpy as np
from rembg import remove
from PIL import Image
import os
import uuid

# Permanent session cache
fitting_cache = {}
# Track current outfit state per session (in production, use session management)
outfit_state = {}


def fit_on_dummy(input_path, garment_type, base_dummy_path=None, session_id="default"):
    """
    Fits garment on dummy as a flat overlay (sticker-like) without body wrapping.
    Maintains aspect ratio and centers garment at anatomically correct positions.
    
    Args:
        input_path: Path to the garment image
        garment_type: 'top', 'bottom', or 'dress'
        base_dummy_path: Optional path to a previous result to overlay on (for combining garments)
        session_id: Session identifier for tracking outfit state
    
    Returns:
        Relative URL path to the result image
    """
    global fitting_cache, outfit_state
    script_dir = os.path.dirname(os.path.abspath(__file__))
   
    # 1. Check Cache
    cache_key = f"{os.path.basename(input_path)}_{garment_type}"
    if base_dummy_path:
        cache_key = f"{cache_key}_overlay_{os.path.basename(base_dummy_path)}"
    
    if cache_key in fitting_cache:
        return fitting_cache[cache_key]

    # 2. Load Dummy (or previous result for overlay)
    if base_dummy_path and os.path.exists(base_dummy_path):
        dummy = cv2.imread(base_dummy_path, cv2.IMREAD_UNCHANGED)
        print(f"Loading base image from: {base_dummy_path}")
    else:
        dummy_path = os.path.join(script_dir, 'static/images/avatar.png')
        dummy = cv2.imread(dummy_path, cv2.IMREAD_UNCHANGED)
    
    if dummy is None: 
        print("Error: Dummy avatar not found")
        return None

    # Convert to BGRA if needed for consistent alpha handling
    if len(dummy.shape) == 2 or dummy.shape[2] == 3:
        dummy = cv2.cvtColor(dummy, cv2.COLOR_BGR2BGRA)

    # 3. Process Garment
    if not os.path.exists(input_path):
        print(f"Error: Garment image not found: {input_path}")
        return None
        
    input_img = Image.open(input_path).convert("RGBA")
    input_img.thumbnail((1200, 1200))  # Increased for better quality
   
    no_bg = remove(input_img, alpha_matting=False)
    garment_cv = cv2.cvtColor(np.array(no_bg), cv2.COLOR_RGBA2BGRA)
   
    # Auto-Crop to remove empty space
    alpha = garment_cv[:, :, 3]
    y, x = np.where(alpha > 0)
    if len(y) == 0: 
        print("Error: Garment is empty or fully transparent")
        return None
    
    cropped = garment_cv[np.min(y):np.max(y)+1, np.min(x):np.max(x)+1]

    # 4. Get dimensions
    h, w = cropped.shape[:2]
    AV_H, AV_W = dummy.shape[:2]
    
    print(f"Dummy size: {AV_W}x{AV_H}")
    print(f"Original garment size: {w}x{h}")
   
    # 5. Anatomical reference points (proportional to dummy)
    SHOULDER_WIDTH = int(AV_W * 0.46)   # Shoulder span
    WAIST_WIDTH = int(AV_W * 0.42)      # Waist width (slightly wider)
    HIP_WIDTH = int(AV_W * 0.50)        # Hip width
    
    # Vertical anchor points - ADJUSTED for better positioning
    SHOULDER_Y = int(AV_H * 0.21)       # Shoulder line (tops/dresses start here)
    WAIST_Y = int(AV_H * 0.40)          # Waist line (bottoms start here) - MOVED UP
    
    # 6. Calculate target dimensions based on garment type
    # CRITICAL: Maintain aspect ratio - scale by width, then calculate height
    if garment_type == "dress":
        # Dress fits at shoulders, extends downward to feet
        target_w = SHOULDER_WIDTH + 10  # Slightly wider for dress flow
        scale = target_w / w
        target_h = int(h * scale)
        
        # Allow dress to extend to near bottom of dummy
        max_h = int(AV_H - SHOULDER_Y - 15)  # Leave small margin at bottom
        if target_h > max_h:
            target_h = max_h
            target_w = int(target_h * (w / h))  # Recalculate width to maintain ratio
        
        anchor_y = SHOULDER_Y
        print("Fitting DRESS")
        
    elif garment_type == "top":
        # Top fits at shoulders, limited to torso area
        target_w = SHOULDER_WIDTH
        scale = target_w / w
        target_h = int(h * scale)
        
        # Limit to torso length (shoulders to below waist)
        max_top_h = int(WAIST_Y - SHOULDER_Y + 120)
        if target_h > max_top_h:
            target_h = max_top_h
            target_w = int(target_h * (w / h))
        
        anchor_y = SHOULDER_Y
        print("Fitting TOP")
        
    elif garment_type in ["bottom", "skirt", "skirts"]:
        # Bottoms fit at waist/hips - IMPROVED POSITIONING
        target_w = HIP_WIDTH
        scale = target_w / w
        target_h = int(h * scale)
        
        # Allow bottoms to extend down but not off the dummy
        max_bottom_h = int(AV_H - WAIST_Y - 15)  # Leave margin at feet
        if target_h > max_bottom_h:
            target_h = max_bottom_h
            target_w = int(target_h * (w / h))
        
        anchor_y = WAIST_Y
        print(f"Fitting BOTTOM ({garment_type})")
        
    else:
        # Default fallback (treat as top)
        print(f"Warning: Unknown garment type '{garment_type}', defaulting to 'top'")
        target_w = SHOULDER_WIDTH
        scale = target_w / w
        target_h = int(h * scale)
        anchor_y = SHOULDER_Y
    
    print(f"Scaled garment size: {target_w}x{target_h}")
    
    # 7. Resize with high-quality interpolation (maintains aspect ratio)
    resized = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
    
    # 8. Center horizontally on dummy
    anchor_x = (AV_W - target_w) // 2
    
    # Bounds checking
    if anchor_x < 0:
        anchor_x = 0
    if anchor_y < 0:
        anchor_y = 0

    # 9. Calculate overlay region with safety checks
    y1, y2 = anchor_y, min(anchor_y + target_h, AV_H)
    x1, x2 = anchor_x, min(anchor_x + target_w, AV_W)
    
    # Slice the resized garment to fit within bounds
    resized_part = resized[0:y2-y1, 0:x2-x1]
    
    print(f"Placement position: ({x1}, {y1}) to ({x2}, {y2})")

    # 10. Alpha blending for smooth overlay
    alpha_s = resized_part[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s
    
    for c in range(3):
        dummy[y1:y2, x1:x2, c] = (
            alpha_s * resized_part[:, :, c] + 
            alpha_l * dummy[y1:y2, x1:x2, c]
        )
    
    # Update alpha channel
    dummy[y1:y2, x1:x2, 3] = np.maximum(
        dummy[y1:y2, x1:x2, 3],
        resized_part[:, :, 3]
    )

    # 11. Save result
    out_name = f"final_{uuid.uuid4().hex}.png"
    out_path = os.path.join(script_dir, 'static/uploads', out_name)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    cv2.imwrite(out_path, dummy)
    print(f"✓ Saved result to {out_path}")
   
    relative_url = f"/static/uploads/{out_name}"
    fitting_cache[cache_key] = relative_url
    return relative_url


def build_outfit(garments_dict, session_id="default"):
    """
    Builds a complete outfit by layering multiple garments.
    
    Args:
        garments_dict: Dictionary with keys 'top', 'bottom', 'dress' containing file paths
                      Example: {'top': 'path/to/shirt.png', 'bottom': 'path/to/pants.png'}
        session_id: Session identifier
    
    Returns:
        Relative URL path to the final combined result
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_path = os.path.join(script_dir, 'static/images/avatar.png')
    
    # Order matters: dress first (if present), then bottom, then top
    # This ensures tops appear over bottoms
    order = ['dress', 'bottom', 'skirt', 'skirts', 'top']
    
    current_base = None
    result_url = None
    
    for garment_type in order:
        if garment_type in garments_dict and garments_dict[garment_type]:
            garment_path = garments_dict[garment_type]
            
            if not os.path.exists(garment_path):
                print(f"Warning: Garment not found: {garment_path}")
                continue
            
            print(f"\n--- Layering {garment_type} ---")
            
            if current_base:
                # Overlay on previous result
                base_path = os.path.join(script_dir, current_base.lstrip('/'))
                result_url = fit_on_dummy(garment_path, garment_type, base_dummy_path=base_path, session_id=session_id)
            else:
                # First garment - use original dummy
                result_url = fit_on_dummy(garment_path, garment_type, session_id=session_id)
            
            if result_url:
                current_base = result_url
    
    return result_url


def clear_outfit_cache(session_id="default"):
    """Clear outfit state for a session"""
    global outfit_state
    if session_id in outfit_state:
        del outfit_state[session_id]