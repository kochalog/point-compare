"""
scrapers/moppy.py  – 2025/06/24
────────────────────────────────────────────────────────────
■ 概要
  1. 検索キーワードごとに
  2. PC / iOS / Android ３種類の User-Agent で HTML を取得
  3. タイトル・還元率をパースし、
     devices 列には p,s,i,a をカンマ区切りで格納する
     （同タイトル行は最高還元率＆デバイス集合でマージ）
────────────────────────────────────────────────────────────
"""

import re, datetime, urllib.parse
from collections import defaultdict
from pprint import pprint

import requests
from bs4 import BeautifulSoup

# 検索キーワードを増やしたい場合はここに追加
KEYWORDS = ["楽天市場", "マージキャンプ"]

# UA コード → 実際の User-Agent 文字列
UAS = {
    "p": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "i": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "a": "Mozilla/5.0 (Linux; Android 14)",
}

# ────────────── HTML セレクタ設定 ──────────────
SELECTORS = {
    "item":  "li.m-list__item",                       # 1 件コンテナ
    "title": ".m-list__item__action--line-clamp1",    # タイトル
    "point": ".m-list__item__point",                  # 還元率
}
# 必ず moppy.html を開いて class 名が合わない場合は上を書き換えてください
# ──────────────────────────────────────────────


def build_url(keyword: str) -> str:
    """キーワードを URL エンコードして正式検索 URL を作る"""
    encoded = urllib.parse.quote(keyword, safe="")
    return f"https://pc.moppy.jp/search/?word={encoded}"


def _fetch_html(url: str, ua: str) -> str:
    res = requests.get(url, headers={"User-Agent": ua}, timeout=15)
    res.raise_for_status()
    return res.text


def _parse(html: str):
    """HTML から (title, reward_decimal) を yield"""
    soup = BeautifulSoup(html, "html.parser")
    for box in soup.select(SELECTORS["item"]):
        t = box.select_one(SELECTORS["title"])
        p = box.select_one(SELECTORS["point"])
        if not (t and p):
            continue
        title = t.get_text(strip=True)

        m = re.search(r"(\d+(?:\.\d+)?)", p.get_text(strip=True))
        reward = float(m.group(1)) if m else 0.0
        yield title, reward


def scrape_moppy():
    """
    returns list[dict]:
      {title, reward_decimal, devices}
    """
    merged = defaultdict(lambda: {"reward_decimal": 0.0, "devices": set()})

    for kw in KEYWORDS:
        url = build_url(kw)
        for code, ua in UAS.items():           # p / i / a
            html = _fetch_html(url, ua)
            for title, reward in _parse(html):
                m = merged[title]
                m["title"] = title
                m["reward_decimal"] = max(m["reward_decimal"], reward)
                m["devices"].add(code)

    # set → 'p,i,a' のように並びを固定してカンマ連結
    return [
        {
            "title": v["title"],
            "reward_decimal": v["reward_decimal"],
            "devices": ",".join(sorted(v["devices"])),
        }
        for v in merged.values()
    ]


# ────────────── デバッグ用 ──────────────────
if __name__ == "__main__":
    # PC 版 HTML を保存：セレクタ確認に使う
    first_url = build_url(KEYWORDS[0])
    with open("moppy.html", "w", encoding="utf-8") as f:
        f.write(_fetch_html(first_url, UAS["p"]))
    print("moppy.html を保存しました → open して class 名を確認できます")

    # スクレイプ結果プレビュー
    items = scrape_moppy()
    print(f"取得件数: {len(items)} 件")
    pprint(items[:10])
