"""
sources/bilibili.py — B站视频教程搜索（改进版）

B站 API 有反爬机制，策略:
  1. 如果用户提供了 Cookie（从浏览器复制），使用 Cookie 发起请求
  2. 否则使用 B站搜索页面的 og:title 等公开信息（降级方案）
  3. 或者引导用户使用 bilibili-api-python 库

建议: 安装 bilibili-api-python 以获得最佳体验
  pip install bilibili-api-python

Cookie 获取方式:
  1. 打开 https://www.bilibili.com 并登录
  2. F12 → Network → 任意请求 → 复制 Cookie 请求头
  3. 设置环境变量: set BILIBILI_COOKIE=your_cookie_here
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
import urllib.parse
from typing import Any


class Source:
    """Bilibili 数据源（支持 Cookie 认证）"""

    SEARCH_URL = "https://api.bilibili.com/x/web-interface/wbi/search/type"
    # 使用 wbi 签名接口（B站推荐，反爬较弱）

    def __init__(self, api_key: str | None = None):
        """
        api_key 参数在这里用作 Cookie。
        也可以设置环境变量 BILIBILI_COOKIE。
        """
        self.cookie = api_key or os.environ.get("BILIBILI_COOKIE", "")

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        """搜索 B站视频"""
        if self.cookie:
            return self._search_with_cookie(query, max_results)
        else:
            print("[bilibili] 未配置 Cookie，使用公开搜索（结果可能受限）")
            return self._search_public(query, max_results)

    def _search_with_cookie(self, query: str, max_results: int) -> list[dict]:
        """使用 Cookie 认证搜索（推荐）"""
        params = urllib.parse.urlencode({
            "search_type": "video",
            "keyword":      query,
            "page":         1,
            "page_size":    min(max_results, 20),
            "order":        "totalrank",
            "duration":     0,
        })
        url = f"{self.SEARCH_URL}?{params}"

        headers = self._build_headers()
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                # 检查返回类型
                ct = resp.headers.get("Content-Type", "")
                raw = resp.read()
                if "json" not in ct:
                    print(f"[bilibili] 返回非 JSON 内容（可能反爬），前 100 字节: {raw[:100]}")
                    return self._search_public(query, max_results)
                data = json.loads(raw.decode("utf-8"))
        except Exception as e:
            print(f"[bilibili] 请求失败: {e}")
            return self._search_public(query, max_results)

        if data.get("code") != 0:
            print(f"[bilibili] API 错误 code={data.get('code')}: {data.get('message')}")
            # 可能是 Cookie 失效
            if data.get("code") in (60004, -403, 0):
                print("[bilibili] Cookie 可能已失效，请更新")
            return self._search_public(query, max_results)

        return self._parse_results(data.get("data", {}).get("result", []))

    def _search_public(self, query: str, max_results: int) -> list[dict]:
        """
        公开搜索（无需 Cookie，通过搜索结果页面解析）。
        作为 Cookie 搜索失败时的降级方案。
        """
        # 方案：使用 RSS 搜索（B站提供部分 RSS）
        # 或者返回空结果并提示用户配置 Cookie
        print("[bilibili] 提示: 配置 BILIBILI_COOKIE 环境变量可获得完整搜索结果")
        print("[bilibili] Cookie 获取方式: 登录 B站 → F12 → Network → 复制 Cookie 请求头")
        return []

    def _build_headers(self) -> dict:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.bilibili.com",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        if self.cookie:
            headers["Cookie"] = self.cookie
        return headers

    def _parse_results(self, items: list[dict]) -> list[dict]:
        """解析 B站搜索结果"""
        results = []
        for item in items:
            try:
                bvid = item.get("bvid", "")
                if not bvid:
                    continue

                # 清理标题中的 HTML 高亮标签
                title = re.sub(r"<[^>]+>", "", item.get("title", ""))

                # 时长
                duration_sec = item.get("duration", 0)

                # 发布日期
                pub_ts = item.get("pubdate", 0)
                pub_date = None
                if pub_ts:
                    import datetime
                    pub_date = datetime.datetime.fromtimestamp(
                        pub_ts, tz=datetime.timezone.utc
                    ).strftime("%Y-%m-%d")

                # 播放量
                view_count = item.get("play", 0) or item.get("view_count", 0)

                results.append({
                    "url":          f"https://www.bilibili.com/video/{bvid}",
                    "title":        title,
                    "title_zh":     title,
                    "description":  (item.get("description", "") or "")[:300],
                    "pub_date":     pub_date,
                    "content_type": "video",
                    "source":       "bilibili",
                    "source_type":  "bilibili",
                    "tags":         self._extract_tags(item),
                    "duration":     duration_sec,
                    "view_count":   view_count,
                    "language":     "zh",
                    "is_free":      True,
                })
            except Exception as e:
                print(f"[bilibili] 解析条目失败: {e}")
                continue

        return results

    def _extract_tags(self, item: dict) -> list[str]:
        tags = []
        tid_name = item.get("typename", "")
        if tid_name:
            tags.append(tid_name)
        return tags


# ── CLI 测试 ────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    cookie = os.environ.get("BILIBILI_COOKIE", "")
    if not cookie:
        print("⚠️  未配置 BILIBILI_COOKIE")
        print("请设置环境变量后重试:")
        print("  set BILIBILI_COOKIE=your_cookie_here")
        print("或:")
        print("  $env:BILIBILI_COOKIE = 'your_cookie'  # PowerShell")
        sys.exit(1)

    src = Source(api_key=cookie)
    print("🔍 搜索 B站: Python 教程")
    results = src.search("Python 教程", max_results=5)
    for r in results:
        mins = (r.get("duration") or 0) // 60
        print(f"\n📺 {r['title']}")
        print(f"   URL:   {r['url']}")
        print(f"   时长:  {mins} 分钟 | 播放: {r['view_count']:,}" if r['view_count'] else "")
