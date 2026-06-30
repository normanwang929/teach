#!/usr/bin/env python3
"""
search_course_materials.py — 课程资料搜索引擎 主入口

输入主题 → 并发搜索所有数据源 → 质量评分 → 去重 → 输出 JSON

用法:
    python search_course_materials.py "Python 编程"
    python search_course_materials.py "Transformer 模型" --max-results 20
    python search_course_materials.py "机器学习" --sources arxiv,bilibili,wikipedia
    python search_course_materials.py "Python" --output resources.json
"""

from __future__ import annotations

import argparse
import json
import sys
import os
import time
from typing import Any

# ── 导入各模块 ──────────────────────────────────────────────────
from quality_scorer import score_resources
from dedup import dedup_resources

# 动态导入 sources（延迟加载，避免启动慢）
def _import_source(name: str, api_key: str | None = None):
    import importlib
    mod = importlib.import_module(f"sources.{name}")
    if hasattr(mod, "Source"):
        return mod.Source(api_key=api_key)
    return mod


# ── 数据源配置 ──────────────────────────────────────────────────
DEFAULT_SOURCES: list[str] = [
    "arxiv",
    "bilibili",
    "wikipedia",
    # 以下需要 API Key 或特殊配置，默认关闭
    # "youtube",      # 需要 YOUTUBE_API_KEY
    # "zhihu",        # 需要 Cookie
    # "open_courses",
    # "podcasts",
    # "anysearch",
]

# 数据源 → 所需 API Key 环境变量
SOURCE_API_KEY_ENV: dict[str, str] = {
    "youtube": "YOUTUBE_API_KEY",
    "zhihu":   "ZHIHU_COOKIE",
    "anysearch": "ANYSEARCH_API_KEY",
}


def search_all(
    query: str,
    sources: list[str] | None = None,
    max_per_source: int = 10,
    max_total: int = 50,
    api_keys: dict[str, str] | None = None,
) -> list[dict]:
    """
    并发搜索所有数据源，汇总结果。

    Args:
        query:          搜索主题
        sources:       要使用的源列表（None=全部默认）
        max_per_source: 每个源最多返回条数
        max_total:      总结果数上限
        api_keys:       {source_name: api_key} 映射

    Returns:
        评分 + 去重后的资源列表
    """
    if sources is None:
        sources = DEFAULT_SOURCES

    api_keys = api_keys or {}
    all_results: list[dict] = []
    errors: list[str] = []

    print(f"\n🔍 搜索主题: \"{query}\"")
    print(f"📡 数据源: {', '.join(sources)}")
    print(f"📊 每源上限: {max_per_source}, 总计上限: {max_total}\n")

    for src_name in sources:
        api_key = api_keys.get(src_name) or os.environ.get(
            SOURCE_API_KEY_ENV.get(src_name, ""), None
        )

        try:
            src = _import_source(src_name, api_key=api_key)
            print(f"  ⏳ [{src_name}] 搜索中...", end=" ", flush=True)

            start = time.time()
            results = src.search(query, max_results=max_per_source)
            elapsed = time.time() - start

            print(f"✅ {len(results)} 条 ({elapsed:.1f}s)")
            all_results.extend(results)

        except Exception as e:
            err_msg = f"[{src_name}] 搜索失败: {e}"
            print(f"❌ {err_msg}")
            errors.append(err_msg)
            continue

    if not all_results:
        print("\n⚠️  所有数据源均未返回结果")
        if errors:
            print("错误汇总:")
            for e in errors:
                print(f"  - {e}")
        return []

    # ── 去重 ────────────────────────────────────────────────────
    print(f"\n🔄 去重前: {len(all_results)} 条")
    unique = dedup_resources(all_results)
    print(f"🔄 去重后: {len(unique)} 条")

    # ── 质量评分 + 排序 ─────────────────────────────────────────
    print(f"📊 质量评分中...")
    scored = score_resources(unique)
    scored = scored[:max_total]

    print(f"✅ 最终结果: {len(scored)} 条\n")

    return scored


def format_output(results: list[dict], fmt: str = "json") -> str:
    """格式化输出"""
    if fmt == "json":
        # 去掉内部字段（如 _mock）
        clean = []
        for r in results:
            item = {k: v for k, v in r.items() if not k.startswith("_")}
            clean.append(item)
        return json.dumps(clean, ensure_ascii=False, indent=2)

    if fmt == "markdown":
        lines = ["# 课程资料搜索结果\n"]
        for i, r in enumerate(results, 1):
            score = r.get("quality_score", {}).get("total", 0)
            lines.append(f"\n## {i}. {r['title']} (评分: {score}/100)\n")
            lines.append(f"- **来源**: {r.get('source', '?')}")
            lines.append(f"- **链接**: {r['url']}")
            lines.append(f"- **类型**: {r.get('content_type', '?')}")
            if r.get("description"):
                lines.append(f"- **简介**: {r['description'][:200]}")
            if r.get("pub_date"):
                lines.append(f"- **发布**: {r['pub_date']}")
            if r.get("duration"):
                mins = r["duration"] // 60
                lines.append(f"- **时长**: {mins} 分钟")
            if r.get("tags"):
                lines.append(f"- **标签**: {', '.join(r['tags'])}")
            lines.append("")

        return "\n".join(lines)

    if fmt == "csv":
        import csv
        import io
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=[
            "title", "url", "source", "content_type", "pub_date", "score"
        ])
        writer.writeheader()
        for r in results:
            score = r.get("quality_score", {}).get("total", 0)
            writer.writerow({
                "title":        r.get("title", ""),
                "url":          r.get("url", ""),
                "source":       r.get("source", ""),
                "content_type": r.get("content_type", ""),
                "pub_date":     r.get("pub_date", ""),
                "score":        score,
            })
        return buf.getvalue()

    return json.dumps(results, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="课程资料搜索引擎 — 输入主题，自动搜索全网免费优质资源"
    )
    parser.add_argument("query",               help="搜索主题，如 'Python 编程'")
    parser.add_argument("--sources",           help="使用的数据源（逗号分隔），默认: arxiv,bilibili,wikipedia")
    parser.add_argument("--max-per-source",    type=int, default=10,  help="每源最多返回条数 (默认 10)")
    parser.add_argument("--max-total",          type=int, default=50,  help="总结果数上限 (默认 50)")
    parser.add_argument("--output", "-o",                               help="输出文件路径（默认 stdout）")
    parser.add_argument("--format", "-f",      choices=["json", "markdown", "csv"],
                                            default="json",          help="输出格式 (默认 json)")
    parser.add_argument("--youtube-key",                                  help="YouTube API Key（或设 YOUTUBE_API_KEY 环境变量）")
    parser.add_argument("--list-sources",     action="store_true",     help="列出所有可用数据源")

    args = parser.parse_args()

    # 列出所有数据源
    if args.list_sources:
        from sources import AVAILABLE_SOURCES, REQUIRES_API_KEY
        print("可用数据源:\n")
        for name, desc in AVAILABLE_SOURCES.items():
            key_info = " (需要 API Key)" if name in REQUIRES_API_KEY else " (免费)"
            print(f"  {name:15s} {desc}{key_info}")
        return

    # 解析数据源
    sources = args.sources.split(",") if args.sources else None

    # 构建 API keys
    api_keys = {}
    if args.youtube_key:
        api_keys["youtube"] = args.youtube_key

    # 执行搜索
    results = search_all(
        query           = args.query,
        sources         = sources,
        max_per_source  = args.max_per_source,
        max_total       = args.max_total,
        api_keys        = api_keys or None,
    )

    # 输出
    output = format_output(results, fmt=args.format)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"💾 结果已保存到: {args.output}")
        print(f"   共 {len(results)} 条，格式: {args.format}")
    else:
        print("\n" + "=" * 60)
        print("📋 搜索结果")
        print("=" * 60)
        print(output)


if __name__ == "__main__":
    main()
