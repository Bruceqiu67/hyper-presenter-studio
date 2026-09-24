#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HyperPresenter Studio - 100% Automated ChatCut / CapCut Assembly Engine (Production Overhaul)
Supports both Horizontal (16:9) and Vertical (9:16) compositions.
Zero hardcoded paths. Real automated face tracking. Full 3-scheme implementation.
True JianYing/CapCut desktop draft indexing.
"""

import os
import sys
import json
import uuid
import time
import argparse
import subprocess
from pathlib import Path
import cv2
import numpy as np

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Import core utilities
sys.path.insert(0, str(Path(__file__).resolve().parent))
import core_utils


def safe_unlink(path: Path):
    """Safely unlink a file with retry to avoid Windows file lock race conditions."""
    if not path or not path.exists():
        return
    for _ in range(5):
        try:
            path.unlink()
            return
        except Exception:
            time.sleep(0.1)


def assemble_method_bubble(root_dir: Path, broll_path: Path, presenter_path: Path, audio_path: Path, output_path: Path, ratio: str = "16:9", theme: str = "ink-wash"):
    """
    Method 1: Dynamic Centered Face Bubble.
    Supports both 16:9 (1920x1080) and 9:16 (1080x1920) canvases.
    Automated face tracking with EMA smoothing and freeze-frame hold.
    """
    print(f"\n🚀 [ChatCut Engine] Executing Method 1: Face Bubble (发光圆框动态居中) [{ratio}] (Theme: {theme})")

    is_vertical = (ratio == "9:16")
    canvas_w, canvas_h = (1080, 1920) if is_vertical else (1920, 1080)
    bubble_size = 360 if is_vertical else 440
    crop_size = 490

    # Placement coordinates
    if is_vertical:
        # Bottom-right safe zone in vertical mobile UI (avoiding TikTok/Douyin right side buttons)
        bx = canvas_w - bubble_size - 40  # 680
        by = canvas_h - bubble_size - 220  # 1340 (above bottom caption area)
    else:
        # Bottom-right corner with 60px margin
        bx = canvas_w - bubble_size - 60  # 1420
        by = canvas_h - bubble_size - 60  # 580

    mask_3ch, ring_rgb_bgr, ring_alpha_3ch = core_utils.ensure_ring_and_mask(bubble_size, theme=theme)

    cap_bg = cv2.VideoCapture(str(broll_path))
    cap_fg = cv2.VideoCapture(str(presenter_path))

    fps = cap_bg.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap_bg.get(cv2.CAP_PROP_FRAME_COUNT)) or 300
    temp_video = root_dir / "output" / f"temp_bubble_{ratio.replace(':', '_')}.mp4"

    # Automated Face Tracking
    trajectory = core_utils.auto_track_face(presenter_path, total_frames, fps, crop_size=crop_size)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_video), fourcc, fps, (canvas_w, canvas_h))

    last_valid_fg = None

    for frame_idx in range(total_frames):
        ret_bg, frame_bg = cap_bg.read()
        ret_fg, frame_fg = cap_fg.read()

        if not ret_bg:
            break

        if ret_fg:
            last_valid_fg = frame_fg
        else:
            # Freeze-frame on last frame if presenter is shorter than B-roll
            frame_fg = last_valid_fg if last_valid_fg is not None else np.zeros((960, 544, 3), dtype=np.uint8)

        # Scale background to canvas if needed
        if frame_bg.shape[1] != canvas_w or frame_bg.shape[0] != canvas_h:
            frame_bg = cv2.resize(frame_bg, (canvas_w, canvas_h), interpolation=cv2.INTER_LANCZOS4)

        # Crop using tracked trajectory
        x1, y1 = trajectory[min(frame_idx, len(trajectory) - 1)]
        crop = frame_fg[y1:y1 + crop_size, x1:x1 + crop_size]
        crop_resized = cv2.resize(crop, (bubble_size, bubble_size), interpolation=cv2.INTER_LANCZOS4)

        roi = frame_bg[by:by + bubble_size, bx:bx + bubble_size].astype(np.float32)
        crop_float = crop_resized.astype(np.float32)

        # Blend circular bubble
        blended = roi * (1.0 - mask_3ch) + crop_float * mask_3ch
        final_bubble = blended * (1.0 - ring_alpha_3ch) + ring_rgb_bgr * ring_alpha_3ch
        frame_bg[by:by + bubble_size, bx:bx + bubble_size] = np.clip(final_bubble, 0, 255).astype(np.uint8)

        writer.write(frame_bg)

    cap_bg.release()
    cap_fg.release()
    writer.release()

    # Mux audio via ffmpeg
    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(audio_path if audio_path else presenter_path),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path)
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        print(f"❌ FFmpeg Error in Method 1: {proc.stderr}")
        raise RuntimeError("FFmpeg encoding failed.")

    safe_unlink(temp_video)
    print(f"✅ Method 1 Complete! Output saved to: {output_path}")


def assemble_method_split(root_dir: Path, broll_path: Path, presenter_path: Path, audio_path: Path, output_path: Path, ratio: str = "16:9", theme: str = "ink-wash"):
    """
    Method 2: Full-Canvas Studio Stage Fusion (全屏无损演播室人景融合).
    Keeps B-roll at 100% full scale (1920x1080 or 1080x1920).
    Seamlessly integrates presenter on the dedicated stage pedestal with glowing aurora ring.
    Zero downscaling, zero fragmentation.
    """
    print(f"\n🚀 [ChatCut Engine] Executing Method 2: Full-Canvas Studio Stage Fusion [{ratio}] (Theme: {theme})")

    is_vertical = (ratio == "9:16")
    canvas_w, canvas_h = (1080, 1920) if is_vertical else (1920, 1080)

    cap_bg = cv2.VideoCapture(str(broll_path))
    cap_fg = cv2.VideoCapture(str(presenter_path))

    fps = cap_bg.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap_bg.get(cv2.CAP_PROP_FRAME_COUNT)) or 300
    temp_video = root_dir / "output" / f"temp_stage_{ratio.replace(':', '_')}.mp4"

    if is_vertical:
        bubble_size = 380
        crop_size = 490
        bx = (canvas_w - bubble_size) // 2
        by = canvas_h - bubble_size - 180
        mask_3ch, ring_rgb_bgr, ring_alpha_3ch = core_utils.ensure_ring_and_mask(bubble_size, theme=theme)
        trajectory = core_utils.auto_track_face(presenter_path, total_frames, fps, crop_size=crop_size)
    else:
        # 16:9 Studio Window Perfect Fit: 560x740 rounded window at x:1270, y:221
        bw, bh = 560, 740
        bx = 1270
        by = 221
        radius = 22
        mask_3ch, border_rgb_bgr, border_alpha_3ch = core_utils.ensure_rounded_rect_window_assets(bw, bh, radius=radius, theme=theme)
        trajectory = core_utils.auto_track_face_rect(presenter_path, total_frames, fps, target_w=bw, target_h=bh)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_video), fourcc, fps, (canvas_w, canvas_h))

    last_valid_fg = None

    for frame_idx in range(total_frames):
        ret_bg, frame_bg = cap_bg.read()
        ret_fg, frame_fg = cap_fg.read()

        if not ret_bg:
            break

        if ret_fg:
            last_valid_fg = frame_fg
        else:
            frame_fg = last_valid_fg if last_valid_fg is not None else np.zeros((960, 544, 3), dtype=np.uint8)

        if frame_bg.shape[1] != canvas_w or frame_bg.shape[0] != canvas_h:
            frame_bg = cv2.resize(frame_bg, (canvas_w, canvas_h), interpolation=cv2.INTER_LANCZOS4)

        if is_vertical:
            x1, y1 = trajectory[min(frame_idx, len(trajectory) - 1)]
            crop = frame_fg[y1:y1 + crop_size, x1:x1 + crop_size]
            crop_resized = cv2.resize(crop, (bubble_size, bubble_size), interpolation=cv2.INTER_LANCZOS4)

            roi = frame_bg[by:by + bubble_size, bx:bx + bubble_size].astype(np.float32)
            crop_float = crop_resized.astype(np.float32)

            blended = roi * (1.0 - mask_3ch) + crop_float * mask_3ch
            final_bubble = blended * (1.0 - ring_alpha_3ch) + ring_rgb_bgr * ring_alpha_3ch
            frame_bg[by:by + bubble_size, bx:bx + bubble_size] = np.clip(final_bubble, 0, 255).astype(np.uint8)
        else:
            x1, y1, cw, ch = trajectory[min(frame_idx, len(trajectory) - 1)]
            crop = frame_fg[y1:y1 + ch, x1:x1 + cw]
            crop_resized = cv2.resize(crop, (bw, bh), interpolation=cv2.INTER_LANCZOS4)

            roi = frame_bg[by:by + bh, bx:bx + bw].astype(np.float32)
            crop_float = crop_resized.astype(np.float32)

            blended = roi * (1.0 - mask_3ch) + crop_float * mask_3ch
            final_box = blended * (1.0 - border_alpha_3ch) + border_rgb_bgr * border_alpha_3ch
            frame_bg[by:by + bh, bx:bx + bw] = np.clip(final_box, 0, 255).astype(np.uint8)

        writer.write(frame_bg)

    cap_bg.release()
    cap_fg.release()
    writer.release()

    # Mux audio via ffmpeg
    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(audio_path if audio_path else presenter_path),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", "10",
        str(output_path)
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        print(f"❌ FFmpeg Error in Method 2: {proc.stderr}")
        raise RuntimeError("FFmpeg encoding failed.")

    safe_unlink(temp_video)
    print(f"✅ Method 2 Complete! Output saved to: {output_path}")


def assemble_method_dynamic(root_dir: Path, broll_path: Path, presenter_path: Path, audio_path: Path, output_path: Path, ratio: str = "16:9", theme: str = "ink-wash"):
    """
    Method 3: Multi-Shot Dynamic Cutaways.
    Shot 1 (0-2.5s): Full Presenter Hook (Hero Intro)
    Shot 2 (2.5-7.5s): Full B-roll terminal with compact Face Bubble
    Shot 3 (7.5-10s): Tech Split Screen signoff
    """
    print(f"\n🚀 [ChatCut Engine] Executing Method 3: Dynamic Multi-Shot Cutaways [{ratio}] (Theme: {theme})")

    is_vertical = (ratio == "9:16")
    canvas_w, canvas_h = (1080, 1920) if is_vertical else (1920, 1080)

    # Temporary renders for each shot
    shot1_out = root_dir / "output" / "temp_shot1.mp4"
    shot2_out = root_dir / "output" / "temp_shot2.mp4"
    shot3_out = root_dir / "output" / "temp_shot3.mp4"

    # Shot 1 (0 ~ 2.5s): Presenter Center Spotlight
    pad_color = "0xfbfbfa" if theme == "ink-wash" else ("0xfaf7ee" if theme == "ai-coach" else "0x0a0e17")
    cmd1 = [
        "ffmpeg", "-y",
        "-ss", "0.0", "-t", "2.5", "-i", str(presenter_path),
        "-vf", f"scale=w={canvas_w}:h={canvas_h}:force_original_aspect_ratio=decrease,pad={canvas_w}:{canvas_h}:(ow-iw)/2:(oh-ih)/2:color={pad_color}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30",
        "-an", str(shot1_out)
    ]
    proc1 = subprocess.run(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if proc1.returncode != 0:
        print(f"❌ FFmpeg Error in Shot 1: {proc1.stderr}")
        raise RuntimeError("Shot 1 failed.")

    # Shot 2 (2.0 ~ 7.5s): Studio Window Fusion (NO circular bubble!)
    shot2_full = root_dir / "output" / f"temp_stage_full_{ratio.replace(':', '_')}.mp4"
    assemble_method_split(root_dir, broll_path, presenter_path, audio_path, shot2_full, ratio=ratio, theme=theme)

    cmd2 = [
        "ffmpeg", "-y",
        "-ss", "2.0", "-t", "5.5", "-i", str(shot2_full),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30",
        "-an", str(shot2_out)
    ]
    proc2 = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if proc2.returncode != 0:
        print(f"❌ FFmpeg Error in Shot 2: {proc2.stderr}")
        raise RuntimeError("Shot 2 failed.")

    # Shot 3 (7.5 ~ 10.0s): Stage Window Finish
    cmd3 = [
        "ffmpeg", "-y",
        "-ss", "7.5", "-t", "2.5", "-i", str(shot2_full),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30",
        "-an", str(shot3_out)
    ]
    proc3 = subprocess.run(cmd3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if proc3.returncode != 0:
        print(f"❌ FFmpeg Error in Shot 3: {proc3.stderr}")
        raise RuntimeError("Shot 3 failed.")

    # Concatenate the 3 shots
    concat_txt = root_dir / "output" / "temp_concat.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        f.write(f"file '{shot1_out.name}'\n")
        f.write(f"file '{shot2_out.name}'\n")
        f.write(f"file '{shot3_out.name}'\n")

    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-i", str(audio_path if audio_path else presenter_path),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", "10",
        str(output_path)
    ]
    proc_concat = subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if proc_concat.returncode != 0:
        print(f"❌ FFmpeg Error in Method 3 Concatenate: {proc_concat.stderr}")
        raise RuntimeError("FFmpeg concatenate failed.")

    # Cleanup temporary files
    for tmp in [shot1_out, shot2_out, shot3_out, shot2_full, concat_txt]:
        safe_unlink(tmp)

    print(f"✅ Method 3 Complete! Output saved to: {output_path}")


def build_chatcut_desktop_draft(project_name: str, method: str, a_roll_path: Path, broll_path: Path, ratio: str = "16:9"):
    """
    Generates a native JianYing / CapCut draft folder AND registers it in root_meta_info.json.
    Ensures 100% immediate appearance in JianYing's Recent Projects list.
    """
    draft_root = core_utils.get_jianying_draft_root()
    draft_id = str(uuid.uuid4()).upper()
    aspect_tag = "vert" if ratio == "9:16" else "horiz"
    draft_folder_name = f"ChatCut_{project_name}_{method}_{aspect_tag}_{draft_id[:6]}"
    target_draft_dir = draft_root / draft_folder_name
    target_draft_dir.mkdir(parents=True, exist_ok=True)

    is_vertical = (ratio == "9:16")
    canvas_w, canvas_h = (1080, 1920) if is_vertical else (1920, 1080)

    # Probe real dimensions of presenter and broll
    cap_pres = cv2.VideoCapture(str(a_roll_path))
    pres_w = int(cap_pres.get(cv2.CAP_PROP_FRAME_WIDTH)) or 544
    pres_h = int(cap_pres.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 960
    cap_pres.release()

    cap_broll = cv2.VideoCapture(str(broll_path))
    broll_w = int(cap_broll.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1920
    broll_h = int(cap_broll.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 1080
    cap_broll.release()

    # 1. Draft Meta Info
    meta_info = {
        "draft_id": draft_id,
        "draft_name": f"{project_name} [{method.upper()}-{ratio}]",
        "draft_root_path": str(draft_root),
        "draft_removable_storage_device": False,
        "tm_draft_create": int(time.time() * 1000000),
        "tm_draft_modified": int(time.time() * 1000000),
        "draft_version": 6000,
        "draft_timeline_materials_size_": 0,
        "creator": "chatcut_desktop_engine",
    }
    with open(target_draft_dir / "draft_meta_info.json", "w", encoding="utf-8") as f:
        json.dump(meta_info, f, indent=2, ensure_ascii=False)

    # 2. Materials
    broll_mat_id = str(uuid.uuid4()).upper()
    pres_mat_id = str(uuid.uuid4()).upper()
    video_materials = [
        {"id": broll_mat_id, "path": str(broll_path.resolve()), "type": "video", "duration": 10000000, "width": broll_w, "height": broll_h},
        {"id": pres_mat_id, "path": str(a_roll_path.resolve()), "type": "video", "duration": 10000000, "width": pres_w, "height": pres_h}
    ]

    # 3. Tracks
    tracks = []
    if method == "bubble":
        tracks.append({
            "id": str(uuid.uuid4()).upper(), "type": "video",
            "segments": [{"material_id": broll_mat_id, "target_timerange": {"start": 0, "duration": 10000000}, "source_timerange": {"start": 0, "duration": 10000000}, "render_index": 0}]
        })
        tracks.append({
            "id": str(uuid.uuid4()).upper(), "type": "video",
            "segments": [{"material_id": pres_mat_id, "target_timerange": {"start": 0, "duration": 10000000}, "source_timerange": {"start": 0, "duration": 10000000}, "render_index": 1,
                          "clip": {"alpha": 1.0, "scale": {"x": 0.45, "y": 0.45}, "transform": {"x": 0.38, "y": -0.32}}}]
        })
    else:  # split / dynamic: 100% full scale B-roll + presenter fitted in right window
        tracks.append({
            "id": str(uuid.uuid4()).upper(), "type": "video",
            "segments": [{"material_id": broll_mat_id, "target_timerange": {"start": 0, "duration": 10000000}, "source_timerange": {"start": 0, "duration": 10000000}, "render_index": 0,
                          "clip": {"scale": {"x": 1.0, "y": 1.0}, "transform": {"x": 0.0, "y": 0.0}}}]
        })
        tracks.append({
            "id": str(uuid.uuid4()).upper(), "type": "video",
            "segments": [{"material_id": pres_mat_id, "target_timerange": {"start": 0, "duration": 10000000}, "source_timerange": {"start": 0, "duration": 10000000}, "render_index": 1,
                          "clip": {"scale": {"x": 0.77 if not is_vertical else 1.0, "y": 0.77 if not is_vertical else 1.0},
                                   "transform": {"x": 0.307 if not is_vertical else 0.0, "y": -0.047 if not is_vertical else -0.28}}}]
        })

    draft_content = {
        "id": draft_id, "fps": 30.0, "duration": 10000000,
        "canvas_config": {"width": canvas_w, "height": canvas_h, "ratio": ratio},
        "tracks": tracks,
        "materials": {"videos": video_materials, "audios": [], "texts": [], "speeds": []}
    }
    with open(target_draft_dir / "draft_content.json", "w", encoding="utf-8") as f:
        json.dump(draft_content, f, indent=2, ensure_ascii=False)

    # 4. Register in JianYing index
    core_utils.register_jianying_draft_index(draft_root, draft_id, draft_folder_name, meta_info["draft_name"])
    print(f"📁 [ChatCut Draft] Auto-generated & registered: {target_draft_dir}")


def main():
    parser = argparse.ArgumentParser(description="ChatCut Autonomous Assembly Pipeline (Overhauled)")
    parser.add_argument("--mode", choices=["bubble", "split", "dynamic", "all"], default="all",
                        help="Assembly mode: bubble (Method 1), split (Method 2), dynamic (Method 3), or all")
    parser.add_argument("--ratio", choices=["16:9", "9:16"], default="16:9", help="Canvas aspect ratio: 16:9 or 9:16")
    parser.add_argument("--theme", default="ink-wash", help="Design theme: ink-wash, prismatic-aurora, cyber-dark, etc.")
    parser.add_argument("--project-name", default="HyperPresenter_Studio", help="Project name")
    args = parser.parse_args()

    root_dir = core_utils.get_project_root()
    broll_path = core_utils.find_broll_video()
    presenter_path = core_utils.find_presenter_video()

    if not presenter_path or not presenter_path.exists():
        print(f"❌ Error: No presenter video found in {root_dir / '03_presenter_aroll'}")
        sys.exit(1)
    if not broll_path or not broll_path.exists():
        print(f"❌ Error: No B-roll video found in {root_dir / 'output'}")
        sys.exit(1)

    audio_path = core_utils.ensure_audio_wav(presenter_path)

    res_str = "1080x1920_vertical" if args.ratio == "9:16" else "1920x1080"
    bubble_out = root_dir / "output" / f"face_bubble_optimized_{res_str}.mp4"
    split_out = root_dir / "output" / f"split_presenter_{res_str}.mp4"
    dynamic_out = root_dir / "output" / f"dynamic_cutaways_{res_str}.mp4"

    print("=" * 70)
    print("🎬 ChatCut Autonomous Assembly Engine - Zero Human Editing")
    print(f"📂 Root: {root_dir}")
    print(f"📹 Presenter: {presenter_path.name}")
    print(f"💻 B-Roll: {broll_path.name}")
    print(f"📐 Aspect Ratio: {args.ratio}")
    print(f"🎨 Theme: {args.theme}")
    print(f"🎯 Mode: {args.mode.upper()}")
    print("=" * 70)

    if args.mode in ["bubble", "all"]:
        assemble_method_bubble(root_dir, broll_path, presenter_path, audio_path, bubble_out, ratio=args.ratio, theme=args.theme)
        build_chatcut_desktop_draft(args.project_name, "bubble", presenter_path, broll_path, ratio=args.ratio)

    if args.mode in ["split", "all"]:
        assemble_method_split(root_dir, broll_path, presenter_path, audio_path, split_out, ratio=args.ratio, theme=args.theme)
        build_chatcut_desktop_draft(args.project_name, "split", presenter_path, broll_path, ratio=args.ratio)

    if args.mode in ["dynamic", "all"]:
        assemble_method_dynamic(root_dir, broll_path, presenter_path, audio_path, dynamic_out, ratio=args.ratio, theme=args.theme)
        build_chatcut_desktop_draft(args.project_name, "dynamic", presenter_path, broll_path, ratio=args.ratio)

    print("\n" + "=" * 70)
    print(f"🎉 Assembly complete for [{args.ratio}]! 100% autonomous, zero manual operations.")
    print("=" * 70)


if __name__ == "__main__":
    main()
