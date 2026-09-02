#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
构建全离线版 index-offline.html
- 道具图片以 data URI 内嵌（160px WebP，来自 images_webp/）
- 背景/封面/logo 同样内嵌（复用 build.py 的 b64 缓存）
- 服务器缺失的 30 张图保留原 URL（在线版同样无法显示，行为一致）
"""
import base64
import json
from pathlib import Path

base = Path(__file__).parent

# 1. 读取道具数据（紧凑数组格式）
items = json.loads((base / "items_inline.json").read_text(encoding="utf-8"))

# 2. 图片 URL → data URI 映射
webp_dir = base / "images_webp"
data_uris = {}
missing = 0
for it in items:
    url = it[4]
    fname = url.rsplit("/", 1)[-1]
    stem = fname.rsplit(".", 1)[0]
    webp = webp_dir / (stem + ".webp")
    if webp.exists():
        # 缓存同一文件的 data URI（有 21 个道具共享图片）
        if stem not in data_uris:
            b64 = base64.b64encode(webp.read_bytes()).decode("ascii")
            data_uris[stem] = f"data:image/webp;base64,{b64}"
        it[4] = data_uris[stem]
    else:
        missing += 1

print(f"✓ 道具内嵌: {len(items) - missing}/{len(items)}（{missing} 张服务器缺失，保留原 URL）")

# 3. 读模板并注入
template = (base / "index.html.template").read_text(encoding="utf-8")

items_json = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
result = template.replace("/*#__INLINE_ITEMS__*/null", items_json)

# 4. 背景与 logo（复用 .b64 缓存，占位符与 build.py 一致）
for var, cache in [("__INLINE_BG1__", "bg1.b64"), ("__INLINE_BG2__", "bg2.b64"), ("__INLINE_LOGO__", "logo.b64")]:
    cache_file = base / cache
    if cache_file.exists():
        b64 = cache_file.read_text(encoding="utf-8").strip()
        ext = "jpeg" if cache.startswith("bg") else "png"
        result = result.replace(f"/*#{var}*/''", f'"data:image/{ext};base64,{b64}"')

# 注入 JSZip 库（保证离线可用，无 CDN 依赖；用于打包导出 ZIP）
jszip_src = (base / "jszip.inline.js").read_text(encoding="utf-8")
result = result.replace("/*#__INLINE_JSZIP__*/", jszip_src)

# 5. 写出
out = base / "index-offline.html"
out.write_text(result, encoding="utf-8")
print(f"✓ 生成: {out}")
print(f"  大小: {out.stat().st_size / 1024 / 1024:.1f} MB")
