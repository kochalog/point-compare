"""
run.py – 各スクレイパーを呼び出し Supabase に upsert
.env を先に読み込み、SUPABASE_URL / SERVICE_KEY を確実に取得する版
"""

from dotenv import load_dotenv           # ← ❶ 追加
load_dotenv(dotenv_path=".env")          # ← ❷ .env を読む

import os, datetime
from supabase import create_client, Client

# ===== スクレイパー =====
from scrapers.moppy import scrape_moppy
# from scrapers.hapitas import scrape_hapitas
# from scrapers.warau   import scrape_warau
# ========================

# --- 環境変数を取得（strip で余分な空白を除去） ---
SB_URL = (os.getenv("SUPABASE_URL") or "").strip()
SB_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or "").strip()

if not SB_URL or not SB_KEY:
    raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_KEY が読み込めていません")

# デバッグ表示（問題解決後は削除可）
print("DEBUG_SB_URL :", SB_URL)
print("DEBUG_SB_KEY :", SB_KEY[:20] + "…")

sb: Client = create_client(SB_URL, SB_KEY)

SITE_IDS = { "moppy": 1 }  # ハードコード例

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
