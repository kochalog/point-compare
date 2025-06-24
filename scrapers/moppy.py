"""
scrapers/moppy.py  – iOS/Android 対応・ポイント表記補正版
2025/06/24
"""

import re, datetime, urllib.parse
from collections import defaultdict
from pprint import pprint

import requests
from bs4 import BeautifulSoup

# ─── 検索キーワード ───
KEYWORDS = ["楽天市場", "マージキャンプ"]

# ─── UA 3 種 ───
UAS = {
    "p": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "i": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "a": "Mozilla/5.0 (Linux; Android 14)",
}

# ─── HTML セレクタ（iOS 実HTMLに合わせて修正） ───
SELECTORS = {
    # ↓ PC・iOS・Android すべて拾えるよう 3 パターンをカンマ区切り
    "item":  "li.m-list__item, li.a-list__item, div.a-list__item",
    "title": ".a-list__item__title",
    "point": ".a-list__item__point",
}
# ───────────────────────────────────────────────

# モッピーは 1P = 1円
EXCHANGE_RATE = 1.0


def build_url(keyword: str) -> str:
    encoded = urllib.parse.quote(keyword, safe="")
    return f"https://pc.moppy.jp/search/?word={encoded}"


def _fetch_html(url: str, ua: str) -> str:
    r = requests.get(url, headers={"User-Agent": ua}, timeout=15)
    r.raise_for_status()
    return r.text


def _parse(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for box in soup.select(SELECTORS["item"]):
        t = box.select_one(SELECTORS["title"])
        p = box.select_one(SELECTORS["point"])
        if not (t and p):
            continue

        title = t.get_text(strip=True)
        raw = p.get_text(strip=True)       # 例 '1.2%' or '477P'

        # ％ or P 判定
        m = re.search(r"(\d+(?:\.\d+)?)", raw)
        if not m:
            continue
        val = float(m.group(1))
        reward = val if "%" in raw else val * EXCHANGE_RATE  # P→円換算

        yield title, reward


def scrape_moppy():
    merged = defaultdict(lambda: {"reward_decimal": 0.0, "devices": set()})

    for kw in KEYWORDS:
        url = build_url(kw)
        for code, ua in UAS.items():
            html = _fetch_html(url, ua)
            for title, reward in _parse(html):
                m = merged[title]
                m["title"] = title
                m["reward_decimal"] = max(m["reward_decimal"], reward)
                m["devices"].add(code)

    return [
        {
            "title": v["title"],
            "reward_decimal": v["reward_decimal"],
            "devices": ",".join(sorted(v["devices"])),  # Ex. 'i,a'
        }
        for v in merged.values()
    ]


# ─── デバッグ用 ───
if __name__ == "__main__":
    # PC 版 HTML を保存してセレクタ確認に利用
    with open("moppy.html", "w", encoding="utf-8") as f:
        f.write(_fetch_html(build_url(KEYWORDS[0]), UAS["p"]))
    print("moppy.html 保存完了 → open moppy.html で構造確認可")

    items = scrape_moppy()
    print(f"取得件数: {len(items)}")
    pprint(items[:10])
