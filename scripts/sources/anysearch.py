"""
sources/anysearch.py — AnySearch 通用/学术搜索封装

AnySearch 是一个聚合搜索工具，支持:
  - 通用搜索（网页）
  - 学术搜索（论文）

此模块提供一个简单的 wrapper，如果 AnySearch 以 HTTP 服务形式运行，
则直接调用；否则返回模拟数据。
"""

from __future__ import annotations

import json
import urllib.request
import urllib.parse
from typing import Any


class Source:
    """
    AnySearch 数据源。

    如果 AnySearch 以 MCP 工具形式提供，此模块可以尝试通过
    subprocess 调用；如果以 HTTP API 形式提供，则直接请求。

    默认: 返回模拟数据（开发用）。
    """

    # 如果 AnySearch 部署为本地服务，填入此地址
    API_BASE = "http://localhost:8080"

    def __init__(self, api_key: str | None = None):
        self.api_base = self.API_BASE

    def search(self, query: str, max_results: int = 10, search_type: str = "general") -> list[dict]:
        """
        通过 AnySearch 搜索。
        search_type: "general" | "scholar"
        """
        # 尝试调用 AnySearch API（如果可用）
        url = f"{self.api_base}/search"
        payload = json.dumps({
            "query": query,
            "type":  search_type,
            "limit": max_results,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return self._parse_results(data, search_type)
        except Exception:
            # AnySearch 不可用，返回模拟数据
            return self._mock_results(query, max_results, search_type)

    def search_general(self, query: str, max_results: int = 10) -> list[dict]:
        """通用网页搜索"""
        return self.search(query, max_results, "general")

    def search_scholar(self, query: str, max_results: int = 10) -> list[dict]:
        """学术搜索"""
        return self.search(query, max_results, "scholar")

    def _parse_results(self, data: dict, search_type: str) -> list[dict]:
        """解析 AnySearch 返回结果"""
        results = []
        items = data.get("results", data.get("items", []))

        for item in items:
            results.append({
                "url":          item.get("url", item.get("link", "")),
                "title":        item.get("title", ""),
                "title_zh":     item.get("title_zh"),
                "description":  item.get("snippet", item.get("description", ""))[:300],
                "pub_date":     item.get("date") or item.get("pub_date"),
                "content_type": "article" if search_type == "general" else "paper",
                "source":       "anysearch",
                "source_type":  "anysearch",
                "tags":         item.get("tags", []) or [search_type],
                "language":     item.get("language", "en"),
            })

        return results

    def _mock_results(self, query: str, max_results: int, search_type: str) -> list[dict]:
        """模拟数据（AnySearch 不可用时的降级方案）"""
        print(f"[anysearch] AnySearch 不可用，返回模拟数据")
        return [
            {
                "url":          f"https://example.com/search?q={urllib.parse.quote(query)}",
                "title":        f"[模拟] {query} - 搜索结果",
                "title_zh":     None,
                "description":  f"关于 {query} 的搜索结果摘要...",
                "pub_date":     "2025-01-01",
                "content_type": "article",
                "source":       "anysearch",
                "source_type":  "anysearch",
                "tags":         [query, search_type],
                "language":     "zh",
                "_mock":        True,
            }
        ]


# ── CLI 测试 ────────────────────────────────────────────────────
if __name__ == "__main__":
    src = Source()
    print("🔍 AnySearch 通用搜索:", "Python 教程")
    results = src.search_general("Python 教程", max_results=3)
    for r in results:
        mock_flag = " [模拟]" if r.get("_mock") else ""
        print(f"  📄 {r['title']}{mock_flag}")
