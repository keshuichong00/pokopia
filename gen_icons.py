#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成 PWA 图标：紫色宝珠风格，品牌一致，无字体依赖。"""
from PIL import Image, ImageDraw

PRIMARY = (181, 154, 217)        # #b59ad9
WHITE = (255, 255, 255)


def make(size, maskable):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = size // 2
    if maskable:
        # maskable：整图不透明紫底，内容留 20% 安全边
        d.rectangle([0, 0, size, size], fill=PRIMARY)
        R = int(size * 0.40)
    else:
        R = int(size * 0.46)
    bbox = [cx - R, cy - R, cx + R, cy + R]
    d.ellipse(bbox, fill=PRIMARY)                 # 紫球
    bh = max(2, int(R * 0.16))
    d.rectangle([cx - R, cy - bh, cx + R, cy + bh], fill=WHITE)   # 横带
    cr = int(R * 0.24)
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=WHITE)   # 中心白圆
    ir = max(2, int(cr * 0.5))
    d.ellipse([cx - ir, cy - ir, cx + ir, cy + ir], fill=PRIMARY)  # 中心紫点
    return img


for nm, size, mask in [
    ('icon-192.png', 192, False),
    ('icon-512.png', 512, False),
    ('icon-maskable-512.png', 512, True),
]:
    make(size, mask).save(nm)
    print('✓ 生成', nm, f'{size}x{size}')
