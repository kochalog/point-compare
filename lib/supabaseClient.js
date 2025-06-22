import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

// — デバッグ用: ブラウザコンソールから supabase を呼び出せるように —
if (typeof window !== 'undefined') {
  window.supabase = supabase;
}
