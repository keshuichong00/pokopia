#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
并发下载全部道具图片到 images/ 目录
- 已存在的文件跳过（增量下载）
- 失败自动重试 3 次
- 结束输出统计报告
"""
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE = Path(__file__).parent
IMG_DIR = BASE / "images"
IMG_DIR.mkdir(exist_ok=True)

with open(BASE / "items.json", encoding="utf-8") as f:
    items = json.load(f)["items"]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
MAX_WORKERS = 16
RETRIES = 3


def download(item):
    url = item["image"]
    fname = url.rsplit("/", 1)[-1]
    dest = IMG_DIR / fname
    if dest.exists() and dest.stat().st_size > 0:
        return ("skip", fname, dest.stat().st_size)
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers=UA)
            data = urllib.request.urlopen(req, timeout=30).read()
            dest.write_bytes(data)
            return ("ok", fname, len(data))
        except Exception as e:
            if attempt == RETRIES - 1:
                return ("fail", fname, 0)
            time.sleep(1.5 * (attempt + 1))
    return ("fail", fname, 0)


stats = {"ok": 0, "skip": 0, "fail": 0}
fails = []
t0 = time.time()

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
    futures = {ex.submit(download, it): it for it in items}
    done = 0
    for fu in as_completed(futures):
        status, fname, size = fu.result()
        stats[status] += 1
        if status == "fail":
            fails.append(fname)
        done += 1
        if done % 200 == 0:
            print(f"  进度 {done}/{len(items)}...")

elapsed = time.time() - t0
total_size = sum(f.stat().st_size for f in IMG_DIR.glob("*.png"))
print(f"\n===== 下载完成 ({elapsed:.0f}s) =====")
print(f"  新下载: {stats['ok']}, 跳过(已存在): {stats['skip']}, 失败: {stats['fail']}")
print(f"  图片目录: {IMG_DIR}")
print(f"  文件总数: {len(list(IMG_DIR.glob('*.png')))}, 总大小: {total_size/1024/1024:.1f} MB, 平均: {total_size/1697/1024:.1f} KB")
if fails:
    print(f"  失败列表(前20): {fails[:20]}")
