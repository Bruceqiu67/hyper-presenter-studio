# ⚡ Phase 2: HyperFrames 代码动效工程 (Code Motion)

本目录是原生的 **HyperFrames 动效工程**，基于 HTML5 / CSS3 / GSAP 动画时间轴，以 60fps 渲染高质量科技感终端、3D 视差及动态 B-Roll。

---

## 常用命令

```bash
# 1. 启动交互式预览工作室 (实时在浏览器中播放并拖拽时间轴)
npm run dev
# 或
npx hyperframes preview

# 2. 检查动画工程语法与契约
npm run check
# 或
npx hyperframes check

# 3. 渲染导出 1080P/60fps 广播级 MP4
npm run render
# 或
npx hyperframes render -o ../output/reasonix_broll.mp4

# 4. 渲染透明背景 WebM (用于画中画浮动贴在真人上)
npx hyperframes render --format webm -o ../output/reasonix_overlay.webm
```

---

## 动效参数规范 (Design & Animation Metrics)
- **Canvas**：`1920 × 1080` (60 FPS)；
- **终端敲击节拍**：字符步进间隔建议 `0.06s ~ 0.09s`，符合人类真实击键节奏；
- **回车卡点**：命令敲击完成后，留白 `0.3s` 停顿，再以物理微弹冲（Scale Punch 1.03x）触发依赖下载流水线。
