"""
sources/wikipedia.py — 维基百科搜索

使用 Wikipedia MediaWiki API（无需 Key）:
  https://en.wikipedia.org/w/api.php

返回摘要 + 全文链接，适合作为课程背景知识来源。
"""

from __future__ import annotations

import json
import urllib.request
import urllib.parse
from typing import Any


class Source:
    """维基百科数据源"""

    # MediaWiki API（免费，无需 Key）
    WIKI_API_EN = "https://en.wikipedia.org/w/api.php"
    WIKI_API_ZH = "https://zh.wikipedia.org/w/api.php"

    def __init__(self, api_key: str | None = None):
        pass

    def search(self, query: str, max_results: int = 10, lang: str = "auto") -> list[dict]:
        """
        搜索维基百科文章。
        lang: "auto" | "en" | "zh"
        """
        # 自动检测语言
        if lang == "auto":
            has_cn = any("\u4e00" <= c <= "\u9fff" for c in query)
            lang = "zh" if has_cn else "en"

        api_url = self.WIKI_API_ZH if lang == "zh" else self.WIKI_API_EN

        # 使用 MediaWiki API 搜索
        params = urllib.parse.urlencode({
            "action":   "query",
            "list":     "search",
            "srsearch":  query,
            "srlimit":  max_results,
            "format":   "json",
            "srprop":   "timestamp|snippet",
        })
        url = f"{api_url}?{params}"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "TeachPlatform/1.0 (mailto:teach@example.com)"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return self._parse_search_results(data, lang)
        except Exception as e:
            print(f"[wikipedia] 搜索失败: {e}")
            return self._mock_results(query, max_results, lang)

    def _parse_search_results(self, data: dict, lang: str) -> list[dict]:
        """解析 MediaWiki API 搜索结果"""
        results = []
        search_results = data.get("query", {}).get("search", [])

        for item in search_results:
            title = item.get("title", "")
            if not title:
                continue

            snippet = item.get("snippet", "")
            # 去掉 HTML 标签
            import re
            snippet = re.sub(r"<[^>]+>", "", snippet)

            # 构建 URL
            url = self._build_url(title, lang)

            # 获取摘要
            description = self._fetch_summary(title, lang)

            results.append({
                "url":          url,
                "title":        title,
                "title_zh":     None,
                "description":  description or snippet[:300],
                "pub_date":     None,  # 维基百科不提供固定发布日期
                "content_type": "article",
                "source":       "wikipedia",
                "source_type":  "wikipedia",
                "tags":         [lang],
                "language":     lang,
                "is_free":      True,
            })

        return results

    def _fetch_summary(self, title: str, lang: str, sentence_count: int = 3) -> str:
        """
        获取文章摘要（通过 MediaWiki API extract）。
        返回纯文本摘要。
        """
        params = urllib.parse.urlencode({
            "action":        "query",
            "titles":         title,
            "prop":           "extracts",
            "exintro":        "1",       # 只要导言段
            "explaintext":    "1",       # 纯文本（不要 HTML）
            "exsentences":    sentence_count,
            "format":         "json",
        })
        api_url = self.WIKI_API_ZH if lang == "zh" else self.WIKI_API_EN
        url = f"{api_url}?{params}"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "TeachPlatform/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                extract = page.get("extract", "")
                if extract:
                    return extract[:500]
        except Exception:
            pass
        return ""

    def _build_url(self, title: str, lang: str) -> str:
        """构建维基百科文章 URL"""
        encoded = urllib.parse.quote(title.replace(" ", "_"), safe="")
        domain = "zh.wikipedia.org" if lang == "zh" else "en.wikipedia.org"
        return f"https://{domain}/wiki/{encoded}"

    def get_full_article(self, title: str, lang: str = "en") -> str | None:
        """获取完整文章内容（通过 MediaWiki API）"""
        params = urllib.parse.urlencode({
            "action": "query",
            "titles":  title,
            "prop":    "extracts",
            "explaintext": "1",
            "format":  "json",
        })
        api_url = self.WIKI_API_ZH if lang == "zh" else self.WIKI_API_EN
        url = f"{api_url}?{params}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TeachPlatform/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                return page.get("extract", "")
        except Exception as e:
            print(f"[wikipedia] 获取全文失败: {e}")
            return None

    def _mock_results(self, query: str, max_results: int, lang: str) -> list[dict]:
        """模拟数据（开发/测试用）"""
        print(f"[wikipedia] 使用模拟数据")
        return [
            {
                "url":          self._build_url(query, lang),
                "title":        query,
                "title_zh":     None,
                "description":  f"维基百科关于 {query} 的条目...",
                "pub_date":     None,
                "content_type": "article",
                "source":       "wikipedia",
                "source_type":  "wikipedia",
                "tags":         [query],
                "language":     lang,
                "is_free":      True,
                "_mock":        True,
            }
        ]


# ── CLI 测试 ────────────────────────────────────────────────────
if __name__ == "__main__":
    src = Source()

    print("🔍 搜索维基百科 (英文): Python (programming language)")
    results = src.search("Python (programming language)", max_results=2, lang="en")
    for r in results:
        mock_flag = " [模拟]" if r.get("_mock") else ""
        print(f"\n📖 {r['title']}{mock_flag}")
        print(f"   {r['description'][:150]}...")

    print("\n\n🔍 搜索维基百科 (中文): Python 编程语言")
    results_zh = src.search("Python 编程语言", max_results=2, lang="zh")
    for r in results_zh:
        print(f"\n📖 {r['title']}")
        print(f"   {r['description'][:150]}...")
