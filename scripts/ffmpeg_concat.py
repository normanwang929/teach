#!/usr/bin/env python3
"""
ffmpeg_concat.py — FFmpeg 音视频拼接工具

提供常用的 FFmpeg 拼接操作封装：
  - 音频文件拼接
  - 视频片段拼接
  - 图片序列 → 视频
  - 添加背景音乐
  - 添加字幕
  - 视频尺寸调整

用法（作为模块）:
    from ffmpeg_concat import concat_audio, concat_videos, images_to_video

用法（CLI）:
    python ffmpeg_concat.py concat-audio *.mp3 -o output.mp3
    python ffmpeg_concat.py images-to-video slides/ output.mp4 --fps 1
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from typing import Optional


def check_ffmpeg() -> bool:
    """检查 FFmpeg 是否可用"""
    try:
        r = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True, text=True, timeout=10,
        )
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def concat_audio(
    audio_files: list[str],
    output_path: str,
    fade_ms: int = 200,
) -> bool:
    """
    拼接多个音频文件为一个。
    fade_ms: 交叉淡入淡出时长（毫秒），0 表示直接拼接。

    返回 True 表示成功。
    """
    if not audio_files:
        return False
    if not check_ffmpeg():
        print("❌ 未找到 FFmpeg")
        return False

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        list_file = f.name
        for af in audio_files:
            f.write(f"file '{os.path.abspath(af)}'\n")

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-c:a", "libmp3lame", "-b:a", "128k",
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            print(f"❌ 拼接失败: {r.stderr[-300:]}")
            return False
        print(f"✅ 音频已拼接: {output_path}")
        return True
    finally:
        if os.path.exists(list_file):
            os.unlink(list_file)


def concat_videos(
    video_files: list[str],
    output_path: str,
) -> bool:
    """
    拼接多个视频文件（要求编码参数一致）。
    """
    if not video_files:
        return False
    if not check_ffmpeg():
        return False

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        list_file = f.name
        for vf in video_files:
            f.write(f"file '{os.path.abspath(vf)}'\n")

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            # 编码不一致，重新编码
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", list_file,
                "-c:v", "libx264", "-c:a", "aac",
                output_path,
            ]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            print(f"❌ 视频拼接失败: {r.stderr[-300:]}")
            return False
        print(f"✅ 视频已拼接: {output_path}")
        return True
    finally:
        if os.path.exists(list_file):
            os.unlink(list_file)


def images_to_video(
    image_files: list[str],
    output_path: str,
    durations: list[float] | None = None,
    fps: float = 1.0,
    resolution: tuple = (1280, 720),
    audio_file: str | None = None,
) -> bool:
    """
    将图片序列转为视频。
      - image_files: 图片路径列表
      - durations:   每张图片显示时长（秒），None 表示统一用 fps
      - fps:         帧率（当 durations=None 时使用）
      - audio_file:  可选配音音频
    """
    if not image_files:
        return False
    if not check_ffmpeg():
        return False

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        concat_file = f.name
        for img, dur in zip(image_files, durations or [1.0 / fps] * len(image_files)):
            f.write(f"file '{os.path.abspath(img)}'\nduration {dur}\n")
        f.write(f"file '{os.path.abspath(image_files[-1])}'\n")

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_file,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-vf", f"scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease,pad={resolution[0]}:{resolution[1]}:(ow-iw)/2:(oh-ih)/2",
            "-pix_fmt", "yuv420p",
        ]
        if audio_file and os.path.exists(audio_file):
            cmd += ["-i", audio_file, "-c:a", "aac", "-b:a", "128k", "-shortest"]
        else:
            cmd += ["-an"]

        cmd.append(output_path)

        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            print(f"❌ 视频生成失败: {r.stderr[-500:]}")
            return False
        print(f"✅ 视频已生成: {output_path}")
        return True
    finally:
        if os.path.exists(concat_file):
            os.unlink(concat_file)


def add_subtitles(
    video_path: str,
    srt_path: str,
    output_path: str,
    font_name: str = "Microsoft YaHei",
    font_size: int = 18,
) -> bool:
    """给视频添加字幕"""
    if not check_ffmpeg():
        return False

    filter_str = (
        f"subtitles={srt_path}:"
        f"force_style='FontName={font_name},FontSize={font_size}'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", filter_str,
        "-c:a", "copy",
        output_path,
    ]

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(f"❌ 添加字幕失败: {r.stderr[-300:]}")
        return False
    print(f"✅ 字幕已添加: {output_path}")
    return True


def add_background_music(
    voice_path: str,
    bg_music_path: str,
    output_path: str,
    bg_volume: float = 0.15,
) -> bool:
    """
    给人声添加背景音乐。
    bg_volume: 背景音乐音量（0-1）
    """
    if not check_ffmpeg():
        return False

    cmd = [
        "ffmpeg", "-y",
        "-i", voice_path,
        "-i", bg_music_path,
        "-filter_complex",
        f"[1:a]volume={bg_volume}[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=0",
        "-c:a", "libmp3lame", "-b:a", "128k",
        output_path,
    ]

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"❌ 混音失败: {r.stderr[-300:]}")
        return False
    print(f"✅ 背景音乐已添加: {output_path}")
    return True


def resize_video(
    input_path: str,
    output_path: str,
    width: int,
    height: int,
) -> bool:
    """调整视频尺寸"""
    if not check_ffmpeg():
        return False

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"scale={width}:{height}",
        "-c:a", "copy",
        output_path,
    ]

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"❌ 调整尺寸失败: {r.stderr[-300:]}")
        return False
    print(f"✅ 视频已调整: {output_path}")
    return True


# ── CLI ─────────────────────────────────────────────────────────
def main():
    import argparse

    parser = argparse.ArgumentParser(description="FFmpeg 音视频拼接工具")
    sub = parser.add_subparsers(dest="command")

    # concat-audio
    p_audio = sub.add_parser("concat-audio", help="拼接音频文件")
    p_audio.add_argument("files", nargs="+", help="音频文件列表")
    p_audio.add_argument("--output", "-o", required=True)

    # images-to-video
    p_img = sub.add_parser("images-to-video", help="图片序列转视频")
    p_img.add_argument("images", nargs="+", help="图片文件列表")
    p_img.add_argument("--output", "-o", required=True)
    p_img.add_argument("--fps", type=float, default=1.0)
    p_img.add_argument("--resolution", default="1280x720")
    p_img.add_argument("--audio", help="配音音频文件")

    # add-subtitles
    p_sub = sub.add_parser("add-subtitles", help="添加字幕")
    p_sub.add_argument("video", help="视频文件")
    p_sub.add_argument("srt", help="SRT 字幕文件")
    p_sub.add_argument("--output", "-o", required=True)

    args = parser.parse_args()

    if args.command == "concat-audio":
        concat_audio(args.files, args.output)
    elif args.command == "images-to-video":
        w, h = map(int, args.resolution.split("x"))
        images_to_video(args.images, args.output, fps=args.fps, resolution=(w, h), audio_file=args.audio)
    elif args.command == "add-subtitles":
        add_subtitles(args.video, args.srt, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
