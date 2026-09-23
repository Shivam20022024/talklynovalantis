'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Building2, Loader2 } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import { fetchApi } from '@/lib/api';
import { useAuth } from '@/components/providers/AuthProvider';

export default function AdminCompaniesPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [busy, setBusy] = useState<string | null>(null);
  const router = useRouter();
  const { setCompanyContext } = useAuth();

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetchApi(`/api/v1/admin/companies?limit=200${query ? `&search=${encodeURIComponent(query)}` : ''}`);
      setCompanies(r.data || []);
    } finally {
      setLoading(false);
    }
  }, [query]);

  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [load]);

  const toggleStatus = async (c: any) => {
    setBusy(c.company_id);
    try {
      const action = c.status === 'ACTIVE' ? 'deactivate' : 'activate';
      await fetchApi(`/api/v1/admin/companies/${c.company_id}/${action}`, { method: 'POST' });
      await load();
    } catch (e: any) {
      alert(e.message || 'Failed');
    } finally {
      setBusy(null);
    }
  };

  const view = (c: any) => {
    setCompanyContext({ id: c.company_id, name: c.name });
    router.push(`/admin/companies/${c.company_id}`);
  };

  return (
    <AppLayout title="Companies">
      <section className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
        <div>
          <p className="eyebrow text-primary">Platform / Companies</p>
          <h1 className="mt-2 text-3xl font-bold tracking-[-0.06em] sm:text-[34px]">Company Management</h1>
          <p className="mt-2 text-sm text-muted-foreground">Search, inspect, and activate/deactivate tenant companies.</p>
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card p-5">
        <div className="relative w-full max-w-xs">
          <Search className="absolute left-3 top-2.5 text-primary" size={14} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search companies"
            className="h-9 w-full rounded-lg border border-primary/30 bg-background pl-9 pr-3 text-xs outline-none focus:ring-2 focus:ring-primary/40"
          />
        </div>

        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[820px] text-left">
            <thead>
              <tr className="border-b border-border h-12 text-xs font-bold uppercase tracking-wider text-foreground">
                <th className="px-3">Company</th>
                <th className="px-3 text-center">Users</th>
                <th className="px-3 text-center">Calls</th>
                <th className="px-3 text-center">Leads</th>
                <th className="px-3">Bolna agent</th>
                <th className="px-3">Status</th>
                <th className="px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {loading ? (
                <tr><td colSpan={7} className="py-10 text-center text-sm text-muted-foreground">Loading…</td></tr>
              ) : companies.length === 0 ? (
                <tr><td colSpan={7} className="py-10 text-center text-sm text-muted-foreground">No companies found.</td></tr>
              ) : (
                companies.map((c) => (
                  <tr key={c.company_id} className="h-14 hover:bg-muted/30">
                    <td className="px-3">
                      <button onClick={() => view(c)} className="flex items-center gap-2 text-sm font-bold text-foreground hover:text-primary">
                        <Building2 size={15} className="text-muted-foreground" />
                        {c.name}
                      </button>
                    </td>
                    <td className="px-3 text-center text-sm">{c.stats?.users ?? 0}</td>
                    <td className="px-3 text-center text-sm">{c.stats?.calls ?? 0}</td>
                    <td className="px-3 text-center text-sm">{c.stats?.leads ?? 0}</td>
                    <td className="px-3 text-xs font-mono text-muted-foreground">
                      {c.bolna_agent_id ? `${String(c.bolna_agent_id).slice(0, 10)}…` : <span className="text-amber-600">not set</span>}
                    </td>
                    <td className="px-3">
                      <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-bold ${c.status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-700'}`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${c.status === 'ACTIVE' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                        {c.status}
                      </span>
                    </td>
                    <td className="px-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => view(c)} className="rounded-md bg-primary px-3 py-1.5 text-xs font-semibold text-primary-foreground hover:opacity-90">View</button>
                        <button onClick={() => toggleStatus(c)} disabled={busy === c.company_id} className="rounded-md border border-border px-3 py-1.5 text-xs font-semibold hover:bg-muted disabled:opacity-50">
                          {busy === c.company_id ? <Loader2 size={13} className="animate-spin" /> : c.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}
                        </button>
                      </div>
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
