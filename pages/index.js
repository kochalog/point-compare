import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';

/* ── デバイス表記ヘルパー ───────────────────────── */
const DEVICE_LABEL = { p: 'PC', s: 'iOS/Android', i: 'iOS', a: 'Android' };
const formatDevices = (raw) =>
  !raw
    ? 'PC/スマホ共通'
    : raw
        .split(',')
        .map((c) => DEVICE_LABEL[c.trim()] || c)
        .join(', ');
/* ─────────────────────────────────────────────── */

export default function Home() {
  /* 検索入力 & 結果 */
  const [kw, setKw] = useState('');
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(false);

  /* ポイントサイト一覧（検索用に保持するだけ） */
  const [sites, setSites] = useState([]);        // [{id,name},…]
  const [selected, setSelected] = useState([]);  // site_id[]

  /* 初回：サイト一覧フェッチ & 選択済みを localStorage から復元 */
  useEffect(() => {
    (async () => {
      const { data } = await supabase
        .from('point_sites')
        .select('id,name')
        .order('id');
      setSites(data || []);

      const saved = JSON.parse(localStorage.getItem('siteIds') || '[]');
      setSelected(saved.length ? saved : data?.map((s) => s.id) || []);
    })();
  }, []);

  /* 検索実行 */
  async function handleSearch(e) {
    e.preventDefault();
    const trimmed = kw.trim();
    if (!trimmed) return setOffers([]);

    setLoading(true);

    const words = trimmed.split(/\s+/);
    let query = supabase
      .from('offers')
      .select('id,title,reward_decimal,devices,point_sites(name)')
      .order('reward_decimal', { ascending: false });

    /* 選択サイトで絞り込み */
    if (selected.length) query = query.in('site_id', selected);

    /* AND 検索 */
    words.forEach((w) => (query = query.ilike('title', `%${w}%`)));

    const { data } = await query;
    setOffers(data || []);
    setLoading(false);
  }

  return (
    <main style={{ maxWidth: 800, margin: '40px auto', padding: 16 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>どこ得クローン</h1>
        <a href="/customize" style={{ color: '#0070f3', textDecoration: 'underline' }}>
          サイトカスタマイズ
        </a>
      </header>

      {/* ── 検索フォーム ── */}
      <form onSubmit={handleSearch} style={{ marginTop: 12 }}>
        <input
          value={kw}
          onChange={(e) => setKw(e.target.value)}
          placeholder="案件名（スペースで AND 検索）"
          style={{ width: '100%', padding: 8, border: '1px solid #ccc', borderRadius: 4 }}
        />
      </form>

      {loading && <p style={{ marginTop: 8 }}>検索中…</p>}

      {/* ── 結果テーブル ── */}
      {offers.length > 0 && (
        <table style={{ width: '100%', marginTop: 24, borderCollapse: 'collapse' }}>
          <thead style={{ background: '#f4f4f4' }}>
            <tr>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>案件</th>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>サイト</th>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>デバイス</th>
              <th style={{ border: '1px solid #ddd', padding: 8 }}>還元値</th>
            </tr>
          </thead>
          <tbody>
            {offers.map((o) => (
              <tr key={o.id}>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{o.title}</td>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{o.point_sites?.name}</td>
                <td style={{ border: '1px solid #ddd', padding: 8 }}>{formatDevices(o.devices)}</td>
                <td style={{ border: '1px solid #ddd', padding: 8, textAlign: 'right' }}>
                  {o.reward_decimal}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {offers.length === 0 && kw && !loading && (
        <p style={{ marginTop: 16 }}>該当する案件がありませんでした。</p>
      )}
    </main>
  );
}
