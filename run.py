"""
run.py — 各スクレイパーを呼び出して Supabase に upsert
2025-06-24  最終版（.env を override で読み込み）
"""

# ─── .env 読み込み ─────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env", override=True)   # 既存 env を .env で上書き
# ────────────────────────────────────────────────────────

import os, datetime
from supabase import create_client, Client

# =========== スクレイパー ================
from scrapers.moppy import scrape_moppy
# from scrapers.hapitas import scrape_hapitas
# from scrapers.warau   import scrape_warau
# =========================================

# ─── Supabase クレデンシャル ──────────────────────────────
SB_URL: str = (os.getenv("SUPABASE_URL") or "").strip()
SB_KEY: str = (os.getenv("SUPABASE_SERVICE_KEY") or "").strip()
if not SB_URL or not SB_KEY:
    raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_KEY が読み込めていません")
sb: Client = create_client(SB_URL, SB_KEY)
# ────────────────────────────────────────────────────────

# points_sites.id を固定（必要に応じて追加）
SITE_IDS = {
    "moppy": 1,
    # "hapitas": 2,
    # "warau":   3,
}

def save(site_key: str, items: list[dict]) -> None:
    """
    1 サイト分のスクレイプ結果を offers テーブルに upsert
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
                "updated_at": datetime.datetime.utcnow().isoformat(),
            },
            on_conflict="site_id,title",
        ).execute()

def main() -> None:
    print("モッピー取得中 …")
    save("moppy", scrape_moppy())

    # ↓ 追加サイトのスクレイパーを実装したらコメントアウトを外す
    # print("ハピタス取得中 …")
    # save("hapitas", scrape_hapitas())
    # print("ワラウ取得中 …")
    # save("warau", scrape_warau())

    print("全サイト upsert 完了")

if __name__ == "__main__":
    main()
