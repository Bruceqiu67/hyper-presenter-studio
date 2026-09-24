#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HyperPresenter Studio - Pre-Assembly Editing Scheme Proposer (Dual-Ratio Edition)
Analyzes presenter video and B-roll, formulates 3 distinct editing proposals (bubble, split/stack, dynamic),
generates visual demo stills for each scheme (16:9 landscape or 9:16 vertical),
and outputs an interactive proposal report with clickable file links and CLI execution commands.
"""

import os
import sys
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


def generate_scheme_previews(root_dir: Path, broll_path: Path, presenter_path: Path, ratio: str = "16:9"):
    """
    Renders 3 pixel-accurate demo still frames for:
    - Scheme 1: Face Bubble (发光圆框动态居中)
    - Scheme 2: Tech Split / Social Stack (科技双分屏 / 竖屏堆叠)
    - Scheme 3: Dynamic Cutaways (多镜头节奏切景)
    """
    output_dir = root_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    is_vertical = (ratio == "9:16")
    aspect_tag = "9x16" if is_vertical else "16x9"
    canvas_w, canvas_h = (1080, 1920) if is_vertical else (1920, 1080)

    p1 = output_dir / f"demo_proposal_scheme1_{aspect_tag}.jpg"
    p2 = output_dir / f"demo_proposal_scheme2_{aspect_tag}.jpg"
    p3 = output_dir / f"demo_proposal_scheme3_{aspect_tag}.jpg"

    # --- Scheme 1 Preview: Real Circular Bubble with Glowing Ring ---
    bubble_size = 360 if is_vertical else 440
    crop_size = 490
    if is_vertical:
        bx = canvas_w - bubble_size - 40
        by = canvas_h - bubble_size - 220
    else:
        bx = canvas_w - bubble_size - 60
        by = canvas_h - bubble_size - 60

    mask_3ch, ring_rgb_bgr, ring_alpha_3ch = core_utils.ensure_ring_and_mask(bubble_size)

    # Read frame at 4.0s
    cap_bg = cv2.VideoCapture(str(broll_path))
    cap_fg = cv2.VideoCapture(str(presenter_path))
    cap_bg.set(cv2.CAP_PROP_POS_MSEC, 4000)
    cap_fg.set(cv2.CAP_PROP_POS_MSEC, 4000)

    ret_bg, frame_bg = cap_bg.read()
    ret_fg, frame_fg = cap_fg.read()

    if not ret_bg:
        cap_bg.set(cv2.CAP_PROP_POS_MSEC, 0)
        ret_bg, frame_bg = cap_bg.read()
    if not ret_fg:
        cap_fg.set(cv2.CAP_PROP_POS_MSEC, 0)
        ret_fg, frame_fg = cap_fg.read()

    cap_bg.release()
    cap_fg.release()

    if frame_bg is not None and frame_fg is not None:
        if frame_bg.shape[1] != canvas_w or frame_bg.shape[0] != canvas_h:
            frame_bg_bubble = cv2.resize(frame_bg, (canvas_w, canvas_h), interpolation=cv2.INTER_LANCZOS4)
        else:
            frame_bg_bubble = frame_bg.copy()

        # Face center crop
        fg_h, fg_w = frame_fg.shape[:2]
        cx, cy = int(fg_w / 2), int(fg_h * 0.45)
        x1 = max(0, min(fg_w - crop_size, cx - crop_size // 2))
        y1 = max(0, min(fg_h - crop_size, cy - crop_size // 2))

        crop = frame_fg[y1:y1 + crop_size, x1:x1 + crop_size]
        crop_resized = cv2.resize(crop, (bubble_size, bubble_size), interpolation=cv2.INTER_LANCZOS4)

        roi = frame_bg_bubble[by:by + bubble_size, bx:bx + bubble_size].astype(np.float32)
        crop_float = crop_resized.astype(np.float32)

        blended = roi * (1.0 - mask_3ch) + crop_float * mask_3ch
        final_bubble = blended * (1.0 - ring_alpha_3ch) + ring_rgb_bgr * ring_alpha_3ch
        frame_bg_bubble[by:by + bubble_size, bx:bx + bubble_size] = np.clip(final_bubble, 0, 255).astype(np.uint8)

        cv2.imwrite(str(p1), frame_bg_bubble)
    else:
        # Fallback via ffmpeg
        subprocess.run(["ffmpeg", "-y", "-ss", "3.0", "-i", str(broll_path), "-vframes", "1", str(p1)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # --- Scheme 2 Preview: Split (16:9) or Social Stack (9:16) ---
    if is_vertical:
        cmd2 = [
            "ffmpeg", "-y",
            "-ss", "4.0", "-i", str(broll_path),
            "-ss", "4.0", "-i", str(presenter_path),
            "-filter_complex",
            "[0:v]scale=1000:562:flags=lanczos[broll];"
            "[1:v]scale=1080:1080:flags=lanczos[pres];"
            "color=c=0x07090e:s=1080x1920:d=1[bg];"
            "[bg][broll]overlay=40:220[bg1];"
            "[bg1][pres]overlay=0:840[v]",
            "-map", "[v]",
            "-vframes", "1",
            str(p2)
        ]
    else:
        cmd2 = [
            "ffmpeg", "-y",
            "-ss", "4.0", "-i", str(broll_path),
            "-ss", "4.0", "-i", str(presenter_path),
            "-filter_complex",
            "[0:v]scale=1200:675:flags=lanczos[broll];"
            "[1:v]scale=544:960:flags=lanczos[pres];"
            "color=c=0x07090e:s=1920x1080:d=1[bg];"
            "[bg][broll]overlay=60:202[bg1];"
            "[bg1][pres]overlay=1316:60[v]",
            "-map", "[v]",
            "-vframes", "1",
            str(p2)
        ]
    subprocess.run(cmd2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # --- Scheme 3 Preview: Dynamic Cutaways Hero Still ---
    cmd3 = [
        "ffmpeg", "-y",
        "-ss", "1.5", "-i", str(presenter_path),
        "-vf", f"scale=-1:{canvas_h},crop={canvas_w}:{canvas_h}",
        "-vframes", "1",
        str(p3)
    ]
    subprocess.run(cmd3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return str(p1), str(p2), str(p3)


def generate_proposal_report(root_dir: Path, p1: str, p2: str, p3: str, ratio: str = "16:9") -> str:
    is_vertical = (ratio == "9:16")
    aspect_tag = "9x16" if is_vertical else "16x9"
    report_filename = f"EDITING_PROPOSAL_{aspect_tag.upper()}.md" if is_vertical else "EDITING_PROPOSAL.md"
    report_file = root_dir / "output" / report_filename

    p1_unix = p1.replace("\\", "/")
    p2_unix = p2.replace("\\", "/")
    p3_unix = p3.replace("\\", "/")

    ratio_title = "竖屏 9:16 移动端爆款版 (1080×1920)" if is_vertical else "横屏 16:9 极客大片版 (1920×1080)"
    scheme2_name = "【科技竖屏社交卡片堆叠 · Social Stack】" if is_vertical else "【科技黄金双分屏 · Tech Split】"
    scheme2_desc = (
        "- **融合手法**: 上半屏 1000×562 浮动终端操作窗口；下半屏 1080×1080 真人口播近景，手势向上呼应终端；\n"
        "- **安全区设计**: 完美避开抖音/小红书顶部搜索栏与底部 20% 交互/标题区。"
        if is_vertical else
        "- **融合手法**: 左侧 1200×675 黄金画幅呈现极客终端操作与编译状态；右侧 544×960 展现口播半身与指引手势；\n"
        "- **氛围设计**: 底部深色网格科技微光烘托，专业度与信任感拉满。"
    )
    cmd_ratio_flag = " --ratio 9:16" if is_vertical else ""

    md = f"""# 🎬 HyperPresenter Studio - 剪辑总装方案提案 ({ratio_title})

> **检测到用户实拍素材与 B-Roll 渲染已全部就绪！**  
> 在正式执行自动化总装前，以下是为你量身定制的 **3 套顶级剪辑融合与切景方案**（画幅比例：`{ratio}`）。  
> 请审查各方案的镜头规划与 Demo 预览效果，拍板你中意的方案后一键出片：

---

## 📸 方案对比与视觉 Demo 预览

### 🎯 方案一：【极客发光圆框 · Face Bubble】
- **预览截图**: [{os.path.basename(p1)}](file:///{p1_unix})
- **融合手法**: 
  - 背景代码演示窗口占满全屏，全景聚焦核心编译逻辑；
  - 画面搭载圆形科技气泡包裹真人（尺寸：`{"360×360" if is_vertical else "440×440"}`），外沿带有 `#38bdf8` 赛博霓虹能量光环；
  - **动态平滑追踪 (EMA Face Tracking)**：自适应居中算法保证面部始终在圆心，绝不切脸、不跳跃。
- **切景与节奏规划**:
  - `00:00 - 00:01`: 终端全景配合淡入，圆框弹跳入画（Scale Elastic）；
  - `00:01 - 00:08`: 终端打字敲击卡点，跑满依赖条；
  - `00:08 - 00:10`: 命令完成，圆框微发光脉冲，口播食指卡点，全片收尾。
- **适用场景**: 开发者工具教学、CLI 快速演示、Twitter/X/抖音极客短视频。
- **一键拍板命令**:
  ```bash
  python 04_assembly_capcut/chatcut_auto_assembly.py --mode bubble{cmd_ratio_flag}
  ```

---

### 🖥️ 方案二：{scheme2_name}
- **预览截图**: [{os.path.basename(p2)}](file:///{p2_unix})
{scheme2_desc}
- **切景与节奏规划**:
  - 双轨并列稳定呈现，无需频繁切镜头，保持视觉极简与信息清晰；
  - 重点台词出现时，终端窗口伴随微妙的 3D 浮动视差推拉。
- **适用场景**: 科技新品发布会、重大版本 Release 官宣、高规格技术大片。
- **一键拍板命令**:
  ```bash
  python 04_assembly_capcut/chatcut_auto_assembly.py --mode split{cmd_ratio_flag}
  ```

---

### 🔄 方案三：【动静态智能多镜头切景 · Dynamic Cutaways】
- **预览截图**: [{os.path.basename(p3)}](file:///{p3_unix})
- **融合手法**: 
  - 多景别切换节奏大师：全景真人与局部代码交替叙事。
- **切景与节奏规划**:
  - **Shot 1 (00:00 - 00:02.5)**：全景真人出镜（痛点共鸣与疑问），抓住前 3 秒黄金留存；
  - **Shot 2 (00:02.5 - 00:07.5)**：镜头快速推入（Push In）切为【发光圆框】，全屏聚焦终端安装代码流；
  - **Shot 3 (00:07.5 - 00:10.0)**：切为【分屏/堆叠】，真人手势与编译对勾双重亮相。
- **适用场景**: 抖音/B站/视频号快节奏干货、高完播率信息流爆款短视频。
- **一键拍板命令**:
  ```bash
  python 04_assembly_capcut/chatcut_auto_assembly.py --mode dynamic{cmd_ratio_flag}
  ```

---

## 🚀 你的拍板指令 (Your Decision)
请审查上述 3 个 Demo，直接回复你的选择（如：“选方案一”或“选方案二”），或在终端直接运行对应命令，ChatCut 将立即为你 100% 自动总装成片并注入剪映桌面端草稿！
"""
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"✅ Editing Proposal Report Generated: {report_file}")
    return str(report_file)


def main():
    parser = argparse.ArgumentParser(description="Formulate editing proposals for HyperPresenter Studio")
    parser.add_argument("--ratio", choices=["16:9", "9:16", "all"], default="16:9", help="Aspect ratio for proposals")
    args = parser.parse_args()

    root_dir = core_utils.get_project_root()
    broll_path = core_utils.find_broll_video()
    presenter_path = core_utils.find_presenter_video()

    if not presenter_path or not presenter_path.exists():
        print("❌ Error: No presenter video found in 03_presenter_aroll/.")
        sys.exit(1)
    if not broll_path or not broll_path.exists():
        print("❌ Error: No B-roll video found in output/.")
        sys.exit(1)

    ratios = ["16:9", "9:16"] if args.ratio == "all" else [args.ratio]

    for r in ratios:
        print("=" * 65)
        print(f"🎬 Formulating Pre-Assembly Editing Proposals [{r}]")
        print(f"📹 Presenter Video: {presenter_path.name}")
        print(f"💻 B-Roll Motion: {broll_path.name}")
        print("=" * 65)

        p1, p2, p3 = generate_scheme_previews(root_dir, broll_path, presenter_path, ratio=r)
        report_file = generate_proposal_report(root_dir, p1, p2, p3, ratio=r)

        print("=" * 65)
        print(f"🎉 All 3 editing scheme previews generated successfully for [{r}]!")
        print(f"👉 Review the report at: {report_file}")
        print("=" * 65)


if __name__ == "__main__":
    main()
