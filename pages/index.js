import { useState } from 'react';
import { supabase } from '../lib/supabaseClient';

// ===== デバイス表示のヘルパー =====
const DEVICE_LABEL = {
  p: 'PC',
  s: 'iOS/Android',
  i: 'iOS',
  a: 'Android',
};
function formatDevices(raw) {
  if (!raw) return 'PC/スマホ共通';
  return raw
    .split(',')
    .map((c) => DEVICE_LABEL[c.trim()] || c)
    .join(', ');
}
// ==================================

export default function Home() {
  const [kw, setKw] = useState('');
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleSearch(e) {
    e.preventDefault();
    const trimmed = kw.trim();
    if (!trimmed) return setOffers([]);

    setLoading(true);

    const words = trimmed.split(/\s+/);
    let query = supabase
      .from('offers')
      .select('id,title,reward_decimal,devices,point_sites(name)') // ← devices 追加
      .order('reward_decimal', { ascending: false });

    words.forEach((w) => {
      query = query.ilike('title', `%${w}%`);
    });

    const { data, error } = await query;
    if (!error) setOffers(data);
    setLoading(false);
  }

  return (
    <main style={{ maxWidth: 800, margin: '40px auto', padding: '0 16px' }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 16 }}>
        どこ得クローン MVP①
      </h1>

      <form onSubmit={handleSearch}>
        <input
          value={kw}
          onChange={(e) => setKw(e.target.value)}
          placeholder="案件名を入力（スペースで AND 検索）"
          style={{ width: '100%', padding: 8, border: '1px solid #ccc', borderRadius: 4 }}
        />
      </form>

      {loading && <p>検索中...</p>}

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
    </main>
  );
}
