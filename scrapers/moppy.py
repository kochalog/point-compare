"""
scrapers/moppy.py
────────────────────────────────────────────────────────────
■ 目的
同じ検索 URL を PC / iOS / Android の 3 つの User-Agent で取得し、
    title            : 案件タイトル
    reward_decimal   : 各デバイスの還元率のうち “最高値”
    devices          : p,s,i,a をカンマ区切り
の 1 行に統合したリストを返す。

■ 流れ
1) _fetch_html()     : UA を切り替えて HTML を取得
2) _parse(html)      : BeautifulSoup で 1 ページ分を list[(title,reward)]
3) scrape_moppy()    : 3 ページをマージし devices を作成
4) __main__          : デバッグ用
────────────────────────────────────────────────────────────
※ モッピー側の HTML 構造が変わるとセレクタも変わるので、
   必ず moppy.html を開いて class 名を確認してから調整してください。
"""

import os
import re
import datetime
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from pprint import pprint

# ❶  検索キーワードは自由に変えてOK
URL = "https://pc.moppy.jp/shopping/?keyword=楽天市場"

# ❷  User-Agent 3 種
UAS = {
    "p": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "i": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "a": "Mozilla/5.0 (Linux; Android 14)",
}

# ❸  ──────────── セレクタ設定 ────────────
# moppy.html を開いて合わない場合は書き換えてください
SELECTORS = {
    "item":  "li.m-list__item",                 # 1 件を包むタグ
    "title": ".m-list__item__action--line-clamp1",
    "point": ".m-list__item__point",
}
# ────────────────────────────────────────


def _fetch_html(ua: str) -> str:
    """1 ページを UA 指定で取得して HTML を返す"""
    res = requests.get(URL, headers={"User-Agent": ua}, timeout=15)
    res.raise_for_status()
    return res.text


def _parse(html: str):
    """1 ページ分の HTML から (title, reward_decimal) をイテレート"""
    soup = BeautifulSoup(html, "html.parser")
    for box in soup.select(SELECTORS["item"]):
        t = box.select_one(SELECTORS["title"])
        p = box.select_one(SELECTORS["point"])
        if not (t and p):
            continue
        title = t.get_text(strip=True)

        percent_txt = p.get_text(strip=True)        # '1.2%' など
        m = re.search(r"(\d+(?:\.\d+)?)", percent_txt)
        reward = float(m.group(1)) if m else 0.0

        yield title, reward


def scrape_moppy():
    """
    UA=3 種で取得 → タイトルごとに devices と最高還元率をマージ
    戻り値: list[dict]
    """
    merged = defaultdict(lambda: {"devices": set(), "reward_decimal": 0.0})

    for code, ua in UAS.items():           # p / i / a
        html = _fetch_html(ua)
        for title, reward in _parse(html):
            m = merged[title]
            m["title"] = title
            m["reward_decimal"] = max(m["reward_decimal"], reward)
            m["devices"].add(code)

    return [
        {
            "title": v["title"],
            "reward_decimal": v["reward_decimal"],
            "devices": ",".join(sorted(v["devices"])),  # 'i,a' など
        }
        for v in merged.values()
    ]


# ─────────────── デバッグ用 ────────────────
if __name__ == "__main__":
    # 1) HTML（PC 版）を保存してセレクタ確認に使う
    pc_html = _fetch_html(UAS["p"])
    with open("moppy.html", "w", encoding="utf-8") as f:
        f.write(pc_html)
    print("PC 版 HTML を moppy.html に保存しました → open して class 名を確認してください")

    # 2) スクレイプ結果を確認
    data = scrape_moppy()
    print(f"取得件数: {len(data)}  件")
    pprint(data[:10])
