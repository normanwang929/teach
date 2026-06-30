#!/usr/bin/env python3
"""
generate_course.py - 课程内容生成器

用法：
  # 本地模式（读取 .env 中的 API Key）
  python generate_course.py "Python 编程入门" --materials data/materials.json --output lessons/python-intro

  # 演示模式（无需 API Key）
  python generate_course.py "Python" --materials data/materials.json --output lessons/python --demo
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

# 尝试加载 .env 文件
def load_env():
    """从 .env 文件加载环境变量"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

load_env()


def generate_demo_course(topic: str) -> str:
    """演示模式：生成模板课程（无需 LLM）"""
    return (
        f"# {topic}\n\n"
        f"> 本课程自动生成，涵盖「{topic}」的核心知识点。\n\n"
        "## 第 1 章 入门基础\n"
        "### 1.1 什么是" + topic + "？\n"
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


def load_env():
    """手动加载 .env 文件（兼容无 python-dotenv 的环境）"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip("'\"")
                os.environ.setdefault(key, val)


def call_llm(prompt: str, api_key: str, base_url: str | None = None) -> str:
    """调用 LLM API（兼容 OpenAI / DeepSeek）"""
    try:
        import openai
    except ImportError:
        print("  ⚠️ 未安装 openai 库，正在安装…")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "-q"])
        import openai

    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url or os.getenv("OPENAI_BASE_URL"),
    )

    print("  🤖 正在调用 LLM 生成内容…")
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "deepseek-chat"),
        messages=[
            {"role": "system", "content": "你是一位资深讲师，擅长制作结构清晰、内容详实的中文课程讲义。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=4096,
    )
    return response.choices[0].message.content


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


def generate_quiz_with_llm(lesson_title: str, lesson_content: str, api_key: str) -> list[dict]:
    """用 LLM 生成真实测验题目"""
    prompt = f"""请根据以下课时内容，生成 3 道选择题（单选）。

课时标题：{lesson_title}
课时内容：
{lesson_content[:1000]}

要求：
1. 返回 JSON 格式，包含 3 道题目
2. 每道题包含：question（题目）、options（4个选项）、answer（正确答案索引 0-3）、explanation（解释）
3. 题目要考察核心概念，不是死记硬背
4. 难度适中，适合初学者

输出格式（直接返回 JSON 数组）：
[
  {{
    "question": "题目1",
    "options": ["A", "B", "C", "D"],
    "answer": 0,
    "explanation": "解释"
  }}
]
"""
    try:
        import json
        import re
        response = call_llm(prompt, api_key)
        # 提取 JSON（可能在 ```json 代码块中）
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return json.loads(response)
    except Exception as e:
        print(f"  ⚠️ 测验生成失败，使用演示模式：{e}")
        return generate_demo_quiz(lesson_title)


def generate_course(
    topic: str,
    materials: list[dict],
    output_dir: Path,
    api_key: str | None,
    demo: bool = False,
) -> dict:
    """生成完整课程，返回课程元数据"""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: 生成课程大纲 + 讲义
    print("  📝 生成课程大纲和讲义…")

    # 构建提示词
    prompt = "你是一位资深讲师，请为主题「" + topic + "」设计一门完整的结构化课程。\n\n"
    prompt += "要求：\n"
    prompt += "1. 使用 Markdown 格式\n"
    prompt += "2. 开头用 > 引用格式写课程简介\n"
    prompt += "3. 分多个章节（## 第 X 章 章节名）\n"
    prompt += "4. 每章包含多个课时（### X.Y 课时标题）\n"
    prompt += "5. 每个课时包含：\n"
    prompt += "   - **学习目标：**（- 列表）\n"
    prompt += "   - **讲义：**（详细内容，500字以上）\n"
    prompt += "   - 代码示例（如适用，用 ```语言 代码块）\n"
    prompt += "6. 课程总长度适中，适合 1-2 小时学习\n\n"

    if materials:
        prompt += "参考资料（可用于引用）：\n"
        for i, m in enumerate(materials[:5], 1):
            title = m.get('title', '')
            url = m.get('url', '')
            prompt += f"{i}. {title} - {url}\n"
        prompt += "\n"

    # 调用 LLM 或演示模式
    if api_key and not demo:
        course_md = call_llm(prompt, api_key)
    else:
        if not api_key:
            print("  ⚠️ 未提供 API Key，使用演示模式")
        else:
            print("  ⚠️ 演示模式开启，使用模板内容")
        course_md = generate_demo_course(topic)

    course_file = output_dir / "course.md"
    course_file.write_text(course_md, encoding="utf-8")
    print(f"  ✅ 讲义已保存：{course_file}")

    # Step 2: 生成测验
    print("  🧪 生成课时测验…")
    lessons = extract_lessons(course_md)
    quiz_data = []

    # 提取每个课时的内容（用于生成测验）
    import re
    lesson_sections = re.split(r'### ', course_md)[1:]  # 跳过第一章前的简介

    for i, title in enumerate(lessons, 1):
        # 找到该课时的内容
        lesson_content = ""
        for section in lesson_sections:
            if section.startswith(title):
                lesson_content = section[:1500]  # 取前 1500 字符
                break

        # 用 LLM 生成测验（如果可用）
        if api_key and not demo:
            questions = generate_quiz_with_llm(title, lesson_content, api_key)
        else:
            questions = generate_demo_quiz(title)

        quiz_data.append({
            "lesson_id": i,
            "lesson_title": title,
            "questions": questions,
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
    load_env()
    parser = argparse.ArgumentParser(description="生成课程讲义内容")
    parser.add_argument("topic", help="课程主题")
    parser.add_argument("--materials", required=True, help="资料 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出目录")
    parser.add_argument("--api-key", help="LLM API Key（可选，默认读 .env）")
    parser.add_argument("--demo", action="store_true", help="演示模式（不调用 LLM）")
    args = parser.parse_args()

    # 读取资料
    materials = []
    if args.materials and Path(args.materials).exists():
        materials = json.loads(Path(args.materials).read_text(encoding="utf-8"))

    # 获取 API Key（优先级：命令行 > 环境变量 > .env）
    api_key = args.api_key or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")

    output_dir = Path(args.output)
    meta = generate_course(args.topic, materials, output_dir, api_key, args.demo)

    print(f"\n✅ 课程生成完成！")
    print(f"   课程 ID：{meta['id']}")
    print(f"   输出目录：{output_dir}")
    print(f"\n📂 生成的文件：")
    print(f"   - course.md  （课程讲义）")
    print(f"   - quiz.json   （测验题目）")
    print(f"   - meta.json   （课程元数据）")


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
