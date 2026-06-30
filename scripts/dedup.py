"""
dedup.py — 课程资料去重与合并

策略：
1. URL 归一化去重（去掉 utm_*, fbclid 等参数）
2. 标题相似度去重（基于词集合 Jaccard 相似度）
3. 同一资源多来源合并（保留最高分来源）

用法:
    from dedup import dedup_resources
    unique = dedup_resources(resources_list)
"""

from __future__ import annotations

import hashlib
import re
from typing import Any
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


# ── URL 归一化 ──────────────────────────────────────────────────
# 需要去掉的跟踪参数
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "msclkid", "twclid",
    "ref", "referrer", "source", "_ga",
    "share", "sharing", "from", "timestamp",
}

# 视频平台 ID 参数（保留，用于去重）
VIDEO_ID_PARAMS = {"v", "bvid", "av"}


def normalize_url(url: str) -> str:
    """
    归一化 URL：
    - 去掉协议头（http/https 统一）
    - 去掉跟踪参数
    - 去掉尾部斜杠
    - 去掉 #fragment
    - 对视频平台，提取核心 ID 作为 key
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return url.strip().lower()

    # 统一协议
    scheme = "https"

    # 视频平台特殊处理
    netloc = parsed.netloc.lower().replace("www.", "")

    if "youtube.com" in netloc or "youtu.be" in netloc:
        return _normalize_youtube(url, parsed)
    if "bilibili.com" in netloc:
        return _normalize_bilibili(url, parsed)

    # 去掉跟踪参数
    query = parse_qs(parsed.query)
    filtered = {k: v for k, v in query.items()
                if k not in TRACKING_PARAMS and k not in VIDEO_ID_PARAMS}
    # 参数排序，保证一致性
    sorted_query = sorted(filtered.items(), key=lambda x: x[0])
    new_query = urlencode(sorted_query, doseq=True) if sorted_query else ""

    # 去掉 fragment
    path = parsed.path.rstrip("/")
    if not path:
        path = ""

    normalized = urlunparse((scheme, netloc, path, "", new_query, ""))
    return normalized


def _normalize_youtube(url: str, parsed: Any) -> str:
    """YouTube URL 归一化：提取 video ID"""
    qs = parse_qs(parsed.query)
    vid = qs.get("v", [""])[0]
    if vid:
        return f"https://youtube.com/watch?v={vid}"
    # youtu.be/VID 格式
    if "youtu.be" in parsed.netloc:
        vid = parsed.path.strip("/")
        return f"https://youtube.com/watch?v={vid}"
    return url


def _normalize_bilibili(url: str, parsed: Any) -> str:
    """B站 URL 归一化：提取 BV 号或 AV 号"""
    qs = parse_qs(parsed.query)
    bvid = qs.get("bvid", [""])[0]
    avid = qs.get("avid", qs.get("av", [""]))[0]
    if bvid:
        return f"https://bilibili.com/video/{bvid}"
    if avid:
        return f"https://bilibili.com/video/av{avid}"
    # 尝试从 path 提取 BV 号
    m = re.search(r"/(BV[a-zA-Z0-9]+)", url)
    if m:
        return f"https://bilibili.com/video/{m.group(1)}"
    return url


# ── 标题相似度 ──────────────────────────────────────────────────
def tokenize_title(title: str) -> set[str]:
    """将标题分词为词集合（小写 + 去标点）"""
    # 中英文分别处理
    # 英文：按空格/标点分词
    text = title.lower()
    text = re.sub(r"[^\w\s\u4e00-\u9fff]", " ", text)
    tokens = set()
    for word in text.split():
        if len(word) >= 2:  # 去掉单字符噪声
            tokens.add(word)
    return tokens


def title_similarity(title_a: str, title_b: str) -> float:
    """Jaccard 相似度 (0-1)"""
    a = tokenize_title(title_a)
    b = tokenize_title(title_b)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def is_same_resource(r1: dict, r2: dict, threshold: float = 0.6) -> bool:
    """判断两个资源是否为同一内容（URL 或标题相似）"""
    # URL 归一化后相同
    if normalize_url(r1.get("url", "")) == normalize_url(r2.get("url", "")):
        return True
    # 标题高度相似
    sim = title_similarity(r1.get("title", ""), r2.get("title", ""))
    return sim >= threshold


# ── 合并逻辑 ────────────────────────────────────────────────────
def merge_resources(duplicates: list[dict]) -> dict:
    """
    合并一组重复资源，保留信息最全的版本。
    优先保留:
      1. 质量分最高的
      2. 有描述的最长的
      3. 来源最权威的
    """
    if len(duplicates) == 1:
        return duplicates[0]

    # 按质量分排序
    scored = sorted(duplicates,
                    key=lambda r: r.get("quality_score", {}).get("total", 0),
                    reverse=True)

    primary = scored[0].copy()

    # 合并所有来源的 URL（保留多平台链接）
    all_urls = [normalize_url(r.get("url", "")) for r in scored]
    all_urls = list(dict.fromkeys(all_urls))  # 去重保序
    primary["alt_urls"] = [u for u in all_urls if u != normalize_url(primary.get("url", ""))]

    # 合并标签
    all_tags = []
    for r in scored:
        all_tags.extend(r.get("tags", []))
    primary["tags"] = list(dict.fromkeys(all_tags))

    # 补全缺失字段（取第一个非空值）
    for r in scored:
        for key in ("description", "pub_date", "duration", "view_count"):
            if not primary.get(key) and r.get(key):
                primary[key] = r[key]

    # 合并来源列表
    sources = list({r.get("source", "unknown") for r in scored})
    primary["sources"] = sources

    return primary


# ── 主去重入口 ──────────────────────────────────────────────────
def dedup_resources(resources: list[dict], sim_threshold: float = 0.6) -> list[dict]:
    """
    对资源列表去重，返回唯一资源列表。

    Args:
        resources: 资源字典列表
        sim_threshold: 标题相似度阈值 (0-1)，默认 0.6

    Returns:
        去重后的资源列表
    """
    if not resources:
        return []

    # 第一遍：URL 精确去重
    url_map: dict[str, list[int]] = {}  # normalized_url -> indices
    for i, r in enumerate(resources):
        nurl = normalize_url(r.get("url", ""))
        url_map.setdefault(nurl, []).append(i)

    # 第二遍：跨 URL 标题相似度去重
    # 构建分组
    groups: list[list[int]] = []
    url_group_map: dict[str, int] = {}  # normalized_url -> group_id

    for nurl, indices in url_map.items():
        if nurl in url_group_map:
            # 已分组的 URL，加入同组
            gid = url_group_map[nurl]
            groups[gid].extend(indices)
        else:
            # 新 URL，检查是否与已有组标题相似
            title = resources[indices[0]].get("title", "")
            matched = False
            for gid, g_indices in enumerate(groups):
                rep_title = resources[g_indices[0]].get("title", "")
                if title_similarity(title, rep_title) >= sim_threshold:
                    groups[gid].extend(indices)
                    url_group_map[nurl] = gid
                    matched = True
                    break
            if not matched:
                gid = len(groups)
                groups.append(indices)
                url_group_map[nurl] = gid

    # 合并每组
    result = []
    for group in groups:
        unique_indices = list(dict.fromkeys(group))  # 去重
        dups = [resources[i] for i in unique_indices]
        merged = merge_resources(dups)
        result.append(merged)

    return result


# ── CLI 测试 ────────────────────────────────────────────────────
if __name__ == "__main__":
    test_resources = [
        {
            "url":         "https://www.youtube.com/watch?v=abc123&utm_source=share",
            "title":       "Python Tutorial for Beginners - Full Course",
            "description": "Learn Python from scratch",
            "source":      "youtube",
            "content_type":"video",
        },
        {
            "url":         "https://youtu.be/abc123",
            "title":       "Python Tutorial for Beginners - Full Course",
            "description": "Same course, different URL",
            "source":      "youtube_short",
            "content_type":"video",
        },
        {
            "url":         "https://www.bilibili.com/video/BV1xx411c7mD?from=share",
            "title":       "Python 入门教程【全12集】",
            "description": "B站Python教程",
            "source":      "bilibili",
            "content_type":"video",
        },
        {
            "url":         "https://www.youtube.com/watch?v=def456",
            "title":       "Advanced Python - Decorators and Generators",
            "description": "Deep dive into Python advanced topics",
            "source":      "youtube",
            "content_type":"video",
        },
    ]

    print(f"去重前: {len(test_resources)} 条")
    unique = dedup_resources(test_resources)
    print(f"去重后: {len(unique)} 条")
    for r in unique:
        print(f"  - {r['title']} [{r.get('source','?')}]")
        if r.get("alt_urls"):
            print(f"    备选URL: {r['alt_urls']}")
