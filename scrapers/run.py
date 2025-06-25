"""
run.py — 各スクレイパーを呼び出し Supabase に upsert（JST 書き込み）
2025-06-25
"""

# ── .env を読み込む ──────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(".env", override=True)          # .env の値で既存 env を上書き
# ───────────────────────────────────────────────────────

import os, datetime, zoneinfo
from supabase import create_client, Client

# ========== スクレイパー ========== #
from scrapers.moppy import scrape_moppy
# from scrapers.hapitas import scrape_hapitas
# from scrapers.warau   import scrape_warau
# ================================== #

# ── Supabase 接続 ───────────────────────────────────────
SB_URL = (os.getenv("SUPABASE_URL") or "").strip()
SB_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or "").strip()
if not SB_URL or not SB_KEY:
    raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_KEY が未設定です")
sb: Client = create_client(SB_URL, SB_KEY)
# ───────────────────────────────────────────────────────

# JST タイムゾーン
JST = zoneinfo.ZoneInfo("Asia/Tokyo")

# point_sites.id を固定（必要に応じて追加）
SITE_IDS = {
    "moppy": 1,
    # "hapitas": 2,
    # "warau":   3,
}

def save(site_key: str, items: list[dict]) -> None:
    """
    1 サイト分のアイテムを offers に upsert
    (site_id, title) を一意キーとして衝突時は更新
    """
    site_id = SITE_IDS[site_key]
    for it in items:
        sb.table("offers").upsert(
            {
                "site_id": site_id,
                "title": it["title"],
                "reward_decimal": it["reward_decimal"],
                "devices": it["devices"],
                # JST で書き込む
                "updated_at": datetime.datetime.now(JST).isoformat(),
            },
            on_conflict="site_id,title",
        ).execute()

def main() -> None:
    print("モッピー取得中 …")
    save("moppy", scrape_moppy())

    # 追加サイトができたらコメントアウトを外す
    # print("ハピタス取得中 …")
    # save("hapitas", scrape_hapitas())
    # print("ワラウ取得中 …")
    # save("warau", scrape_warau())

    print("全サイト upsert 完了")

if __name__ == "__main__":
    main()
