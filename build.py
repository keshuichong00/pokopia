#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 items 数据 + 附件背景图 base64 注入到 HTML 模板"""
from pathlib import Path

base = Path("D:/WorkBuddy/pokopia-toolkit")
template = (base / "index.html.template").read_text(encoding="utf-8")
items_json = (base / "items_inline.json").read_text(encoding="utf-8")

# 注入道具数据
result = template.replace("/*#__INLINE_ITEMS__*/null", items_json)

# 注入附件背景图 (data:image/jpeg;base64,XXX)
bg1_b64 = (base / "bg1.b64").read_text().strip()
bg2_b64 = (base / "bg2.b64").read_text().strip()
result = result.replace("/*#__INLINE_BG1__*/''", '"data:image/jpeg;base64,' + bg1_b64 + '"')
result = result.replace("/*#__INLINE_BG2__*/''", '"data:image/jpeg;base64,' + bg2_b64 + '"')

# 注入 logo (data:image/png;base64,XXX)
logo_b64 = (base / "logo.b64").read_text().strip()
result = result.replace("/*#__INLINE_LOGO__*/''", '"data:image/png;base64,' + logo_b64 + '"')

# 注入 JSZip 库（保证离线可用，无 CDN 依赖；用于打包导出 ZIP）
jszip_src = (base / "jszip.inline.js").read_text(encoding="utf-8")
result = result.replace("/*#__INLINE_JSZIP__*/", jszip_src)

out = base / "index.html"
out.write_text(result, encoding="utf-8")
print(f"✓ 生成: {out}")
print(f"  大小: {out.stat().st_size:,} 字节 ({out.stat().st_size/1024:.1f} KB)")
