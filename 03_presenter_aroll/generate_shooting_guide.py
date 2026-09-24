#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HyperPresenter Studio - Presenter Shooting Guide & Teleprompter Generator (Dual-Ratio Edition)
Calculates exact duration, word count limits, camera distance, body cues,
safe zone boundaries (16:9 horizontal vs 9:16 mobile),
and outputs a second-by-second shooting blueprint for the presenter.
"""

import os
import sys
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def generate_guide_markdown(title: str, duration: int, core_command: str, ratio: str = "16:9", theme: str = "ink-wash") -> str:
    is_vertical = (ratio == "9:16")
    min_words = int(duration * 3.2)
    max_words = int(duration * 4.0)

    # Dynamic 3-act split based on duration
    t1_end = round(duration * 0.32, 1)
    t2_end = round(duration * 0.75, 1)

    act1_words = max(8, int(min_words * 0.32))
    act2_words = max(12, int(min_words * 0.43))
    act3_words = max(8, min_words - act1_words - act2_words)

    ratio_title = "竖屏 9:16 (抖音/视频号/小红书/Reels)" if is_vertical else "横屏 16:9 (B站/YouTube/科技官网)"

    if is_vertical:
        camera_cue = "手机固定在支架上，**双眼对齐屏幕上方 35% 水平线**，绝不要大仰角仰拍下巴；人像置于中下部"
        safe_zone_cue = "• **避开顶部 15%**（平台搜索栏与返回键）<br>• **避开底部 20%**（双行字幕、评论点赞输入区）<br>• 面部与手部集中在中部核心黄金安全区"
        gesture_cue = f"• **右手食指抬起向上方微扬**（指引观众视线上移观看浮动终端卡片）<br>• 语气自信、干练、节奏卡点紧凑"
        framing_strategy = "竖屏录制半身人像，在 ChatCut 竖屏模式中会自动构建【上方浮动代码卡片 + 下方真人出镜】的 Social Stack 结构"
    else:
        camera_cue = "手机或相机水平横置，**双眼对齐画面上方 1/3 水平线**，面部居中微偏右"
        safe_zone_cue = "• 四周留出 5% 电视播控安全边距<br>• 保持左右画面干净，方便后期叠加发光圆框或双分屏"
        gesture_cue = f"• **右手抬起，食指坚定指向左侧/前方**（指引观众看向左侧大屏代码窗口）<br>• 语气笃定、专业、有掌控感"
        framing_strategy = "横屏或竖屏半身录制均可，ChatCut 自动进行 EMA 人脸追踪居中裁剪，生成全画幅演播室无损融合"

    # Theme-aware B-roll visual cues
    if theme == "ink-wash":
        cue_act1 = "宣纸泼墨展卷，Ma Shan Zheng 书法大字与终端命令淡入，光标流转"
        cue_act2 = "键盘极客敲击声起，依赖进度条 0% 飙至 100%，朱砂印章与对勾点亮"
        cue_act3 = "三幕成片 Bento 矩阵铺展，全画幅演播室无损融合，朱砂印章钤印"
        script_act1 = "“告别繁琐安装，一行指令开启极简创作！”"
        script_act2 = f"“终端敲入 `{core_command}`，全流程秒级跑通！”"
        script_act3 = "“一键自动总装，广播级成片即刻出炉！”"
    elif theme == "ai-coach":
        cue_act1 = "杂志手账暖纸展卷，客户痛点秒挂纸片人红叉警示，荧光笔划出核心痛点"
        cue_act2 = "24关拟真对战闯关卡铺展，对战音频声波流转，实战拆解动态浮现"
        cue_act3 = "45分体检全面逆袭，五星战力评级炸裂，金色通关印章重磅钤印"
        script_act1 = "“电话刚开口就被客户秒挂？别慌！”"
        script_act2 = f"“好帮手 AI 话术私教，24 关真机拟真实战，招招拆解！”"
        script_act3 = "“从 45 分到五星逆袭，让高转化成交像呼吸一样自然！”"
    else:
        cue_act1 = "终端窗口淡入，光标高频闪烁，准备就绪"
        cue_act2 = "键盘极客敲击声起，依赖安装条 0% 飙到 100%，绿色对勾亮起"
        cue_act3 = "科技高光粒子划过，Pipeline 流式状态初始化完成"
        script_act1 = "“还在为繁琐的配置头疼？看这里！”"
        script_act2 = f"“只需在终端敲入 `{core_command}`，一键跑通！”"
        script_act3 = "“立即体验，把时间留给创造。”"

    md = f"""# 🎙️ 《{title}》极客口播拍摄蓝图与提词卡 ({ratio_title})

> **生成目标**：{title} 官方演示视频（配套 HyperFrames 工业级代码动效 B-Roll）  
> **画幅标准**：**{ratio} ({ratio_title})**  
> **视觉主题**：**{theme}**  
> **严格时长约束**：**{duration} 秒（误差建议控制在 ±1 秒以内）**  
> **推荐总字数**：**{min_words} ~ {max_words} 字**（中文自然语速约 3.5 字/秒，切忌过快或拖沓）

---

## 📐 一、 摄制环境与机位设置规范 (Camera Setup)

| 检查项 | 工业级设置要求 | 极客技巧 / 避免踩坑 |
| :--- | :--- | :--- |
| **拍摄画幅** | **手机竖屏 9:16**（1080×1920 或 4K） | {framing_strategy} |
| **镜头距离** | **50 cm ~ 70 cm**（胸口至头顶完整半身） | 避免离镜头过近（避免大头贴广角畸变），也避免过远（面部微表情需清晰可见） |
| **视线水平** | **平视或微俯角（3°~5°）** | {camera_cue} |
| **画面安全区** | **核心视效安全区** | {safe_zone_cue} |
| **收音要求** | **无线麦克风 / 领夹麦 / 降噪耳机** | 距离嘴巴 15cm 左右，防喷麦，环境底噪控制在 `-40dB` 以下 |
| **光线环境** | **正前方柔光或侧前方自然光** | 面部光线均匀，避免头顶单一直射顶光造成“眼窝阴影” |

---

## 🎬 二、 秒级分镜卡点与动作指引 (Second-by-Second Cues)

在录制口播时，**肢体动作与眼神卡点**是让视频充满信赖感与网感的核心，请严格对照以下时间节点做动作：

| 时间戳 | 口播台词 (建议字数) | 真人肢体动作 (Visual Cue) | 对应演示画面 (B-Roll Sync) |
| :---: | :--- | :--- | :--- |
| **00:00 - {t1_end:04.1f}s**<br>(第一幕：安装篇) | **{script_act1}**<br>(约 {act1_words} 字) | • **眼神锁定镜头**，表情微带疑问与共鸣<br>• 身体微微前倾，拉近与观众心理距离 | {cue_act1} |
| **{t1_end:04.1f} - {t2_end:04.1f}s**<br>(第二幕：使用篇) | **{script_act2}**<br>(约 {act2_words} 字) | {gesture_cue} | {cue_act2} |
| **{t2_end:04.1f} - {duration:04.1f}s**<br>(第三幕：成片篇) | **{script_act3}**<br>(约 {act3_words} 字) | • 嘴角微收露出笃定微笑<br>• **竖起大拇指或点头确认**，眼神持续停留 0.5s 后再按暂停 | {cue_act3} |

---

## 💡 三、 录制避坑黄金法则

1. **录制首尾各留 0.5 秒“静止帧”**：
   - 按下录制键后，**先对镜头保持微笑与定格 0.5 秒**再开口说话；
   - 讲完最后一句话后，**眼神保持看镜头 0.5 秒**再伸手关机，方便后期无缝入画！
2. **手势动作尽量在上半身胸口至下巴之间**：
   - 指向动作、手掌强调要利落，切忌在胸口以下乱晃，否则容易出画。
3. **录完视频直接放入本目录**：
   - 将录制好的视频命名为 `presenter.mp4` 存入 `03_presenter_aroll/` 目录；
   - 自动化剪辑引擎将自动完成面部检测、音频提取与画幅自适应总装！
"""
    return md


def main():
    parser = argparse.ArgumentParser(description="Generate shooting guide and teleprompter")
    parser.add_argument("--title", default="HyperPresenter Studio 演示", help="Video Title")
    parser.add_argument("--duration", type=int, default=10, help="Target duration in seconds")
    parser.add_argument("--command", default="npx hyper-presenter setup", help="Core command/feature mentioned")
    parser.add_argument("--theme", default="ink-wash", help="Visual theme: ink-wash, prismatic-aurora, cyber-dark, etc.")
    parser.add_argument("--ratio", choices=["16:9", "9:16", "all"], default="all", help="Aspect ratio for guide")
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent

    ratios = ["16:9", "9:16"] if args.ratio == "all" else [args.ratio]

    for r in ratios:
        suffix = "_9x16" if r == "9:16" else ""
        out_file = root_dir / f"CURRENT_SHOOTING_GUIDE{suffix}.md"
        md_content = generate_guide_markdown(args.title, args.duration, args.command, ratio=r, theme=args.theme)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        print("=" * 65)
        print(f"🎙️ Presenter Shooting Guide Generated [{r}]!")
        print(f"⏱️ Target Duration: {args.duration}s (Exact)")
        print(f"📁 Guide Saved: {out_file.name}")
        print("=" * 65)


if __name__ == "__main__":
    main()
