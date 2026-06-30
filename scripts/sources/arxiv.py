"""
sources/arxiv.py — arXiv 学术论文搜索

使用 arXiv 公开 API（无需 Key）:
  https://arxiv.org/help/api/index

返回格式符合 sources/__init__.py 规范。
"""

from __future__ import annotations

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any


class Source:
    """arXiv 数据源"""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, api_key: str | None = None):
        pass  # arXiv 无需 API Key

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        """
        搜索 arXiv 论文。
        query: 搜索关键词（支持 AND/OR 语法）
        """
        params = urllib.parse.urlencode({
            "search_query": f"all:{query}",
            "start":        0,
            "max_results":  max_results,
            "sortBy":       "relevance",
            "sortOrder":    "descending",
        })
        url = f"{self.BASE_URL}?{params}"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "TeachPlatform/1.0 (mailto:teach@example.com)"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml_data = resp.read()
        except Exception as e:
            print(f"[arxiv] 请求失败: {e}")
            return []

        return self._parse_xml(xml_data)

    def search_by_category(self, category: str, max_results: int = 10) -> list[dict]:
        """
        按学科分类搜索。
        category 示例: "cs.AI", "cs.LG", "stat.ML", "cs.CL"
        """
        params = urllib.parse.urlencode({
            "search_query": f"cat:{category}",
            "start":        0,
            "max_results":  max_results,
            "sortBy":       "submittedDate",
            "sortOrder":    "descending",
        })
        url = f"{self.BASE_URL}?{params}"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "TeachPlatform/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml_data = resp.read()
            return self._parse_xml(xml_data)
        except Exception as e:
            print(f"[arxiv] 分类搜索失败: {e}")
            return []

    def _parse_xml(self, xml_data: bytes) -> list[dict]:
        """解析 arXiv API 返回的 Atom XML"""
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            print(f"[arxiv] XML 解析失败: {e}")
            return []

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        results = []

        for entry in root.findall("atom:entry", ns):
            try:
                title_el = entry.find("atom:title", ns)
                title = title_el.text.strip().replace("\n", " ") if title_el is not None else ""

                summary_el = entry.find("atom:summary", ns)
                description = summary_el.text.strip().replace("\n", " ")[:500] if summary_el is not None else ""

                id_el = entry.find("atom:id", ns)
                url = id_el.text.strip() if id_el is not None else ""

                published_el = entry.find("atom:published", ns)
                pub_date = published_el.text[:10] if published_el is not None else None

                authors = []
                for author in entry.findall("atom:author", ns):
                    name_el = author.find("atom:name", ns)
                    if name_el is not None:
                        authors.append(name_el.text.strip())

                # 提取分类标签
                tags = []
                for category in entry.findall("atom:category", ns):
                    term = category.get("term", "")
                    if term:
                        tags.append(term)

                results.append({
                    "url":          url,
                    "title":        title,
                    "title_zh":     None,
                    "description":  description,
                    "pub_date":     pub_date,
                    "content_type": "paper",
                    "source":       "arxiv",
                    "source_type":  "arxiv",
                    "tags":         tags,
                    "authors":      authors,
                    "language":     "en",
                    "citations":    None,  # arXiv API 不直接提供引用数
                })
            except Exception as e:
                print(f"[arxiv] 解析条目失败: {e}")
                continue

        return results


# ── CLI 测试 ────────────────────────────────────────────────────
if __name__ == "__main__":
    src = Source()
    print("🔍 搜索: transformer")
    results = src.search("transformer", max_results=3)
    for r in results:
        print(f"\n📄 {r['title']}")
        print(f"   URL:  {r['url']}")
        print(f"   日期: {r['pub_date']}")
        print(f"   标签: {', '.join(r['tags'][:5])}")

    print("\n\n🔍 按分类搜索: cs.AI (最新)")
    results2 = src.search_by_category("cs.AI", max_results=3)
    for r in results2:
        print(f"  📄 {r['title'][:60]}  [{r['pub_date']}]")
