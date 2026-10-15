#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_spacing.py — 框间距审计：把"并列框之间 / 组与组之间"的实际间距列出来，并标出不符合约定的。

约定（设计系统，写在 style-tokens.md）：
  S = 12px  同级并列框之间（同一组内的兄弟框）
  G = 24px  组与组之间 / 框与通栏之间 / 框与产出框之间
  T = 40px  大区块之间（如内容区与底部通栏）
用 --scale 覆盖（如 --scale 8,16,32）。

判定方式：取每个方框，沿 x/y 找"投影重叠 ≥50%"的最近邻方框，算净距；净距不在 scale 中即 FLAG
（并列组内应等于 S，组间应等于 G 或 T；数值本身对不上就说明间距随手写的）。

用法: python check_spacing.py 图1.svg [...] [--scale 12,24,40] [--tol 3]
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from xml.etree import ElementTree as ET

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SVG = "{http://www.w3.org/2000/svg}"


def num(v, d=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def rects_of(root):
    cw, ch = num(root.get("width")), num(root.get("height"))
    out = []
    for el in root.iter(SVG + "rect"):
        w, h = num(el.get("width")), num(el.get("height"))
        if w <= 20 or h <= 20:
            continue
        if cw and ch and w >= 0.8 * cw and h >= 0.8 * ch:
            continue
        out.append((num(el.get("x")), num(el.get("y")), w, h))
    return out


def overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def gaps(rects):
    """返回 [(方向, 净距, 框A索引, 框B索引)]，同向取最近邻。"""
    out = []
    for i, a in enumerate(rects):
        best = {"vertical": None, "horizontal": None}
        for j, b in enumerate(rects):
            if i == j:
                continue
            # 纵向：x 投影重叠 ≥50% 且 b 在 a 下方
            ox = overlap(a[0], a[0] + a[2], b[0], b[0] + b[2])
            if ox >= 0.5 * min(a[2], b[2]) and b[1] >= a[1] + a[3] - 1:
                d = b[1] - (a[1] + a[3])
                if best["vertical"] is None or d < best["vertical"][0]:
                    best["vertical"] = (d, j)
            # 横向：y 投影重叠 ≥50% 且 b 在 a 右侧
            oy = overlap(a[1], a[1] + a[3], b[1], b[1] + b[3])
            if oy >= 0.5 * min(a[3], b[3]) and b[0] >= a[0] + a[2] - 1:
                d = b[0] - (a[0] + a[2])
                if best["horizontal"] is None or d < best["horizontal"][0]:
                    best["horizontal"] = (d, j)
        for k, v in best.items():
            if v is not None and v[0] < 400:  # 超过 400px 视为不同区块，不参与
                out.append((k, round(v[0], 1), i, v[1]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="框间距审计")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--scale", default="12,24,40", help="允许的间距档位（px，逗号分隔）")
    ap.add_argument("--tol", type=float, default=3.0, help="与档位的允许偏差")
    a = ap.parse_args()
    scale = [float(v) for v in a.scale.split(",")]

    rc = 0
    for p in a.paths:
        root = ET.parse(p).getroot()
        rs = rects_of(root)
        gs = gaps(rs)
        cnt = Counter(g[1] for g in gs)
        print(f"== {p}  方框 {len(rs)}  相邻间距 {len(gs)}")
        print("   间距分布：" + "  ".join(f"{d}px×{c}" for d, c in sorted(cnt.items())))
        bad = [g for g in gs if not any(abs(g[1] - v) <= a.tol for v in scale)]
        for k, d, i, j in bad:
            ai, bj = rs[i], rs[j]
            print(f"   ⚠ {k} 间距 {d}px 不符合约定 {scale}："
                  f"{tuple(round(v) for v in ai)} ↔ {tuple(round(v) for v in bj)}")
        if bad:
            rc = 1
    if rc == 0:
        print("✅ 所有相邻间距都落在约定档位上")
    return rc


if __name__ == "__main__":
    sys.exit(main())
