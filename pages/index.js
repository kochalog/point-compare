export default function Home() {
  return <h1>Next.js Starter — OK!</h1>;
}

// 変換マップ
const DEVICE_LABEL = {
  p: 'PC',
  s: 'iOS/Android',
  i: 'iOS',
  a: 'Android',
};

// "p,s" → "PC, iOS/Android"
function formatDevices(raw) {
  if (!raw) return 'PC/スマホ共通';
  return raw
    .split(',')
    .map((c) => DEVICE_LABEL[c.trim()] || c)
    .join(', ');
}
