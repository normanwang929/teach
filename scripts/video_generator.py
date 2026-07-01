#!/usr/bin/env python3
"""
video_generator.py — 课程 → 教学视频 生成管线

管线:
  课程 Markdown/HTML
      → 提取关键内容，生成幻灯片列表
      → 渲染幻灯片为图片
      → TTS 生成配音
      → FFmpeg 合成视频（图片序列 + 音频 + 字幕）
      → 输出 MP4

依赖:
  pip install edge-tts pillow  # TTS + 图片生成
  # FFmpeg 需系统安装

用法:
  python video_generator.py lesson.md --output lesson.mp4
  python video_generator.py lesson.md --resolution 1920x1080
  python video_generator.py lesson.md --tts-voice zh-CN-YunxiNeural
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


# ── 幻灯片数据模型 ──────────────────────────────────────────────
def extract_slides_from_course(course_text: str) -> list[dict]:
    """
    从课程内容提取幻灯片列表。

    每张幻灯片:
      {
        "index":    1,
        "title":    "标题",
        "body":     "正文内容（列表或段落）",
        "type":     "title" | "content" | "code" | "summary",
        "duration": 30,   # 秒，根据内容长度自动估算
      }
    """
    slides = []

    # 封面幻灯片
    # 尝试从第一个 H1 提取标题
    h1_match = re.search(r"^#\s+(.+)$", course_text, re.MULTILINE)
    course_title = h1_match.group(1).strip() if h1_match else "课程"

    slides.append({
        "index":    0,
        "title":    course_title,
        "body":     "教学视频",
        "type":     "title",
        "duration": 5,
    })

    # 按 Markdown 标题分段
    current_slide = None
    for line in course_text.split("\n"):
        line = line.rstrip()

        # H1/H2/H3 → 新幻灯片
        h_match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if h_match:
            if current_slide:
                slides.append(current_slide)
            level = len(h_match.group(1))
            title = h_match.group(2).strip()
            current_slide = {
                "index":    len(slides),
                "title":    title,
                "body":     [],
                "type":     "content",
                "duration": 20,  # 默认 20 秒
            }
            continue

        # 代码块
        if line.startswith("```"):
            if current_slide:
                current_slide["type"] = "code"
            continue

        # 列表项 / 普通文本
        if current_slide and line.strip():
            body = current_slide.setdefault("body", [])
            # 估算时长：每 100 字约 30 秒
            if isinstance(body, list):
                body.append(line.strip())
                text_len = sum(len(b) for b in body)
                current_slide["duration"] = max(15, min(60, text_len // 10))

    if current_slide:
        slides.append(current_slide)

    # 结束幻灯片
    slides.append({
        "index":    len(slides),
        "title":    "谢谢观看！",
        "body":     "更多内容请访问课程页面",
        "type":     "summary",
        "duration": 5,
    })

    return slides


# ── 幻灯片渲染 ──────────────────────────────────────────────────
def render_slide_image(slide: dict, output_path: str, resolution: tuple = (1280, 720)) -> bool:
    """
    将幻灯片渲染为图片。
    使用 Pillow 绘制简洁的教学幻灯片风格。
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("❌ 未安装 Pillow，请运行: pip install pillow")
        return False

    W, H = resolution
    BG_COLOR = (15, 15, 30)       # 深蓝黑背景
    ACCENT    = (99, 102, 241)    # 强调色（Indigo）
    TEXT_COLOR = (240, 240, 245)
    SUBTEXT   = (160, 165, 180)

    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 顶部装饰条
    draw.rectangle([0, 0, W, 6], fill=ACCENT)

    # 尝试加载字体（跨平台）
    font_title = None
    font_body = None
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",    # 黑体
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font_title = ImageFont.truetype(fp, size=int(W * 0.045))
                font_body  = ImageFont.truetype(fp, size=int(W * 0.028))
                break
            except Exception:
                continue

    if font_title is None:
        font_title = ImageFont.load_default()
        font_body  = ImageFont.load_default()

    # 绘制标题
    title = slide.get("title", "")
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((W - title_w) // 2, int(H * 0.25)), title, font=font_title, fill=TEXT_COLOR)

    # 绘制正文
    body = slide.get("body", [])
    if isinstance(body, str):
        body = [body]
    if body:
        y = int(H * 0.40)
        line_h = int(W * 0.038)
        for item in body[:8]:  # 最多 8 行
            item = re.sub(r"[#*`_]", "", item)  # 去掉 Markdown
            if item.startswith("- ") or item.startswith("* "):
                item = "• " + item[2:]
            draw.text((int(W * 0.12), y), item, font=font_body, fill=SUBTEXT)
            y += line_h

    # 底部页码
    page_text = f"{slide['index'] + 1}"
    draw.text((W - 80, H - 50), page_text, font=font_body, fill=SUBTEXT)

    img.save(output_path, "PNG")
    return True


def render_all_slides(slides: list[dict], output_dir: str, resolution: tuple = (1280, 720)) -> list[str]:
    """渲染所有幻灯片，返回图片路径列表"""
    os.makedirs(output_dir, exist_ok=True)
    image_files = []

    for slide in slides:
        path = os.path.join(output_dir, f"slide_{slide['index']:03d}.png")
        ok = render_slide_image(slide, path, resolution=resolution)
        if ok:
            image_files.append(path)
        else:
            print(f"  ⚠️  幻灯片 {slide['index']} 渲染失败")

    return image_files


# ── 字幕生成 ────────────────────────────────────────────────────
def generate_srt(segments: list[dict], output_path: str) -> bool:
    """
    生成 SRT 字幕文件。
    segments: [{"text": "...", "start": 0.0, "end": 30.0}, ...]
    """
    def fmt_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{fmt_time(seg['start'])} --> {fmt_time(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")

    return True


# ── 视频合成 ────────────────────────────────────────────────────
def build_ffmpeg_slide_video(
    image_files: list[str],
    audio_file: str | None,
    output_path: str,
    slide_durations: list[float],
    srt_file: str | None = None,
    resolution: tuple = (1280, 720),
) -> bool:
    """
    用 FFmpeg 将图片序列 + 音频合成为视频。
    """
    import subprocess

    # 检查 FFmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 未找到 FFmpeg")
        return False

    # 构建 FFmpeg 命令
    # 方案：用 concat demuxer 控制每张幻灯片时长
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        concat_file = f.name
        for img_path, dur in zip(image_files, slide_durations):
            f.write(f"file '{os.path.abspath(img_path)}'\nduration {dur}\n")
        # 最后一张图片需要重复（FFmpeg concat 要求）
        f.write(f"file '{os.path.abspath(image_files[-1])}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_file,
    ]

    # 有配音才加音频输入
    if audio_file and os.path.exists(audio_file):
        cmd += ["-i", audio_file, "-c:a", "aac", "-b:a", "128k", "-shortest"]
    else:
        cmd += ["-an"]  # 无音频

    cmd += [
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-vf", f"scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease,pad={resolution[0]}:{resolution[1]}:(ow-iw)/2:(oh-ih)/2",
        output_path,
    ]

    # 如果有字幕，加入字幕滤镜
    if srt_file and os.path.exists(srt_file):
        cmd.insert(-1, "-vf")
        cmd.insert(-1, f"subtitles={srt_file}:force_style='FontName=Microsoft YaHei,FontSize=18'")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ 视频已生成: {output_path}")
            return True
        else:
            print(f"❌ FFmpeg 失败:\n{result.stderr[-500:]}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg 超时（视频过长）")
        return False
    finally:
        os.unlink(concat_file)


# ── TTS 配音 ────────────────────────────────────────────────────
def generate_voiceover_script(slides: list[dict]) -> str:
    """
    根据幻灯片内容生成配音脚本（纯文本，用于 TTS）。
    """
    lines = []
    for slide in slides:
        # 标题朗读
        lines.append(slide["title"])
        # 正文朗读（列表项）
        body = slide.get("body", [])
        if isinstance(body, list):
            for item in body:
                cleaned = re.sub(r"^[•\-*]\s*", "", item).strip()
                cleaned = re.sub(r"[#*`_\[\]]", "", cleaned)
                if cleaned:
                    lines.append(cleaned)
        elif isinstance(body, str):
            lines.append(body)
        lines.append("")  # 停顿

    return "\n".join(lines)


def generate_voiceover_audio(
    script: str,
    output_path: str,
    voice: str = "zh-CN-XiaoxiaoNeural",
) -> bool:
    """用 gTTS 生成配音音频"""
    try:
        from gtts import gTTS
        tts = gTTS(text=script, lang='zh-cn', slow=False)
        tts.save(output_path)
        return os.path.exists(output_path)
    except ImportError:
        print("❌ 未安装 gTTS: pip install gtts")
        return False
    except Exception as e:
        print(f"❌ TTS 失败: {e}")
        return False


# ── 主流程 ─────────────────────────────────────────────────────
def generate_video(
    course_path: str,
    output_path: str = "lesson.mp4",
    voice: str = "zh-CN-XiaoxiaoNeural",
    resolution: tuple = (1280, 720),
    add_subtitles: bool = True,
) -> bool:
    """
    完整视频生成流程。
    """
    import asyncio

    print(f"\n🎬 视频生成管线")
    print(f"   输入: {course_path}")
    print(f"   分辨率: {resolution[0]}x{resolution[1]}\n")

    # 1. 读取课程
    print("  📖 读取课程内容...")
    with open(course_path, encoding="utf-8") as f:
        course_text = f.read()
    print(f"  ✅ {len(course_text)} 字符")

    # 2. 提取幻灯片
    print("\n  🎞️  提取幻灯片...")
    slides = extract_slides_from_course(course_text)
    print(f"  ✅ 共 {len(slides)} 张幻灯片")

    # 3. 渲染幻灯片图片
    print("\n  🖼️  渲染幻灯片图片...")
    tmp_dir = tempfile.mkdtemp(prefix="video_slides_")
    image_files = render_all_slides(slides, tmp_dir, resolution=resolution)
    print(f"  ✅ 已渲染 {len(image_files)} 张图片")

    # 4. 生成配音脚本 + 音频
    print("\n  🔊 生成配音...")
    voiceover_script = generate_voiceover_script(slides)
    audio_path = os.path.join(tmp_dir, "voiceover.mp3")
    ok = generate_voiceover_audio(voiceover_script, audio_path, voice=voice)
    if not ok:
        print("  ⚠️  配音生成失败，继续（视频将无声音）")
        audio_path = None

    # 5. 生成字幕（可选）
    srt_path = None
    if add_subtitles and audio_path:
        print("\n  📝 生成字幕...")
        srt_path = os.path.join(tmp_dir, "subtitles.srt")
        # 简单字幕：每段对应一张幻灯片
        segments = []
        t = 0.0
        for slide in slides:
            dur = slide.get("duration", 20)
            text = slide.get("title", "")
            segments.append({"text": text, "start": t, "end": t + dur})
            t += dur
        generate_srt(segments, srt_path)
        print(f"  ✅ 字幕已保存: {srt_path}")

    # 6. 合成视频（先不加字幕，避免 Windows 路径问题）
    print("\n  🎥 合成视频...")
    slide_durations = [s.get("duration", 20) for s in slides]

    actual_audio_path = None
    if audio_path and os.path.exists(audio_path):
        try:
            import mutagen.mp3
            audio_info = mutagen.mp3.MP3(audio_path)
            total_audio = audio_info.info.length
            slide_durations = [total_audio / len(slides)] * len(slides)
            actual_audio_path = audio_path
        except ImportError:
            actual_audio_path = audio_path
        except Exception:
            pass

    # 暂时禁用字幕（Windows 路径问题）
    ok = build_ffmpeg_slide_video(
        image_files, actual_audio_path,
        output_path, slide_durations,
        srt_file=None,  # 先不加字幕
        resolution=resolution,
    )

    # 清理
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return ok


# ── CLI ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="课程 → 教学视频 生成器")
    parser.add_argument("course",                help="课程文件路径 (.md / .html)")
    parser.add_argument("--output", "-o",         default="lesson.mp4",     help="输出 MP4 路径")
    parser.add_argument("--resolution",           default="1280x720",       help="分辨率 (默认 1280x720)")
    parser.add_argument("--voice",                default="zh-CN-XiaoxiaoNeural", help="TTS 语音")
    parser.add_argument("--no-subtitles",        action="store_true",       help="不生成字幕")
    args = parser.parse_args()

    # 解析分辨率
    try:
        w, h = map(int, args.resolution.split("x"))
        resolution = (w, h)
    except ValueError:
        resolution = (1280, 720)

    ok = generate_video(
        course_path     = args.course,
        output_path     = args.output,
        voice           = args.voice,
        resolution      = resolution,
        add_subtitles   = not args.no_subtitles,
    )

    if ok:
        print(f"\n🎉 视频生成完成！")
        print(f"   文件: {args.output}")
    else:
        print(f"\n❌ 视频生成失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
