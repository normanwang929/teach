#!/usr/bin/env python3
"""
Teach Platform - 本地 API 服务器（简化版）
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
TEACH_WEB = BASE_DIR / "teach-web"
SCRIPTS_DIR = BASE_DIR / "scripts"

app = Flask(__name__, static_folder=str(TEACH_WEB))
CORS(app)

# 存储任务状态
tasks = {}


@app.route("/")
def index():
    return send_from_directory(str(TEACH_WEB), "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(str(TEACH_WEB), path)


@app.route("/api/generate", methods=["POST"])
def generate():
    """生成课程API"""
    try:
        data = request.get_json(force=True)
        topic = data.get("topic", "").strip()
        
        if not topic:
            return jsonify({"error": "请输入课程主题"}), 400
        
        # 创建任务
        task_id = f"task_{int(time.time())}"
        tasks[task_id] = {
            "status": "running",
            "progress": 0,
            "message": "开始生成...",
            "topic": topic
        }
        
        # 启动后台线程
        t = threading.Thread(target=generate_course_task, args=(task_id, topic))
        t.daemon = True
        t.start()
        
        return jsonify({"task_id": task_id, "message": "任务已启动"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_course_task(task_id, topic):
    """后台生成课程"""
    try:
        slug = topic.replace(" ", "-").lower()
        output_dir = TEACH_WEB / "lessons" / slug
        
        # 更新进度
        tasks[task_id]["progress"] = 10
        tasks[task_id]["message"] = "搜索学习资料..."
        
        # 搜索资料
        materials_file = TEACH_WEB / "data" / f"materials-{slug}.json"
        subprocess.run([
            sys.executable,
            str(SCRIPTS_DIR / "search_course_materials.py"),
            topic
        ], cwd=str(BASE_DIR), capture_output=True)
        
        tasks[task_id]["progress"] = 30
        tasks[task_id]["message"] = "生成课程讲义..."
        
        # 生成课程
        subprocess.run([
            sys.executable,
            str(SCRIPTS_DIR / "generate_course.py"),
            topic,
            "--materials", str(materials_file),
            "--output", str(output_dir)
        ], cwd=str(BASE_DIR), capture_output=True)
        
        tasks[task_id]["progress"] = 60
        tasks[task_id]["message"] = "生成播客音频..."
        
        # 生成音频
        course_file = output_dir / "course.md"
        if course_file.exists():
            subprocess.run([
                sys.executable,
                str(SCRIPTS_DIR / "podcast_generator.py"),
                str(course_file),
                "--output", str(output_dir / "audio.mp3")
            ], cwd=str(BASE_DIR), capture_output=True)
        
        tasks[task_id]["progress"] = 90
        tasks[task_id]["message"] = "更新课程索引..."
        
        # 更新索引
        subprocess.run([
            sys.executable,
            str(SCRIPTS_DIR / "update_course_index.py"),
            "--topic", topic,
            "--lesson-dir", str(output_dir),
            "--output", str(TEACH_WEB / "data" / "courses.json")
        ], cwd=str(BASE_DIR), capture_output=True)
        
        tasks[task_id]["status"] = "done"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["message"] = "生成完成！"
        
    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["message"] = f"错误: {str(e)}"


@app.route("/api/status/<task_id>")
def get_status(task_id):
    """查询任务状态"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "任务不存在"}), 404
    return jsonify(task)


@app.route("/api/courses")
def get_courses():
    """获取课程列表"""
    courses_file = TEACH_WEB / "data" / "courses.json"
    if courses_file.exists():
        with open(courses_file, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"courses": []})


if __name__ == "__main__":
    print("=" * 60)
    print("Teach Platform 本地服务器")
    print("=" * 60)
    print("前端: http://localhost:5000")
    print("API:  http://localhost:5000/api/generate")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)
