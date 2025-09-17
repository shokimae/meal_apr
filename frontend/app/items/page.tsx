
'use client';

import { useEffect, useState } from 'react';
import { fetchJSON } from '@/lib/api';

type Item = { id: string; name: string; warning?: string };

export default function ItemsPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      setError(null);
      const data = await fetchJSON<Item[]>('/api/items');
      setItems(data);
    } catch (e: any) {
      setError(e.message);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      setLoading(true);
      const created = await fetchJSON<Item>('/api/items', {
        method: 'POST',
        body: JSON.stringify({ name }),
      });
      setName('');
      await load();
      alert(created.warning ? `Saved (fallback): ${created.name}` : `Saved: ${created.name}`);
    } catch (e: any) {
      alert(`Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ fontSize: 20, fontWeight: 700 }}>Items</h2>

      <form onSubmit={onAdd} style={{ marginTop: 12, display: 'flex', gap: 8 }}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Item name"
          style={{ padding: 8, border: '1px solid #ccc', borderRadius: 6 }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #333', background: '#fff' }}
        >
          {loading ? 'Saving…' : 'Add'}
        </button>
      </form>

      {error && <p style={{ color: 'crimson' }}>Error: {error}</p>}

      <ul style={{ marginTop: 16 }}>
        {items.map((it) => (
          <li key={it.id}>
            {it.name} {it.warning ? <em style={{ color: '#a60' }}>(fallback)</em> : null}
          </li>
        ))}
      </ul>
    </div>
  );
}
