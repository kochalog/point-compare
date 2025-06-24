"""
run.py – 各スクレイパーを呼び出し Supabase に upsert
2025/06/24  修正版（.env を確実に読み込む）
"""
from dotenv import load_dotenv          # ← ① 追加
load_dotenv(dotenv_path=".env")         # ← ② .env を読む

import os, datetime
from supabase import create_client, Client
from scrapers.moppy import scrape_moppy

# ── .env の値を取得（strip で改行・空白を除去） ──
SB_URL = (os.getenv("SUPABASE_URL") or "").strip()
SB_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or "").strip()

# デバッグで中身を確認（動いたら削除してOK）
print("DEBUG_SB_URL :", SB_URL)
print("DEBUG_SB_KEY :", SB_KEY[:20] + "…")

if not SB_URL or not SB_KEY:
    raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_KEY が読み込めていません")

sb: Client = create_client(SB_URL, SB_KEY)

SITE_IDS = { "moppy": 1 }

def save(site_key: str, items: list[dict]):
    for it in items:
        sb.table("offers").upsert(
            {
                "site_id": SITE_IDS[site_key],
                "title": it["title"],
                "reward_decimal": it["reward_decimal"],
                "devices": it["devices"],
                "updated_at": datetime.datetime.utcnow().isoformat(),
            },
            on_conflict="site_id,title",
        ).execute()

def main():
    print("モッピー取得中 …")
    save("moppy", scrape_moppy())
    print("全サイト upsert 完了")

if __name__ == "__main__":
    main()
