#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HyperPresenter Studio - Core Assembly Utilities
Universal asset locator, automated face tracking, programmatic asset generator,
and native JianYing/CapCut draft indexing.
"""

import os
import sys
import glob
import json
import time
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def get_project_root() -> Path:
    """Returns absolute path of the hyper-presenter-studio repository root."""
    return Path(__file__).resolve().parent.parent


def find_presenter_video(presenter_dir: str = None) -> Path:
    """Dynamically finds the presenter talking-head video file."""
    if presenter_dir is None:
        presenter_dir = get_project_root() / "03_presenter_aroll"
    else:
        presenter_dir = Path(presenter_dir)

    patterns = ["*.mp4", "*.mov", "*.m4v", "*.webm"]
    candidates = []
    for pat in patterns:
        candidates.extend(presenter_dir.glob(pat))

    if not candidates:
        return None

    # Priority 1: Exact presenter.mp4
    for c in candidates:
        if c.name.lower() == "presenter.mp4":
            return c

    # Priority 2: Contains presenter
    for c in candidates:
        if "presenter" in c.name.lower():
            return c

    # Priority 3: Most recently modified video file
    candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return candidates[0]


def find_broll_video(output_dir: str = None) -> Path:
    """Dynamically finds the rendered HyperFrames B-roll video."""
    if output_dir is None:
        output_dir = get_project_root() / "output"
    else:
        output_dir = Path(output_dir)

    candidates = [
        output_dir / "broll_motion.mp4",
        output_dir / "reasonix_broll_10s.mp4",
    ]
    for c in candidates:
        if c.exists() and c.stat().st_size > 0:
            return c

    # Fallback to any mp4 in output
    all_mp4s = list(output_dir.glob("*.mp4"))
    if all_mp4s:
        all_mp4s.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return all_mp4s[0]
    return None


def ensure_audio_wav(presenter_video_path: Path) -> Path:
    """Extracts or verifies clean audio wav from presenter video."""
    audio_path = presenter_video_path.parent / "presenter.wav"
    if audio_path.exists() and audio_path.stat().st_size > 1000:
        return audio_path

    # Extract audio via ffmpeg
    cmd = [
        "ffmpeg", "-y",
        "-i", str(presenter_video_path),
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        str(audio_path)
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"⚠️ Warning: Could not extract separate audio WAV: {e}")
        return None
    return audio_path


THEME_RING_COLORS = {
    "ink-wash": {
        "glow": (220, 38, 38),       # 朱砂红光晕
        "core": (220, 38, 38),       # 朱砂印泥实心环
        "highlight": (217, 119, 6)   # 琥珀金高光
    },
    "prismatic-aurora": {
        "glow": (56, 189, 248),
        "core": (244, 114, 182),
        "highlight": (251, 191, 36)
    },
    "cyber-dark": {
        "glow": (56, 189, 248),
        "core": (56, 189, 248),
        "highlight": (255, 255, 255)
    },
    "matrix-neon": {
        "glow": (16, 185, 129),
        "core": (16, 185, 129),
        "highlight": (167, 243, 208)
    },
    "cyber-purple": {
        "glow": (192, 132, 252),
        "core": (192, 132, 252),
        "highlight": (244, 114, 182)
    },
    "ai-coach": {
        "glow": (245, 158, 11),       # 暖金光晕
        "core": (234, 88, 12),        # 复古砖橙/印泥
        "highlight": (251, 191, 36)   # 荧光亮金高光
    }
}


def ensure_ring_and_mask(bubble_size: int = 440, theme: str = "ink-wash"):
    """
    Returns (mask_3ch, ring_rgb_bgr, ring_alpha_3ch).
    Generates theme-aware glowing rings and circular masks with Pillow.
    """
    assets_dir = get_project_root() / "assets"
    assets_dir.mkdir(exist_ok=True)

    theme_info = THEME_RING_COLORS.get(theme, THEME_RING_COLORS["ink-wash"])
    ring_path = assets_dir / f"circle_ring_{theme}.png"
    mask_path = assets_dir / "circle_mask.png"

    # Generate circle mask if missing
    if not mask_path.exists():
        mask_img = Image.new("L", (bubble_size, bubble_size), 0)
        draw = ImageDraw.Draw(mask_img)
        draw.ellipse((2, 2, bubble_size - 2, bubble_size - 2), fill=255)
        mask_img.save(mask_path)

    # Generate theme-aware ring if missing
    if not ring_path.exists():
        ring_img = Image.new("RGBA", (bubble_size, bubble_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(ring_img)
        glow_rgb = theme_info["glow"]
        core_rgb = theme_info["core"]
        hi_rgb = theme_info["highlight"]

        # Outer glow
        for width_delta in range(6, 0, -1):
            alpha = int(45 / width_delta)
            draw.ellipse(
                (width_delta, width_delta, bubble_size - width_delta, bubble_size - width_delta),
                outline=(glow_rgb[0], glow_rgb[1], glow_rgb[2], alpha),
                width=3
            )
        # Inner solid core
        draw.ellipse((3, 3, bubble_size - 3, bubble_size - 3), outline=(core_rgb[0], core_rgb[1], core_rgb[2], 240), width=4)
        # Highlight accent line
        draw.ellipse((4, 4, bubble_size - 4, bubble_size - 4), outline=(hi_rgb[0], hi_rgb[1], hi_rgb[2], 200), width=1)
        ring_img.save(ring_path)

    mask_img = Image.open(mask_path).convert("L")
    if mask_img.size != (bubble_size, bubble_size):
        mask_img = mask_img.resize((bubble_size, bubble_size), Image.Resampling.LANCZOS)
    mask_np = np.array(mask_img).astype(np.float32) / 255.0
    mask_3ch = np.dstack([mask_np, mask_np, mask_np])

    ring_img = Image.open(ring_path).convert("RGBA")
    if ring_img.size != (bubble_size, bubble_size):
        ring_img = ring_img.resize((bubble_size, bubble_size), Image.Resampling.LANCZOS)
    ring_np = np.array(ring_img)
    ring_rgb_bgr = ring_np[:, :, :3][:, :, ::-1].astype(np.float32)
    ring_alpha = ring_np[:, :, 3].astype(np.float32) / 255.0
    ring_alpha_3ch = np.dstack([ring_alpha, ring_alpha, ring_alpha])

    return mask_3ch, ring_rgb_bgr, ring_alpha_3ch


def ensure_rounded_rect_window_assets(width: int = 560, height: int = 740, radius: int = 22, theme: str = "ai-coach", border_width: int = 2):
    """
    Returns (mask_3ch, border_rgb_bgr, border_alpha_3ch).
    Generates anti-aliased rounded rectangle mask and theme-aware inner/outer border frame.
    """
    theme_info = THEME_RING_COLORS.get(theme, THEME_RING_COLORS["ai-coach"])
    core_rgb = theme_info["core"]
    glow_rgb = theme_info["glow"]

    # 1. Anti-aliased rounded rectangle mask
    mask_img = Image.new("L", (width, height), 0)
    draw_mask = ImageDraw.Draw(mask_img)
    draw_mask.rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)
    mask_img = mask_img.filter(ImageFilter.GaussianBlur(radius=0.75))
    mask_arr = np.array(mask_img).astype(np.float32) / 255.0
    mask_3ch = np.repeat(mask_arr[:, :, np.newaxis], 3, axis=2)

    # 2. Sleek theme border
    border_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_border = ImageDraw.Draw(border_img)
    draw_border.rounded_rectangle(
        (0, 0, width - 1, height - 1),
        radius=radius,
        outline=(glow_rgb[0], glow_rgb[1], glow_rgb[2], 90),
        width=border_width + 1
    )
    draw_border.rounded_rectangle(
        (1, 1, width - 2, height - 2),
        radius=radius,
        outline=(core_rgb[0], core_rgb[1], core_rgb[2], 220),
        width=border_width
    )
    border_arr = np.array(border_img).astype(np.float32)
    border_rgb_bgr = border_arr[:, :, :3][:, :, ::-1]  # RGB to BGR
    border_alpha_3ch = np.repeat(border_arr[:, :, 3:4] / 255.0, 3, axis=2)

    return mask_3ch, border_rgb_bgr, border_alpha_3ch


def auto_track_face_rect(presenter_path: Path, total_frames: int, fps: float, target_w: int = 560, target_h: int = 740):
    """
    Automated Face Tracking for rectangular windows.
    Calculates the exact (x1, y1, crop_w, crop_h) to crop from the presenter video for each frame,
    keeping the speaker's face comfortably centered around 33% vertical height (golden eye level).
    """
    cap = cv2.VideoCapture(str(presenter_path))
    fg_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 544
    fg_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 960

    target_ratio = target_w / float(target_h)
    source_ratio = fg_w / float(fg_h)

    if source_ratio < target_ratio:
        crop_w = fg_w
        crop_h = int(fg_w / target_ratio)
    else:
        crop_h = fg_h
        crop_w = int(fg_h * target_ratio)

    default_cx = fg_w / 2.0
    default_cy = fg_h * 0.42

    cascade_loaded = False
    face_cascade = None
    if hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
        cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        if os.path.exists(cascade_path) and hasattr(cv2, "CascadeClassifier"):
            try:
                face_cascade = cv2.CascadeClassifier(cascade_path)
                cascade_loaded = True
            except Exception:
                cascade_loaded = False

    trajectory = []
    last_cx, last_cy = default_cx, default_cy
    step = 5
    sampled_centers = {}

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % step == 0:
            detected = False
            if cascade_loaded and face_cascade is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=4, minSize=(100, 100))
                if len(faces) > 0:
                    fx, fy, fw, fh = max(faces, key=lambda b: b[2] * b[3])
                    last_cx = fx + fw / 2.0
                    last_cy = fy + fh / 2.0
                    detected = True

            if not detected:
                ycrcb = cv2.cvtColor(frame[:int(fg_h * 0.8), :], cv2.COLOR_BGR2YCrCb)
                mask = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if cnts:
                    valid_cnts = [c for c in cnts if cv2.contourArea(c) > 5000]
                    if valid_cnts:
                        c = max(valid_cnts, key=cv2.contourArea)
                        x, y, w, h = cv2.boundingRect(c)
                        last_cx = x + w / 2.0
                        last_cy = y + h / 2.0

            sampled_centers[frame_idx] = (last_cx, last_cy)
        frame_idx += 1

    cap.release()

    ema_cx, ema_cy = default_cx, default_cy
    alpha = 0.18

    for i in range(total_frames):
        sample_key = (i // step) * step
        target_cx, target_cy = sampled_centers.get(sample_key, (last_cx, last_cy))
        ema_cx = alpha * target_cx + (1.0 - alpha) * ema_cx
        ema_cy = alpha * target_cy + (1.0 - alpha) * ema_cy

        clamp_x = max(0, min(fg_w - crop_w, int(ema_cx - crop_w / 2.0)))
        clamp_y = max(0, min(fg_h - crop_h, int(ema_cy - 0.33 * crop_h)))
        trajectory.append((clamp_x, clamp_y, crop_w, crop_h))

    return trajectory



def auto_track_face(presenter_path: Path, total_frames: int, fps: float, crop_size: int = 490):
    """
    Automated Face Tracking & Re-centering Engine.
    Samples video frames, tracks face center (cx, cy), applies EMA smoothing and forward-fill.
    Falls back gracefully to upper-third golden framing if no face is detected.
    """
    cap = cv2.VideoCapture(str(presenter_path))
    fg_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 544
    fg_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 960

    # Default fallback: centered horizontally, 40% height (eye level upper third)
    default_cx = fg_w / 2.0
    default_cy = fg_h * 0.45

    # Check for OpenCV Haar Cascades
    cascade_loaded = False
    face_cascade = None
    if hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
        cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        if os.path.exists(cascade_path) and hasattr(cv2, "CascadeClassifier"):
            try:
                face_cascade = cv2.CascadeClassifier(cascade_path)
                cascade_loaded = True
            except Exception:
                cascade_loaded = False

    trajectory = []
    last_cx, last_cy = default_cx, default_cy

    # Sample rate for detection: every 5 frames (~6 times/sec) to ensure real-time speed
    step = 5
    sampled_centers = {}

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % step == 0:
            detected = False
            if cascade_loaded and face_cascade is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=4, minSize=(100, 100))
                if len(faces) > 0:
                    # Choose largest face
                    fx, fy, fw, fh = max(faces, key=lambda b: b[2] * b[3])
                    last_cx = fx + fw / 2.0
                    last_cy = fy + fh / 2.0
                    detected = True

            if not detected:
                # Skin color centroid heuristic in upper 80% of frame
                ycrcb = cv2.cvtColor(frame[:int(fg_h * 0.8), :], cv2.COLOR_BGR2YCrCb)
                mask = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if cnts:
                    valid_cnts = [c for c in cnts if cv2.contourArea(c) > 5000]
                    if valid_cnts:
                        c = max(valid_cnts, key=cv2.contourArea)
                        x, y, w, h = cv2.boundingRect(c)
                        last_cx = x + w / 2.0
                        last_cy = y + h / 2.0

            sampled_centers[frame_idx] = (last_cx, last_cy)
        frame_idx += 1

    cap.release()

    # Interpolate & EMA smooth across all frames
    ema_cx, ema_cy = default_cx, default_cy
    alpha = 0.18  # EMA smoothing factor (lower = smoother camera glide)

    for i in range(total_frames):
        # Find nearest sampled center
        sample_key = (i // step) * step
        target_cx, target_cy = sampled_centers.get(sample_key, (last_cx, last_cy))

        ema_cx = alpha * target_cx + (1.0 - alpha) * ema_cx
        ema_cy = alpha * target_cy + (1.0 - alpha) * ema_cy

        # Boundary clamping so crop box stays strictly inside presenter frame
        clamp_x = max(0, min(fg_w - crop_size, int(ema_cx - crop_size / 2.0)))
        clamp_y = max(0, min(fg_h - crop_size, int(ema_cy - crop_size / 2.0)))
        trajectory.append((clamp_x, clamp_y))

    return trajectory


def get_jianying_draft_root() -> Path:
    """Detect default JianYing / CapCut Pro drafts folder across platforms."""
    home = Path.home()
    system = sys.platform

    if system == "win32":
        candidates = [
            home / "AppData" / "Local" / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft",
            home / "AppData" / "Local" / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft",
        ]
        for c in candidates:
            if c.exists():
                return c
        return candidates[0]
    elif system == "darwin":
        candidates = [
            home / "Movies" / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft",
            home / "Movies" / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft",
        ]
        for c in candidates:
            if c.exists():
                return c
        return candidates[0]
    return home / ".jianying" / "drafts"


def register_jianying_draft_index(draft_root: Path, draft_id: str, draft_folder_name: str, draft_name: str):
    """
    Registers the newly generated draft in JianYing's root_meta_info.json index database.
    Ensures the draft appears in the desktop app's Recent Projects list.
    """
    index_file = draft_root / "root_meta_info.json"
    data = {"all_draft_store": []}
    if index_file.exists():
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"all_draft_store": []}

    draft_store = data.get("all_draft_store", [])

    # Remove existing entry if duplicate
    draft_store = [d for d in draft_store if d.get("draft_id") != draft_id and d.get("draft_name") != draft_name]

    # Prepend new draft
    new_entry = {
        "draft_id": draft_id,
        "draft_name": draft_name,
        "draft_fold_path": str(draft_root / draft_folder_name),
        "tm_draft_create": int(time.time() * 1000000),
        "tm_draft_modified": int(time.time() * 1000000),
        "draft_version": 6000,
        "creator": "chatcut_desktop_engine"
    }
    draft_store.insert(0, new_entry)
    data["all_draft_store"] = draft_store

    try:
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"📑 Registered draft in JianYing index: {draft_name}")
    except Exception as e:
        print(f"⚠️ Warning: Could not update root_meta_info.json: {e}")
