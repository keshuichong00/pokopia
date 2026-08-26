#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 pokokit.com 的 JS bundle 提取所有道具数据
用法: python scrape_items.py [bundle路径]
  不带参数时自动从官网下载最新 comfort-estimate bundle
"""
import json
import re
import sys
import datetime
from pathlib import Path

# 数据文件路径：命令行参数 > 本地缓存
data_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("scrape_tmp/comfort.js")

if not data_file.exists():
    # 自动下载最新 bundle（comfort-estimate chunk 携带全部道具表）
    import urllib.request
    print("本地无缓存，开始下载最新 bundle...")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        "https://www.pokokit.com/_astro/comfort-estimate.DT70QqPK.js",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    data_file.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    print(f"✓ 已下载: {data_file} ({data_file.stat().st_size:,} 字节)")

content = data_file.read_text(encoding="utf-8")

print(f"读取 {data_file}, 大小: {len(content):,} 字符")

# 1. 提取中文名映射 Sl = JSON.parse('{"18":"结实的树枝",...}')
zh_name_match = re.search(r"=JSON\.parse\('(\{[^\']+\})'\)", content)
if not zh_name_match:
    print("❌ 找不到中文名表")
    exit(1)

zh_names = json.loads(zh_name_match.group(1))
print(f"✓ 中文名表: {len(zh_names)} 条")

# 2. 提取 item 数组 (有 menuCategory 字段的对象)
# 用更宽松的匹配，匹配每个对象 {...}
item_pattern = re.compile(
    r'\{[^{}]*?"id":(-?\d+),'
    r'[^{}]*?"name":"([^"]+)",'
    r'[^{}]*?"slug":"([^"]+)",'
    r'[^{}]*?"menuCategory":"([^"]+)",'
    r'[^{}]*?"imageFileName":"([^"]+)"'
    r'[^{}]*?\}'
)

items = []
seen_ids = set()
for m in item_pattern.finditer(content):
    item_id = int(m.group(1))
    if item_id in seen_ids:
        continue
    seen_ids.add(item_id)

    en_name = m.group(2)
    slug = m.group(3)
    category = m.group(4)
    image = m.group(5)

    # 匹配中文名
    zh_name = zh_names.get(str(item_id), en_name)

    items.append({
        "id": item_id,
        "name_en": en_name,
        "name_zh": zh_name,
        "slug": slug,
        "category": category,
        "image": f"https://www.pokokit.com/assets/pokopia_image_sources/item_portraits/{image}",
    })

print(f"✓ item 总数: {len(items)}")

# 3. 分类中英对照
category_map = {
    "Buildings": "建筑",
    "Furniture": "家具",
    "Utilities": "功能",
    "Outdoor": "户外",
    "Nature": "自然",
    "Food": "食物",
    "Materials": "材料",
    "Blocks": "地块",
    "Misc.": "杂项",
    "Kits": "套组",
    "Key Items": "重要物品",
    "Other": "其他",
}

# 4. 统计分类
from collections import Counter
cat_count = Counter(item["category"] for item in items)
print(f"\n分类统计:")
for cat_en, count in sorted(cat_count.items(), key=lambda x: -x[1]):
    cat_zh = category_map.get(cat_en, cat_en)
    print(f"  {cat_zh:>6} ({cat_en:>12}): {count:>4}")

# 5. 验证：检查 1697 这个数
print(f"\n总数校验: {sum(cat_count.values())} (期望 1697)")

# 6. 保存 JSON
output = {
    "source": "https://www.pokokit.com",
    "scraped_at": datetime.date.today().isoformat(),
    "total": len(items),
    "category_map": category_map,
    "items": items,
}

out_path = Path(__file__).parent / "items.json"
out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ 已保存到: {out_path}")
print(f"  文件大小: {out_path.stat().st_size:,} 字节")
