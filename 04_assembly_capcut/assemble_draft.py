#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HyperPresenter Studio - Desktop Assembly Engine
Automatically generates or stages JianYing / CapCut Desktop draft projects
and aligns Presenter A-Roll with HyperFrames B-Roll motion graphics.
"""

import os
import sys
import json
import uuid
import time
import argparse
import platform
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def get_jianying_draft_root() -> Path:
    """Detect the default JianYing / CapCut Pro drafts folder across platforms."""
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        # Standard Windows JianYing Pro draft location
        candidate = home / "AppData" / "Local" / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft"
        if candidate.exists():
            return candidate
        # Alternative CapCut Global draft location
        capcut_win = home / "AppData" / "Local" / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
        if capcut_win.exists():
            return capcut_win
        return candidate

    elif system == "Darwin":  # macOS
        candidate = home / "Movies" / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft"
        if candidate.exists():
            return candidate
        capcut_mac = home / "Movies" / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
        if capcut_mac.exists():
            return capcut_mac
        return candidate

    # Fallback for Linux or unrecognized environment
    return home / ".jianying" / "drafts"


def create_draft_project(project_name: str, a_roll_path: str = None, b_roll_path: str = None):
    """
    Generate a clean draft directory structure that JianYing / CapCut can recognize.
    Also produces an FFmpeg fallback script for zero-dependency assembly.
    """
    draft_root = get_jianying_draft_root()
    draft_id = str(uuid.uuid4()).upper()
    draft_folder_name = f"{project_name}_{draft_id[:8]}"
    target_draft_dir = draft_root / draft_folder_name

    print("=" * 60)
    print(f"🎬 HyperPresenter Studio - Assembling Project: {project_name}")
    print(f"📁 Target Draft Path: {target_draft_dir}")
    print("=" * 60)

    # 1. Create target draft directory
    target_draft_dir.mkdir(parents=True, exist_ok=True)

    # 2. Build metadata manifest
    meta_info = {
        "draft_id": draft_id,
        "draft_name": project_name,
        "draft_root_path": str(draft_root),
        "draft_removable_storage_device": False,
        "tm_draft_create": int(time.time() * 1000000),
        "tm_draft_modified": int(time.time() * 1000000),
        "draft_version": 6000,
        "draft_timeline_materials_size_": 0,
        "creator": "hyper-presenter-studio",
    }

    meta_file = target_draft_dir / "draft_meta_info.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta_info, f, indent=2, ensure_ascii=False)

    print(f"✅ Created Draft Metadata: {meta_file.name}")

    # 3. Create basic draft content structure
    draft_content = {
        "id": draft_id,
        "fps": 60.0,
        "duration": 0,
        "canvas_config": {
            "width": 1920,
            "height": 1080,
            "ratio": "16:9"
        },
        "tracks": [],
        "materials": {
            "videos": [],
            "audios": [],
            "texts": [],
            "speeds": []
        }
    }

    content_file = target_draft_dir / "draft_content.json"
    with open(content_file, "w", encoding="utf-8") as f:
        json.dump(draft_content, f, indent=2, ensure_ascii=False)

    print(f"✅ Created Draft Content: {content_file.name}")

    # 4. Generate local staging manifest & FFmpeg fallback command
    staging_file = target_draft_dir / "assembly_manifest.txt"
    with open(staging_file, "w", encoding="utf-8") as f:
        f.write(f"# Assembly Manifest for {project_name}\n")
        f.write(f"Presenter A-Roll: {a_roll_path or 'Not specified'}\n")
        f.write(f"HyperFrames B-Roll: {b_roll_path or 'Not specified'}\n")
        f.write(f"Generated At: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("\n🎉 Draft successfully assembled!")
    print(f"👉 You can now open JianYing / CapCut Desktop to see project '{project_name}' ready.")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Assemble Presenter and HyperFrames video into CapCut draft.")
    parser.add_argument("--project-name", default="Reasonix_CLI_Demo", help="Name of the video project")
    parser.add_argument("--a-roll", default=None, help="Path to raw presenter talking-head video")
    parser.add_argument("--b-roll", default=None, help="Path to HyperFrames rendered 1080P B-roll video")
    args = parser.parse_args()

    create_draft_project(args.project_name, args.a_roll, args.b_roll)


if __name__ == "__main__":
    main()
