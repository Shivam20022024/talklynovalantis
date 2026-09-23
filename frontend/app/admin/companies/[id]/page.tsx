'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { Loader2, Save } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import { MetricCard } from '@/components/ui/MetricCard';
import { Phone, Users, Target, Sparkles } from 'lucide-react';
import { fetchApi } from '@/lib/api';
import { useAuth } from '@/components/providers/AuthProvider';

const TABS = ['Overview', 'Users', 'Calls', 'Campaigns', 'Leads', 'Analytics', 'Billing', 'Prompt'] as const;
type Tab = (typeof TABS)[number];

export default function AdminCompanyDetail() {
  const params = useParams();
  const companyId = params.id as string;
  const { setCompanyContext } = useAuth();

  const [company, setCompany] = useState<any>(null);
  const [tab, setTab] = useState<Tab>('Overview');
  const [tabData, setTabData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [agentDraft, setAgentDraft] = useState('');
  const [savingAgent, setSavingAgent] = useState(false);

  useEffect(() => {
    fetchApi(`/api/v1/admin/companies/${companyId}`)
      .then((r) => {
        setCompany(r.data);
        setAgentDraft(r.data?.bolna_agent_id || '');
        setCompanyContext({ id: companyId, name: r.data?.name || 'Company' });
      })
      .catch(() => {});
  }, [companyId, setCompanyContext]);

  const endpointFor = (t: Tab): string | null => {
    switch (t) {
      case 'Overview': return `/api/v1/admin/companies/${companyId}/overview`;
      case 'Users': return `/api/v1/admin/companies/${companyId}/users`;
      case 'Calls': return `/api/v1/admin/companies/${companyId}/calls`;
      case 'Campaigns': return `/api/v1/admin/companies/${companyId}/campaigns`;
      case 'Leads': return `/api/v1/admin/companies/${companyId}/leads`;
      case 'Analytics': return `/api/v1/admin/companies/${companyId}/analytics`;
      case 'Billing': return `/api/v1/admin/companies/${companyId}/billing`;
      case 'Prompt': return `/api/v1/admin/companies/${companyId}/prompt`;
    }
  };

  const loadTab = useCallback(async (t: Tab) => {
    setLoading(true);
    setTabData(null);
    try {
      const ep = endpointFor(t);
      if (ep) {
        const r = await fetchApi(ep);
        setTabData(r.data);
      }
    } finally {
      setLoading(false);
    }
  }, [companyId]);

  useEffect(() => { loadTab(tab); }, [tab, loadTab]);

  const saveAgent = async () => {
    setSavingAgent(true);
    try {
      await fetchApi(`/api/v1/admin/companies/${companyId}`, {
        method: 'PATCH',
        body: JSON.stringify({ bolna_agent_id: agentDraft || null }),
      });
      setCompany((c: any) => ({ ...c, bolna_agent_id: agentDraft }));
      alert('Saved');
    } catch (e: any) {
      alert(e.message || 'Failed');
    } finally {
      setSavingAgent(false);
    }
  };

  return (
    <AppLayout title={company?.name || 'Company'}>
      <section>
        <p className="eyebrow text-primary">Platform / Companies / {company?.name || '…'}</p>
        <h1 className="mt-2 text-3xl font-bold tracking-[-0.06em]">{company?.name || 'Company'}</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Status: <span className="font-semibold">{company?.status}</span> · ID <span className="font-mono text-xs">{companyId}</span>
        </p>
      </section>

      <section className="rounded-xl border border-border bg-card p-4">
        <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Dedicated Bolna agent ID</label>
        <div className="mt-2 flex gap-2">
          <input
            value={agentDraft}
            onChange={(e) => setAgentDraft(e.target.value)}
            placeholder="bolna agent id for this company"
            className="flex-1 rounded-lg border border-border bg-background px-3 py-2 font-mono text-sm outline-none focus:border-primary"
          />
          <button onClick={saveAgent} disabled={savingAgent} className="flex items-center gap-2 rounded-lg bg-primary px-3.5 py-2 text-xs font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-50">
            {savingAgent ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}Save
          </button>
        </div>
      </section>

      <div className="flex flex-wrap gap-1 border-b border-border">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-3 py-2 text-sm font-semibold transition-colors ${tab === t ? 'border-b-2 border-primary text-primary' : 'text-muted-foreground hover:text-foreground'}`}
          >
            {t}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex h-[240px] items-center justify-center text-muted-foreground"><Loader2 className="animate-spin" /></div>
      ) : (
        <TabContent tab={tab} data={tabData} />
      )}
    </AppLayout>
  );
}

function TabContent({ tab, data }: { tab: Tab; data: any }) {
  if (!data) return <p className="text-sm text-muted-foreground">No data.</p>;

  if (tab === 'Overview') {
    return (
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <MetricCard label="Total calls" value={String(data.total_calls ?? 0)} change="" Icon={Phone} tone="violet" />
        <MetricCard label="Inbound calls" value={String(data.inbound_calls ?? 0)} change="" Icon={Phone} tone="blue" />
        <MetricCard label="Outbound calls" value={String(data.outbound_calls ?? 0)} change="" Icon={Phone} tone="green" />
        <MetricCard label="Total leads" value={String(data.total_leads ?? 0)} change="" Icon={Users} tone="blue" />
        <MetricCard label="Hot leads" value={String(data.hot_leads ?? 0)} change="" Icon={Sparkles} tone="orange" />
        <MetricCard label="Total spend (₹)" value={String(data.total_spending ?? 0)} change="" Icon={Target} tone="green" />
      </section>
    );
  }

  if (tab === 'Analytics') {
    return (
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <MetricCard label="Total leads" value={String(data.total_leads ?? 0)} change="" Icon={Users} tone="blue" />
        <MetricCard label="Calls made" value={String(data.calls_made ?? 0)} change="" Icon={Phone} tone="violet" />
        <MetricCard label="Connected" value={String(data.connected_calls ?? 0)} change="" Icon={Phone} tone="green" />
        <MetricCard label="Qualified" value={String(data.qualified_leads ?? 0)} change="" Icon={Target} tone="orange" />
        <MetricCard label="Converted" value={String(data.converted_leads ?? 0)} change="" Icon={Sparkles} tone="green" />
        <MetricCard label="Conversion rate" value={String(data.conversion_rate ?? '0%')} change="" Icon={Target} tone="blue" />
      </section>
    );
  }

  if (tab === 'Billing') {
    return (
      <div className="space-y-4">
        <section className="grid gap-3 sm:grid-cols-3">
          <MetricCard label="Wallet balance" value={String(data.wallet?.balance ?? 0)} change="" Icon={Target} tone="green" />
          <MetricCard label="Minutes used" value={String(data.wallet?.minutes_used ?? 0)} change="" Icon={Phone} tone="violet" />
          <MetricCard label="Total spending" value={String(data.wallet?.total_spending ?? 0)} change="" Icon={Sparkles} tone="orange" />
        </section>
        <SimpleTable rows={data.usage || []} columns={['created_at', 'service_type', 'billed_minutes', 'customer_cost']} />
      </div>
    );
  }

  if (tab === 'Prompt') {
    return (
      <div className="space-y-4">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Status: {data.prompt_status}</p>
        <pre className="whitespace-pre-wrap rounded-xl border border-border bg-card p-4 text-sm">{data.prompt || '(no prompt)'}</pre>
      </div>
    );
  }

  const rows = Array.isArray(data) ? data : [];
  const columns =
    tab === 'Users' ? ['name', 'email', 'role', 'is_active']
    : tab === 'Calls' ? ['call_id', 'customer_name', 'direction', 'status', 'created_at']
    : tab === 'Campaigns' ? ['name', 'status', 'leads_count', 'calls_made', 'created_at']
    : ['name', 'phone', 'status', 'aiScore', 'created_at'];
  return <SimpleTable rows={rows} columns={columns} />;
}

function SimpleTable({ rows, columns }: { rows: any[]; columns: string[] }) {
  if (!rows.length) return <p className="text-sm text-muted-foreground">Nothing to show.</p>;
  return (
    <div className="overflow-x-auto rounded-xl border border-border bg-card">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead>
          <tr className="border-b border-border text-xs font-bold uppercase tracking-wider text-muted-foreground">
            {columns.map((c) => <th key={c} className="px-3 py-2">{c.replace(/_/g, ' ')}</th>)}
          </tr>
        </thead>
        <tbody className="divide-y divide-border/50">
          {rows.map((r, i) => (
            <tr key={i} className="hover:bg-muted/30">
              {columns.map((c) => (
                <td key={c} className="px-3 py-2">
                  {typeof r[c] === 'boolean' ? (r[c] ? 'Yes' : 'No') : String(r[c] ?? '—')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
