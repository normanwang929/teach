"""
sources/zhihu.py — 知乎深度文章搜索

使用知乎搜索 API（无需官方 Key，但需模拟浏览器请求）。
生产环境建议传入有效 Cookie。
"""

from __future__ import annotations

import json
import urllib.request
import urllib.parse
from typing import Any


class Source:
    """知乎数据源"""

    SEARCH_URL = "https://www.zhihu.com/api/v4/search_v3"

    def __init__(self, api_key: str | None = None):
        self.cookie = api_key  # 可选：传入 cookie

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        """
        搜索知乎文章和回答。
        """
        params = urllib.parse.urlencode({
            "t":           "general",
            "q":           query,
            "correction":  "1",
            "offset":      "0",
            "limit":       str(min(max_results, 20)),
            "search_source": "Normal",
        })
        url = f"{self.SEARCH_URL}?{params}"

        headers = self._build_headers()
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[zhihu] 请求失败: {e}")
            # 返回模拟数据，用于开发和测试
            return self._mock_results(query, max_results)

        return self._parse_results(data)

    def search_articles(self, query: str, max_results: int = 10) -> list[dict]:
        """只搜索知乎文章（质量通常比回答高）"""
        params = urllib.parse.urlencode({
            "t":          "zhihu",
            "q":          query,
            "correction": "1",
            "offset":     "0",
            "limit":      str(min(max_results, 20)),
            "type":       "articles",
        })
        url = f"{self.SEARCH_URL}?{params}"
        headers = self._build_headers()
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return self._parse_results(data)
        except Exception:
            return self._mock_results(query, max_results)

    def _build_headers(self) -> dict:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.zhihu.com",
            "Accept": "application/json, text/plain, */*",
            "x-requested-with": "fetch",
        }
        if self.cookie:
            headers["Cookie"] = self.cookie
        return headers

    def _parse_results(self, data: dict) -> list[dict]:
        """解析知乎搜索结果"""
        results = []
        items = data.get("data", [])

        for item in items:
            try:
                obj = item.get("object", {})
                if not obj:
                    continue

                obj_type = obj.get("type", "")

                # 只处理文章和回答
                if obj_type not in ("article", "answer", "question"):
                    continue

                title = obj.get("title", "") or obj.get("question", {}).get("title", "")
                if not title:
                    continue

                # 构建 URL
                url = ""
                if obj_type == "article":
                    article_id = obj.get("id", "")
                    url = f"https://zhuanlan.zhihu.com/p/{article_id}"
                elif obj_type == "answer":
                    question_id = obj.get("question", {}).get("id", "")
                    answer_id = obj.get("id", "")
                    url = f"https://www.zhihu.com/question/{question_id}/answer/{answer_id}"
                elif obj_type == "question":
                    question_id = obj.get("id", "")
                    url = f"https://www.zhihu.com/question/{question_id}"

                # 描述/摘要
                description = (
                    obj.get("excerpt", "")
                    or obj.get("content", "")[:300]
                    or ""
                )
                # 去掉 HTML 标签
                import re
                description = re.sub(r"<[^>]+>", "", description).strip()

                # 发布日期
                created = obj.get("created_time") or obj.get("updated_time")
                pub_date = None
                if created:
                    import datetime
                    pub_date = datetime.datetime.fromtimestamp(
                        created, tz=datetime.timezone.utc
                    ).strftime("%Y-%m-%d")

                results.append({
                    "url":          url,
                    "title":        title,
                    "title_zh":     title,
                    "description":  description,
                    "pub_date":     pub_date,
                    "content_type": "article" if obj_type == "article" else "qa",
                    "source":       "zhihu",
                    "source_type":  "zhihu",
                    "tags":         [],
                    "language":     "zh",
                    "vote_count":   obj.get("voteup_count", 0),
                })
            except Exception as e:
                print(f"[zhihu] 解析条目失败: {e}")
                continue

        return results

    def _mock_results(self, query: str, max_results: int) -> list[dict]:
        """当 API 不可用时返回模拟数据（开发/测试用）"""
        print(f"[zhihu] API 不可用，返回模拟数据（请配置 Cookie 以访问真实数据）")
        return [
            {
                "url":          f"https://zhuanlan.zhihu.com/p/mock-{query}",
                "title":        f"[模拟] 关于{query}的深度解析",
                "title_zh":     f"[模拟] 关于{query}的深度解析",
                "description":  f"这是一篇关于{query}的知乎文章摘要...",
                "pub_date":     "2025-01-01",
                "content_type": "article",
                "source":       "zhihu",
                "source_type":  "zhihu",
                "tags":         [query, "教程"],
                "language":     "zh",
                "vote_count":   100,
                "_mock":        True,
            }
        ]


# ── CLI 测试 ────────────────────────────────────────────────────
if __name__ == "__main__":
    src = Source()
    print("🔍 搜索知乎: Transformer 模型")
    results = src.search("Transformer 模型", max_results=3)
    for r in results:
        mock_flag = " [模拟]" if r.get("_mock") else ""
        print(f"\n📝 {r['title']}{mock_flag}")
        print(f"   URL:  {r['url']}")
        print(f"   摘要: {r['description'][:80]}...")
