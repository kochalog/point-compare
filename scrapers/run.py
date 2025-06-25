"""
run.py — 各スクレイパーを呼び出して Supabase に upsert（レスポンス可視化版）
2025-06-24
"""

# ─── .env を読み込む ─────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env", override=True)   # .env の値で既存 env を上書き
# ────────────────────────────────────────────────────────

import os, datetime
from supabase import create_client, Client

# =========== スクレイパー ================
from scrapers.moppy import scrape_moppy
# 追加サイトがあれば ↓ に import を増やす
# from scrapers.hapitas import scrape_hapitas
# =========================================

# ─── Supabase 接続 ───────────────────────
SB_URL = (os.getenv("SUPABASE_URL") or "").strip()
SB_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or "").strip()
if not SB_URL or not SB_KEY:
    raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_KEY が未設定です")
sb: Client = create_client(SB_URL, SB_KEY)
# ────────────────────────────────────────

# point_sites.id を固定（必要に応じて追加）
SITE_IDS = {
    "moppy": 1,
    # "hapitas": 2,
}

def save(site_key: str, items: list[dict]) -> None:
    """
    1 サイト分のアイテムを offers に upsert
    (site_id, title) を一意キーとして衝突時は更新
    Supabase のレスポンスを print してデバッグ
    """
    site_id = SITE_IDS[site_key]
    for it in items:
        resp = sb.table("offers").upsert(
            {
                "site_id": site_id,
                "title": it["title"],
                "reward_decimal": it["reward_decimal"],
                "devices": it["devices"],
                "updated_at": datetime.datetime.utcnow().isoformat(),
            },
            on_conflict="site_id,title",
        ).execute()
        # —— レスポンスを表示 ——
        print(f"UPSERT resp for {it['title'][:30]}… →", resp)

def main() -> None:
    print("モッピー取得中 …")
    save("moppy", scrape_moppy())
    print("全サイト upsert 完了")

if __name__ == "__main__":
    main()
