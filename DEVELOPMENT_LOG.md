# 📜 HyperPresenter Studio - 研发全流程开发日志 (Development Log)

> **项目定位**：下一代人机协同极客短视频工业化工作流 (Next-Gen Human-AI Hybrid Video Studio)  
> **核心范式**：确定性工程工具（OpenDesign + HyperFrames + OpenCV + 剪映桌面端自动化）与人类创作者创意的毫秒级咬合。  
> **维护规范**：遵循 `session-continuity-logger` 规范，按时间线增量记录关键架构决策、版本演进与实施里程碑。

---

## 📌 当前状态速览 (Current Status & Health)

- **当前版本**：`v1.2.0-industrial`
- **默认画幅**：`16:9` (1920×1080 横屏极客大片) & `9:16` (1080×1920 移动端 Social Stack)
- **视觉美学系统**：内置 5 套主题，默认激活 `ink-wash` (现代新中式宣白水墨风)
- **流水线健康度**：
  - [x] Stage 1 · OpenDesign 原型与 Tokens 生成 (`tokens_ink-wash.json`, `prototype_ink-wash.html`)
  - [x] Stage 1.5 · 自动化三幕实拍图走查引擎 (`scripts/capture_demo_shots.js`)
  - [x] Stage 2 · 1080P 60FPS 极客动效 B-Roll 渲染与自动抽帧 (`output/broll_motion.mp4`, 10.4s)
  - [x] Stage 3 · 专属 10s 秒级口播拍摄指南与提词蓝图 (`CURRENT_SHOOTING_GUIDE.md`)
  - [x] Stage 4 · OpenCV EMA 人脸追踪重定帧与剪映桌面端草稿自动注入 (`chatcut_auto_assembly.py`)
  - [x] Master Orchestrator · 统一总控 CLI (`run_pipeline.py`)

---

## 📅 研发历史里程碑 (Milestones Timeline)

### 📅 [2026-09-24 10:00 - 12:30] Milestone 1: 概念验证与系统审查 (Inception & Review)
- **🎯 核心目标**：针对开源 CLI/开发者工具痛点，搭建“真人口播 + 终端代码动效 + 剪映”最小可行性雏形 (PoC)。
- **✅ 核心产出**：
  - 跑通 10 秒 Reasonix CLI 终端打字效果并输出初代 `reasonix_broll_10s.mp4`；
  - 产出 [REVIEW.md](file:///d:/video/视频3/hyper-presenter-studio/REVIEW.md)，深度审查出仓库存在的 7 项核心架构缺陷（路径写死、无真实人脸追踪、缺乏双画幅支持、缺少 requirements.txt、多文件命名冲突）。
- **🧠 技术决策**：
  - 拒绝简单打补丁，决定对整套系统进行工业级重构，按四大模块分工（OpenDesign / HyperFrames / Presenter / ChatCut）建立清晰契约。

---

### 📅 [2026-09-24 13:00 - 15:00] Milestone 2: 双画幅工业化重构 (Dual-Ratio Overhaul)
- **🎯 核心目标**：彻底解决移动端（9:16）与桌面端（16:9）画幅割裂，建立自动化原型与设计 Token 导出机制。
- **✅ 核心产出**：
  - 编写 `01_prototype_opendesign/generate_prototype.py`，支持一键生成全画幅与竖屏卡片原型；
  - 建立 Design Tokens 资产库（`tokens_cyber-dark.json`, `tokens_matrix-neon.json`, `tokens_cyber-purple.json`）；
  - 编写 `04_assembly_capcut/propose_edit_schemes.py`，实现方案一（圆框）、方案二（分屏/堆叠）、方案三（动态切景）的自动化预览图渲染。
- **🧠 技术决策**：
  - 采用安全 HTML 实体转义 (`html.escape`) 杜绝命令行特殊字符破坏 DOM；
  - 建立统一的色彩 Token 映射，确保原型与动效风格完全同源。

---

### 📅 [2026-09-24 15:00 - 16:30] Milestone 3: OpenCV EMA 人脸平滑追踪与剪映草稿自动化 (Smart Assembly)
- **🎯 核心目标**：消除人工拖拽关键帧，实现真实人脸跟踪居中裁剪与剪映桌面端草稿无缝注册。
- **✅ 核心产出**：
  - 在 `04_assembly_capcut/core_utils.py` 中实现 **双模态人脸追踪算法**（Haar 级联 + YCrCb 肤色聚类质心）结合 $\alpha = 0.18$ 的指数移动平均（EMA）平滑滤波；
  - 编写 `04_assembly_capcut/chatcut_auto_assembly.py`，实现零人工拖拽的 3 种成片合成；
  - 实现剪映桌面端 `root_meta_info.json` 索引库读写注入，让生成的工程直接置顶出现在剪映“最近项目”中。
- **🧠 技术决策**：
  - 引入边缘智能夹紧（Boundary Clamping），杜绝裁剪框越界崩溃；
  - 引入尾帧定格（Freeze-Frame Hold），解决真人视频比动效短时的黑屏回跳问题。

---

### 📅 [2026-09-24 16:30 - 17:15] Milestone 4: 五阶人机协同导演工作流确立 (The 5-Stage Co-Director Paradigm)
- **🎯 核心目标**：针对“AI 盲目开工、不问需求直接硬做、仅发链接用户无法感知”的交互缺陷，建立人机协同导演黄金法则。
- **✅ 核心产出**：
  - 确立并执行 **五阶人机协同工作流**：
    1. **Step 0 需求问诊**：先定画幅、时长、视觉风格、演示核心焦点；
    2. **Step 1 方案策划与用户拍板**：AI 提出三幕分镜与 Tokens，用户明确回复“确认方案”；
    3. **Step 2 高保真 Demo 与实拍图直出走查**：开发 `scripts/capture_demo_shots.js`，通过 Puppeteer 自动截取 3 幕 1080P 实拍图嵌入对话走查；
    4. **Step 3 用户走查确认**：用户审查实图确认后再启动渲染；
    5. **Step 4 动效编译与抽帧验收**：HyperFrames 编译 60FPS 演示视频，自动 FFmpeg 抽帧呈递；
    6. **Step 5 秒级提词卡与剪映总装**：交付《专属口播拍摄指南》并完成桌面端总装。
- **🧠 技术决策**：
  - 严禁先斩后奏，设立“确认方案”与“确认 Demo”两道强制 Checkpoints；
  - 杜绝仅发链接，必须依托无头浏览器生成实拍图供人类视觉走查。

---

### 📅 [2026-09-24 17:15 - 17:35] Milestone 5: 现代新中式宣白水墨体系与动效引擎避坑 (Ink-Wash & Stability)
- **🎯 核心目标**：解决传统左右分屏导致左侧内容缩小看不清的割裂痛点，打造现代宣白水墨风并攻克 HyperFrames 引擎稳定性难题。
- **✅ 核心产出**：
  - 确立并实现 **现代新中式宣白水墨风 (`ink-wash`)**：
    - 背景：宣纸宣白 (`#fbfbfa`) + 意境山水画底 (`assets/ink_wash_bg.jpg`)；
    - 字体：76px+ 毛笔书法大字 (`Ma Shan Zheng`)，主次分明，大字至上；
    - 配色：朱砂印泥红 (`#dc2626`) + 琥珀金 (`#d97706`) + 浓墨黑 (`#18181b`)；
  - 提出并落地 **全画幅演播室无损融合策略 (Full-Canvas Studio Stage Fusion)**：左侧演示内容 100% 原始尺寸不缩放，右侧演播台通过发光环柔和融合；
  - 攻克 **HyperFrames 动效渲染两大深水坑**：
    1. 彻底移除 `repeat: -1` 无限循环，避免渲染器报 `planValidation: Render duration is out of range (10000000000s)`；
    2. 将竖屏备用模板隔离在 `templates/` 子目录下，防止多 Root HTML 导致的画幅混淆。
- **🧠 技术决策**：
  - GSAP 循环必须设定有限次数（如 5s 动画设置 `repeat: 1` 刚好覆盖 10s）；
  - 主挂载容器严格遵循 `<div id="root" data-composition-id="main" data-width="1920" data-height="1080">` 契约。

---

### 📅 [2026-09-24 17:35 - 17:45] Milestone 6: 全局总控 CLI 与工程化资产规范 (Orchestration & Hygiene)
- **🎯 核心目标**：统一全流程入口，消除写死路径与冗余临时素材，整理项目准备发布。
- **✅ 核心产出**：
  - 重写根目录 `run_pipeline.py`，支持 `--status`, `--step 1..4`, `--capture-demo`, `--all`, `--restore-demo`，支持 `--theme` 参数动态感应；
  - 同步重写 `SKILL.md`, `WORKFLOW_SOP.md`, `ARCHITECTURE.md`, `REVIEW.md`；
  - 清理过期调试脚本与测试帧，配置 `.gitignore`，保留归档测试素材 `archive/session_explainer_assets_20260924.zip`。

### 📅 [2026-09-24 17:45 - 18:05] Milestone 7: 《好帮手 AI 话术私教》手账折页视频全流程贯通 (AI Coach Studio Delivery)
- **🎯 核心目标**：从 `human-ai-video-director` 摄取真实业务素材，验证 5 阶人机协同工作流在垂直业务（教育/保险/销售培训）下的实战表现。
- **✅ 核心产出**：
  - **素材吸纳与手账美学体系落地**：
    - 摄取客户挂断记录、24关实战闯关卡、45分诊断报告、纸片人贴纸；
    - 确立暖米白纸质底 (`#faf7ee`)、砖橙印泥环 (`#ea580c`) 与亮金高光 (`#f59e0b`) 的手账折页视觉规范；
    - 产出 [tokens_ai-coach.json](file:///d:/video/视频3/hyper-presenter-studio/01_prototype_opendesign/tokens/tokens_ai-coach.json) 与 [prototype_ai-coach.html](file:///d:/video/视频3/hyper-presenter-studio/01_prototype_opendesign/prototype_ai-coach.html)；
  - **60FPS 极客动效 B-Roll 渲染**：
    - 编译 [output/broll_motion.mp4](file:///d:/video/视频3/hyper-presenter-studio/output/broll_motion.mp4) (2.8 MB, 10.4s, 1920×1080 @ 60FPS)；
    - 提取 3 幕验证高清图：痛点秒挂 ➔ 24关对战 ➔ 45分体检逆袭；
  - **专属 10s 拍摄指南与提词蓝图**：
    - 生成 [03_presenter_aroll/CURRENT_SHOOTING_GUIDE.md](file:///d:/video/视频3/hyper-presenter-studio/03_presenter_aroll/CURRENT_SHOOTING_GUIDE.md) 与 9:16 移动版提词卡；
  - **ChatCut 智能总装与剪映草稿直出**：
    - 结合 EMA 人脸平滑追踪，完成 3 种成片直出：
      - `dynamic_cutaways_1920x1080.mp4` (Method 3 多景别智能切镜成片)
      - `split_presenter_1920x1080.mp4` (Method 2 全画幅无损演播室融合)
      - `face_bubble_optimized_1920x1080.mp4` (Method 1 发光圆框动态居中)
    - 自动在剪映 `root_meta_info.json` 注册工程并置顶；
  - **Windows 文件系统鲁棒性加固**：
    - 引入 `safe_unlink` 重试机制，消除并发与 FFmpeg 释放滞后引发的 `PermissionError: [WinError 32]` 异常。

---

## 🔮 未来演进规划 (Roadmap & Next Steps)

- [ ] **多模态实时口播语音驱动**：接入 Edge-TTS 与音频波形驱动，在未录制真人素材时自动生成高质量口播伴音；
- [ ] **更多东方与科技美学主题**：增加宋代天青汝窑风 (`celadon-glaze`)、极简冷灰商务风 (`slate-minimal`)；
- [ ] **CapCut 关键帧曲线扩展**：在剪映草稿中直接注入贝塞尔曲线缓动关键帧，替代硬切景。
