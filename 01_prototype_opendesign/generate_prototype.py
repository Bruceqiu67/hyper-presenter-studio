#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HyperPresenter Studio - OpenDesign Prototype Generator (Dual-Ratio Edition)
Generates high-fidelity UI/UX design prototypes and style tokens for tech demo videos.
Supports interactive HTML/CSS previews for both Landscape (16:9 / 1920x1080)
and Vertical Mobile (9:16 / 1080x1920) viewports, plus design token export.
"""

import os
import sys
import html
import json
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

STYLE_THEMES = {
    "cyber-dark": {
        "name": "Cyber Dark (赛博青暗黑极客风)",
        "bg_gradient": "radial-gradient(ellipse at 50% 30%, #0d192b 0%, #050811 100%)",
        "primary": "#38bdf8",
        "secondary": "#818cf8",
        "accent": "#34d399",
        "window_bg": "rgba(13, 20, 36, 0.78)",
        "window_border": "rgba(56, 189, 248, 0.22)",
        "window_glow": "0 24px 70px rgba(56, 189, 248, 0.16)",
        "text_main": "#f8fafc",
        "text_dim": "#64748b",
        "dot_red": "#ef4444",
        "dot_yellow": "#f59e0b",
        "dot_green": "#10b981",
        "tag_bg": "rgba(56, 189, 248, 0.14)",
        "tag_border": "rgba(56, 189, 248, 0.35)",
    },
    "matrix-neon": {
        "name": "Matrix Neon (极客骇客绿)",
        "bg_gradient": "radial-gradient(ellipse at 50% 30%, #0a1f14 0%, #030a06 100%)",
        "primary": "#10b981",
        "secondary": "#34d399",
        "accent": "#a7f3d0",
        "window_bg": "rgba(8, 26, 17, 0.82)",
        "window_border": "rgba(16, 185, 129, 0.25)",
        "window_glow": "0 24px 70px rgba(16, 185, 129, 0.18)",
        "text_main": "#ecfdf5",
        "text_dim": "#4b7a60",
        "dot_red": "#ef4444",
        "dot_yellow": "#f59e0b",
        "dot_green": "#10b981",
        "tag_bg": "rgba(16, 185, 129, 0.14)",
        "tag_border": "rgba(16, 185, 129, 0.35)",
    },
    "cyber-purple": {
        "name": "Cyber Purple (赛博霓虹紫)",
        "bg_gradient": "radial-gradient(ellipse at 50% 30%, #1e1136 0%, #07040d 100%)",
        "primary": "#c084fc",
        "secondary": "#f472b6",
        "accent": "#38bdf8",
        "window_bg": "rgba(23, 14, 43, 0.8)",
        "window_border": "rgba(192, 132, 252, 0.25)",
        "window_glow": "0 24px 70px rgba(192, 132, 252, 0.2)",
        "text_main": "#faf5ff",
        "text_dim": "#7e6c9e",
        "dot_red": "#ef4444",
        "dot_yellow": "#f59e0b",
        "dot_green": "#10b981",
        "tag_bg": "rgba(192, 132, 252, 0.14)",
        "tag_border": "rgba(192, 132, 252, 0.35)",
    },
    "prismatic-aurora": {
        "name": "Prismatic Aurora (极光五彩绚烂风)",
        "bg_gradient": "radial-gradient(ellipse at 50% 25%, #22123d 0%, #0d081c 55%, #040208 100%)",
        "primary": "#38bdf8",
        "secondary": "#f472b6",
        "accent": "#fbbf24",
        "window_bg": "rgba(20, 14, 38, 0.84)",
        "window_border": "rgba(244, 114, 182, 0.38)",
        "window_glow": "0 24px 80px rgba(192, 132, 252, 0.3), 0 0 60px rgba(56, 189, 248, 0.25)",
        "text_main": "#ffffff",
        "text_dim": "#a5b4fc",
        "dot_red": "#ff4d6d",
        "dot_yellow": "#ffb703",
        "dot_green": "#06d6a0",
        "tag_bg": "linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(244, 114, 182, 0.2))",
        "tag_border": "rgba(244, 114, 182, 0.5)",
    },
    "ink-wash": {
        "name": "Ink Wash (现代新中式宣白水墨风)",
        "bg_gradient": "radial-gradient(circle at 50% 35%, #ffffff 0%, #f7f6f0 60%, #eeebe3 100%)",
        "primary": "#18181b",
        "secondary": "#dc2626",
        "accent": "#0d9488",
        "window_bg": "rgba(255, 255, 255, 0.94)",
        "window_border": "rgba(24, 24, 27, 0.12)",
        "window_glow": "0 24px 60px rgba(0, 0, 0, 0.06), 0 2px 10px rgba(0, 0, 0, 0.03)",
        "text_main": "#18181b",
        "text_dim": "#52525b",
        "dot_red": "#dc2626",
        "dot_yellow": "#d97706",
        "dot_green": "#059669",
        "tag_bg": "rgba(220, 38, 38, 0.08)",
        "tag_border": "rgba(220, 38, 38, 0.3)",
    }
}


def generate_prototype_html(title: str, command: str, feature_desc: str, theme_key: str = "cyber-dark", ratio: str = "16:9", mode: str = "pipeline") -> str:
    theme = STYLE_THEMES.get(theme_key, STYLE_THEMES["cyber-dark"])
    is_vertical = (ratio == "9:16")
    is_pipeline_mode = (mode == "pipeline")

    # Safe HTML escape to prevent XSS and template breakage
    safe_title = html.escape(title)
    safe_command = html.escape(command)
    safe_desc = html.escape(feature_desc)

    default_block = f"""
        <div class="info-line">executing command sequence [····················] running</div>
        <div class="progress-box">
          <div class="progress-bar"></div>
        </div>
        <div class="status-line">
          <span>✔</span>
          <span>{safe_title.lower()} ready</span>
          <span class="highlight-badge">Autonomous Mode</span>
        </div>
        <div class="info-line" style="margin-top: 10px;">
          → {safe_desc}
        </div>
        <div class="status-line" style="color: {theme['primary']};">
          <span>⚡</span>
          <span>Pipeline Initialized. Ready for streaming.</span>
        </div>
    """

    pipeline_block = f"""
        <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 8px;">
          <div style="display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;">
            <span style="font-size: 13px; font-weight: 700; padding: 2px 8px; border-radius: 4px; background: rgba(192,132,252,0.2); color: #c084fc; border: 1px solid rgba(192,132,252,0.4);">Phase 1</span>
            <span style="flex: 1; font-size: 15px; color: #e2e8f0;">OpenDesign: AI 动态生成高保真极光 UI 原型与 Design Tokens</span>
            <span style="color: #06d6a0; font-weight: 600; font-size: 14px;">✔ Verified</span>
          </div>
          <div style="display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;">
            <span style="font-size: 13px; font-weight: 700; padding: 2px 8px; border-radius: 4px; background: rgba(56,189,248,0.2); color: #38bdf8; border: 1px solid rgba(56,189,248,0.4);">Phase 2</span>
            <span style="flex: 1; font-size: 15px; color: #e2e8f0;">HyperFrames: 纯代码无损编译 1080P 60fps 极客动效 B-Roll</span>
            <span style="color: #06d6a0; font-weight: 600; font-size: 14px;">✔ 100% 60fps</span>
          </div>
          <div style="display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;">
            <span style="font-size: 13px; font-weight: 700; padding: 2px 8px; border-radius: 4px; background: rgba(251,191,36,0.2); color: #fbbf24; border: 1px solid rgba(251,191,36,0.4);">Phase 3</span>
            <span style="flex: 1; font-size: 15px; color: #e2e8f0;">Script Master: 10s 秒级分镜卡点蓝图、手势与眼神视线指引</span>
            <span style="color: #06d6a0; font-weight: 600; font-size: 14px;">✔ Generated</span>
          </div>
          <div style="display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;">
            <span style="font-size: 13px; font-weight: 700; padding: 2px 8px; border-radius: 4px; background: rgba(6,214,160,0.2); color: #06d6a0; border: 1px solid rgba(6,214,160,0.4);">Phase 4</span>
            <span style="flex: 1; font-size: 15px; color: #e2e8f0;">ChatCut Engine: OpenCV 实时人脸追踪重定帧 + 剪映草稿置顶注册</span>
            <span style="color: #06d6a0; font-weight: 600; font-size: 14px;">✔ Ready</span>
          </div>
        </div>
        <div style="margin-top: 10px; padding: 10px 16px; background: linear-gradient(135deg, rgba(56,189,248,0.15), rgba(244,114,182,0.15)); border: 1px solid rgba(244,114,182,0.4); border-radius: 8px; display: flex; align-items: center; justify-content: space-between;">
          <span style="font-size: 15px; font-weight: 700; color: #ffffff;">🚀 100% 工业化人机协同全流程就绪 · 零人工手动拖拽剪辑</span>
          <span style="font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 9999px; background: #06d6a0; color: #05030a;">PIPELINE ACTIVE</span>
        </div>
    """

    # Dimensional configs
    canvas_w = 1080 if is_vertical else 1920
    canvas_h = 1920 if is_vertical else 1080
    stage_w = "920px" if is_vertical else "1280px"
    terminal_w = "920px" if is_vertical else "1280px"
    terminal_h = "1100px" if is_vertical else "720px"
    progress_w = "420px" if is_vertical else "520px"
    headline_size = "34px" if is_vertical else "40px"
    body_pad = "32px 36px" if is_vertical else "36px 44px"
    font_size_body = "18px" if is_vertical else "20px"

    headline_grad = "linear-gradient(135deg, #ffffff 15%, #38bdf8 35%, #c084fc 60%, #f472b6 80%, #fbbf24 100%)" if theme_key == "prismatic-aurora" else f"linear-gradient(135deg, #ffffff 30%, {theme['primary']} 100%)"
    progress_grad = "linear-gradient(90deg, #38bdf8, #818cf8, #c084fc, #f472b6, #fbbf24)" if theme_key == "prismatic-aurora" else f"linear-gradient(90deg, {theme['primary']}, {theme['secondary']})"
    terminal_border = "border: 2px solid transparent; background-image: linear-gradient(rgba(20, 14, 38, 0.92), rgba(20, 14, 38, 0.92)), linear-gradient(135deg, #38bdf8, #c084fc, #f472b6, #fbbf24, #34d399); background-origin: border-box; background-clip: padding-box, border-box;" if theme_key == "prismatic-aurora" else f"border: 1px solid {theme['window_border']}; background: {theme['window_bg']};"

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width={canvas_w}, height={canvas_h}, initial-scale=1.0">
  <title>OpenDesign Prototype - {safe_title} [{ratio}]</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Outfit:wght@500;700;800&display=swap" rel="stylesheet">
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      width: {canvas_w}px;
      height: {canvas_h}px;
      overflow: hidden;
      background: {theme["bg_gradient"]};
      font-family: 'JetBrains Mono', Consolas, Menlo, Monaco, monospace;
      color: {theme["text_main"]};
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
    }}

    /* Cyber Tech Background Grid */
    .grid-overlay {{
      position: absolute;
      inset: 0;
      background-image: 
        linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
      background-size: 60px 60px;
      mask-image: radial-gradient(circle at 50% 50%, black 40%, transparent 80%);
      pointer-events: none;
    }}

    /* Main Container */
    .stage-container {{
      width: {stage_w};
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: {"24px" if is_vertical else "32px"};
      z-index: 10;
    }}

    /* Header Badge */
    .header-bar {{
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      justify-content: center;
    }}
    .badge {{
      font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
      font-size: 14px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 2px;
      padding: 6px 18px;
      border-radius: 9999px;
      background: {theme["tag_bg"]};
      border: 1px solid {theme["tag_border"]};
      color: {theme["primary"]};
      box-shadow: 0 0 20px {theme["tag_bg"]};
    }}

    .headline {{
      font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
      font-size: {headline_size};
      font-weight: 800;
      letter-spacing: -0.5px;
      background: {headline_grad};
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-align: center;
    }}

    /* Terminal Mockup Window */
    .terminal-window {{
      width: {terminal_w};
      height: {terminal_h};
      {terminal_border}
      border-radius: 20px;
      box-shadow: {theme["window_glow"]};
      backdrop-filter: blur(24px);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      position: relative;
    }}

    /* Title Bar */
    .title-bar {{
      height: 52px;
      background: rgba(255, 255, 255, 0.02);
      border-bottom: 1px solid {theme["window_border"]};
      display: flex;
      align-items: center;
      padding: 0 24px;
      position: relative;
    }}
    .traffic-dots {{
      display: flex;
      gap: 10px;
    }}
    .dot {{
      width: 13px;
      height: 13px;
      border-radius: 50%;
    }}
    .dot.red {{ background: {theme["dot_red"]}; }}
    .dot.yellow {{ background: {theme["dot_yellow"]}; }}
    .dot.green {{ background: {theme["dot_green"]}; }}

    .title-text {{
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
      font-size: 14px;
      color: {theme["text_dim"]};
      letter-spacing: 0.5px;
    }}

    /* Terminal Body */
    .terminal-body {{
      flex: 1;
      padding: {body_pad};
      font-size: {font_size_body};
      line-height: 1.8;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    .cmd-line {{
      display: flex;
      align-items: center;
      gap: 14px;
      color: {theme["text_main"]};
      font-weight: 600;
      word-break: break-all;
    }}
    .prompt {{
      color: {theme["primary"]};
    }}
    .command-text {{
      color: #ffffff;
    }}

    /* Progress bar */
    .progress-box {{
      margin: 12px 0;
      width: {progress_w};
      max-width: 100%;
      height: 8px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 999px;
      overflow: hidden;
      position: relative;
    }}
    .progress-bar {{
      width: 100%;
      height: 100%;
      background: {progress_grad};
      border-radius: 999px;
      box-shadow: 0 0 16px {theme["primary"]};
    }}

    .status-line {{
      display: flex;
      align-items: center;
      gap: 12px;
      color: {theme["accent"]};
      font-size: 18px;
      flex-wrap: wrap;
    }}
    .info-line {{
      color: {theme["text_dim"]};
      font-size: 17px;
    }}
    .highlight-badge {{
      display: inline-block;
      padding: 2px 10px;
      border-radius: 6px;
      background: {theme["tag_bg"]};
      border: 1px solid {theme["tag_border"]};
      color: {theme["primary"]};
      font-size: 14px;
      margin-left: 8px;
    }}

    /* Pulsing Cursor */
    .cursor {{
      display: inline-block;
      width: 12px;
      height: 22px;
      background: {theme["primary"]};
      vertical-align: middle;
      box-shadow: 0 0 10px {theme["primary"]};
      animation: blink 1s step-start infinite;
    }}
    @keyframes blink {{
      50% {{ opacity: 0; }}
    }}
  </style>
</head>
<body>
  <div class="grid-overlay"></div>

  <div class="stage-container">
    <div class="header-bar">
      <div class="badge">OpenDesign Prototype [{ratio}]</div>
      <div class="headline">{safe_title}</div>
    </div>

    <div class="terminal-window">
      <div class="title-bar">
        <div class="traffic-dots">
          <div class="dot red"></div>
          <div class="dot yellow"></div>
          <div class="dot green"></div>
        </div>
        <div class="title-text">bash — user@hyper-studio: ~ — {terminal_w}×{terminal_h}</div>
      </div>

      <div class="terminal-body">
        <div class="cmd-line">
          <span class="prompt">❯</span>
          <span class="command-text">{safe_command}</span>
          <span class="cursor"></span>
        </div>

        {pipeline_block if is_pipeline_mode else default_block}
      </div>
    </div>
  </div>
</body>
</html>
"""
    return html_content


def export_design_tokens(title: str, theme_key: str, output_path: str, ratio: str = "16:9"):
    theme = STYLE_THEMES.get(theme_key, STYLE_THEMES["cyber-dark"])
    is_vertical = (ratio == "9:16")
    w, h = (1080, 1920) if is_vertical else (1920, 1080)
    tw, th = (920, 1100) if is_vertical else (1280, 720)

    tokens = {
        "project": title,
        "theme": theme_key,
        "name": theme["name"],
        "resolution": {"width": w, "height": h, "ratio": ratio},
        "colors": {
            "primary": theme["primary"],
            "secondary": theme["secondary"],
            "accent": theme["accent"],
            "window_background": theme["window_bg"],
            "window_border": theme["window_border"],
            "text_main": theme["text_main"],
            "text_dim": theme["text_dim"],
            "tag_background": theme["tag_bg"],
            "tag_border": theme["tag_border"]
        },
        "typography": {
            "font_family_code": "JetBrains Mono, Consolas, monospace",
            "font_family_heading": "Outfit, -apple-system, sans-serif",
            "font_size_terminal": "18px" if is_vertical else "20px"
        },
        "layout": {
            "terminal_width": tw,
            "terminal_height": th,
            "border_radius": 20
        }
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2, ensure_ascii=False)
    print(f"✅ Exported OpenDesign Tokens: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="OpenDesign Prototype Generator for HyperPresenter Studio")
    parser.add_argument("--title", default="HyperPresenter Studio", help="Project / Tool Title")
    parser.add_argument("--command", default="hyper-presenter run pipeline --project 'HyperPresenter Studio'", help="Primary command or feature text")
    parser.add_argument("--desc", default="4-Phase Autonomous Workflow: Prototype + Motion + Prompter + ChatCut", help="Feature description text")
    parser.add_argument("--mode", choices=["pipeline", "default"], default="pipeline", help="Display mode: pipeline (4-stage workflow) or default")
    parser.add_argument("--theme", choices=list(STYLE_THEMES.keys()) + ["all"], default="cyber-dark", help="Design theme palette")
    parser.add_argument("--ratio", choices=["16:9", "9:16", "all"], default="all", help="Aspect ratio for prototypes")
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent
    tokens_dir = root_dir / "tokens"
    tokens_dir.mkdir(exist_ok=True)

    print("=" * 65)
    print("🎨 OpenDesign Prototype Generator (Dual-Ratio)")
    print(f"📌 Title: {args.title}")
    print(f"💻 Command: {args.command}")
    print(f"🔄 Mode: {args.mode}")
    print(f"📐 Ratio: {args.ratio}")
    print("=" * 65)

    themes_to_generate = list(STYLE_THEMES.keys()) if args.theme == "all" else [args.theme]
    ratios_to_generate = ["16:9", "9:16"] if args.ratio == "all" else [args.ratio]

    for r in ratios_to_generate:
        ratio_tag = "" if r == "16:9" else "_9x16"
        for t in themes_to_generate:
            html_content = generate_prototype_html(args.title, args.command, args.desc, t, ratio=r, mode=args.mode)
            out_html = root_dir / f"prototype_{t}{ratio_tag}.html"
            with open(out_html, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"✨ Generated Prototype Demo [{t} - {r}]: {out_html.name}")

            tokens_json = tokens_dir / f"tokens_{t}{ratio_tag}.json"
            export_design_tokens(args.title, t, str(tokens_json), ratio=r)

    print("\n💡 Open any generated prototype HTML file in your browser to inspect design demos!")
    print("=" * 65)


if __name__ == "__main__":
    main()
