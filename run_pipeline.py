#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HyperPresenter Studio - Unified Pipeline Master Orchestrator
Industrial Human-AI Collaborative Video Production CLI.
Orchestrates the complete 4-stage pipeline from zero to final delivery:
  Stage 1: OpenDesign UI Prototype & Design Tokens
  Stage 2: HyperFrames Code-Driven 60FPS Motion B-Roll
  Stage 3: Script Master & 10s Prompter Blueprint
  Stage 4: ChatCut Face Tracking, Dynamic Cutaways & JianYing Pro Draft Injection
"""

import os
import sys
import time
import zipfile
import argparse
import subprocess
from pathlib import Path

# Ensure UTF-8 console output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"
AROLL_DIR = ROOT_DIR / "03_presenter_aroll"
ARCHIVE_DIR = ROOT_DIR / "archive"
OUTPUT_DIR.mkdir(exist_ok=True)


def print_banner():
    banner = """
======================================================================
  ⚡ HYPERPRESENTER STUDIO — UNIFIED PIPELINE ORCHESTRATOR
  人机协同全流程 AI 短视频工业化创作工坊 (Zero Manual Editing)
======================================================================
"""
    print(banner)


def check_status(theme: str = "ink-wash"):
    """Prints current pipeline asset status across all stages with theme awareness."""
    print("🔍 [Pipeline Health & Asset Status]")
    print("-" * 65)

    # Stage 1: Prototype & Design Tokens
    tokens_dir = ROOT_DIR / "01_prototype_opendesign" / "tokens"
    tokens_file = tokens_dir / f"tokens_{theme}.json"
    proto_file = ROOT_DIR / "01_prototype_opendesign" / f"prototype_{theme}.html"
    
    # Fallback to any available tokens/prototype if specific theme not generated yet
    if not tokens_file.exists():
        avail_tokens = list(tokens_dir.glob("tokens_*.json"))
        if avail_tokens:
            tokens_file = avail_tokens[0]
    if not proto_file.exists():
        avail_proto = list((ROOT_DIR / "01_prototype_opendesign").glob("prototype_*.html"))
        if avail_proto:
            proto_file = avail_proto[0]

    s1_ok = tokens_file.exists() and proto_file.exists()
    print(f"  Stage 1 · OpenDesign Prototype:    {'[READY ✔]' if s1_ok else '[PENDING ⏳]'}")
    if s1_ok:
        print(f"            └─ Tokens: {tokens_file.name}, HTML: {proto_file.name}")

    # Stage 2: Motion B-Roll
    broll_file = OUTPUT_DIR / "broll_motion.mp4"
    s2_ok = broll_file.exists() and broll_file.stat().st_size > 1000
    print(f"  Stage 2 · HyperFrames Motion B-Roll:{'[READY ✔]' if s2_ok else '[PENDING ⏳]'}")
    if s2_ok:
        size_mb = broll_file.stat().st_size / (1024 * 1024)
        print(f"            └─ Video: {broll_file.name} ({size_mb:.2f} MB)")

    # Stage 3: Presenter Footage
    sys.path.insert(0, str(ROOT_DIR / "04_assembly_capcut"))
    import core_utils
    presenter_file = core_utils.find_presenter_video()
    s3_ok = presenter_file is not None and presenter_file.exists()
    print(f"  Stage 3 · Presenter A-Roll Footage: {'[READY ✔]' if s3_ok else '[AWAITING FOOTAGE 📹]'}")
    if s3_ok:
        size_mb = presenter_file.stat().st_size / (1024 * 1024)
        print(f"            └─ File: {presenter_file.name} ({size_mb:.2f} MB)")
    else:
        print(f"            └─ Place your recording (.mp4/.mov) into 03_presenter_aroll/")

    # Stage 4: Delivery & JianYing Draft
    final_16x9 = OUTPUT_DIR / "dynamic_cutaways_1920x1080.mp4"
    final_9x16 = OUTPUT_DIR / "dynamic_cutaways_1080x1920_vertical.mp4"
    s4_ok = final_16x9.exists() or final_9x16.exists()
    print(f"  Stage 4 · Final Delivery & JianYing:{'[READY ✔]' if s4_ok else '[PENDING ⏳]'}")
    if s4_ok:
        if final_16x9.exists():
            print(f"            ├─ 16:9 Master: {final_16x9.name}")
        if final_9x16.exists():
            print(f"            └─ 9:16 Master: {final_9x16.name}")

    print("-" * 65)


def run_stage_1(theme="ink-wash", ratio="all"):
    """Stage 1: Generate UI Prototype & Design Tokens."""
    print(f"\n🎨 [Stage 1/4] Running OpenDesign Prototype Generator (Theme: {theme})...")
    cmd = [
        sys.executable,
        str(ROOT_DIR / "01_prototype_opendesign" / "generate_prototype.py"),
        "--title", "HyperPresenter Studio",
        "--command", "npx hyper-presenter setup --preset ink-wash",
        "--theme", theme,
        "--ratio", ratio,
        "--mode", "pipeline"
    ]
    subprocess.run(cmd, check=True)
    print("✅ [Stage 1/4] Prototype & Tokens generated successfully!")


def extract_broll_frames(broll_path: Path):
    """Extracts 3 verification frames from the rendered B-Roll MP4 for visual review."""
    print("📸 Extracting 3 verification frames from rendered MP4...")
    shots_dir = OUTPUT_DIR / "screenshots"
    shots_dir.mkdir(exist_ok=True)
    times = [("act1", "00:00:02.000"), ("act2", "00:00:05.000"), ("act3", "00:00:08.500")]
    for act, t in times:
        out_jpg = shots_dir / f"broll_rendered_{act}.jpg"
        cmd = ["ffmpeg", "-y", "-ss", t, "-i", str(broll_path), "-vframes", "1", "-update", "1", "-q:v", "2", str(out_jpg)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if out_jpg.exists():
            print(f"  ✔ Rendered frame [{act}]: {out_jpg.name}")


def capture_demo(html_path="01_prototype_opendesign/prototype_ink-wash.html"):
    """Captures screenshots of all 3 acts of the prototype for immediate visual review."""
    print(f"\n📸 [Stage 1.5] Capturing visual screenshots for: {html_path}...")
    cmd = ["node", str(ROOT_DIR / "scripts" / "capture_demo_shots.js"), "--input", str(html_path)]
    subprocess.run(cmd, cwd=str(ROOT_DIR), check=True, shell=(sys.platform == "win32"))
    print("✅ [Stage 1.5] Visual screenshots saved to output/screenshots/ and artifacts!")


def run_stage_2():
    """Stage 2: Render 1080P 60FPS HyperFrames B-Roll."""
    print("\n⚡ [Stage 2/4] Compiling 60FPS 3-Act Explainer B-Roll via HyperFrames...")
    out_broll = OUTPUT_DIR / "broll_motion.mp4"
    npx_bin = "npx.cmd" if sys.platform == "win32" else "npx"
    cmd = [
        npx_bin, "--yes", "hyperframes@0.8.70",
        "render", "./02_motion_hyperframes",
        "-o", str(out_broll)
    ]
    proc = subprocess.run(cmd, cwd=str(ROOT_DIR), check=True, shell=(sys.platform == "win32"))
    if out_broll.exists():
        size_mb = out_broll.stat().st_size / (1024 * 1024)
        print(f"✅ [Stage 2/4] Motion B-Roll compiled: {out_broll.name} ({size_mb:.2f} MB)")
        extract_broll_frames(out_broll)


def run_stage_3(topic="HyperPresenter Studio"):
    """Stage 3: Generate 10-Second Teleprompter Script & Shooting Blueprint."""
    print(f"\n🎙️ [Stage 3/4] Generating 10s Prompter & Shooting Blueprint for: '{topic}'...")
    cmd = [
        sys.executable,
        str(ROOT_DIR / "03_presenter_aroll" / "generate_shooting_guide.py"),
        "--title", topic,
        "--duration", "10",
        "--command", "npx hyper-presenter setup"
    ]
    subprocess.run(cmd, check=True)
    print("✅ [Stage 3/4] Shooting Guide generated! Check 03_presenter_aroll/CURRENT_SHOOTING_GUIDE.md")


def run_stage_4(ratio="all", project_name="HyperPresenter_Studio", theme="ink-wash"):
    """Stage 4: Automated Face Tracking, Dynamic Cutaways & JianYing Pro Draft Injection."""
    print(f"\n🎬 [Stage 4/4] Executing ChatCut Autonomous Assembly (Theme: {theme})...")
    sys.path.insert(0, str(ROOT_DIR / "04_assembly_capcut"))
    import core_utils
    presenter_file = core_utils.find_presenter_video()
    if not presenter_file or not presenter_file.exists():
        print("❌ Error: No presenter video found in 03_presenter_aroll/!")
        print("💡 Hint: Place your recorded MP4 into '03_presenter_aroll/', or run with '--restore-demo' to use the demo recording.")
        return False

    ratios = ["16:9", "9:16"] if ratio == "all" else [ratio]
    for r in ratios:
        cmd = [
            sys.executable,
            str(ROOT_DIR / "04_assembly_capcut" / "chatcut_auto_assembly.py"),
            "--ratio", r,
            "--mode", "dynamic",
            "--theme", theme,
            "--project-name", project_name
        ]
        subprocess.run(cmd, check=True)

    print("✅ [Stage 4/4] Final Assembly & JianYing Pro Draft Injection Complete!")
    return True


def restore_demo():
    """Restores the recorded demo video from the session archive for fast end-to-end verification."""
    print("\n📦 Restoring demo presenter video from archive...")
    zip_candidates = list(ARCHIVE_DIR.glob("*.zip"))
    if not zip_candidates:
        print("⚠️ No archive zip found in archive/.")
        return False

    zip_candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    target_zip = zip_candidates[0]
    print(f"  Unpacking from: {target_zip.name}...")

    with zipfile.ZipFile(target_zip, 'r') as zf:
        for member in zf.namelist():
            if "03_presenter_aroll" in member and member.endswith((".mp4", ".mov", ".m4v")):
                zf.extract(member, ROOT_DIR)
                print(f"  ✔ Restored presenter video: {member}")
                return True
    print("⚠️ Could not find presenter video in archive.")
    return False


def main():
    parser = argparse.ArgumentParser(description="HyperPresenter Studio Unified Pipeline Orchestrator")
    parser.add_argument("--status", action="store_true", help="Inspect pipeline health and asset status across all 4 stages")
    parser.add_argument("--step", type=int, choices=[1, 2, 3, 4], help="Run a specific stage (1=Prototype, 2=Motion, 3=Guide, 4=Assembly)")
    parser.add_argument("--capture-demo", action="store_true", help="Capture high-res screenshots of the 3-act prototype for immediate visual review")
    parser.add_argument("--all", action="store_true", help="Run the entire 4-stage pipeline sequentially")
    parser.add_argument("--restore-demo", action="store_true", help="Restore demo presenter video from archive to run test assembly")
    parser.add_argument("--ratio", choices=["16:9", "9:16", "all"], default="all", help="Aspect ratio target")
    parser.add_argument("--theme", default="ink-wash", help="Design theme: ink-wash, prismatic-aurora, cyber-dark, matrix-neon, cyber-purple")
    parser.add_argument("--project-name", default="HyperPresenter_Studio", help="Project / Draft Name")
    args = parser.parse_args()

    print_banner()

    if args.restore_demo:
        restore_demo()
        check_status(theme=args.theme)
        return

    if args.capture_demo:
        capture_demo()
        return

    if args.status or (not args.step and not args.all):
        check_status(theme=args.theme)
        print("\n💡 Available Pipeline Commands:")
        print("  python run_pipeline.py --step 1        # [Stage 1] 生成现代水墨/极光 UI 原型与 Tokens")
        print("  python run_pipeline.py --capture-demo  # [Review]  提取三幕高清实拍图供用户视觉走查")
        print("  python run_pipeline.py --step 2        # [Stage 2] 编译三幕式 60FPS 极客动效 B-Roll 并抽帧")
        print("  python run_pipeline.py --step 3        # [Stage 3] 生成 10s 秒级分镜卡点与提词蓝图")
        print("  python run_pipeline.py --step 4        # [Stage 4] 运行人脸追踪、景别切镜并注入剪映草稿")
        print("  python run_pipeline.py --all           # [Full]    一键贯通跑完全部 4 阶流水线")
        print("  python run_pipeline.py --restore-demo  # [Demo]    恢复存档口播视频用于快速实测")
        return

    if args.step == 1 or args.all:
        run_stage_1(theme=args.theme, ratio=args.ratio)

    if args.step == 2 or args.all:
        run_stage_2()

    if args.step == 3 or args.all:
        run_stage_3()

    if args.step == 4 or args.all:
        run_stage_4(ratio=args.ratio, project_name=args.project_name, theme=args.theme)

    print("\n" + "=" * 65)
    print("🎉 Pipeline Execution Finished!")
    check_status(theme=args.theme)
    print("=" * 65)


if __name__ == "__main__":
    main()
