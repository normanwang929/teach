#!/usr/bin/env python3
"""测试 API 服务器"""
import requests
import json
import time

API_BASE = "http://localhost:5000"

# 测试 1：生成课程
print("测试 1: 生成课程...")
resp = requests.post(
    f"{API_BASE}/api/generate",
    json={"topic": "Python 基础"}
)
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.json()}")

if resp.status_code == 200:
    task_id = resp.json()["task_id"]
    print(f"\n任务 ID: {task_id}")
    
    # 测试 2：查询进度
    print("\n测试 2: 查询进度...")
    for i in range(10):
        time.sleep(3)
        resp = requests.get(f"{API_BASE}/api/status/{task_id}")
        status = resp.json()
        print(f"进度: {status.get('progress')}% - {status.get('message')}")
        
        if status.get("status") in ["done", "error"]:
            break
    
    # 测试 3：查看课程列表
    print("\n测试 3: 查看课程列表...")
    resp = requests.get(f"{API_BASE}/api/courses")
    courses = resp.json()
    print(f"课程数量: {len(courses.get('courses', []))}")

print("\n测试完成！")
