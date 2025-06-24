import re, requests
from bs4 import BeautifulSoup

URL = "https://pc.moppy.jp/shopping/?keyword=楽天市場"

def scrape_moppy():
    res = requests.get(URL, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    items = []
    for box in soup.select(".itemBox"):          # ボックス1件
        title = box.select_one(".contents__title").get_text(strip=True)

        percent = box.select_one(".contents__percent span").get_text(strip=True)
        reward_decimal = float(re.sub(r"[%％]", "", percent))  # "1.2%" → 1.2

        # デバイス判定（例: alt="pc" alt="sp"）
        icons = box.select(".iconList img[alt]")
        devices = ",".join({
            "pc": "p", "sp": "s", "ios": "i", "android": "a"
        }.get(i["alt"].lower(), "") for i in icons if i["alt"])

        items.append({
            "title": title,
            "reward_decimal": reward_decimal,
            "devices": devices or ""
        })
    return items

if __name__ == "__main__":
    from pprint import pprint
    pprint(scrape_moppy()[:3])
