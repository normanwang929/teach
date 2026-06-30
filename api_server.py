#!/usr/bin/env python3
"""
Teach Platform - 本地 API 服务器

提供前端调用的 API 接口，真正生成课程内容。

运行：
  python api_server.py

然后使用：
  http://localhost:5000  （前端页面）
  POST http://localhost:5000/api/generate  （触发生成）
"""

from __future__ import annotations
import json
import os
import subprocess
import sys
import threading
import time
import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS

# ── 配置 ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
TEACH_WEB_DIR = BASE_DIR / "teach-web"
SCRIPTS_DIR = BASE_DIR / "scripts"
OUTPUT_DIR = TEACH_WEB_DIR / "lessons"

# 任务状态存储
tasks = {}

app = Flask(__name__, static_folder=str(TEACH_WEB_DIR))
CORS(app)


# ── 路由：静态文件 ──────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(str(TEACH_WEB_DIR), "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(str(TEACH_WEB_DIR), path)


# ── API：开始生成课程 ───────────────────────────────────────────────────────
@app.route("/api/generate", methods=["POST"])
def generate():
    """接收生成请求，启动后台任务"""
    data = request.get_json()
    topic = data.get("topic", "").strip()
    
    if not topic:
        return jsonify({"error": "请输入课程主题"}), 400
    
    # 创建任务
    task_id = f"task_{int(time.time())}"
    tasks[task_id] = {
        "topic": topic,
        "status": "running",
        "progress": 0,
        "steps": [],
        "result": None,
        "error": None,
    }
    
    # 启动后台线程
    thread = threading.Thread(target=run_generation, args=(task_id, topic))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "task_id": task_id,
        "message": "生成任务已启动",
    })


def run_generation(task_id: str, topic: str):
    """后台执行生成流程"""
    task = tasks[task_id]
    slug = topic.replace(" ", "_").lower()
    output_dir = OUTPUT_DIR / slug
    
    try:
        # Step 1: 搜索资料
        update_task(task_id, 10, "搜索学习资料...")
        materials_file = TEACH_WEB_DIR / "data" / f"materials-{slug}.json"
        
        # 运行搜索脚本
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "search_course_materials.py"), topic],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR),
        )
        
        # 保存搜索结果
        materials = []
        if materials_file.exists():
            with open(materials_file, "r", encoding="utf-8") as f:
                materials = json.load(f)
        
        if not materials:
            # 如果没有搜索到，创建默认资料
            materials = [
                {
                    "url": f"https://www.google.com/search?q={topic}",
                    "title": f"{topic} 相关资料",
                    "description": f"关于 {topic} 的学习资料",
                    "content_type": "article",
                    "source": "web",
                    "language": "zh",
                    "is_free": True,
                }
            ]
        
        update_task(task_id, 20, f"找到 {len(materials)} 个相关资料")
        
        # Step 2: 生成课程
        update_task(task_id, 30, "生成课程大纲和讲义...")
        subprocess.run([
            sys.executable,
            str(SCRIPTS_DIR / "generate_course.py"),
            topic,
            "--materials", str(materials_file),
            "--output", str(output_dir),
        ], cwd=str(BASE_DIR))
        
        update_task(task_id, 60, "课程讲义生成完成")
        
        # Step 3: 生成播客
        update_task(task_id, 70, "生成播客音频...")
        course_file = output_dir / "course.md"
        audio_file = output_dir / "audio.mp3"
        
        if course_file.exists():
            subprocess.run([
                sys.executable,
                str(SCRIPTS_DIR / "podcast_generator.py"),
                str(course_file),
                "--output", str(audio_file),
            ], cwd=str(BASE_DIR))
        
        update_task(task_id, 85, "播客音频生成完成")
        
        # Step 4: 更新课程索引
        update_task(task_id, 90, "更新课程索引...")
        subprocess.run([
            sys.executable,
            str(SCRIPTS_DIR / "update_course_index.py"),
            "--topic", topic,
            "--lesson-dir", str(output_dir),
            "--output", str(TEACH_WEB_DIR / "data" / "courses.json"),
        ], cwd=str(BASE_DIR))
        
        update_task(task_id, 100, "课程生成完成！")
        task["status"] = "done"
        task["result"] = {
            "course_id": slug,
            "title": topic,
            "url": f"/library.html?course={slug}",
        }
        
    except Exception as e:
        import traceback
        task["status"] = "error"
        task["error"] = str(e)
        task["traceback"] = traceback.format_exc()
        update_task(task_id, task["progress"], f"错误：{e}")


def update_task(task_id: str, progress: int, message: str):
    """更新任务状态"""
    task = tasks[task_id]
    task["progress"] = progress
    task["steps"].append({
        "progress": progress,
        "message": message,
        "time": datetime.datetime.now().isoformat(),
    })


# ── API：查询任务状态 ───────────────────────────────────────────────────────
@app.route("/api/status/<task_id>")
def get_status(task_id):
    """返回任务状态和进度"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "任务不存在"}), 404
    
    return jsonify({
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "steps": task["steps"],
        "result": task["result"],
        "error": task["error"],
    })


# ── API：列出所有课程 ───────────────────────────────────────────────────────
@app.route("/api/courses")
def list_courses():
    """返回课程列表"""
    courses_file = TEACH_WEB_DIR / "data" / "courses.json"
    if not courses_file.exists():
        return jsonify({"courses": []})
    
    with open(courses_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return jsonify(data)


# ── API：获取课程详情 ───────────────────────────────────────────────────────
@app.route("/api/courses/<course_id>")
def get_course(course_id):
    """返回课程详情"""
    course_dir = OUTPUT_DIR / course_id
    
    if not course_dir.exists():
        return jsonify({"error": "课程不存在"}), 404
    
    result = {}
    
    # 读取元数据
    meta_file = course_dir / "meta.json"
    if meta_file.exists():
        with open(meta_file, "r", encoding="utf-8") as f:
            result["meta"] = json.load(f)
    
    # 读取讲义
    course_file = course_dir / "course.md"
    if course_file.exists():
        with open(course_file, "r", encoding="utf-8") as f:
            result["content"] = f.read()
    
    # 读取测验
    quiz_file = course_dir / "quiz.json"
    if quiz_file.exists():
        with open(quiz_file, "r", encoding="utf-8") as f:
            result["quiz"] = json.load(f)
    
    # 检查音频/视频
    result["has_audio"] = (course_dir / "audio.mp3").exists()
    result["has_video"] = (course_dir / "video.mp4").exists()
    
    return jsonify(result)


# ── 主函数 ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Teach Platform - 本地服务器")
    print("=" * 60)
    print()
    print("  🌐 前端页面：http://localhost:5000")
    print("  📡 API 接口：http://localhost:5000/api/generate")
    print()
    print("  按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()
    
    app.run(host="0.0.0.0", port=5000, debug=False)
