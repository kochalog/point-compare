import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';

/* ── デバイス表記ヘルパー ───────────────────────── */
const DEVICE_LABEL = { p: 'PC', s: 'iOS/Android', i: 'iOS', a: 'Android' };
function formatDevices(raw) {
  if (!raw) return 'PC/スマホ共通';
  return raw
    .split(',')
    .map((c) => DEVICE_LABEL[c.trim()] || c)
    .join(', ');
}
/* ─────────────────────────────────────────────── */

export default function Home() {
  /* 検索フォーム用 state */
  const [kw, setKw] = useState('');
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(false);

  /* ★ ポイントサイト選択用 state ★ */
  const [sites, setSites] = useState([]);       // 取得したサイト一覧 [{id,name},…]
  const [selected, setSelected] = useState([]); // チェックが入った site_id 配列

  /* ── 初回マウント時：ポイントサイト一覧を取得 ── */
  useEffect(() => {
    (async () => {
      const { data } = await supabase
        .from('point_sites')
        .select('id,name')
        .order('id');
      setSites(data || []);
      setSelected(data?.map((s) => s.id) || []); // 初期状態は “全選択”
    })();
  }, []);

  /* ── 検索実行 ── */
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

    /* ★ サイト ID で絞り込み ★ */
    if (selected.length) query = query.in('site_id', selected);

    /* AND 検索 */
    words.forEach((w) => (query = query.ilike('title', `%${w}%`)));

    const { data, error } = await query;
    if (!error) setOffers(data);
    setLoading(false);
  }

  return (
    <main style={{ maxWidth: 800, margin: '40px auto', padding: 16 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 12 }}>どこ得クローン</h1>

      {/* ── ポイントサイト選択 ── */}
      <div style={{ marginBottom: 12 }}>
        {sites.map((s) => (
          <label key={s.id} style={{ marginRight: 12 }}>
            <input
              type="checkbox"
              checked={selected.includes(s.id)}
              onChange={(e) =>
                setSelected((prev) =>
                  e.target.checked
                    ? [...prev, s.id]                  // ✅ 追加
                    : prev.filter((id) => id !== s.id) // ⛔ 除外
                )
              }
            />{' '}
            {s.name}
          </label>
        ))}
      </div>

      {/* ── 検索フォーム ── */}
      <form onSubmit={handleSearch}>
        <input
          value={kw}
          onChange={(e) => setKw(e.target.value)}
          placeholder="案件名（スペースで AND 検索）"
          style={{
            width: '100%',
            padding: 8,
            border: '1px solid #ccc',
            borderRadius: 4,
          }}
        />
      </form>

      {loading && <p>検索中…</p>}

      {/* ── 検索結果テーブル ── */}
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
                <td style={{ border: '1px solid #ddd', padding: 8 }}>
                  {formatDevices(o.devices)}
                </td>
                <td style={{ border: '1px solid #ddd', padding: 8, textAlign: 'right' }}>
                  {o.reward_decimal}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
