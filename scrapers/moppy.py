"""
scrapers/moppy.py — モッピー検索結果スクレイパー（PC/iOS/Android 対応）
2025-06-25  production 版
  取得フィールド:
    title           案件タイトル
    reward_decimal  還元率 (%) または 円
    devices         'p,i,a' 形式  (p=PC, i=iOS, a=Android)
"""

from __future__ import annotations
import re, urllib.parse
from collections import defaultdict
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

# ─── 設定 ──────────────────────────────────────────────
KEYWORDS = ["楽天市場", "マージキャンプ"]

UAS = {  # 端末別 User-Agent
    "p": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "i": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "a": "Mozilla/5.0 (Linux; Android 14)",
}

SELECTORS = {                       # list__item を含む li / div を全部拾う
    "item":  "li[class*='list__item'], div[class*='list__item']",
    "title": ".a-list__item__title",
    "point": ".a-list__item__point",
}

EXCHANGE_RATE = 1.0                 # 1P = 1円
# ────────────────────────────────────────────────────


def build_url(keyword: str) -> str:
    return f"https://pc.moppy.jp/search/?word={urllib.parse.quote(keyword, safe='')}"

def fetch_html(url: str, ua: str) -> str:
    res = requests.get(url, headers={"User-Agent": ua}, timeout=15)
    res.raise_for_status()
    return res.text

def parse(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for box in soup.select(SELECTORS["item"]):
        t = box.select_one(SELECTORS["title"])
        p = box.select_one(SELECTORS["point"])
        if not (t and p):
            continue

        title = t.get_text(strip=True)
        raw   = p.get_text(strip=True)        # '1.0%' or '477P'

        m = re.search(r"(\d+(?:\.\d+)?)", raw)
        if not m:
            continue
        val = float(m.group(1))
        reward_decimal = val if "%" in raw else val * EXCHANGE_RATE

        yield title, reward_decimal

def scrape_moppy() -> List[Dict]:
    """
    端末 3 種 (PC/iOS/Android) それぞれで検索し、最高還元率をマージして返す
    """
    merged: Dict[str, Dict] = defaultdict(lambda: {"reward_decimal": 0.0, "devices": set()})

    for kw in KEYWORDS:
        url = build_url(kw)
        for code, ua in UAS.items():
            html = fetch_html(url, ua)
            for title, reward in parse(html):
                m = merged[title]
                m["title"] = title
                m["reward_decimal"] = max(m["reward_decimal"], reward)
                m["devices"].add(code)

    return [
        {
            "title": v["title"],
            "reward_decimal": v["reward_decimal"],
            "devices": ",".join(sorted(v["devices"])),   # 例 'a,i,p'
        }
        for v in merged.values()
    ]

# ─── 手動テスト用 ──────────────────────────────────────
if __name__ == "__main__":
    # PC 版 HTML を保存してブラウザ検証したい場合はコメントを外す
    # with open("moppy.html", "w", encoding="utf-8") as f:
    #     f.write(fetch_html(build_url(KEYWORDS[0]), UAS["p"]))
    # print("moppy.html 保存完了")

    data = scrape_moppy()
    print("取得件数:", len(data))
    for d in data[:10]:
        print(d)
