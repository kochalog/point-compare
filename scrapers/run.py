"""
scrapers/run.py  – すべてのスクレイパーを呼び出し Supabase に upsert
"""
import os, datetime
from supabase import create_client, Client

# === ここにスクレイパーを import ===
from scrapers.moppy import scrape_moppy        # ほかのサイトが出来たら追加
# from scrapers.hapitas import scrape_hapitas
# from scrapers.warau   import scrape_warau

SB_URL  = os.environ["SUPABASE_URL"]
SB_KEY  = os.environ["SUPABASE_SERVICE_KEY"]   # service_role キー
sb: Client = create_client(SB_URL, SB_KEY)

# point_sites.id をハードコード（例：モッピー=1）
SITE_IDS = {
    "moppy": 1,
    # "hapitas": 2,
    # "warau": 3,
}

def save(site_key: str, items: list[dict]):
    site_id = SITE_IDS[site_key]
    for it in items:
        sb.table("offers").upsert(
            {
                "site_id": site_id,
                "title": it["title"],
                "reward_decimal": it["reward_decimal"],
                "devices": it["devices"],
                "updated_at": datetime.datetime.utcnow().isoformat()
            },
            on_conflict="site_id,title"     # タイトル重複を更新
        ).execute()

def main():
    print("モッピー取得中 …")
    save("moppy", scrape_moppy())
    # print("ハピタス取得中 …")
    # save("hapitas", scrape_hapitas())
    # print("ワラウ取得中 …")
    # save("warau", scrape_warau())
    print("全サイト upsert 完了")

if __name__ == "__main__":
    main()
