#!/usr/bin/env python3
"""测试运行 generate_course.py 并捕获完整错误"""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent / "generate_course.py"
PYTHON = "C:/Users/norman/.workbuddy/binaries/python/versions/3.13.12/python.exe"

cmd = [
    PYTHON, str(SCRIPT),
    "Python 基础入门",
    "--materials", "../teach-web/data/materials-python-基础入门.json",
    "--output", "../teach-web/lessons/python-基础入门",
]

print("运行命令：", " ".join(cmd))
print("=" * 60)

result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    cwd=Path(__file__).parent,
)

print("退出码：", result.returncode)
print("=" * 60)
if result.stdout:
    print("【标准输出】")
    print(result.stdout)
print("=" * 60)
if result.stderr:
    print("【错误输出】")
    print(result.stderr)
print("=" * 60)
