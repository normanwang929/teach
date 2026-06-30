#!/usr/bin/env python3
"""
update_course_index.py - 更新课程索引

将新生成的课程添加到 data/courses.json。

用法：
  python update_course_index.py \
    --topic "Python 编程入门" \
    --lesson-dir ../teach-web/lessons/python-intro \
    --output ../teach-web/data/courses.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def update_index(topic: str, lesson_dir: Path, output_file: Path) -> None:
    """将新课程添加到 courses.json"""
    import datetime

    # 读取现有课程
    courses = []
    if output_file.exists():
        data = json.loads(output_file.read_text(encoding="utf-8"))
        courses = data.get("courses", [])

    # 构建新课程条目
    course_id = topic.lower().replace(" ", "-").replace("/", "-")
    meta_file = lesson_dir / "meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    else:
        meta = {}

    new_course = {
        "id": meta.get("id", course_id),
        "title": topic,
        "description": meta.get("description", f"关于「{topic}」的自动生成课程"),
        "icon": meta.get("icon", "📚"),
        "tags": meta.get("tags", ["自动生成"]),
        "progress": 0,
        "lesson_count": meta.get("lesson_count", 0),
        "created_at": meta.get("created_at", datetime.datetime.now().isoformat()),
        "path": f"lessons/{course_id}/course.md",
        "podcast": f"lessons/{course_id}/podcast.mp3",
        "video": f"lessons/{course_id}/video.mp4",
        "quiz": f"lessons/{course_id}/quiz.json",
    }

    # 去重：如果已存在则更新
    existed = False
    for i, c in enumerate(courses):
        if c.get("id") == new_course["id"]:
            courses[i] = new_course
            existed = True
            break

    if not existed:
        courses.insert(0, new_course)  # 新课程插到最前面

    # 写回
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps({"courses": courses}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✅ 课程索引已更新：{output_file}")
    print(f"   新课程：{topic}")


def main():
    parser = argparse.ArgumentParser(description="更新课程索引")
    parser.add_argument("--topic", required=True, help="课程主题")
    parser.add_argument("--lesson-dir", required=True, help="课程目录")
    parser.add_argument("--output", required=True, help="courses.json 输出路径")
    args = parser.parse_args()

    lesson_dir = Path(args.lesson_dir)
    output_file = Path(args.output)
    update_index(args.topic, lesson_dir, output_file)


if __name__ == "__main__":
    main()
