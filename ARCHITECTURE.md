# 📑 HyperPresenter Studio - 系统架构与设计文档 (System Architecture)

本文档客观陈述 `hyper-presenter-studio` 的系统全景设计、模块职责切分与底层技术实现。

---

## 一、 系统定位与设计哲学 (Design Philosophy)

本项目定位为**人机协同极客短视频工业化工作流**（面向开源项目、CLI工具、SaaS、API 等技术场景）。

针对传统制作中“纯真人口播太枯燥”与“纯代码逐帧微调视频太累”的矛盾，系统采用**“四权分立，各司其职”**的解耦架构：
- **OpenDesign** 负责**视觉基调与布局**（高精度 UI 原型、暗黑科技配色 Tokens、跨端自适应布局）；
- **HyperFrames** 负责**灵魂动效**（真实键盘打字节奏、终端扫描线、3D 视差推拉、无损 60fps 渲染）；
- **真人创作者** 负责**温度与可信度**（眼神交流、观点表达、情绪感染力、视线与手势指引）；
- **ChatCut / 剪映自动化** 负责**总装与自适应融合**（实时人脸平滑追踪重定帧、双轨对齐、自动索引注册剪映桌面端草稿）。

---

## 二、 系统架构与模块分工 (System Architecture)

```mermaid
flowchart TD
    subgraph S0["Stage 0 & 1: 需求问诊与方案拍板 (Intake & Proposal)"]
        I1["前置问诊 4 大参数 (画幅/时长/风格/演示焦点)"] --> I2["方案策划 (三幕分镜 + Tokens + 演播室无损融合)"]
        I2 --> I3{"用户明确回复【确认方案】"}
    end

    subgraph S2["Stage 2: 原型构建与实拍图走查 (OpenDesign & Capture)"]
        I3 --> A1["generate_prototype.py (现代水墨 / 极光 / 赛博主题)"]
        A1 --> A2["capture_demo_shots.js (自动提取 3 幕 1080P 实拍图嵌入对话)"]
        A2 --> A3{"用户走查实拍图并回复【确认 Demo / 下一步】"}
    end

    subgraph S3["Stage 3: HyperFrames 代码动效编译 (60FPS B-Roll)"]
        A3 --> B1["index.html (16:9 根入口，隔离竖屏至 templates/)"]
        B1 --> B2["HyperFrames CLI 渲染 1080P 60FPS broll_motion.mp4"]
        B2 --> B3["FFmpeg 自动抽取 3 幕成片实拍帧呈递用户验收"]
    end

    subgraph S4["Stage 4: 真人拍摄指南与提词卡 (Presenter A-Roll)"]
        B3 --> C1["generate_shooting_guide.py (秒级分镜卡点与肢体手势指引)"]
        C1 --> C2["CURRENT_SHOOTING_GUIDE.md (10s 提词蓝图)"]
        C2 --> C3["用户拍摄并存入 03_presenter_aroll/presenter.mp4"]
    end

    subgraph S5["Stage 5: ChatCut 自动化总装与草稿注入 (Desktop Assembly)"]
        B2 & C3 --> D1["core_utils.py (OpenCV EMA 人脸平滑居中追踪)"]
        D1 --> D2["chatcut_auto_assembly.py (全画幅演播室融合 / 动态切景)"]
        D2 --> E1["手法 A: 极客发光圆框 (Face Bubble)"]
        D2 --> E2["手法 B: 全画幅演播室无损融合 (Full-Canvas Stage Fusion)"]
        D2 --> E3["手法 C: 多镜头智能切景 (Dynamic Cutaways)"]
        D2 --> E4["注入剪映草稿并注册 root_meta_info.json 置顶项目"]
    end
```

---

## 三、 核心技术实现与算法 (Technical Implementations)

### 1. 全自动实时人脸追踪与平滑重定帧 (Real-Time EMA Face Tracking Engine)
- **挑战**：传统固定框裁剪在口播者微动或手势变化时，容易导致人脸偏移或被边缘切割；硬编码关键帧则缺乏泛化性。
- **算法设计**（位于 `04_assembly_capcut/core_utils.py`）：
  1. **双模态智能检测**：优先采用 OpenCV Haar Cascade 级联分类器检测人脸中心；若侧脸或低照度漏检，自动回退至人体 YCrCb 肤色聚类质心算法（Skin Color Centroid Heuristic）；
  2. **EMA 指数移动平均平滑滤波**：
     $$\text{ema}_t = \alpha \cdot \text{target}_t + (1 - \alpha) \cdot \text{ema}_{t-1} \quad (\alpha = 0.18)$$
     消除离散帧跳跃，使镜头运动如物理滑轨般平滑丝滑；
  3. **边缘智能夹紧 (Boundary Clamping)**：动态保证 490×490 裁剪视窗始终严格处于视频物理边界内部，杜绝黑边与越界崩溃；
  4. **尾帧定格自适应 (Freeze-Frame Hold)**：当真人素材时长短于 B-Roll 时，自动定格最后一帧微笑画面，避免帧跳回第 0 帧。

### 2. 全画幅演播室无损融合技术 (Full-Canvas Studio Stage Fusion)
- **痛点破局**：传统左右分屏强制将 16:9 内容压缩至半屏，造成字号骤缩至 14px 以下、文字模糊看不清，且人与画面割裂感极强；
- **无损解决方案**：
  - **100% 原始尺寸保留**：演示窗口全程保持 1920×1080 完整无损尺寸，核心字号保持在 76px 磅礴大字；
  - **右侧演播台自然嵌合**：真人置于画面右侧专属演播台区域，通过双发光能量环（或水墨柔边印泥光环）与背景完美融合，既保证演示细节纤毫毕现，又赋予画面强烈的沉浸式科技演播室质感。

### 3. 横屏 (16:9) 与竖屏 (9:16) 双画幅工业化支持 (Dual Aspect Ratio Architecture)
- **横屏 (16:9 / 1920×1080)**：
  - **Bubble 模式**：440×440 圆框居于右下角 (`1420, 580`)，外沿环绕主题专属能量环；
  - **Stage Fusion 模式**：全画幅演示窗口 + 右侧演播台真人嵌合；
  - **Dynamic 模式**：Shot 1 (0-2.5s) 全屏居中真人 ➔ Shot 2 (2.5-7.5s) 全屏演示+圆框 ➔ Shot 3 (7.5-10s) 演播台无损融合收尾。
- **竖屏 (9:16 / 1080×1920)**：
  - **Bubble 模式**：360×360 紧凑气泡，定位在底部安全区上方 (`680, 1340`)，避开平台点赞与评论按钮；
  - **Social Stack 模式**：上半屏 1000×562 浮动终端卡片 + 下半屏 1080×1080 真人口播半身，完美契合短视频受众注意力；
  - **Dynamic 模式**：Shot 1 (0-2.5s) 竖屏人像 Hook ➔ Shot 2 (2.5-7.5s) 移动端发光圆框 ➔ Shot 3 (7.5-10s) 上下堆叠收尾。

### 4. 剪映 / CapCut 桌面端自动草稿注入与索引注册 (Draft Indexing)
- 自动嗅探操作系统默认草稿根目录（Windows: `AppData/Local/JianyingPro/`，macOS: `Movies/JianyingPro/`）；
- 构建 `draft_meta_info.json` 与 `draft_content.json`，多轨道、时间戳与 Transform 几何坐标预置就绪；
- **全自动更新 `root_meta_info.json` 索引库**：使得生成的草稿立即可见于剪映桌面端“最近项目”首位。

---

## 四、 仓库目录规范 (Directory Layout)

```text
hyper-presenter-studio/
├── 01_prototype_opendesign/          # 【阶段一】OpenDesign 原型生成
│   ├── generate_prototype.py         # 原型与 Token 自动化生成脚本 (16:9 & 9:16)
│   ├── prototype_cyber-dark.html     # 赛博暗黑主题 (横屏 1920x1080)
│   ├── prototype_cyber-dark_9x16.html# 赛博暗黑主题 (竖屏 1080x1920 移动端卡片)
│   ├── prototype_matrix-neon.html    # 极客骇客绿主题
│   ├── prototype_cyber-purple.html   # 赛博霓虹紫主题
│   └── tokens/                       # 导出的 JSON 设计 Token
│
├── 02_motion_hyperframes/            # 【阶段二】HyperFrames 代码动效
│   ├── index.html                    # 横屏 16:9 动效工程 (逐字打字机)
│   ├── index_vertical.html           # 竖屏 9:16 移动端动效工程
│   └── hyperframes.json              # 动效工程配置
│
├── 03_presenter_aroll/               # 【阶段三】真人口播摄制
│   ├── generate_shooting_guide.py    # 专属拍摄指南与提词卡生成器
│   ├── CURRENT_SHOOTING_GUIDE.md     # 横屏拍摄指南 (向左前方指引)
│   └── CURRENT_SHOOTING_GUIDE_9x16.md# 竖屏拍摄指南 (向上指引/平台安全区)
│
├── 04_assembly_capcut/               # 【阶段四】ChatCut 自动化总装
│   ├── core_utils.py                 # 底层工具库：人脸平滑跟踪、动态资产定位、剪映索引注册
│   ├── propose_edit_schemes.py       # 剪辑提案与 Demo 抽帧预览生成器 (双画幅)
│   └── chatcut_auto_assembly.py      # 100% 自动总装引擎 (Bubble / Split / Dynamic)
│
├── assets/                           # 永久视效资产库
│   ├── circle_ring.png               # 赛博青 #38bdf8 霓虹能量光环
│   └── circle_mask.png               # 极客抗锯齿圆形蒙版
│
├── output/                           # 产出交付库
│   ├── broll_motion.mp4              # HyperFrames 渲染的标准 B-Roll 视频
│   ├── EDITING_PROPOSAL.md           # 16:9 剪辑提案审查报告
│   ├── EDITING_PROPOSAL_9X16.md      # 9:16 剪辑提案审查报告
│   ├── face_bubble_optimized_1920x1080.mp4
│   ├── split_presenter_1920x1080.mp4
│   ├── dynamic_cutaways_1920x1080.mp4
│   ├── face_bubble_optimized_1080x1920_vertical.mp4
│   ├── split_presenter_1080x1920_vertical.mp4
│   └── dynamic_cutaways_1080x1920_vertical.mp4
│
├── WORKFLOW_SOP.md                   # 4 阶段全流程标准作业程序 (SOP)
├── ARCHITECTURE.md                   # 本技术架构文档
├── REVIEW.md                         # 架构盲审报告与修复追踪
├── requirements.txt                  # Python 依赖清单
├── package.json                      # 统一 npm scripts 入口
└── LICENSE                           # MIT License
```
