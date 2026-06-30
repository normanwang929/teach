"""
sources/podcasts.py — 教育类播客搜索

通过播客 RSS Feed 搜索教育类播客。
使用 iTunes/Apple Podcasts Search API（免费，无需 Key）发现播客，
然后直接解析 RSS Feed 获取剧集列表。
"""

from __future__ import annotations

import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any


class Source:
    """教育播客数据源"""

    ITUNES_SEARCH_API = "https://itunes.apple.com/search"

    # 知名教育播客 RSS Feed（直接可用，无需搜索）
    KNOWN_EDU_FEEDS: list[dict] = [
        {
            "name":    "Programming Throwdown",
            "rss":     "https://feeds.feedburner.com/programmingthrowdown",
            "topics":  ["programming", "cs"],
        },
        {
            "name":    "Talk Python To Me",
            "rss":     "https://talkpython.fm/episodes/rss",
            "topics":  ["python", "programming"],
        },
        {
            "name":    "Data Skeptic",
            "rss":     "https://dataskeptic.com/feed",
            "topics":  ["data science", "statistics", "ml"],
        },
        {
            "name":    "Linear Digressions",
            "rss":     "http://lineardigressions.com/rss.xml",
            "topics":  ["data science", "ml", "ai"],
        },
        {
            "name":    "The Changelog",
            "rss":     "https://changelog.com/podcast/feed",
            "topics":  ["programming", "open source", "tech"],
        },
        {
            "name":    "CodeNewbie",
            "rss":     "https://www.codenewbie.org/podcast?format=rss",
            "topics":  ["programming", "beginner", "coding"],
        },
    ]

    def __init__(self, api_key: str | None = None):
        pass

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        """
        搜索教育播客剧集。
        策略:
          1. 用 iTunes API 搜索相关播客
          2. 解析播客 RSS 获取最新剧集
          3. 按关键词过滤剧集标题
        """
        results = []

        # 搜索 iTunes Podcasts
        itunes_results = self._search_itunes(query, limit=5)
        for podcast in itunes_results:
            episodes = self._fetch_episodes(podcast["rss"], query, max_episodes=3)
            results.extend(episodes)

        # 从已知教育播客中搜索
        known_results = self._search_known_feeds(query, max_results=5)
        results.extend(known_results)

        return results[:max_results]

    def _search_itunes(self, query: str, limit: int = 5) -> list[dict]:
        """通过 iTunes Search API 搜索播客"""
        params = urllib.parse.urlencode({
            "term":     query,
            "media":    "podcast",
            "limit":    limit,
            "country":  "US",
        })
        url = f"{self.ITUNES_SEARCH_API}?{params}"

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return [
                {
                    "name": podcast.get("collectionName", ""),
                    "rss":  podcast.get("feedUrl", ""),
                    "author": podcast.get("artistName", ""),
                }
                for podcast in data.get("results", [])
                if podcast.get("feedUrl")
            ]
        except Exception as e:
            print(f"[podcasts] iTunes 搜索失败: {e}")
            return []

    def _fetch_episodes(self, rss_url: str, query: str, max_episodes: int = 3) -> list[dict]:
        """解析播客 RSS，获取匹配关键词的剧集"""
        try:
            req = urllib.request.Request(
                rss_url,
                headers={"User-Agent": "TeachPlatform/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml_data = resp.read()
        except Exception as e:
            return []

        return self._parse_rss_episodes(xml_data, rss_url, query, max_episodes)

    def _parse_rss_episodes(self, xml_data: bytes, rss_url: str, query: str, max_episodes: int) -> list[dict]:
        """解析 RSS XML，提取剧集"""
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError:
            return []

        results = []
        query_l = query.lower()

        # 播客名称
        channel = root.find("channel")
        podcast_name = ""
        if channel is not None:
            title_el = channel.find("title")
            if title_el is not None:
                podcast_name = title_el.text or ""

        for item in root.findall(".//item"):
            try:
                title_el = item.find("title")
                title = title_el.text if title_el is not None else ""

                # 按关键词过滤
                if query_l not in title.lower():
                    continue

                link_el = item.find("link")
                url = link_el.text if link_el is not None else ""

                desc_el = item.find("description")
                description = (desc_el.text or "")[:300]

                date_el = item.find("pubDate")
                pub_date = None
                if date_el is not None and date_el.text:
                    # RFC 822 格式，尝试提取 YYYY-MM-DD
                    import email.utils
                    try:
                        _, date_tuple = email.utils.parsedate_to_datetime(date_el.text)
                        pub_date = f"{date_tuple[0]}-{date_tuple[1]:02d}-{date_tuple[2]:02d}"
                    except Exception:
                        pass

                # 时长
                duration_el = item.find("duration") or item.find("{http://www.itunes.com/dtds/podcast-1.0.dtd}duration")
                duration = None
                if duration_el is not None and duration_el.text:
                    duration = self._parse_duration(duration_el.text)

                # 音频 URL
                enclosure = item.find("enclosure")
                audio_url = ""
                if enclosure is not None:
                    audio_url = enclosure.get("url", "")

                results.append({
                    "url":          url or audio_url,
                    "title":        title,
                    "title_zh":     None,
                    "description":  description,
                    "pub_date":     pub_date,
                    "content_type": "podcast",
                    "source":       "podcast",
                    "source_type":  "podcast",
                    "podcast_name": podcast_name,
                    "audio_url":    audio_url,
                    "duration":     duration,
                    "tags":         [query],
                    "language":     "en",
                })

                if len(results) >= max_episodes:
                    break
            except Exception:
                continue

        return results

    def _search_known_feeds(self, query: str, max_results: int) -> list[dict]:
        """从已知教育播客中搜索"""
        results = []
        query_l = query.lower()

        for feed_info in self.KNOWN_EDU_FEEDS:
            # 检查是否匹配查询
            if not any(t in query_l or query_l in t for t in feed_info["topics"]):
                continue

            episodes = self._fetch_episodes(feed_info["rss"], query, max_episodes=2)
            # 标记播客名称
            for ep in episodes:
                ep["podcast_name"] = feed_info["name"]
            results.extend(episodes)

            if len(results) >= max_results:
                break

        return results[:max_results]

    def _parse_duration(self, duration_str: str) -> int | None:
        """解析播客时长（HH:MM:SS 或 MM:SS 格式）为秒"""
        parts = duration_str.strip().split(":")
        try:
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
        except ValueError:
            pass
        return None


# ── CLI 测试 ────────────────────────────────────────────────────
if __name__ == "__main__":
    src = Source()
    print("🔍 搜索教育播客: Python")
    results = src.search("Python", max_results=5)
    for r in results:
        mins = (r.get("duration") or 0) // 60
        print(f"\n🎙️  {r['title']}")
        print(f"   播客: {r.get('podcast_name', '?')}")
        print(f"   时长: {mins} 分钟" if r.get("duration") else "")
