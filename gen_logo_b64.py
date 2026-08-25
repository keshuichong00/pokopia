#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate logo.b64 base64 cache from logo.png"""
import base64
from pathlib import Path

base = Path("D:/WorkBuddy/pokopia-toolkit")
src = base / "logo.png"
dst = base / "logo.b64"
dst.write_text(base64.b64encode(src.read_bytes()).decode())
print(f"logo.b64 generated: {dst.stat().st_size:,} bytes")
