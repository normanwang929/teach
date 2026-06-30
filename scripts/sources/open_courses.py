"""
sources/open_courses.py — 公开课程搜索

数据源:
  - MIT OpenCourseWare (OCW) — 通过 RSS/API 获取课程列表
  - Coursera — 通过搜索页面抓取（需解析）
  - Khan Academy — 公开 API（部分）
  - freeCodeCamp — 课程目录（静态）

优先使用 RSS/公开 API，避免爬取。
"""

from __future__ import annotations

import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any


class Source:
    """公开课程数据源"""

    def __init__(self, api_key: str | None = None):
        pass

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        """
        跨平台搜索公开课程。
        目前实现: MIT OCW RSS + 课程目录搜索
        """
        results = []

        # MIT OCW
        mit_results = self._search_mit_ocw(query, max_results // 2)
        results.extend(mit_results)

        # 如果有剩余配额，搜索其他平台
        remaining = max_results - len(results)
        if remaining > 0:
            khan_results = self._search_khan(query, remaining)
            results.extend(khan_results)

        return results[:max_results]

    def _search_mit_ocw(self, query: str, max_results: int) -> list[dict]:
        """
        搜索 MIT OpenCourseWare。
        使用 MIT OCW API (https://ocw.mit.edu/api/v0/)。
        """
        # MIT OCW 提供 RSS feed，我们通过 RSS 获取最新课程
        # 同时也支持通过 sitemap 或 API 搜索
        # 这里使用简化方案：通过 MIT OCW 搜索页面 RSS

        # 注意：MIT OCW 没有免费的搜索 API
        # 这里提供一个基于 RSS 的最新课程列表 + 本地过滤方案
        rss_url = "https://ocw.mit.edu/feed/"

        try:
            req = urllib.request.Request(
                rss_url,
                headers={"User-Agent": "TeachPlatform/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml_data = resp.read()
        except Exception as e:
            print(f"[open_courses] MIT OCW RSS 获取失败: {e}")
            return self._mock_mit_results(query, max_results)

        return self._parse_mit_rss(xml_data, query, max_results)

    def _parse_mit_rss(self, xml_data: bytes, query: str, max_results: int) -> list[dict]:
        """解析 MIT OCW RSS feed，按关键词过滤"""
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError:
            return []

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        results = []
        query_l = query.lower()

        for entry in root.findall("atom:entry", ns) or root.findall(".//item"):
            try:
                # 兼容 Atom 和 RSS 格式
                if entry.tag.endswith("entry"):  # Atom
                    title_el = entry.find("atom:title", ns)
                    title = title_el.text if title_el is not None else ""
                    link_el = entry.find("atom:link", ns)
                    url = link_el.get("href", "") if link_el is not None else ""
                    desc_el = entry.find("atom:summary", ns)
                    description = desc_el.text if desc_el is not None else ""
                    date_el = entry.find("atom:updated", ns) or entry.find("atom:published", ns)
                    pub_date = date_el.text[:10] if date_el is not None else None
                else:  # RSS
                    title = entry.findtext("title", "")
                    url = entry.findtext("link", "")
                    description = entry.findtext("description", "")[:300]
                    pub_date = entry.findtext("pubDate", "")[:10] if entry.findtext("pubDate") else None

                # 按关键词过滤
                if query_l not in title.lower() and query_l not in description.lower():
                    continue

                results.append({
                    "url":          url,
                    "title":        title,
                    "title_zh":     None,
                    "description":  description[:300],
                    "pub_date":     pub_date,
                    "content_type": "course",
                    "source":       "mit_ocw",
                    "source_type":  "mit_ocw",
                    "tags":         self._extract_mit_tags(title, description),
                    "language":     "en",
                    "is_free":      True,
                })

                if len(results) >= max_results:
                    break
            except Exception:
                continue

        return results

    def _extract_mit_tags(self, title: str, description: str) -> list[str]:
        """从标题和描述中提取可能的学科标签"""
        text = f"{title} {description}".lower()
        known_tags = ["python", "ai", "machine learning", "deep learning",
                      "linear algebra", "calculus", "statistics", "cs",
                      "computer science", "programming", "data science"]
        return [t for t in known_tags if t in text]

    def _search_khan(self, query: str, max_results: int) -> list[dict]:
        """
        搜索 Khan Academy。
        Khan Academy 提供公开 API: https://www.khanacademy.org/api/v1
        """
        # Khan Academy 的 /api/v1/topics 可以搜索
        # 这里提供一个简化实现
        print(f"[open_courses] Khan Academy 搜索: {query} (模拟)")
        return self._mock_khan_results(query, max_results)

    def _mock_mit_results(self, query: str, max_results: int) -> list[dict]:
        """MIT OCW 模拟数据"""
        return [
            {
                "url":          f"https://ocw.mit.edu/courses/6-0001-introduction-to-python/",
                "title":        f"Introduction to Python Programming ({query} related)",
                "title_zh":     None,
                "description":  f"MIT 课程: Python 编程入门，含视频、作业、考试",
                "pub_date":     "2023-09-01",
                "content_type": "course",
                "source":       "mit_ocw",
                "source_type":  "mit_ocw",
                "tags":         ["python", "programming", "cs"],
                "language":     "en",
                "is_free":      True,
                "_mock":        True,
            }
        ]

    def _mock_khan_results(self, query: str, max_results: int) -> list[dict]:
        """Khan Academy 模拟数据"""
        return [
            {
                "url":          f"https://www.khanacademy.org/computing/computer-programming/{query}",
                "title":        f"Khan Academy: {query} 编程课程",
                "title_zh":     None,
                "description":  f"Khan Academy 免费互动课程: {query}",
                "pub_date":     "2024-01-01",
                "content_type": "course",
                "source":       "khan_academy",
                "source_type":  "khan_academy",
                "tags":         [query, "interactive"],
                "language":     "en",
                "is_free":      True,
                "_mock":        True,
            }
        ]


# ── CLI 测试 ────────────────────────────────────────────────────
if __name__ == "__main__":
    src = Source()
    print("🔍 搜索公开课程: Python")
    results = src.search("Python", max_results=3)
    for r in results:
        mock_flag = " [模拟]" if r.get("_mock") else ""
        print(f"\n🎓 {r['title']}{mock_flag}")
        print(f"   来源: {r['source']}")
        print(f"   URL:  {r['url']}")
