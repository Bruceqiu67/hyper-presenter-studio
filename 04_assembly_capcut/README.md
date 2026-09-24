# 🎬 Phase 4: ChatCut / 剪映自动化总装 (ChatCut Autonomous Assembly)

本目录提供 **100% 全自动化的多轨装配与渲染流水线**。告别一切手动拖拽、切片与对齐，完全由 ChatCut 自动化脚本与本地草稿引擎全权驱动。

---

## 目录结构
```text
04_assembly_capcut/
├── README.md                 # 本说明
├── chatcut_auto_assembly.py  # 核心：ChatCut 全自动剪辑总装引擎 (支持 Face Bubble 与 Tech Split)
├── assemble_draft.py         # 剪映本地草稿快速构建器
└── config/
    └── track_rules.json      # 轨道编排规则（层级、混合模式、音量比例）
```

---

## 两种全自动合成手法 (The 2 Automated Styles)

本项目原生封装并支持两种顶尖科技视频排版手法，零人工调整：

### 🎯 手法一：智能自适应居中·极客发光圆框 (Dynamic Centered Face Bubble)
- **成片文件**: `output/face_bubble_optimized_1920x1080.mp4`
- **执行命令**: `npm run assemble:bubble`
- **设计特点**: 类似 Loom / CleanShot 极客风格。结合人脸轨迹与 Smoothstep 连续曲线插值，平滑自动重定帧（Auto-Reframing），不论口播者大幅前倾或后仰，面部与手势始终稳定处于 440×440 青色（#38bdf8）发光能量环内，背景终端全景占比 >90%。

### 🖥️ 手法二：左侧极客演示 + 右侧口播双分屏 (Side-by-Side Tech Split)
- **成片文件**: `output/split_right_presenter_1920x1080.mp4`
- **执行命令**: `npm run assemble:split`
- **设计特点**: 科技发布会官宣级大片排版。左侧 1200×675 黄金画幅呈现 HyperFrames 终端动效与代码流，右侧竖屏展示口播真人半身表达与手势卡点，科技质感与真诚信任感兼备。

---

## ⚡ 一键全自动运行 (Zero Manual Operations)

```bash
# 一键自动生成两种手法的 1080P 成片 + 剪映/CapCut 本地工程草稿
npm run assemble

# 或者单独运行指定模式：
npm run assemble:bubble  # 仅生成发光圆框模式
npm run assemble:split   # 仅生成双分屏模式
```

脚本运行后：
1. **自动渲染** 1080P/60fps 广播级成品 MP4 并写入 `output/`；
2. **自动注入** 剪映 / CapCut 本地草稿库（`com.lveditor.draft`），打开剪映即可看到已排好音轨与画中画的就绪工程，全程**零手动干预**！

