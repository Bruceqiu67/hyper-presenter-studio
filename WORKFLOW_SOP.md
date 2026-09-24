# 📋 极客真人口播视频全流程实操 SOP (Interactive Studio SOP)

> **定位**：面向技术开发者、科技博主与技术布道师的 1080P 极客网感口播视频工业化创作指南。  
> **画幅标准**：全面覆盖 **16:9 横屏极客大片** 与 **9:16 移动端社交爆款 (Social Stack)**。  
> **核心原则**：**问诊先行、方案确认、实图走查、确认再渲染、零人工拖拽出片**。

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

## ⚡ 极速起步：全自动流水线总控 (Master CLI)

项目根目录提供了统一的工业级流水线总控脚本 `run_pipeline.py`：

```bash
# 1. 检查全流程流水线健康度与素材准备情况
python run_pipeline.py --status

# 2. 阶段执行命令
python run_pipeline.py --step 1        # [Stage 1] 生成现代水墨/极光 UI 原型与 Tokens
python run_pipeline.py --capture-demo  # [Review]  自动提取 3 幕高清实拍图嵌入供走查
python run_pipeline.py --step 2        # [Stage 2] 编译三幕式 60FPS 极客动效 B-Roll 并抽帧
python run_pipeline.py --step 3        # [Stage 3] 生成 10s 秒级分镜卡点与提词蓝图
python run_pipeline.py --step 4        # [Stage 4] 运行人脸追踪、景别切镜并注入剪映草稿

# 3. 终极一键全贯通出片 (在放入 presenter.mp4 之后)
python run_pipeline.py --all

# 4. 快速体验与验收 (手头暂无录音时，一键恢复测试素材体验总装)
python run_pipeline.py --restore-demo
```

---

## 🎨 视觉设计体系与官方主题 (Visual Themes)

项目内置 5 套经工业化调优的现代设计主题，每个主题均配备专属的 Tokens、字体、配色与背景质感：

| 主题标识 (`--theme`) | 风格定位 | 画布背景 | 核心配色 | 适用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **`ink-wash` (现代新中式宣白水墨风)** | 东方美学、留白写意、高信噪比 | 宣纸宣白 (`#fbfbfa`) + 意境山水背景 | 浓墨黑 (`#111113`) + 朱砂红 (`#dc2626`) + 墨青 (`#0d9488`) | 具有人文底蕴的开源工具、CLI、独立产品官宣 |
| **`prismatic-aurora` (极光五彩绚烂风)** | 深夜流光、玻璃拟态、多重光晕 | 深紫夜幕 (`#11092a`) + 弥散光晕 | 天蓝 (`#38bdf8`) + 洋红 (`#f472b6`) + 暖金 (`#fbbf24`) | AI 大模型、前沿算法库、酷炫 Web3 / 全栈框架 |
| **`cyber-dark` (赛博青暗黑极客风)** | 冷峻深邃、极简高对比 | 太空深蓝 (`#050811`) + 科技经纬网 | 冰蓝高亮 (`#38bdf8`) + 靛蓝 (`#818cf8`) + 翡翠绿 (`#34d399`) | 基础架构、云原生、DevOps、数据库工具 |
| **`matrix-neon` (极客骇客绿)** | 经典黑客帝国、命令行信仰 | 矩阵深黑 (`#030a06`) | 荧光翠绿 (`#10b981`) + 浅绿高光 (`#a7f3d0`) | 安全审计工具、Linux 内核、逆向分析项目 |
| **`cyber-purple` (赛博霓虹紫)** | 潮流元宇宙、赛博朋克 | 深邃暗紫 (`#07040d`) | 霓虹紫 (`#c084fc`) + 荧光粉 (`#f472b6`) | 创意工具、新媒体框架、设计工程化套件 |

---

## 🛡️ 工业化工程红线与避坑黄金法则 (Engineering Red Lines)

在全流程开发与交付中，**必须坚守以下铁律**：

### 1. 人机协同交互红线 (Director Red Lines)
- ❌ **严禁盲目开工**：任何演示视频制作前，必须先完成画幅、时长、风格、内容的**前置问诊**；
- ❌ **严禁先斩后奏**：必须给出方案，**待用户明确“确认方案”后**，方可制作 Demo；
- ❌ **严禁仅给网页链接让用户脑补**：提供 Demo 时，**必须使用截屏引擎将 3 幕高清实拍效果图直接贴进对话中**；
- ❌ **严禁未经确认直接渲染视频**：用户审查实拍图并回复**“确认 Demo / 下一步”**后，才准启动 HyperFrames 编译渲染。

### 2. 排版与视觉红线 (Typography & Layout Red Lines)
- 📏 **大字至上原则**：主标题必须采用 **76px 以上磅礴大字**（推荐搭配书法体如 `Ma Shan Zheng` 或粗宋 `Noto Serif SC 900`），核心命令不低于 36px，Bento 卡片标题不低于 42px，**杜绝任何密集小字看不清的问题**；
- 🖥️ **全画幅演播室融合原则**：成片展示区域必须保持 **100% 原始尺寸无损呈现**，真人口播演播台作为专属融合区置于右侧（带双发光能量环与水墨柔和晕染），**绝不允许将左侧内容强制缩放导致字体模糊割裂**。

### 3. HyperFrames 动效渲染避坑红线 (HyperFrames Engine Red Lines)
- ⚠️ **严禁在 Master Timeline 中使用 `repeat: -1`**：无休止循环会导致 HyperFrames 探测出 `10000000000s` 的异常无限时长，触发 `planValidation: Render duration is out of range` 崩溃。必须使用有限次数循环（如 `repeat: 1` 配合 5s 动画刚好覆盖 10s）；
- 📐 **严格遵守 `#root` 契约**：页面主挂载容器必须为 `<div id="root" data-composition-id="main" data-width="1920" data-height="1080">`，明确画幅尺寸；
- 🗂️ **避免同目录多 Root HTML 冲突**：一个动效目录根层级只能保留一个 `index.html`，备用模板（如竖屏版）必须隔离存放在 `templates/` 或 `compositions/` 目录下，防止编译器画幅混淆。

---

## 🎬 阶段实操详解 (Phase Details)

### 阶段一：需求问诊、方案确认与 Demo 走查 (Step 0 ~ 3)
1. 发起前置需求调研（画幅、时长、主题、演示要点）；
2. 输出详尽的三幕结构与 Design Tokens 方案，等待用户回复 **“确认方案”**；
3. 执行原型生成与自动截屏：
   ```bash
   python 01_prototype_opendesign/generate_prototype.py --theme ink-wash --ratio 16:9
   node scripts/capture_demo_shots.js
   ```
4. 将捕获的 3 张高清实拍图嵌入对话，呈递给用户审查；
5. 根据反馈微调，直至用户回复 **“确认 Demo”**。

### 阶段二：HyperFrames 动效编译与成片抽帧 (Step 4)
1. 运行渲染流水线：
   ```bash
   python run_pipeline.py --step 2
   ```
2. 引擎自动完成 1080P 60FPS 逐帧渲染（耗时约 40s），并自动调用 FFmpeg 在 2.0s、5.0s、8.5s 抽取三幕关键帧验证成片。

### 阶段三：专属拍摄指南生成 (Step 5.1)
```bash
python run_pipeline.py --step 3
```
脚本严格根据成片 10.4 秒精确时长计算最佳中文语速（约 3.5 字/秒），生成包含眼神对齐、肢体卡点与提词台词的指南文件：
- 查看指南：[03_presenter_aroll/CURRENT_SHOOTING_GUIDE.md](file:///d:/video/视频3/hyper-presenter-studio/03_presenter_aroll/CURRENT_SHOOTING_GUIDE.md)

### 阶段四：ChatCut 自动化剪辑总装与剪映草稿注入 (Step 5.2)
用户放入录制视频（或运行 `python run_pipeline.py --restore-demo`）：
```bash
python run_pipeline.py --step 4
```
**总装全自动化管线**：
1. **音频分离与波形对齐**：自动匹配口播音频与 B-Roll 背景；
2. **OpenCV EMA 人脸平滑追踪**：自适应识别出镜人脸，消除手持抖动，生成完美稳定的近景 Hook 与演播台特写；
3. **剪映本地草稿置顶注册**：直接将工程写入剪映本地库，并更新 `root_meta_info.json` 索引，打开剪映即可在最近项目中看到置顶草稿！
