import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

frames_data = [
    ("frame_01.jpg", 0.0, 272, 620),
    ("frame_02.jpg", 1.0, 280, 520),
    ("frame_03.jpg", 2.0, 350, 460),
    ("frame_04.jpg", 3.0, 330, 480),
    ("frame_05.jpg", 4.0, 340, 500),
    ("frame_06.jpg", 5.0, 350, 490),
    ("frame_07.jpg", 6.0, 350, 480),
    ("frame_08.jpg", 7.0, 370, 510),
    ("frame_09.jpg", 8.0, 370, 550),
    ("frame_10.jpg", 9.0, 350, 580),
    ("frame_11.jpg", 10.0, 330, 550),
    ("frame_12.jpg", 11.0, 340, 540),
]

output_dir = "d:/video/视频3/hyper-presenter-studio/output"
frames_dir = os.path.join(output_dir, "frames")
test_out_dir = os.path.join(output_dir, "test_crops")
os.makedirs(test_out_dir, exist_ok=True)

# We want circular bubble size = 440x440
bubble_size = 440
crop_size = 480

# Create high-quality circular mask
mask = Image.new("L", (bubble_size, bubble_size), 0)
draw = ImageDraw.Draw(mask)
draw.ellipse((0, 0, bubble_size, bubble_size), fill=255)

# Load ring
ring_path = os.path.join(output_dir, "circle_ring.png")
ring = Image.open(ring_path).convert("RGBA")

for fname, t, cx, cy in frames_data:
    fpath = os.path.join(frames_dir, fname)
    if not os.path.exists(fpath):
        continue
    
    # Read image safely with numpy
    data = np.fromfile(fpath, dtype=np.uint8)
    img_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
    h, w, _ = img_bgr.shape
    
    # Calculate crop coordinates
    x1 = int(cx - crop_size / 2)
    y1 = int(cy - crop_size / 2)
    
    # Clamp
    x1 = max(0, min(w - crop_size, x1))
    y1 = max(0, min(h - crop_size, y1))
    x2 = x1 + crop_size
    y2 = y1 + crop_size
    
    crop = img_bgr[y1:y2, x1:x2]
    crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    
    pil_crop = Image.fromarray(crop_rgb).resize((bubble_size, bubble_size), Image.Resampling.LANCZOS)
    
    # Apply circular mask
    bubble = Image.new("RGBA", (bubble_size, bubble_size), (0, 0, 0, 0))
    bubble.paste(pil_crop, (0, 0), mask)
    
    # Composite ring
    bubble = Image.alpha_composite(bubble, ring)
    
    # Save preview
    out_fpath = os.path.join(test_out_dir, f"bubble_{fname.replace('.jpg', '.png')}")
    bubble.save(out_fpath)
    print(f"Generated {out_fpath} (crop=({x1},{y1},{crop_size},{crop_size}))")
