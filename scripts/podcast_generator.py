#!/usr/bin/env python3
"""
podcast_generator.py — 课程 → 播客音频 生成管线

管线:
  课程 Markdown/HTML
      → LLM 重写为播客脚本（对话式/讲解式）
      → TTS 分段生成音频
      → FFmpeg 拼接 + 可选背景音乐
      → 输出 MP3

依赖:
  pip install edge-tts  # 免费 TTS，无需 Key
  pip install pydub      # 音频处理
  # FFmpeg 需系统安装: https://ffmpeg.org/download.html

用法:
  python podcast_generator.py lesson.md --output podcast.mp3
  python podcast_generator.py lesson.md --voice zh-CN-XiaoxiaoNeural  # 中文女声
  python podcast_generator.py lesson.md --voice en-US-JennyNeural    # 英文女声
  python podcast_generator.py lesson.md --bg-music bg.mp3            # 加背景音乐
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Any


# ── TTS 引擎 ────────────────────────────────────────────────────
def tts_edge(text: str, output_path: str, voice: str = "zh-CN-XiaoxiaoNeural") -> bool:
    """
    使用 edge-tts（免费，无需 Key）生成音频。
    返回 True 表示成功。
    """
    try:
        import edge_tts
    except ImportError:
        print("❌ 未安装 edge-tts，请运行: pip install edge-tts")
        return False

    async def _speak():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    asyncio.run(_speak())
    return os.path.exists(output_path)


def tts_gtts(text: str, output_path: str) -> bool:
    """
    备用 TTS: gTTS（Google TTS，免费但有频率限制）。
    """
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="zh-cn")
        tts.save(output_path)
        return True
    except ImportError:
        print("❌ 未安装 gtts，请运行: pip install gtts")
        return False
    except Exception as e:
        print(f"❌ gTTS 失败: {e}")
        return False


# ── 脚本生成 ────────────────────────────────────────────────────
def rewrite_to_podcast_script(
    course_text: str,
    style: str = "monologue",
    llm_call: callable | None = None,
) -> str:
    """
    将课程文本重写为播客脚本。

    style:
      - "monologue": 单人讲解式
      - "dialogue":   双人对话式（主持人 + 嘉宾）
      - "story":      故事叙述式

    如果没有提供 llm_call，使用内置规则重写（基于文本分段）。
    """
    if llm_call:
        prompt = _build_script_prompt(course_text, style)
        return llm_call(prompt)

    # 无 LLM 时：基于规则重写
    return _rule_based_script(course_text, style)


def _build_script_prompt(course_text: str, style: str) -> str:
    """构建 LLM Prompt，用于将课程重写为播客脚本"""
    style_desc = {
        "monologue": "单人讲解式，像是在和朋友分享知识，口语化，有例子，有互动感（对听众说话）",
        "dialogue":   "双人对话式，主持人和嘉宾讨论，有来有回，自然流畅",
        "story":      "故事叙述式，用故事和场景引入概念，引人入胜",
    }

    return f"""你是一个专业的教育播客脚本撰写者。请将以下课程内容包括播客脚本。

要求:
- 风格: {style_desc.get(style, style_desc['monologue'])}
- 口语化，避免书面语
- 每段不超过 200 字（方便 TTS 分段）
- 加入过渡句（"接下来我们聊聊..."、"有意思的是..."）
- 用[停顿]标记需要停顿的地方
- 用[强调]标记需要强调的词

输出格式: 纯文本，每段用空行分隔。

---
课程内容:
{course_text[:4000]}
"""


def _rule_based_script(course_text: str, style: str) -> str:
    """
    基于规则重写（无 LLM 时的降级方案）。
    将 Markdown 标题转为口语化表达，分段输出。
    """
    lines = course_text.split("\n")
    script_parts = []

    # 开场白
    if style == "monologue":
        script_parts.append("大家好，欢迎收听本期播客。今天我们来聊聊一个很有意思的话题。")
    elif style == "dialogue":
        script_parts.append("主持人: 大家好，欢迎收听本期节目。\n嘉宾: 很高兴来到这里。")

    current_section = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 标题行 → 过渡语
        if re.match(r"^#{1,3}\s+", line):
            title = re.sub(r"^#{1,3}\s+", "", line)
            if style == "monologue":
                transition = f"\n接下来我们聊聊「{title}」。[停顿]\n"
            else:
                transition = f"\n主持人: 我们接下来聊「{title}」吧。\n嘉宾: 好的，这个话题很有意思。[停顿]\n"
            script_parts.append(transition)
            continue

        # 普通段落 → 直接加入（限制长度）
        if len(line) > 20 and not line.startswith("```"):
            cleaned = re.sub(r"[#*`_\[\]]", "", line)  # 去掉 Markdown 标记
            if style == "dialogue" and not current_section:
                cleaned = f"嘉宾: {cleaned}"
                current_section = "guest"
            elif style == "dialogue" and current_section == "guest":
                cleaned = f"主持人: {cleaned}"
                current_section = "host"
            script_parts.append(cleaned)

    # 结束语
    script_parts.append("\n好了，今天的分享就到这里。希望对你有帮助，我们下期再见！")

    return "\n".join(script_parts)


def parse_script_segments(script: str) -> list[dict]:
    """
    将播客脚本解析为分段列表。
    每段是一个字典: {"speaker": "host"|"guest"|"narration", "text": "..."}
    """
    segments = []
    current_speaker = "narration"

    for para in script.split("\n\n"):
        para = para.strip()
        if not para:
            continue

        # 检测说话人
        if para.startswith("主持人:"):
            current_speaker = "host"
            text = para.replace("主持人:", "").strip()
        elif para.startswith("嘉宾:"):
            current_speaker = "guest"
            text = para.replace("嘉宾:", "").strip()
        else:
            text = para

        # 去掉 [停顿] [强调] 标记（TTS 不处理）
        text = re.sub(r"\[停顿\]", "，", text)
        text = re.sub(r"\[强调\]", "", text)

        if text:
            segments.append({
                "speaker": current_speaker,
                "text":    text,
            })

    return segments


# ── 音频生成 ────────────────────────────────────────────────────
VOICE_MAP = {
    "zh-CN-male":   "zh-CN-YunxiNeural",       # 中文男声
    "zh-CN-female": "zh-CN-XiaoxiaoNeural",    # 中文女声（默认）
    "en-US-male":   "en-US-GuyNeural",         # 英文男声
    "en-US-female": "en-US-JennyNeural",       # 英文女声
}

# 说话人 → 语音（对话式播客）
DIALOGUE_VOICES = {
    "host": "zh-CN-YunxiNeural",    # 主持人用男声
    "guest": "zh-CN-XiaoxiaoNeural", # 嘉宾用女声
    "narration": "zh-CN-XiaoxiaoNeural",
}


def generate_audio_segments(
    segments: list[dict],
    output_dir: str,
    voice: str = "zh-CN-XiaoxiaoNeural",
    dialogue_mode: bool = False,
) -> list[str]:
    """
    为每个分段生成音频文件。
    返回音频文件路径列表。
    """
    os.makedirs(output_dir, exist_ok=True)
    audio_files = []

    for i, seg in enumerate(segments):
        seg_voice = voice
        if dialogue_mode:
            seg_voice = DIALOGUE_VOICES.get(seg["speaker"], voice)

        out_path = os.path.join(output_dir, f"segment_{i:03d}.mp3")

        # 跳过已存在的文件（增量生成）
        if os.path.exists(out_path):
            audio_files.append(out_path)
            continue

        print(f"  🎙️  生成第 {i+1}/{len(segments)} 段 ({seg['speaker']})...")
        ok = tts_edge(seg["text"], out_path, voice=seg_voice)
        if ok:
            audio_files.append(out_path)
        else:
            print(f"  ⚠️  第 {i+1} 段生成失败，跳过")

    return audio_files


# ── FFmpeg 拼接 ─────────────────────────────────────────────────
def concat_audio_files(audio_files: list[str], output_path: str, bg_music: str | None = None) -> bool:
    """
    用 FFmpeg 拼接多个音频文件。
    可选叠加背景音乐（自动降低音量）。
    """
    if not audio_files:
        print("❌ 没有音频文件可拼接")
        return False

    # 检查 FFmpeg 是否可用
    import subprocess
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 未找到 FFmpeg，请安装: https://ffmpeg.org/download.html")
        print("   或者手动拼接音频文件:")
        for f in audio_files:
            print(f"   - {f}")
        return False

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        list_file = f.name
        for af in audio_files:
            f.write(f"file '{os.path.abspath(af)}'\n")

    try:
        if bg_music:
            # 有背景音乐：先拼接人声，再混音
            voice_only = output_path.replace(".mp3", "_voice_only.mp3")
            cmd1 = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", list_file,
                "-c", "copy",
                voice_only,
            ]
            subprocess.run(cmd1, capture_output=True, check=True)

            # 混音：人声 + 背景音乐（背景音乐音量 0.15）
            cmd2 = [
                "ffmpeg", "-y",
                "-i", voice_only,
                "-i", bg_music,
                "-filter_complex", "[1:a]volume=0.15[bg];[0:a][bg]amix=inputs=2:duration=first",
                "-c:a", "libmp3lame", "-b:a", "128k",
                output_path,
            ]
            subprocess.run(cmd2, capture_output=True, check=True)
            os.unlink(voice_only)
        else:
            # 直接拼接
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", list_file,
                "-c:a", "libmp3lame", "-b:a", "128k",
                output_path,
            ]
            subprocess.run(cmd, capture_output=True, check=True)

        print(f"✅ 播客已生成: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg 拼接失败: {e}")
        return False
    finally:
        os.unlink(list_file)


# ── 课程文件读取 ────────────────────────────────────────────────
def read_course_file(path: str) -> str:
    """读取课程文件（支持 .md / .html / .txt）"""
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if path.endswith(".html"):
        # 简单 HTML → 文本（去掉标签）
        import re
        content = re.sub(r"<[^>]+>", "", content)
        content = re.sub(r"\s+", " ", content).strip()

    return content


# ── 主流程 ─────────────────────────────────────────────────────
def generate_podcast(
    course_path: str,
    output_path: str = "podcast.mp3",
    voice: str = "zh-CN-XiaoxiaoNeural",
    style: str = "monologue",
    bg_music: str | None = None,
    llm_call: callable | None = None,
) -> bool:
    """
    完整播客生成流程。

    Args:
        course_path:  课程文件路径 (.md / .html)
        output_path:  输出 MP3 路径
        voice:        TTS 语音名（edge-tts 语音列表）
        style:        脚本风格 (monologue / dialogue / story)
        bg_music:     背景音乐文件路径（可选）
        llm_call:     LLM 调用函数（可选，用于脚本生成）

    Returns:
        bool: 是否成功
    """
    print(f"\n🎙️  播客生成管线")
    print(f"   输入: {course_path}")
    print(f"   风格: {style}")
    print(f"   语音: {voice}\n")

    # 1. 读取课程
    print("  📖 读取课程内容...")
    course_text = read_course_file(course_path)
    if not course_text.strip():
        print("  ❌ 课程内容为空")
        return False
    print(f"  ✅ 已读取 {len(course_text)} 字符")

    # 2. 生成播客脚本
    print("\n  ✍️  生成播客脚本...")
    script = rewrite_to_podcast_script(course_text, style=style, llm_call=llm_call)
    script_path = output_path.replace(".mp3", "_script.txt")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)
    print(f"  ✅ 脚本已保存: {script_path}")
    print(f"  📄 脚本预览（前 300 字）:\n{script[:300]}\n")

    # 3. 解析分段
    print("  ✂️  解析脚本分段...")
    segments = parse_script_segments(script)
    print(f"  ✅ 共 {len(segments)} 段")

    # 4. 生成音频
    print("\n  🔊 生成音频段落...")
    tmp_dir = tempfile.mkdtemp(prefix="podcast_")
    dialogue_mode = (style == "dialogue")
    audio_files = generate_audio_segments(
        segments, tmp_dir,
        voice=voice,
        dialogue_mode=dialogue_mode,
    )
    print(f"  ✅ 已生成 {len(audio_files)} 个音频文件")

    # 5. 拼接
    print("\n  🔗 拼接音频...")
    ok = concat_audio_files(audio_files, output_path, bg_music=bg_music)

    # 清理临时文件
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return ok


# ── CLI ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="课程 → 播客音频 生成器"
    )
    parser.add_argument("course",               help="课程文件路径 (.md / .html)")
    parser.add_argument("--output", "-o",        default="podcast.mp3", help="输出 MP3 路径")
    parser.add_argument("--voice",               default="zh-CN-XiaoxiaoNeural",
                        help=f"TTS 语音 (默认 zh-CN-XiaoxiaoNeural)。可选: {', '.join(VOICE_MAP.keys())}")
    parser.add_argument("--style",               choices=["monologue", "dialogue", "story"],
                        default="monologue",    help="播客风格")
    parser.add_argument("--bg-music",            help="背景音乐文件路径（可选）")
    parser.add_argument("--list-voices",        action="store_true",    help="列出可用语音")

    args = parser.parse_args()

    if args.list_voices:
        try:
            import edge_tts
            print("可用语音列表:\n")
            async def _list():
                voices = await edge_tts.list_voices()
                for v in voices:
                    if "Chinese" in v["FriendlyName"] or "English" in v["FriendlyName"]:
                        print(f"  {v['ShortName']:30s} {v['FriendlyName']}")
            asyncio.run(_list())
        except ImportError:
            print("请先安装: pip install edge-tts")
        return

    # 处理语音别名
    voice = VOICE_MAP.get(args.voice, args.voice)

    ok = generate_podcast(
        course_path = args.course,
        output_path = args.output,
        voice       = voice,
        style       = args.style,
        bg_music    = args.bg_music,
    )

    if ok:
        print(f"\n🎉 播客生成完成！")
        print(f"   文件: {args.output}")
    else:
        print(f"\n❌ 播客生成失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
