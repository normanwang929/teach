"""
quality_scorer.py — 课程资料质量评分器

对每个资源打分 0-100，维度：
- 来源权重 (0-40): 正经课程 > 学术论文 > 博客 > 视频 > 社交
- 时效性   (0-25): 近1年 > 近3年 > 更早
- 免费性   (0-15): 免费 > 部分免费 > 付费
- 互动性   (0-10): 有练习/测验 > 纯阅读 > 纯视频
- 质量信号 (0-10): 引用数/播放量/评分

用法:
    from quality_scorer import score_resource
    result = score_resource(resource_dict)
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

# ── 来源权重映射 ──────────────────────────────────────────────
# 越高分越权威
SOURCE_TIER: dict[str, int] = {
    # 顶级：正规课程 / 文档
    "mit_ocw":       40,
    "coursera":      38,
    "edx":           38,
    "khan_academy":  36,
    "codecademy":    34,
    "freecodecamp":  34,
    "mdn":           32,
    "official_docs": 30,
    # 学术
    "arxiv":         28,
    "scholar":       26,
    "paper":         24,
    # 优质博客 / 教程
    "blog":          20,
    "tutorial":      20,
    "devto":         18,
    "medium":        14,
    # 视频平台
    "youtube":       16,
    "bilibili":      14,
    # 百科 / 文档
    "wikipedia":    22,
    # 问答 / 社区
    "zhihu":         12,
    "stackoverflow": 12,
    "reddit":        8,
    # 播客
    "podcast":       10,
    # 其他
    "other":          5,
}

# 来源类型关键词 → tier key
SOURCE_HINTS: list[tuple[str, str]] = [
    ("mit.edu/ocw",              "mit_ocw"),
    ("coursera.org",             "coursera"),
    ("edx.org",                  "edx"),
    ("khanacademy.org",          "khan_academy"),
    ("codecademy.com",           "codecademy"),
    ("freecodecamp.org",         "freecodecamp"),
    ("developer.mozilla.org",    "mdn"),
    ("docs.",                    "official_docs"),
    ("arxiv.org",                "arxiv"),
    ("scholar.google",           "scholar"),
    ("wikipedia.org",            "wikipedia"),
    ("youtube.com",              "youtube"),
    ("bilibili.com",             "bilibili"),
    ("zhihu.com",                "zhihu"),
    ("stackoverflow.com",        "stackoverflow"),
    ("medium.com",               "medium"),
    ("dev.to",                   "devto"),
    (".podcast.",                "podcast"),
    ("/feed/",                   "podcast"),
    ("rss",                      "podcast"),
]

# ── 免费性信号 ──────────────────────────────────────────────────
FREE_SIGNALS = ["free", "开源", "免费", "open access", "public", "no registration"]
PAID_SIGNALS = ["paid", "付费", "subscription", "enroll", "购买", "price", "$"]


def detect_source_tier(url: str, source_type: str = "") -> int:
    """根据 URL 和来源类型判断来源权重分 (0-40)"""
    url_l = url.lower()
    for hint, tier_key in SOURCE_HINTS:
        if hint in url_l:
            return SOURCE_TIER.get(tier_key, 5)
    # 根据 source_type 兜底
    return SOURCE_TIER.get(source_type.lower(), 5)


def detect_freshness(pub_date: str | None) -> int:
    """
    时效性评分 (0-25)。
    pub_date: ISO 格式字符串或 None
    """
    if not pub_date:
        return 10  # 未知日期，给中等分

    try:
        # 尝试解析各种日期格式
        dt = _parse_date(pub_date)
        if dt is None:
            return 10
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta_days = (now - dt).days

        if delta_days <= 180:   return 25  # 半年内
        if delta_days <= 365:   return 22  # 1年内
        if delta_days <= 730:   return 18  # 2年内
        if delta_days <= 1095:  return 12  # 3年内
        if delta_days <= 1825:  return 6   # 5年内
        return 2
    except Exception:
        return 10


def detect_free(url: str, title: str = "", description: str = "") -> int:
    """
    免费性评分 (0-15)。
    返回: 15=免费, 8=部分免费, 0=付费
    """
    text = f"{url} {title} {description}".lower()
    has_paid = any(s in text for s in PAID_SIGNALS)
    has_free = any(s in text for s in FREE_SIGNALS)

    if has_paid and not has_free:
        return 0
    if "course" in text and ("paid" in text or "enroll" in text):
        return 8
    # 已知免费平台
    free_hosts = ["youtube.com", "bilibili.com", "arxiv.org", "mit.edu",
                  "freecodecamp.org", "khanacademy.org", "developer.mozilla.org",
                  "zhihu.com", "dev.to", "medium.com"]
    if any(h in url for h in free_hosts):
        return 15
    if has_free:
        return 15
    return 10  # 默认偏免费


def detect_interactivity(resource: dict) -> int:
    """
    互动性评分 (0-10)。
    有练习/测验/项目 > 纯阅读 > 纯视频
    """
    tags = [t.lower() for t in resource.get("tags", [])]
    desc = resource.get("description", "").lower()
    content_type = resource.get("content_type", "")

    interactive_signals = ["exercise", "quiz", "练习", "测验", "project",
                           "作业", "assignment", "interactive", "互动",
                           "hands-on", "动手", "lab", "实验"]
    has_interactive = any(s in desc for s in interactive_signals) or any(s in tags for s in interactive_signals)

    if has_interactive:
        return 10
    if content_type in ("article", "documentation", "tutorial"):
        return 6
    if content_type in ("video", "podcast"):
        return 3
    return 5


def detect_quality_signal(resource: dict) -> int:
    """
    质量信号评分 (0-10)。
    基于播放量、引用数、评分等。
    """
    score = 0
    # 播放量 / 浏览量
    views = resource.get("view_count") or resource.get("views") or 0
    if isinstance(views, (int, float)):
        if views >= 1_000_000:  score += 5
        elif views >= 100_000:  score += 3
        elif views >= 10_000:   score += 2
        elif views >= 1_000:    score += 1

    # 引用数 (学术论文)
    citations = resource.get("citations") or 0
    if isinstance(citations, (int, float)):
        if citations >= 100:  score += 5
        elif citations >= 10: score += 3

    # 评分
    rating = resource.get("rating") or resource.get("score")
    if isinstance(rating, (int, float)):
        if rating >= 4.5:  score += 3
        elif rating >= 4.0: score += 2
        elif rating >= 3.5: score += 1

    return min(score, 10)


def _parse_date(s: str) -> datetime | None:
    """尝试解析常见日期格式"""
    import dateutil.parser as dp
    try:
        return dp.parse(s)
    except Exception:
        return None


def score_resource(resource: dict) -> dict:
    """
    对单个资源打分，返回带各维度分的字典。

    resource 字段要求:
      - url (str)
      - title (str)
      - description (str, 可选)
      - pub_date (str, 可选, ISO 格式)
      - content_type (str, 可选): video / article / podcast / course
      - source_type (str, 可选): 来源类型 key
      - tags (list[str], 可选)
      - view_count / citations / rating (可选)

    返回:
      { "total": int, "breakdown": { "source":..., "freshness":..., ... } }
    """
    url         = resource.get("url", "")
    title       = resource.get("title", "")
    desc        = resource.get("description", "")
    pub_date    = resource.get("pub_date")
    source_type = resource.get("source_type", "")
    content_type = resource.get("content_type", "article")

    # 如果 resource 没有 content_type，根据 URL 推断
    if not content_type or content_type == "article":
        if "youtube.com" in url or "bilibili.com" in url or "/video/" in url:
            content_type = "video"
        elif "podcast" in url or ".mp3" in url or "rss" in url:
            content_type = "podcast"
        elif "course" in url or "learn" in url or "tutorial" in url:
            content_type = "course"
        resource["content_type"] = content_type

    s_source      = detect_source_tier(url, source_type)
    s_freshness   = detect_freshness(pub_date)
    s_free        = detect_free(url, title, desc)
    s_interactive = detect_interactivity(resource)
    s_quality     = detect_quality_signal(resource)

    total = s_source + s_freshness + s_free + s_interactive + s_quality
    # 总分归一化到 0-100
    total = min(total, 100)

    breakdown = {
        "source":      s_source,
        "freshness":   s_freshness,
        "free":        s_free,
        "interactive": s_interactive,
        "quality":     s_quality,
        "total":       total,
    }

    resource["quality_score"] = breakdown
    return breakdown


def score_resources(resources: list[dict]) -> list[dict]:
    """批量打分并排序（高分在前）"""
    for r in resources:
        score_resource(r)
    return sorted(resources, key=lambda r: r["quality_score"]["total"], reverse=True)


# ── CLI 测试 ───────────────────────────────────────────────────
if __name__ == "__main__":
    samples = [
        {
            "url":         "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/",
            "title":       "MIT 6.0001 Introduction to CS and Programming in Python",
            "description": "Free course with exercises, assignments, and video lectures.",
            "pub_date":    "2023-09-01",
            "content_type":"course",
            "tags":        ["python", "cs", "exercise"],
        },
        {
            "url":         "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "title":       "Python Full Course - 12 Hours",
            "description": "Learn Python in 12 hours",
            "pub_date":    "2025-01-15",
            "content_type":"video",
            "view_count":  500000,
        },
        {
            "url":         "https://arxiv.org/abs/2401.12345",
            "title":       "Attention Is All You Need (Transformer)",
            "description": "Classic paper introducing the Transformer architecture.",
            "pub_date":    "2017-06-12",
            "content_type":"paper",
            "citations":   120000,
        },
    ]

    scored = score_resources(samples)
    for r in scored:
        print(f"\n⭐ 总分 {r['quality_score']['total']}/100  {r['title']}")
        for k, v in r["quality_score"].items():
            if k != "total":
                print(f"   {k}: {v}")
