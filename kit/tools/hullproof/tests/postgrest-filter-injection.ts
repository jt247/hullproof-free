import { createClient } from '@supabase/supabase-js';
declare const supabase: any; declare const q: string; declare const col: string; declare const dir: string;

export async function bad(search: string) {
  // ruleid: hullproof-postgrest-filter-string, hullproof-postgrest-interpolated-filter
  await supabase.from('items').select('id').or(`name.ilike.%${search}%,description.ilike.%${search}%`);
  // ruleid: hullproof-postgrest-filter-string, hullproof-postgrest-interpolated-filter
  await supabase.from('items').select('id').or("name.eq." + search);
  // ruleid: hullproof-postgrest-filter-string
  await supabase.from('items').select('id').or(q);
  // ruleid: hullproof-postgrest-filter-string
  await supabase.from('items').select('id').filter(col, 'eq', search);
  // ruleid: hullproof-postgrest-filter-string
  await supabase.from('items').select('id').order(col, { ascending: dir === 'asc' });
  // ruleid: hullproof-postgrest-filter-string
  await supabase.from('items').select('id').eq(col, search);
  // ruleid: hullproof-postgrest-filter-string, hullproof-postgrest-interpolated-filter
  await supabase.from('items').select(`id,${col}`);
}

export async function good(search: string) {
  // ok: hullproof-postgrest-filter-string, hullproof-postgrest-interpolated-filter
  await supabase.from('items').select('id').or('status.eq.active,status.eq.pending');
  // ok: hullproof-postgrest-filter-string, hullproof-postgrest-interpolated-filter
  await supabase.from('items').select('id').ilike('name', `%${search}%`);
  // ok: hullproof-postgrest-filter-string, hullproof-postgrest-interpolated-filter
  await supabase.from('items').select('id').eq('owner_id', search);
  // ok: hullproof-postgrest-filter-string, hullproof-postgrest-interpolated-filter
  await supabase.from('items').select('id').order('created_at', { ascending: false });
  // ok: hullproof-postgrest-filter-string, hullproof-postgrest-interpolated-filter
  await supabase.from('items').select('id').in('id', [search]);
  // ok: hullproof-postgrest-filter-string, hullproof-postgrest-interpolated-filter
  await supabase.from('items').select('id').or([{ a: 1 }]);
}

declare const z: any;
export const schema = {
  // ok: hullproof-postgrest-filter-string, hullproof-postgrest-interpolated-filter
  social: z.string().url().or(z.literal('')),
};
