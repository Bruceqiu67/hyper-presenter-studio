import os
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import subprocess

def smooth_interp(keyframes, t):
    """Hermite / smoothstep interpolation across keyframe points (t_i, val_i)."""
    if t <= keyframes[0][0]:
        return keyframes[0][1]
    if t >= keyframes[-1][0]:
        return keyframes[-1][1]
    
    for i in range(len(keyframes) - 1):
        t0, v0 = keyframes[i]
        t1, v1 = keyframes[i+1]
        if t0 <= t <= t1:
            ratio = (t - t0) / (t1 - t0)
            # Smoothstep curve: 3*x^2 - 2*x^3
            smooth_ratio = ratio * ratio * (3 - 2 * ratio)
            return v0 + (v1 - v0) * smooth_ratio
    return keyframes[-1][1]

def main():
    root_dir = "d:/video/视频3/hyper-presenter-studio"
    broll_path = os.path.join(root_dir, "output", "reasonix_broll_10s.mp4")
    presenter_path = os.path.join(root_dir, "03_presenter_aroll", "713dcf459dcaaf58953ccb8307874a8e.mp4")
    audio_path = os.path.join(root_dir, "03_presenter_aroll", "presenter.wav")
    ring_path = os.path.join(root_dir, "output", "circle_ring.png")
    output_temp = os.path.join(root_dir, "output", "temp_bubble_tracked.mp4")
    final_output = os.path.join(root_dir, "output", "face_bubble_optimized_1920x1080.mp4")

    # Keyframes for Face Center (t in seconds, cx, cy)
    # Calibrated from 12 probe frames
    kf_cx = [
        (0.0, 272),
        (1.2, 280),
        (2.0, 340),
        (3.0, 330),
        (4.0, 340),
        (5.0, 350),
        (6.0, 350),
        (7.0, 370),
        (8.5, 370),
        (9.5, 350),
        (10.5, 330),
        (12.0, 340),
    ]

    kf_cy = [
        (0.0, 620),  # presenter sitting back, head lower
        (1.2, 540),
        (2.0, 460),  # leaning in
        (3.0, 480),
        (4.0, 500),
        (5.0, 490),
        (6.0, 480),
        (7.0, 510),
        (8.5, 550),
        (9.5, 580),  # gesturing
        (10.5, 550),
        (12.0, 540),
    ]

    # Bubble dimensions
    bubble_size = 440
    crop_size = 490  # Square crop size from presenter 544x960 video

    # Target placement on 1920x1080 canvas
    # Bottom right corner: 60px margin
    bx = 1920 - bubble_size - 60  # 1420
    by = 1080 - bubble_size - 60  # 580

    # Load & prepare alpha mask (feathered edge for anti-aliasing)
    mask_img = Image.new("L", (bubble_size, bubble_size), 0)
    draw = ImageDraw.Draw(mask_img)
    draw.ellipse((2, 2, bubble_size - 2, bubble_size - 2), fill=255)
    mask_np = np.array(mask_img).astype(np.float32) / 255.0
    mask_3ch = np.dstack([mask_np, mask_np, mask_np])

    # Load ring with RGBA
    ring_img = Image.open(ring_path).convert("RGBA")
    ring_np = np.array(ring_img)
    ring_rgb = ring_np[:, :, :3]
    ring_alpha = (ring_np[:, :, 3].astype(np.float32) / 255.0)
    ring_alpha_3ch = np.dstack([ring_alpha, ring_alpha, ring_alpha])

    # Open video captures
    cap_bg = cv2.VideoCapture(broll_path)
    cap_fg = cv2.VideoCapture(presenter_path)

    fps = cap_bg.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap_bg.get(cv2.CAP_PROP_FRAME_COUNT)) or 300
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_temp, fourcc, fps, (1920, 1080))

    fg_w = int(cap_fg.get(cv2.CAP_PROP_FRAME_WIDTH))
    fg_h = int(cap_fg.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Rendering {total_frames} frames at {fps} fps...")

    for frame_idx in range(total_frames):
        ret_bg, frame_bg = cap_bg.read()
        ret_fg, frame_fg = cap_fg.read()

        if not ret_bg:
            break
        if not ret_fg:
            # Loop or hold last frame if presenter ends early
            cap_fg.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret_fg, frame_fg = cap_fg.read()

        t = frame_idx / fps
        cx = smooth_interp(kf_cx, t)
        cy = smooth_interp(kf_cy, t)

        # Calculate crop bounds
        x1 = int(cx - crop_size / 2)
        y1 = int(cy - crop_size / 2)

        # Clamping
        x1 = max(0, min(fg_w - crop_size, x1))
        y1 = max(0, min(fg_h - crop_size, y1))
        x2 = x1 + crop_size
        y2 = y1 + crop_size

        crop = frame_fg[y1:y2, x1:x2]
        crop_resized = cv2.resize(crop, (bubble_size, bubble_size), interpolation=cv2.INTER_LANCZOS4)

        # ROI on canvas
        roi = frame_bg[by:by+bubble_size, bx:bx+bubble_size].astype(np.float32)
        crop_float = crop_resized.astype(np.float32)

        # Blend circular face into background
        blended = roi * (1.0 - mask_3ch) + crop_float * mask_3ch

        # Overlay glowing neon ring
        ring_rgb_bgr = ring_rgb[:, :, ::-1].astype(np.float32)  # RGB to BGR
        final_bubble = blended * (1.0 - ring_alpha_3ch) + ring_rgb_bgr * ring_alpha_3ch

        # Put back into background frame
        frame_bg[by:by+bubble_size, bx:bx+bubble_size] = np.clip(final_bubble, 0, 255).astype(np.uint8)

        writer.write(frame_bg)

        if frame_idx % 60 == 0:
            print(f"Processed frame {frame_idx}/{total_frames} (t={t:.2f}s, cx={cx:.1f}, cy={cy:.1f})")

    cap_bg.release()
    cap_fg.release()
    writer.release()
    print("Video rendering complete! Now muxing audio...")

    # Mux audio using ffmpeg
    cmd = [
        "ffmpeg", "-y",
        "-i", output_temp,
        "-i", audio_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        final_output
    ]
    subprocess.run(cmd, check=True)
    print(f"Final output generated at: {final_output}")

    # Clean up temp video
    if os.path.exists(output_temp):
        os.remove(output_temp)

if __name__ == "__main__":
    main()
