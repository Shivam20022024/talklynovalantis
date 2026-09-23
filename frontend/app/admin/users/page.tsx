'use client';

import { useEffect, useState, useCallback } from 'react';
import { Loader2 } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import { fetchApi } from '@/lib/api';

export default function AdminUsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState('');
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetchApi('/api/v1/admin/users');
      setUsers(r.data || []);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const toggleActive = async (u: any) => {
    setBusy(u.user_id);
    try {
      await fetchApi(`/api/v1/admin/users/${u.user_id}`, {
        method: 'PATCH',
        body: JSON.stringify({ is_active: !(u.is_active !== false) }),
      });
      await load();
    } catch (e: any) {
      alert(e.message || 'Failed');
    } finally {
      setBusy(null);
    }
  };

  const visible = users.filter(
    (u) =>
      (u.name || '').toLowerCase().includes(q.toLowerCase()) ||
      (u.email || '').toLowerCase().includes(q.toLowerCase()) ||
      (u.company_name || '').toLowerCase().includes(q.toLowerCase()),
  );

  return (
    <AppLayout title="Users">
      <section>
        <p className="eyebrow text-primary">Platform / Users</p>
        <h1 className="mt-2 text-3xl font-bold tracking-[-0.06em]">All Users</h1>
        <p className="mt-1 text-sm text-muted-foreground">Every user across all companies.</p>
      </section>

      <section className="rounded-xl border border-border bg-card p-5">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search name, email, company"
          className="h-9 w-full max-w-xs rounded-lg border border-primary/30 bg-background px-3 text-xs outline-none focus:ring-2 focus:ring-primary/40"
        />
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs font-bold uppercase tracking-wider text-muted-foreground">
                <th className="px-3 py-2">Name</th>
                <th className="px-3 py-2">Email</th>
                <th className="px-3 py-2">Company</th>
                <th className="px-3 py-2">Role</th>
                <th className="px-3 py-2">Active</th>
                <th className="px-3 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {loading ? (
                <tr><td colSpan={6} className="py-10 text-center text-muted-foreground">Loading…</td></tr>
              ) : (
                visible.map((u) => (
                  <tr key={u.user_id} className="hover:bg-muted/30">
                    <td className="px-3 py-2 font-semibold">{u.name}</td>
                    <td className="px-3 py-2 text-muted-foreground">{u.email}</td>
                    <td className="px-3 py-2">{u.company_name || (u.role === 'super_admin' ? '— platform —' : '—')}</td>
                    <td className="px-3 py-2">
                      <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ${u.role === 'super_admin' ? 'bg-primary/10 text-primary' : 'bg-muted text-foreground'}`}>{u.role}</span>
                    </td>
                    <td className="px-3 py-2">{u.is_active === false ? 'No' : 'Yes'}</td>
                    <td className="px-3 py-2 text-right">
                      {u.role !== 'super_admin' && (
                        <button onClick={() => toggleActive(u)} disabled={busy === u.user_id} className="rounded-md border border-border px-3 py-1.5 text-xs font-semibold hover:bg-muted disabled:opacity-50">
                          {busy === u.user_id ? <Loader2 size={13} className="animate-spin" /> : u.is_active === false ? 'Activate' : 'Deactivate'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </AppLayout>
  );
}
