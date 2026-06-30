"""
sources/__init__.py — 数据源注册表

所有数据源统一实现:
    async def search(query: str, max_results: int = 10) -> list[dict]

返回的资源 dict 格式:
    {
        "url":          str,
        "title":        str,
        "title_zh":     str | None,
        "description":  str,
        "pub_date":     str | None,   # ISO 8601
        "content_type": str,          # video / article / course / podcast / paper
        "source":       str,          # 数据源名称
        "tags":         list[str],
        "duration":     int | None,   # 视频/音频时长（秒）
        "view_count":   int | None,
        "language":     str,          # zh / en
    }
"""

from __future__ import annotations

from typing import Any

# 所有可用数据源
AVAILABLE_SOURCES: dict[str, str] = {
    "arxiv":        "arXiv 学术论文 (免费)",
    "bilibili":     "B站视频教程 (免费)",
    "zhihu":        "知乎深度文章 (免费)",
    "youtube":      "YouTube 视频 (免费, 需 API Key)",
    "open_courses": "公开课程目录 MIT OCW / Coursera (免费)",
    "podcasts":     "教育类播客 RSS (免费)",
    "wikipedia":    "维基百科 (免费)",
    "anysearch":    "AnySearch 通用搜索 (免费)",
}

# 需要 API Key 的数据源
REQUIRES_API_KEY = {"youtube"}


def get_source(name: str, api_key: str | None = None) -> Any:
    """延迟加载数据源模块"""
    import importlib
    module = importlib.import_module(f".{name}", __package__)
    if hasattr(module, "Source"):
        return module.Source(api_key=api_key)
    return module


__all__ = ["AVAILABLE_SOURCES", "REQUIRES_API_KEY", "get_source"]
