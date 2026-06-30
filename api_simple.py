#!/usr/bin/env python3
"""超简单版本 - 确保能工作"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import os
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

BASE = Path(__file__).parent
TEACH = BASE / "teach-web"
SCRIPTS = BASE / "scripts"


@app.route("/")
def index():
    return send_file(TEACH / "index.html")


@app.route("/<path:path>")
def static(path):
    return send_file(TEACH / path)


@app.route("/api/generate", methods=["POST"])
def generate():
    """生成课程 - 简化版"""
    topic = request.json.get("topic", "")
    if not topic:
        return jsonify({"error": "缺少主题"}), 400
    
    print(f"\n{'='*60}")
    print(f"开始生成课程: {topic}")
    print(f"{'='*60}\n")
    
    # 直接调用生成脚本
    cmd = f'python "{SCRIPTS}/generate_course.py" "{topic}" --output "{TEACH}/lessons/{topic}"'
    print(f"运行命令: {cmd}")
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=str(BASE)
    )
    
    print(f"输出: {result.stdout}")
    if result.stderr:
        print(f"错误: {result.stderr}")
    
    return jsonify({
        "success": True,
        "message": f"课程「{topic}」生成完成！",
        "output": result.stdout
    })


if __name__ == "__main__":
    print("服务器启动: http://localhost:5000")
    app.run(port=5000, debug=True)
