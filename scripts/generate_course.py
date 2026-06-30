#!/usr/bin/env python3
"""
generate_course.py - 课程内容生成器（简化版，避免 f-string 问题）

用法：
  python generate_course.py "Python 编程入门" \
    --materials ../teach-web/data/materials-Python.json \
    --output ../teach-web/lessons/python-intro \
    [--api-key SK-YOUR-KEY]
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path


def generate_demo_course(topic: str) -> str:
    """演示模式：生成模板课程（无需 LLM）"""
    return (
        f"# {topic}\n\n"
        f"> 本课程自动生成，涵盖「{topic}」的核心知识点。\n\n"
        "## 第 1 章 入门基础\n"
        "### 1.1 什么是{topic}？\n"
        "**学习目标：**\n"
        "- 理解基本概念\n"
        "- 了解应用场景\n\n"
        "**讲义：**\n"
        "（此处为自动生成内容。部署后，LLM 将根据实际资料生成完整讲义。）\n\n"
        "## 第 2 章 核心概念\n"
        "### 2.1 基础语法\n"
        "**学习目标：**\n"
        "- 掌握基本语法\n\n"
        "**讲义：**\n"
        "（自动生成内容）\n"
    )


def extract_lessons(course_md: str) -> list[str]:
    """从课程 Markdown 提取课时标题"""
    import re
    # 找 ### 课时标题
    lessons = re.findall(r"### (.+)", course_md)
    if not lessons:
        lessons = ["第 1 课", "第 2 课"]
    return lessons


def generate_demo_quiz(lesson_title: str) -> list[dict]:
    """生成演示测验"""
    return [
        {
            "question": f"关于「{lesson_title}」，以下说法正确的是？",
            "options": ["选项 A", "选项 B", "选项 C", "选项 D"],
            "answer": 0,
            "explanation": "（部署后，LLM 将生成真实测验题目）",
        }
    ]


def generate_course(
    topic: str,
    materials: list[dict],
    output_dir: Path,
    api_key: str | None,
) -> dict:
    """生成完整课程，返回课程元数据"""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: 生成课程大纲 + 讲义
    print("  📝 生成课程大纲和讲义…")
    if api_key:
        print("  ⚠️ LLM 调用未实现，使用演示模式")
    course_md = generate_demo_course(topic)

    course_file = output_dir / "course.md"
    course_file.write_text(course_md, encoding="utf-8")
    print(f"  ✅ 讲义已保存：{course_file}")

    # Step 2: 生成测验
    print("  🧪 生成课时测验…")
    lessons = extract_lessons(course_md)
    quiz_data = []
    for i, title in enumerate(lessons, 1):
        quiz_data.append({
            "lesson_id": i,
            "lesson_title": title,
            "questions": generate_demo_quiz(title),
        })

    quiz_file = output_dir / "quiz.json"
    quiz_file.write_text(
        json.dumps(quiz_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  ✅ 测验已保存：{quiz_file}")

    # Step 3: 生成课程元数据
    import datetime
    meta = {
        "id": topic.lower().replace(" ", "-"),
        "title": topic,
        "description": f"关于「{topic}」的自动生成课程",
        "icon": "📚",
        "tags": ["自动生成"],
        "progress": 0,
        "created_at": datetime.datetime.now().isoformat(),
        "lesson_count": len(quiz_data),
        "files": {
            "course": "course.md",
            "quiz": "quiz.json",
        },
    }
    meta_file = output_dir / "meta.json"
    meta_file.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  ✅ 元数据已保存：{meta_file}")

    return meta


def main():
    parser = argparse.ArgumentParser(description="生成课程讲义内容")
    parser.add_argument("topic", help="课程主题")
    parser.add_argument("--materials", required=True, help="资料 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出目录")
    parser.add_argument("--api-key", help="LLM API Key（可选）")
    args = parser.parse_args()

    # 读取资料
    materials = []
    if args.materials and Path(args.materials).exists():
        materials = json.loads(Path(args.materials).read_text(encoding="utf-8"))

    api_key = args.api_key or os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")

    output_dir = Path(args.output)
    meta = generate_course(args.topic, materials, output_dir, api_key)

    print(f"\n✅ 课程生成完成！")
    print(f"   课程 ID：{meta['id']}")
    print(f"   输出目录：{output_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        log_path = Path(__file__).parent / "error.log"
        with open(log_path, "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        print(f"❌ 错误详情已写入：{log_path}")
        sys.exit(1)
