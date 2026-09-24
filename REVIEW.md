# HyperPresenter Studio 审查与重构升级报告

> **重构更新 (2026-09-24)**：本审查报告中指出的所有架构不一致、硬编码、路径割裂与流程缺陷，已全部在全新升级的工业级流水线中**彻底修复并实测通过**！
> 
> **本次优化落地核心成果**：
> 1. ✅ **五阶人机协同导演工作流 (SOP)**：建立问诊先行、方案确认、实图走查、确认再渲染、零人工总装的标准闭环；
> 2. ✅ **自动化实拍图引擎 (`scripts/capture_demo_shots.js`)**：Puppeteer 无头浏览器自动截取 3 幕 1080P 实拍效果图嵌入对话，彻底杜绝“仅给网页链接让用户脑补”；
> 3. ✅ **现代新中式宣白水墨风 (`ink-wash`)**：高精度山水画底、76px+ 书法大字 (`Ma Shan Zheng`)、朱砂印泥红 (`#dc2626`)、琥珀金 (`#d97706`) 与演播室无损融合；
> 4. ✅ **HyperFrames 动效引擎稳定性加固**：消除无限循环 GSAP 避免编译崩溃，隔离竖屏模板至 `templates/` 杜绝多 Root 冲突；
> 5. ✅ **全自动实时人脸追踪与平滑重定帧**：OpenCV Haar + EMA 滤波居中裁剪，剪映桌面端草稿自动注入与 `root_meta_info.json` 实时索引注册；
> 6. ✅ **统一流水线总控 CLI (`run_pipeline.py`)**：单命令完成全阶段驱动、健康度检查与 demo 快速恢复。

---

## 历史审查记录 (2026-09-24 初始版本)

审查日期：2026-09-24。范围是仓库源码与文档的对照，没有重新跑渲染和合成。

结论：这是一条面向开发者工具口播的四段流水线，仓库里已经有一套写死的 10 秒 Reasonix CLI 样例。文档描述的能力和代码实际能做的事差得很远。换一个产品、换一段口播，这条流水线目前接不上。

## 项目实际是什么

设计上分四步，每步一个目录：

| 阶段 | 目录 | 实际入口 | 产物 |
| --- | --- | --- | --- |
| 原型 | `01_prototype_opendesign/` | `npm run proto:generate` | 三套静态 HTML（暗青、骇客绿、霓虹紫）和配色 JSON |
| 演示动画 | `02_motion_hyperframes/` | `npm run hyperframes:render` | 一段 10 秒终端动画 |
| 拍摄指南 | `03_presenter_aroll/` | `npm run guide:generate` | 秒级提词卡，要求竖屏、50–70 cm、约 32–40 字 |
| 合成 | `04_assembly_capcut/` | `npm run edit:propose`，再 `assemble:bubble` / `assemble:split` | 右下角圆框，或左演示右真人 |

圆框方案用 OpenCV 逐帧裁切、套圆形遮罩和青色环，再用 FFmpeg 压成 H.264。分屏方案整段交给 FFmpeg。`output/` 里已经有按这个样例跑出来的成片和预览图。

原型和动画没有衔接。改 `01_prototype_opendesign/generate_prototype.py` 的标题、命令或配色，不会改到 HyperFrames。`WORKFLOW_SOP.md` 里「锁定 Token，再把原型编译成 B-Roll」这一步不存在。

## 文档和仓库不是同一套东西

根目录 [README.md](README.md)、[ARCHITECTURE.md](ARCHITECTURE.md)、[SKILL.md](SKILL.md)、[WORKFLOW_SOP.md](WORKFLOW_SOP.md) 和四个阶段自己的 README 互相矛盾，也和磁盘上的文件对不上。

- 根 README 写的是 `01_prototype_opendesign/assets/`、`02_motion_hyperframes/src/`。这些目录不存在。真正的原型生成器、总装脚本、`output/`、`scripts/` 都没写进这份目录树。
- 阶段 README 还列了不存在的文件：`logo.svg`、`specs/terminal_layout.md`、`design_tokens.json`、`raw/`、`audio/`、`config/track_rules.json`。
- [package.json](package.json) 的 `"main": "index.js"` 没有对应文件。
- `templates/cli_installation_demo/` 是一份 20–30 秒分镜说明，没有可运行模板。流水线本身被写死成 10 秒 Reasonix。
- 没有 `requirements.txt`。合成依赖 OpenCV、Pillow、NumPy，安装说明只写了 Node 和 Python。
- 没有 `.gitignore`。口播原片、成片、预览图都放在仓库里。

[SKILL.md](SKILL.md) 承诺的逐字敲击（`typingSpeed: 0.08s`）、3D 倾斜、屏幕扫描线、透明 WebM、BGM 侧链，在 `02_motion_hyperframes/index.html` 里都没有。动画是一条 GSAP 时间轴：窗口淡入、两行命令直接出现、进度条从 1.9 秒拉到约 3.1 秒、轻微放大。命令文字一开始就是完整的，没有逐字打出来，光标也没有闪烁。`JetBrains Mono` 和 `Inter` 写在 CSS 里，但没有加载字体。GSAP 从 jsDelivr 拉取，断网时渲染会失败。工程里没有帧率设置，文档里的「1080P / 60fps」没有依据。

HyperFrames 时间轴注册方式本身是对的：暂停的 GSAP，`window.__timelines["main"]` 对得上根节点的 `data-composition-id`。

## 会让流程跑偏的问题

### 1. 渲染产物和合成脚本找的不是同一个文件

根脚本把动画写到 `output/broll_motion.mp4`：

```json
"hyperframes:render": "hyperframes render ./02_motion_hyperframes -o ./output/broll_motion.mp4"
```

见 [package.json](package.json)。合成和提案却固定读取 `output/reasonix_broll_10s.mp4`。阶段二 README 又写成 `../output/reasonix_broll.mp4`。[WORKFLOW_SOP.md](WORKFLOW_SOP.md) 也指向 `reasonix_broll_10s.mp4`。按 README 渲染完再去总装，会找不到画面。

透明浮层同样有两套文件名：根脚本是 `output/broll_overlay.webm`，阶段二 README 是 `../output/reasonix_overlay.webm`。

### 2. 新拍的口播不会被用上

拍摄指南让人把视频存成 `03_presenter_aroll/presenter.mp4`。总装入口写死了这一台机器上的一次素材：

```python
root_dir = "d:/video/视频3/hyper-presenter-studio"
broll_path = os.path.join(root_dir, "output", "reasonix_broll_10s.mp4")
presenter_path = os.path.join(root_dir, "03_presenter_aroll", "713dcf459dcaaf58953ccb8307874a8e.mp4")
audio_path = os.path.join(root_dir, "03_presenter_aroll", "presenter.wav")
```

见 `04_assembly_capcut/chatcut_auto_assembly.py` 的 `main()`。`scripts/render_face_bubble_tracked.py` 和 `scripts/test_crop_frames.py` 也是这个绝对路径。换电脑、换目录、换视频，脚本仍去找旧文件。

`04_assembly_capcut/propose_edit_schemes.py` 会按文件名优先找带 `presenter` 的视频，总装不会。两边看到的不是同一条素材。

### 3. 「面部追踪」是这一条样片的手工关键帧

圆心来自写死的 12 个坐标，例如 0 秒 `(272, 620)`、2 秒 `(340, 460)`。见 `chatcut_auto_assembly.py` 里 `assemble_method_bubble()` 的 `kf_cx` / `kf_cy`。这是针对那条 544×960 样片量出来的，不是人脸检测。换一个人、换机位、换分辨率，圆框会裁到肩膀或背景。

口播比背景短时，代码把人物视频跳回第 0 帧再播，而不是停在最后一帧。

圆框还依赖 `output/circle_ring.png`。环在产出目录里，不在素材目录里。清空 `output/` 之后，圆框合成会在读环时失败。背景若不是 1920×1080，贴圆框时会越界。

`scripts/render_face_bubble_tracked.py` 和 `assemble_method_bubble()` 几乎是同一段逻辑的两份拷贝，之后改一处不会自动改另一处。

### 4. 方案三和「注入剪映就能打开」都没有实现

`propose_edit_schemes.py` 写了三套方案。第三套是 0–2.5 秒全屏人、2.5–7.5 秒圆框、7.5–10 秒分屏，并让用户运行 `npm run assemble`。这个命令实际是 `chatcut_auto_assembly.py --mode all`，只跑圆框和分屏，没有切镜模式。

方案三的预览只把人物放大贴到中间。滤镜读了 B-Roll 作为第二路输入，但没有使用它。

`assemble_draft.py` 写出的草稿只有空轨道。`chatcut_auto_assembly.py` 里的 `build_chatcut_desktop_draft()` 是自制 JSON：时长写死 10 秒，帧率 30，人物素材尺寸写死 544×960，也没有登记进剪映的草稿索引。这不是剪映能直接打开的工程。脚本还会在检测到剪映目录时直接往本机草稿库里建文件夹。

### 5. 预览图和成片不是同一套算法

方案一预览在 5 秒处做固定裁切 `crop=490:490:35:240`，再按矩形叠上去，没有圆遮罩，也没有用那套关键帧。同一时刻成片用的圆心大约是 `(350, 490)`。用户看着预览拍板，出来的成片对不上。

提案脚本把 FFmpeg 的标准输出和标准错误都丢掉，也不检查退出码。文件缺失时仍会写一份「三套方案已生成」的报告。总装那边即使检查退出码，也把 FFmpeg 的报错丢掉了，失败时看不到原因。

### 6. 提词卡和动画时间对不上，而且不会随时长变化

`03_presenter_aroll/CURRENT_SHOOTING_GUIDE.md` 把 3.5–7.5 秒说成「进度条从 0 飙到 100、键盘声、绿勾」。`02_motion_hyperframes/index.html` 里进度条在 1.9–3.1 秒就已经走完，4.5 秒进入第二条命令。指南里的键盘声、粒子、高频闪烁光标，动画里都没有。

`03_presenter_aroll/generate_shooting_guide.py` 会按时长改三段的时间边界和总字数，但三段示例台词永远是那三句固定短句。`--duration 30` 时，时间轴被拉开，提词仍是大约 40 字。

两条合成的声音来源也不一样：圆框用单独的 `presenter.wav`，分屏用视频自带音轨并强制截到 10 秒（`-t 10`）。视频没有音轨时，分屏成片是静音的。

### 7. 原型生成器直接把用户文字嵌进 HTML

`generate_prototype.py` 的 `generate_prototype_html()` 把标题、命令、说明放进 f-string，没有转义。命令里出现 `<` 或 `&` 时页面会坏。

矩阵绿和霓虹紫主题里，`.highlight-badge` 仍写死成青色 `rgba(56, 189, 248, …)`，不跟主题走。

## 现在还能用的部分

作为 Reasonix、10 秒、这一条口播的样例，圆框和分屏的渲染脚本是能跑的：`output/` 里已经有 `face_bubble_optimized_1920x1080.mp4` 和 `split_right_presenter_1920x1080.mp4`。三套 HTML 原型可以在浏览器里打开看配色。HyperFrames 的时间轴注册方式符合运行时约定。

它还不是一个可复用的工坊。

## 建议的修复顺序

1. 统一 B-Roll 和口播的路径，用参数或相对路径，不要写死 `d:/video/视频3/...` 和哈希文件名。
2. 圆框改成真实人脸检测，或明确标成「仅此样片的手工关键帧」。把 `circle_ring.png` 移出 `output/`。
3. 删掉或真正实现方案三和剪映草稿。预览图改成和成片同一套裁切。
4. 让原型、动画、提词共用同一份时长和文案。FFmpeg 失败时把错误打出来。
5. 补上 Python 依赖和 `.gitignore`，把口播原片移出仓库。把各 README 的目录树改成磁盘上真实的文件。
