"""
sources/youtube.py — YouTube 视频搜索

使用 YouTube Data API v3（需要 API Key）。
免费配额: 10,000 单位/天（一次搜索约消耗 100 单位）。

获取 API Key:
  https://console.cloud.google.com/apis/credentials
"""

from __future__ import annotations

import json
import urllib.request
import urllib.parse
from typing import Any


class Source:
    """YouTube 数据源"""

    API_BASE = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        """
        搜索 YouTube 视频。
        需要 self.api_key 已设置。
        """
        if not self.api_key:
            print("[youtube] 未配置 API Key，返回模拟数据")
            print("[youtube] 请在 https://console.cloud.google.com/apis/credentials 获取 Key")
            return self._mock_results(query, max_results)

        # 第一步：搜索视频
        params = urllib.parse.urlencode({
            "part":       "snippet",
            "q":          query,
            "type":       "video",
            "maxResults": min(max_results, 50),
            "key":        self.api_key,
            "relevanceLanguage": "zh",   # 优先中文
            "safeSearch": "none",
        })
        search_url = f"{self.API_BASE}/search?{params}"

        try:
            req = urllib.request.Request(search_url)
            with urllib.request.urlopen(req, timeout=15) as resp:
                search_data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[youtube] 搜索请求失败: {e}")
            return self._mock_results(query, max_results)

        # 第二步：获取视频详情（时长等）
        video_ids = [
            item["id"]["videoId"]
            for item in search_data.get("items", [])
            if item.get("id", {}).get("videoId")
        ]

        if not video_ids:
            return []

        details = self._fetch_video_details(video_ids)

        # 合并结果
        results = []
        for item in search_data.get("items", []):
            vid = item.get("id", {}).get("videoId")
            if not vid:
                continue

            snippet = item.get("snippet", {})
            detail = details.get(vid, {})

            results.append({
                "url":          f"https://www.youtube.com/watch?v={vid}",
                "title":        snippet.get("title", ""),
                "title_zh":     None,
                "description":  snippet.get("description", "")[:300],
                "pub_date":     snippet.get("publishedAt", "")[:10],
                "content_type": "video",
                "source":       "youtube",
                "source_type":  "youtube",
                "tags":         snippet.get("tags", []) or [],
                "duration":     detail.get("duration_seconds"),
                "view_count":   detail.get("view_count"),
                "channel":      snippet.get("channelTitle", ""),
                "language":     "zh" if snippet.get("relevanceLanguage") == "zh" else "en",
            })

        return results

    def _fetch_video_details(self, video_ids: list[str]) -> dict:
        """批量获取视频详情（时长、播放量等）"""
        if not self.api_key or not video_ids:
            return {}

        ids_str = ",".join(video_ids[:50])  # API 限制最多 50 个
        params = urllib.parse.urlencode({
            "part":    "contentDetails,statistics",
            "id":      ids_str,
            "key":     self.api_key,
        })
        url = f"{self.API_BASE}/videos?{params}"

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[youtube] 详情请求失败: {e}")
            return {}

        results = {}
        for item in data.get("items", []):
            vid = item.get("id")
            if not vid:
                continue

            # 解析 ISO 8601 时长 (PT1H30M15S)
            duration_str = item.get("contentDetails", {}).get("duration", "")
            duration_sec = self._parse_iso_duration(duration_str)

            view_count = int(item.get("statistics", {}).get("viewCount", 0))

            results[vid] = {
                "duration_seconds": duration_sec,
                "view_count":       view_count,
            }

        return results

    def _parse_iso_duration(self, duration_str: str) -> int | None:
        """解析 ISO 8601 时长字符串为秒数"""
        import re
        if not duration_str:
            return None
        pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
        m = re.match(pattern, duration_str)
        if not m:
            return None
        h = int(m.group(1) or 0)
        m_val = int(m.group(2) or 0)
        s = int(m.group(3) or 0)
        return h * 3600 + m_val * 60 + s

    def _mock_results(self, query: str, max_results: int) -> list[dict]:
        """模拟数据（开发/测试用）"""
        print(f"[youtube] 使用模拟数据，请配置 YOUTUBE_API_KEY 环境变量")
        mock_videos = [
            {
                "url":          f"https://www.youtube.com/watch?v=mock1&q={query}",
                "title":        f"[模拟] {query} 完整教程",
                "title_zh":     f"[模拟] {query} 完整教程",
                "description":  f"这是一个关于 {query} 的详细视频教程...",
                "pub_date":     "2025-06-01",
                "content_type": "video",
                "source":       "youtube",
                "source_type":  "youtube",
                "tags":         [query, "tutorial", "course"],
                "duration":     3600,  # 1 小时
                "view_count":   50000,
                "channel":      "Mock Channel",
                "language":     "zh",
                "_mock":        True,
            }
        ]
        return mock_videos * min(max_results, 1)


# ── CLI 测试 ────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    api_key = os.environ.get("YOUTUBE_API_KEY")
    src = Source(api_key=api_key)
    print("🔍 搜索 YouTube: Python tutorial")
    results = src.search("Python tutorial", max_results=3)
    for r in results:
        mock_flag = " [模拟]" if r.get("_mock") else ""
        mins = (r.get("duration") or 0) // 60
        print(f"\n📺 {r['title']}{mock_flag}")
        print(f"   频道: {r.get('channel', '?')}")
        print(f"   时长: {mins} 分钟")
