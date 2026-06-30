#!/usr/bin/env python3
"""
本地端到端测试：验证 Teach 平台全链路

测试流程：
  1. 搜索资料（search_course_materials.py）
  2. 生成课程讲义（generate_course.py，演示模式）
  3. 生成播客（podcast_generator.py）
  4. 生成视频（video_generator.py）
  5. 更新课程索引（update_course_index.py）
  6. 验证输出文件

用法：
  python test_full_pipeline.py "Python 编程入门"
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime


PYTHON = "C:/Users/norman/.workbuddy/binaries/python/versions/3.13.12/python.exe"
SCRIPTS_DIR = Path(__file__).parent
TEACH_WEB = SCRIPTS_DIR.parent / "teach-web"
DATA_DIR = TEACH_WEB / "data"
LESSONS_DIR = TEACH_WEB / "lessons"


def run(cmd: list[str], label: str) -> bool:
    """运行命令，返回是否成功"""
    print(f"\n▶ {label}")
    print(f"  命令：{' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode == 0:
        print(f"  ✅ {label} 成功")
        if result.stdout.strip():
            print(f"  输出：{result.stdout.strip()[:200]}")
        return True
    else:
        print(f"  ❌ {label} 失败")
        print(f"  错误：{result.stderr.strip()[:300]}")
        return False


def test_full_pipeline(topic: str) -> None:
    """端到端测试全链路"""
    print("=" * 60)
    print(f"  Teach 平台全链路测试")
    print(f"  主题：{topic}")
    print(f"  时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 清理旧数据
    course_id = topic.lower().replace(" ", "-").replace("，", "-")
    lesson_dir = LESSONS_DIR / course_id
    if lesson_dir.exists():
        shutil.rmtree(lesson_dir)
    lesson_dir.mkdir(parents=True, exist_ok=True)

    materials_file = DATA_DIR / f"materials-{course_id}.json"

    # Step 1: 搜索资料
    ok1 = run([
        PYTHON, str(SCRIPTS_DIR / "search_course_materials.py"),
        topic,
        "--sources", "arxiv,wikipedia,podcasts",
        "--max-per-source", "3",
        "--output", str(materials_file),
        "--format", "json",
    ], "Step 1: 搜索学习资料")

    if not ok1 or not materials_file.exists():
        print("\n❌ Step 1 失败，测试中止")
        return

    # 检查资料数量
    with open(materials_file, encoding="utf-8") as f:
        materials = json.load(f)
    print(f"  📊 找到 {len(materials)} 条资料")

    # Step 2: 生成课程讲义（演示模式，无需 API Key）
    ok2 = run([
        PYTHON, str(SCRIPTS_DIR / "generate_course.py"),
        topic,
        "--materials", str(materials_file),
        "--output", str(lesson_dir),
    ], "Step 2: 生成课程讲义（演示模式）")

    # Step 3: 生成播客
    course_md = lesson_dir / "course.md"
    podcast_mp3 = lesson_dir / "podcast.mp3"
    ok3 = run([
        PYTHON, str(SCRIPTS_DIR / "podcast_generator.py"),
        str(course_md),
        "--output", str(podcast_mp3),
        "--style", "monologue",
    ], "Step 3: 生成播客音频")

    # Step 4: 生成视频
    video_mp4 = lesson_dir / "video.mp4"
    ok4 = run([
        PYTHON, str(SCRIPTS_DIR / "video_generator.py"),
        str(course_md),
        "--output", str(video_mp4),
        "--no-subtitles",
    ], "Step 4: 生成教学视频")

    # Step 5: 更新课程索引
    ok5 = run([
        PYTHON, str(SCRIPTS_DIR / "update_course_index.py"),
        "--topic", topic,
        "--lesson-dir", str(lesson_dir),
        "--output", str(DATA_DIR / "courses.json"),
    ], "Step 5: 更新课程索引")

    # Step 6: 验证输出文件
    print(f"\n▶ Step 6: 验证输出文件")
    files_to_check = [
        lesson_dir / "course.md",
        lesson_dir / "quiz.json",
        lesson_dir / "meta.json",
        podcast_mp3,
        video_mp4,
        DATA_DIR / "courses.json",
    ]

    all_exist = True
    for f in files_to_check:
        if f.exists():
            size = f.stat().st_size
            print(f"  ✅ {f.name}  ({size // 1024}KB)")
        else:
            print(f"  ❌ {f.name} 不存在")
            all_exist = False

    # 总结
    print("\n" + "=" * 60)
    print("  测试总结")
    print("=" * 60)
    steps = [("搜索资料", ok1), ("生成讲义", ok2), ("生成播客", ok3), ("生成视频", ok4), ("更新索引", ok5), ("验证文件", all_exist)]
    for name, ok in steps:
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")

    passed = sum(1 for _, ok in steps if ok)
    total = len(steps)
    print(f"\n  通过：{passed}/{total}")

    if passed == total:
        print("\n🎉 全链路测试通过！")
        print(f"  课程目录：{lesson_dir}")
        print(f"  首页预览：{TEACH_WEB / 'index.html'}")
    else:
        print(f"\n⚠️ 有 {total - passed} 个步骤失败，请检查日志")


def main():
    parser = argparse.ArgumentParser(description="Teach 平台全链路测试")
    parser.add_argument("topic", nargs="?", default="Python 基础入门", help="测试主题")
    args = parser.parse_args()

    test_full_pipeline(args.topic)


if __name__ == "__main__":
    main()
