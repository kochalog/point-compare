"""
scrapers/moppy.py  – DEBUG版 (ヒット件数表示 + ワイルドカードセレクタ)
2025/06/24
"""
import re, urllib.parse
from collections import defaultdict
from pprint import pprint
import requests
from bs4 import BeautifulSoup

KEYWORDS = ["楽天市場", "マージキャンプ"]
UAS = {
    "p": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "i": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "a": "Mozilla/5.0 (Linux; Android 14)",
}
SELECTORS = {                      # list__item を含む li/div を全部拾う
    "item":  "li[class*='list__item'], div[class*='list__item']",
    "title": ".a-list__item__title",
    "point": ".a-list__item__point",
}
EXCHANGE_RATE = 1.0                # 1P = 1円

def build_url(keyword):
    return f"https://pc.moppy.jp/search/?word={urllib.parse.quote(keyword,safe='')}"

def fetch_html(url, ua):
    r = requests.get(url, headers={"User-Agent": ua}, timeout=15)
    r.raise_for_status()
    return r.text

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    cand = soup.select(SELECTORS["item"])
    print("DEBUG:", len(cand), "item-boxes hit for selector", SELECTORS["item"])
    for box in cand:
        t = box.select_one(SELECTORS["title"])
        p = box.select_one(SELECTORS["point"])
        if not (t and p): continue
        title = t.get_text(strip=True)
        raw   = p.get_text(strip=True)            # '1.0%' or '477P'
        m = re.search(r"(\d+(?:\.\d+)?)", raw)
        if not m: continue
        val = float(m.group(1))
        reward = val if "%" in raw else val * EXCHANGE_RATE
        yield title, reward

def scrape_moppy():
    merged = defaultdict(lambda: {"reward_decimal": 0.0, "devices": set()})
    for kw in KEYWORDS:
        url = build_url(kw)
        for code, ua in UAS.items():              # p / i / a
            html = fetch_html(url, ua)
            for title, reward in parse(html):
                m = merged[title]
                m["title"] = title
                m["reward_decimal"] = max(m["reward_decimal"], reward)
                m["devices"].add(code)
    return [{"title": v["title"],
             "reward_decimal": v["reward_decimal"],
             "devices": ",".join(sorted(v["devices"]))}
            for v in merged.values()]

if __name__ == "__main__":
    # PC版HTML保存（構造確認用）
    with open("moppy.html", "w", encoding="utf-8") as f:
        f.write(fetch_html(build_url(KEYWORDS[0]), UAS["p"]))
    print("moppy.html 保存完了 → open で構造確認可")

    data = scrape_moppy()
    print("取得件数:", len(data))
    pprint(data[:10])
