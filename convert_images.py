#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
把 images/ 下的 PNG 道具图统一处理：
- 等比缩放到最长边 160px（导出图标显示尺寸）
- 转 WebP q85（保留透明通道）
- 输出到 images_webp/
"""
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

BASE = Path(__file__).parent
SRC = BASE / "images"
DST = BASE / "images_webp"
DST.mkdir(exist_ok=True)

MAX_SIDE = 160
QUALITY = 85


def convert(p: Path):
    out = DST / (p.stem + ".webp")
    if out.exists() and out.stat().st_size > 0:
        return "skip"
    img = Image.open(p)
    if img.mode not in ("RGBA", "RGB"):
        img = img.convert("RGBA")
    # 只有大于 160 才缩放
    if max(img.size) > MAX_SIDE:
        img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    img.save(out, "WEBP", quality=QUALITY)
    return "ok"


files = sorted(list(SRC.glob("*.png")) + list(SRC.glob("*.webp")))
stats = {"ok": 0, "skip": 0}
t0 = time.time()

with ThreadPoolExecutor(max_workers=8) as ex:
    for r in ex.map(convert, files):
        stats[r] += 1

out_files = list(DST.glob("*.webp"))
total = sum(f.stat().st_size for f in out_files)
print(f"===== 转换完成 ({time.time()-t0:.0f}s) =====")
print(f"  转换: {stats['ok']}, 跳过: {stats['skip']}, 失败: {len(files)-stats['ok']-stats['skip']}")
print(f"  输出: {DST}")
print(f"  文件数: {len(out_files)}, 总大小: {total/1024/1024:.1f} MB, 平均: {total/len(out_files)/1024:.1f} KB")
print(f"  base64 后约: {total*4/3/1024/1024:.1f} MB")
