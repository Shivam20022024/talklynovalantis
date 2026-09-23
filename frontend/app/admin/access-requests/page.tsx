'use client';

import { useEffect, useState, useCallback } from 'react';
import { Loader2, Check, X } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import { fetchApi } from '@/lib/api';

const STATUSES = ['PENDING', 'APPROVED', 'REJECTED', 'ALL'];

export default function AccessRequestsPage() {
  const [items, setItems] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [status, setStatus] = useState('PENDING');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [list, s] = await Promise.all([
        fetchApi(`/api/v1/admin/access-requests?status=${status}&limit=100`),
        fetchApi('/api/v1/admin/access-requests/stats').catch(() => null),
      ]);
      setItems(list.items || []);
      setStats(s);
    } finally {
      setLoading(false);
    }
  }, [status]);

  useEffect(() => { load(); }, [load]);

  const act = async (id: string, kind: 'approve' | 'reject') => {
    if (kind === 'reject' && !confirm('Reject this request?')) return;
    setBusy(id);
    try {
      await fetchApi(`/api/v1/admin/access-requests/${id}/${kind}`, {
        method: 'POST',
        body: kind === 'reject' ? JSON.stringify({ reason: 'Not approved' }) : undefined,
      });
      await load();
    } catch (e: any) {
      alert(e.message || 'Failed');
    } finally {
      setBusy(null);
    }
  };

  return (
    <AppLayout title="Access Requests">
      <section>
        <p className="eyebrow text-primary">Platform / Access Requests</p>
        <h1 className="mt-2 text-3xl font-bold tracking-[-0.06em]">Company Access Requests</h1>
        <p className="mt-1 text-sm text-muted-foreground">Approve a request to provision a company + its admin login.</p>
      </section>

      {stats && (
        <section className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {[['Pending', stats.pending], ['Approved', stats.approved], ['Rejected', stats.rejected], ['Companies', stats.total_companies]].map(([l, v]) => (
            <div key={l as string} className="rounded-xl border border-border bg-card p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{l}</p>
              <p className="mt-1 text-2xl font-bold">{v as number}</p>
            </div>
          ))}
        </section>
      )}

      <div className="flex gap-1 rounded-lg bg-muted p-1 w-fit">
        {STATUSES.map((s) => (
          <button key={s} onClick={() => setStatus(s)} className={`rounded-md px-3 py-1.5 text-xs font-bold ${status === s ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`}>{s}</button>
        ))}
      </div>

      <section className="overflow-x-auto rounded-xl border border-border bg-card">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead>
            <tr className="border-b border-border text-xs font-bold uppercase tracking-wider text-muted-foreground">
              <th className="px-3 py-2">Company</th>
              <th className="px-3 py-2">Contact</th>
              <th className="px-3 py-2">Email</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {loading ? (
              <tr><td colSpan={5} className="py-10 text-center text-muted-foreground">Loading…</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={5} className="py-10 text-center text-muted-foreground">No requests.</td></tr>
            ) : (
              items.map((r, i) => (
                <tr key={r.id || r._id || i} className="hover:bg-muted/30">
                  <td className="px-3 py-2 font-semibold">{r.company_name}</td>
                  <td className="px-3 py-2">{r.contact_name || '—'}</td>
                  <td className="px-3 py-2 text-muted-foreground">{r.email}</td>
                  <td className="px-3 py-2">{r.status}</td>
                  <td className="px-3 py-2 text-right">
                    {r.status === 'PENDING' && (
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => act(r.id, 'approve')} disabled={busy === r.id} className="flex items-center gap-1 rounded-md bg-primary px-3 py-1.5 text-xs font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-50">
                          {busy === r.id ? <Loader2 size={13} className="animate-spin" /> : <Check size={13} />}Approve
                        </button>
                        <button onClick={() => act(r.id, 'reject')} disabled={busy === r.id} className="flex items-center gap-1 rounded-md border border-border px-3 py-1.5 text-xs font-semibold hover:bg-muted disabled:opacity-50">
                          <X size={13} />Reject
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>
    </AppLayout>
  );
}
