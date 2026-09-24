---
name: hyper-presenter-studio
description: Next-Gen Human-AI Hybrid Video Studio. Industrialized 5-Stage Collaborative Workflow (Pre-Intake, Proposal Sign-off, In-Chat Visual Prototype Screenshots, 1080P 60FPS HyperFrames Motion B-Roll & FFmpeg frame validation, Prompter Guides, OpenCV EMA Face Tracking, and Zero-Manual JianYing/CapCut desktop assembly).
---

# ⚡ HyperPresenter Studio 工业级协同制作规范 (Studio Skill)

专为**“极客真人口播 + 纯代码科技/水墨动效 + 剪映桌面端自动化”**打造的 Agent 协同制作规范。

当用户提出想要制作“真人口播科技视频”、“产品/CLI 演示视频”、“带代码动效的真人宣传片”时，智能体激活本 Skill，**严格遵循五阶人机协同导演工作流推进**，坚守所有工程与美学红线。

---

## 🔄 五阶人机协同导演工作流 (The 5-Step Co-Director Flow)

```mermaid
flowchart TD
    subgraph S0["Step 0：前置需求问诊 (Intake)"]
        A0["问诊 4 大核心参数：画幅 / 时长 / 视觉基调 / 演示核心焦点"] --> A1["用户输入具体偏好 (如：16:9 + 10s + 宣白水墨 + 完整三幕)"]
    end

    subgraph S1["Step 1：方案策划与用户拍板 (Proposal)"]
        A1 --> B1["AI 给出定制化策划方案:
        • 视觉设计体系 (Design Tokens、配色、字号规范)
        • 10s 秒级三幕分镜时间轴与镜头规划
        • 演播室舞台融合策略 (100% 无损比例，不缩放)"]
        B1 --> B2{"用户审查并明确回复【确认方案】"}
    end

    subgraph S2["Step 2 & 3：Demo 构建、实拍图走查与确认 (Visual Demo)"]
        B2 --> C1["OpenDesign 生成高保真 HTML 交互原型 Demo"]
        C1 --> C2["📸 必须通过截屏引擎提取 3 幕高清实拍效果图嵌入对话"]
        C2 --> C3{"用户直观查看实拍图走查"}
        C3 -->|提出微调意见 (如：字号放大、换山水背景)| C1
        C3 -->|拍板锁定| C4["用户明确回复【确认 Demo / 下一步】"]
    end

    subgraph S4["Step 4：HyperFrames 动效编译与抽帧验收 (B-Roll Render)"]
        C4 --> D1["锁定 Tokens，HyperFrames 编译 1080P 60FPS 演示视频"]
        D1 --> D2["自动调用 FFmpeg 抽取 3 幕成片实拍帧呈递用户验收"]
    end

    subgraph S5["Step 5：专属拍摄指南与 ChatCut 自动总装 (Assembly)"]
        D2 --> E1["生成《专属口播拍摄指南》 (秒级台词字数 + 手势卡点)"]
        E1 --> E2["用户放入口播视频 (或运行 --restore-demo 快速实测)"]
        E2 --> E3["ChatCut 自动化引擎接管:
        • OpenCV EMA 人脸平滑重定帧居中
        • 全画幅演播室无缝融合
        • 100% 直出成品视频 + 注入剪映桌面端草稿"]
    end
```

---

## 🛡️ 工业化工程红线 (Engineering Red Lines)

在全流程协同开发中，智能体**必须坚守以下 4 大黄金铁律**：

### 1. 导演协同红线 (No Blind Start & Mandatory Checkpoints)
- ❌ **严禁盲目开工**：任何演示视频制作前，必须先完成画幅（16:9 vs 9:16）、时长（如 10s）、视觉风格（水墨、极光、赛博等）、演示要点的**前置问诊**；
- ❌ **严禁先斩后奏**：必须给出方案，**待用户明确回复“确认方案”后**，方可制作 Demo；
- ❌ **严禁仅给网页链接让用户脑补**：提供 Demo 时，**必须使用截屏引擎（`node scripts/capture_demo_shots.js`）将 3 幕高清实拍效果图直接贴进对话中**供直观走查；
- ❌ **严禁未经确认直接渲染视频**：用户审查实拍图并回复**“确认 Demo / 下一步”**后，才准启动 HyperFrames 编译渲染。

### 2. 排版与视觉红线 (Typography & Studio Layout)
- 📏 **大字至上原则**：主标题必须采用 **76px 以上磅礴大字**（搭配书法体如 `Ma Shan Zheng` 或粗宋 `Noto Serif SC 900`），核心命令不低于 36px，Bento 卡片标题不低于 42px，**杜绝任何小字看不清的问题**；
- 🖥️ **全画幅演播室融合原则**：成片展示区域必须保持 **100% 原始尺寸无损呈现**，真人口播演播台作为专属融合区置于右侧（带双发光能量环与水墨/柔和晕染），**绝不允许将左侧演示内容强制缩小导致文字模糊割裂**。

### 3. HyperFrames 动效稳定性红线 (HyperFrames Engine Contract)
- ⚠️ **严禁在 Master Timeline 中使用 `repeat: -1`**：无休止循环会导致 HyperFrames 探测出 `10000000000s` 的异常无限时长，触发 `planValidation: Render duration is out of range` 崩溃。必须使用有限次数循环（如 `repeat: 1` 配合 5s 动画覆盖 10s）；
- 📐 **严格遵守 `#root` 挂载契约**：页面主挂载容器必须为 `<div id="root" data-composition-id="main" data-width="1920" data-height="1080">`，明确画幅尺寸；
- 🗂️ **单一 Root 文件原则**：一个动效目录根层级只能保留一个 `index.html`，备用模板（如竖屏版）必须隔离存放在 `templates/` 子目录下，防止编译器画幅混淆。

---

## 🎨 视觉设计体系 (Visual Themes)

| 主题标识 (`--theme`) | 风格定位 | 画布背景 | 核心配色 | 适用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **`ink-wash` (现代新中式宣白水墨风)** | 东方美学、留白写意、高信噪比 | 宣纸宣白 (`#fbfbfa`) + 意境山水背景 | 浓墨黑 (`#18181b`) + 朱砂红 (`#dc2626`) + 琥珀金 (`#d97706`) | 具有人文底蕴的开源工具、CLI、独立产品官宣 |
| **`prismatic-aurora` (极光五彩绚烂风)** | 深夜流光、玻璃拟态、多重光晕 | 深紫夜幕 (`#11092a`) + 弥散光晕 | 天蓝 (`#38bdf8`) + 洋红 (`#f472b6`) + 暖金 (`#fbbf24`) | AI 大模型、前沿算法库、酷炫 Web3 / 全栈框架 |
| **`cyber-dark` (赛博青暗黑极客风)** | 冷峻深邃、极简高对比 | 太空深蓝 (`#050811`) + 科技经纬网 | 冰蓝高亮 (`#38bdf8`) + 靛蓝 (`#818cf8`) + 翡翠绿 (`#34d399`) | 基础架构、云原生、DevOps、数据库工具 |
| **`matrix-neon` (极客骇客绿)** | 经典黑客帝国、命令行信仰 | 矩阵深黑 (`#030a06`) | 荧光翠绿 (`#10b981`) + 浅绿高光 (`#a7f3d0`) | 安全审计工具、Linux 内核、逆向分析项目 |
| **`cyber-purple` (赛博霓虹紫)** | 潮流元宇宙、赛博朋克 | 深邃暗紫 (`#07040d`) | 霓虹紫 (`#c084fc`) + 荧光粉 (`#f472b6`) | 创意工具、新媒体框架、设计工程化套件 |

---

## ⚡ 统一流水线总控命令 (Master CLI)

```bash
# 检查流水线全阶段就绪情况
python run_pipeline.py --status

# 阶段 1：生成 UI 原型与 Design Tokens
python run_pipeline.py --step 1 --theme ink-wash

# 阶段 1.5：提取三幕高清实拍效果图嵌入对话供用户直观走查
python run_pipeline.py --capture-demo

# 阶段 2：编译 60FPS 3 幕式演示动效 B-Roll 并自动抽帧
python run_pipeline.py --step 2

# 阶段 3：生成 10s 秒级分镜卡点与提词蓝图
python run_pipeline.py --step 3

# 阶段 4：执行人脸平滑重定帧、全画幅融合并注入剪映桌面端草稿
python run_pipeline.py --step 4 --theme ink-wash

# 一键跑通全部流水线 (录入口播后)
python run_pipeline.py --all

# 快速实测：一键恢复测试口播素材进行总装验收
python run_pipeline.py --restore-demo
```
