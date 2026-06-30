"""
sources/anysearch.py — AnySearch MCP 通用/学术搜索封装

通过 AnySearch MCP API 直接搜索，取代不稳定的 Wikipedia/arXiv。
支持通用搜索和学术搜索，返回结构化结果。
"""

from __future__ import annotations

import json
import os
import re
import urllib.parse
from typing import Any

# 从 Hermes 环境变量读取 AnySearch 配置
ANYSEARCH_API_KEY = os.environ.get(
    "ANYSEARCH_API_KEY",
    "as_sk_cff00b5c2453b0e805e3bbaf6997f18b",
)
ANYSEARCH_URL = "https://api.anysearch.com/mcp"


class Source:
    """AnySearch MCP 数据源 — 直接调用 MCP API"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or ANYSEARCH_API_KEY

    def _call_mcp(self, query: str, domain: str | None = None, sub_domain: str | None = None,
                   max_results: int = 10) -> list[dict]:
        """调用 AnySearch MCP 搜索"""
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "search",
                "arguments": {
                    "query": query,
                    "max_results": min(max_results, 10),
                },
            },
            "id": 1,
        }

        # 如果有垂直域，加上 domain/sub_domain
        if domain:
            payload["params"]["arguments"]["domain"] = domain
        if sub_domain:
            payload["params"]["arguments"]["sub_domain"] = sub_domain

        try:
            import urllib.request
            req = urllib.request.Request(
                ANYSEARCH_URL,
                data=json.dumps(payload).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())

            text = ""
            content = data.get("result", {}).get("content", [])
            if content and isinstance(content[0], dict):
                text = content[0].get("text", "")

            return self._parse_markdown_results(text, query)

        except Exception as e:
            print(f"  [anysearch] 请求失败: {e}")
            return []

    def _parse_markdown_results(self, text: str, query: str) -> list[dict]:
        """解析 AnySearch 返回的 Markdown 格式结果"""
        results = []
        # 格式: ### N. title\n- **URL**: https://...\n- 描述...
        lines = text.split("\n")
        current = {}
        for line in lines:
            # 匹配 "### N. title"
            m = re.match(r'^###\s+\d+\.\s+(.+)', line)
            if m:
                if current and current.get("title"):
                    results.append(current)
                current = {"title": m.group(1).strip(), "url": "", "description": ""}
                continue
            # 匹配 "- **URL**: https://..."
            m = re.match(r'^-\s+\*\*URL\*\*:\s+(.+)', line)
            if m and current:
                current["url"] = m.group(1).strip()
                continue
            # 匹配 "- 描述..."
            m = re.match(r'^-\s+(.+)', line)
            if m and current and not line.startswith("- **"):
                if current["description"]:
                    current["description"] += " " + m.group(1).strip()
                else:
                    current["description"] = m.group(1).strip()
                current["description"] = current["description"][:300]

        # 最后一条
        if current and current.get("title") and current.get("url"):
            results.append(current)

        parsed = []
        for item in results:
            title = item["title"].strip()
            url = item["url"].strip()
            desc = item.get("description", "").strip()[:300]
            if not title or not url:
                continue

            has_zh = any('\u4e00' <= c <= '\u9fff' for c in title + desc)
            lang = "zh" if has_zh else "en"

            parsed.append({
                "url": url,
                "title": title,
                "title_zh": None,
                "description": desc,
                "pub_date": None,
                "content_type": "article",
                "source": "anysearch",
                "source_type": "anysearch",
                "tags": [],
                "language": lang,
                "is_free": True,
            })

        return parsed

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        """统一的搜索接口（被 search_course_materials.py 调用）"""
        return self.search_general(query, max_results)

    def search_general(self, query: str, max_results: int = 10) -> list[dict]:
        """通用网页搜索"""
        return self._call_mcp(query, max_results=max_results)

    def search_scholar(self, query: str, max_results: int = 10) -> list[dict]:
        """学术搜索"""
        return self._call_mcp(query, domain="academic", max_results=max_results)


# ── CLI 测试 ──
if __name__ == "__main__":
    src = Source()
    print("🔍 AnySearch 通用搜索:", "Python 基础教程")
    results = src.search_general("Python 基础教程", max_results=5)
    print(f"  结果: {len(results)} 条")
    for r in results[:5]:
        print(f"  📄 {r['title']}")
        print(f"     {r['url']}")
