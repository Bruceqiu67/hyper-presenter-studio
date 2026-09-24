# 🎨 Phase 1: OpenDesign 原型沉淀区

本目录用于存放从 **OpenDesign**（或 Figma / Penpot / 本地设计系统）中导出的视觉原型、设计 Tokens 与静态资产。

---

## 目录结构
```text
01_prototype_opendesign/
├── README.md               # 本说明
├── assets/                 # 存放导出的 SVG / PNG 静态资产
│   ├── logo.svg            # 产品矢量 Logo
│   └── icons/              # 终端控制按钮、科技徽章等
├── tokens/
│   └── design_tokens.json  # 色彩规范、字体、阴影定义
└── specs/
    └── terminal_layout.md  # 终端窗体尺寸、边框半径与字符排版规范
```

---

## 视觉规范推荐 (Cyber Geek Style)
- **分辨率**：`1920 × 1080` (16:9)
- **终端背景**：`rgba(15, 23, 42, 0.85)`（磨砂玻璃质感，Backdrop-filter blur 16px）
- **终端边框**：`1px solid rgba(56, 189, 248, 0.2)`（微亮青蓝发光边）
- **点缀色**：
  - Cyan: `#38BDF8`
  - Green: `#10B981`
  - Amber: `#F59E0B`
  - Violet: `#818CF8`
