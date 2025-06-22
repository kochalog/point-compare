import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { supabase } from '../lib/supabaseClient';

export default function Customize() {
  const router = useRouter();
  const [sites, setSites] = useState([]);
  const [selected, setSelected] = useState([]);

  /* 初期化：DB からサイト一覧 → localStorage から選択済みを取得 */
  useEffect(() => {
    (async () => {
      const { data } = await supabase.from('point_sites').select('id,name').order('id');
      setSites(data || []);

      const saved = JSON.parse(localStorage.getItem('siteIds') || '[]');
      setSelected(saved.length ? saved : data?.map((s) => s.id) || []);
    })();
  }, []);

  /* チェックトグル */
  const toggle = (id, checked) =>
    setSelected((prev) =>
      checked ? [...prev, id] : prev.filter((i) => i !== id)
    );

  /* 保存してトップへ戻る */
  const handleSave = () => {
    localStorage.setItem('siteIds', JSON.stringify(selected));
    router.push('/');
  };

  return (
    <main style={{ maxWidth: 600, margin: '40px auto', padding: 16 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 12 }}>サイトカスタマイズ</h1>

      {sites.map((s) => (
        <label key={s.id} style={{ display: 'block', marginBottom: 8 }}>
          <input
            type="checkbox"
            checked={selected.includes(s.id)}
            onChange={(e) => toggle(s.id, e.target.checked)}
          />{' '}
          {s.name}
        </label>
      ))}

      <button
        onClick={handleSave}
        style={{
          marginTop: 16,
          padding: '8px 24px',
          background: '#0070f3',
          color: '#fff',
          border: 'none',
          borderRadius: 4,
          cursor: 'pointer',
        }}
      >
        保存する
      </button>
    </main>
  );
}
