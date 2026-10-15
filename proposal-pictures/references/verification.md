# 校验流程与脚本用法

> 铁律：**机器自检 + 目视验收，两者都过才算完成**。只跑脚本会漏语义问题；只看图会漏 7px 级几何问题。

## 0. 环境

- Python 3.8+（脚本只用标准库：`re`、`glob`、`xml.etree.ElementTree`、`subprocess`）。
- 渲染需要一个无头浏览器（脚本自动探测，按顺序）：
  - `msedge`（Windows 默认路径 `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`）
  - `chrome` / `chromium` / `google-chrome`
- 若都没有：改用任何浏览器手动截图，或 `cairosvg`/`rsvg-convert`/`inkscape`（非必须）。

## 1. 四步自检

```bash
# ① 渲染（整图）——先确认能打开、不是空白
python scripts/render_svg.py 图1.svg --png out/f1.png
python scripts/render_svg.py 图1.svg --png out/f1_2x.png --scale 2        # 汇报用 2 倍

# ② 几何自检：文字越界 / 压线（关键！）
python scripts/check_overlap.py 图1.svg 图2.svg 图3.svg --pad 12

# ③ 记法自检：禁用符号
python scripts/check_symbols.py 图1.svg

# ④ 文字清单：肉眼核对措辞与对齐
python scripts/audit_text.py 图1.svg --md out/f1_text.md
```

## 2. 怀疑某处有问题时：裁切放大

```bash
# 只渲染 x=300..900, y=540..600 这块，放大 4 倍
python scripts/render_svg.py 图1.svg --png out/zoom.png --crop "300 540 600 60" --scale 4
```

适用场景：浮动标签与连线净距、两行小字是否重叠、指标行是否拼串、边框是否压字。

## 3. 三个脚本各自查什么

### `check_overlap.py`

- 把每个 `<text>` 按"中文 1 字宽 = 字号、其余 0.55 × 字号"估成包围盒（旋转文字跳过）；
- 与所有 `line`、`polyline` 各段、`rect` 的四条边做相交判定；
- 命中即输出"文字 + 包围盒 + 相交的线段"。
- **它能同时查出两类问题**：文字压线（标签被线穿过）与文字出框（撑破方框边框）。
- 局限：估算宽度≠真实字形宽度；旋转/斜排文字不检查；`path` 画的自定义图形不检查。
  → 所以脚本报 0 **不代表**一定没问题，仍须目视。

### `check_symbols.py`

- 扫描禁用符号与记法：`↓↑`、`＋`（非专名）、`·`、`->`、`@距离`、数字与单位间缺空格、`>>>` 等；
- 规则可用 `--rules` 传入 JSON 覆盖/扩展；
- 每条命中都给"位置 + 片段 + 建议改法"。

### `audit_text.py`

- 导出每个 `<text>` 的 `x/y/font-size/text-anchor/是否旋转/字数/文字`；
- 用途：核对术语与措辞、检查字号是否跳档、检查同类元素是否对齐（同列的 `x` 应一致）。

## 4. 目视验收方法

1. 整图看一眼：层次是否清楚、主角是否突出、有没有明显空洞或拥挤。
2. 对照 `audit_text.py` 的清单，逐条读一遍文字（**读，不是看**）：措辞、术语、指标写法。
3. 对以下位置**必须**裁切放大：浮动标签、两行及以上小字、指标通栏、与箭头/边框接近的文字。
4. 换一个查看器再看一遍（浏览器 + 图片查看器）：某些查看器不认 `tspan dy` 或字体缺失，
   问题只在特定环境暴露。

## 5. 与正文的一致性核对（图改完后必做）

> **这套目视方法对数据图同样适用**：`paper-experiment` 的"出图后必须看图"可用同一手法——
> 可疑区域裁切放大（PNG 用任意看图器或图像库放大），并换一个查看器复核。
> 区别只在于数据图没有 SVG 可查几何，越框/超宽要靠出图脚本的告警（如 `run_visualization` 的标题超宽告警）。

```bash
# 图内文字与正文对不上时，用文本 diff 逐字比
python scripts/audit_text.py 图1.svg --md out/f1_text.md
# 再与正文对应段（docx/md）逐字比对；指标行建议整行复制粘贴，不要手打
```

## 6. 交付记录模板

```markdown
## 图 1 · <图名> 自检记录
- 文件：图1_xxx.svg（N 字节）
- XML：ET.parse 通过
- check_overlap：命中 0（上次 2 处：4-3 溢出 47px、4-4 溢出 13px，已修）
- check_symbols：命中 0（豁免：导师示例的 ">>>" 记号，按原样保留）
- 渲染：Edge 无头 1600×900 成功；2 倍渲染用于汇报
- 目视：整图 + 底栏裁切放大（4×）均通过
- 已知偏差：字体依赖本机；导入 PPT 后字形可能微变
```

## 7. 常见失败与定位

| 症状 | 先查什么 | 常见根因 |
| --- | --- | --- |
| 文字"错乱"、两行粘一起 | 是否同一 `<text>` 内多 `<tspan>` | 查看器不认 `dy` → 拆成独立 `<text>` |
| 文字压在线上 | `check_overlap.py` | 折线折点位置与标签重叠 → 挪折点或挪标签 |
| 文字撑出框 | `check_overlap.py`（看是否命中矩形边） | 行内塞了小字说明 → 下沉为第二行 |
| 图上文字与正文不一致 | `audit_text.py` + 正文比对 | 手打指标行 → 改为复制粘贴 |
| 渲染空白/缺字 | 是否用了外部字体或 `<image>` | 改为系统字体、内联图元 |
| 脚本报 0 但人眼看出问题 | — | 估算宽度误差 / 斜排文字 → 以目视为准，必要时放宽 `--pad` |
