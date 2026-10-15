# sk_03 · Proposal Pictures

中文技术申报书 / 技术方案**配图标配**（SVG 优先，可导入 PPT 编辑）的 Claude Code skill 仓库。

> 本仓库把一套实际项目里打磨出来的画图规范固化成可复用 skill：**三类图的版式 + 样式令牌 + 文字与符号规范 + 指标表述规范 + 几何自检脚本 + 图↔文↔方案一致性核对**。

## 安装

**项目级**（推荐，随项目走）：

```bash
mkdir -p <项目>/.claude/skills
cp -r proposal-pictures <项目>/.claude/skills/
```

**用户级**（所有项目可用）：

```bash
# macOS / Linux
mkdir -p ~/.claude/skills && cp -r proposal-pictures ~/.claude/skills/
# Windows PowerShell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse proposal-pictures "$env:USERPROFILE\.claude\skills\"
```

装好后，Claude Code 会在命中触发词（画图 / 配图 / 技术路线图 / 检查图片文字 …）时自动加载 `proposal-pictures/SKILL.md`。

## 仓库结构

```
sk_03/
├── README.md                     本文件
├── LICENSE.txt                   使用许可
└── proposal-pictures/             ← skill 本体（可整个拷进 .claude/skills/）
    ├── SKILL.md                  入口：触发条件、五步工作流、硬规则、自检脚本用法
    ├── references/               按需加载的细节（渐进披露）
    │   ├── figure-types.md       三类图版式：总体框架图 / 技术路线图 / 研究计划矩阵
    │   ├── style-tokens.md       配色、字体、字号、圆角、箭头、安全边距
    │   ├── text-norms.md         文字规范：术语、称谓、符号禁用表、换行、全半角
    │   ├── indicator-wording.md  指标表述规范：单位、基线、限定条件、成对约束、口径
    │   └── verification.md       自检流程与脚本用法、验收清单
    ├── scripts/                  纯标准库 Python，无第三方依赖
    │   ├── audit_text.py         列出 SVG 里每个 text 的坐标/字号/锚点/文字
    │   ├── check_overlap.py      文字包围盒 vs 线段/矩形边框：越界与压线检测
    │   ├── check_symbols.py      禁用符号与记法扫描（↓ / ＋ / · / >>> / @1 km …）
    │   └── render_svg.py         Edge/Chrome 无头渲染整图或裁切放大（用于目视验收）
    └── assets/
        └── template.svg          起手模板：调色板 + 箭头 marker + 标题条骨架
```

## 30 秒上手

```bash
# 1) 渲染出来看
python proposal-pictures/scripts/render_svg.py 图1.svg --png out.png

# 2) 机器自检（越界 / 压线）
python proposal-pictures/scripts/check_overlap.py pictures/*.svg

# 3) 符号与记法检查
python proposal-pictures/scripts/check_symbols.py pictures/*.svg

# 4) 文字清单（人工核对措辞与对齐）
python proposal-pictures/scripts/audit_text.py 图1.svg
```

## 起手模板长这样

![模板预览](proposal-pictures/assets/template_preview.png)

（`proposal-pictures/assets/template.svg` 渲染结果：标题条 + 上级通栏 + 层次带与模块 + 支撑产出框 + 兄弟部分 + 底部指标通栏 + 图注）

## 这套规范解决什么问题

| 常见事故 | 本 skill 的对应手段 |
| --- | --- |
| 文字压线 / 撑出方框 | `check_overlap.py` 几何自检（文字盒 vs 线段与矩形边框） |
| 相邻两根 `tspan` 在某些查看器里拼成一串 | `text-norms.md`：跨行一律拆成独立 `<text>`，行尾补标点 |
| 图上用了 `↓≥10%` 这类自创记法 | `text-norms.md` 符号禁用表 + `check_symbols.py` |
| 图与正文/技术方案指标写法不一致 | `indicator-wording.md`：单位、基线、限定条件、成对约束 |
| 图上写了做不到的承诺 | `indicator-wording.md`「不画大饼」条款：承诺必有依据与限定 |
| 导师/模板给的示例被擅自改写 | `SKILL.md` 硬规则：示例原样使用，差异只进对照表 |
| 目视漏检（人眼看不出 7px 净距） | 几何自检 + 裁切放大目视（`render_svg.py --crop`） |

## 许可

见 `LICENSE.txt`。
