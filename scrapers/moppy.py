"""
scrapers/moppy.py
モッピー（PC 版）の検索結果ページから
  title          : 案件タイトル
  reward_decimal : 還元率(%) を小数にした値
  devices        : p,s,i,a をカンマ区切り
を抜き出すスクレイパー。

最下部 (__main__) では
  1. HTML 全文を moppy.html に保存してデバッグしやすくする
  2. scrape_moppy() の先頭 5 件を pprint で表示する
"""

import re, requests
from bs4 import BeautifulSoup
from pprint import pprint

# ‼️ 検索キーワードは必要に応じて変更してください
URL = "https://pc.moppy.jp/shopping/?keyword=楽天市場"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

ALT_MAP = {  # alt 属性 → 短縮コード
    "pc": "p",
    "sp": "s",
    "ios": "i",
    "android": "a",
}


def scrape_moppy():
    """returns list[dict]"""
    res = requests.get(URL, headers=HEADERS, timeout=15)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    items = []
    # ──────────────────────────────
    # ボックス 1 件 = li.itemBox で構成されている
    # タイトル   → .contents__title
    # 還元率     → .contents__percent span （例 '1.2%'）
    # デバイス   → .iconList img[alt] の alt='pc' など
    # ──────────────────────────────
    for box in soup.select("li.itemBox"):
        title_tag = box.select_one(".contents__title")
        percent_tag = box.select_one(".contents__percent span")
        if not (title_tag and percent_tag):
            continue  # セレクタがマッチしない行はスキップ

        title = title_tag.get_text(strip=True)

        percent_text = percent_tag.get_text(strip=True)  # '1.2%'
        match = re.search(r"(\d+(?:\.\d+)?)", percent_text)
        reward_decimal = float(match.group(1)) if match else 0.0

        icons = box.select(".iconList img[alt]")
        devices = ",".join(
            ALT_MAP.get(img["alt"].strip().lower(), "")
            for img in icons
            if img.get("alt")
        ).strip(",")

        items.append(
            {
                "title": title,
                "reward_decimal": reward_decimal,
                "devices": devices,
            }
        )
    return items


if __name__ == "__main__":
    # 1) HTML を保存して自分のブラウザで構造確認できるように
    res = requests.get(URL, headers=HEADERS, timeout=15)
    with open("moppy.html", "w", encoding="utf-8") as f:
        f.write(res.text)
    print("HTML を moppy.html に保存しました -> open moppy.html で確認できます")
    print("status =", res.status_code, "| length =", len(res.text))

    # 2) スクレイプ結果の先頭 5 件を表示
    data = scrape_moppy()
    print(f"取得件数: {len(data)}")
    pprint(data[:5])
