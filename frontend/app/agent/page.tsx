'use client';

import { useEffect, useState } from 'react';
import { Save, Loader2, Bot } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import { fetchApi } from '@/lib/api';

export default function AgentPage() {
  const [agentId, setAgentId] = useState('');
  const [mappings, setMappings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchApi('/api/v1/agent')
      .then((r) => {
        setAgentId(r.data?.bolna_agent_id || '');
        setMappings(r.data?.language_mappings || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      await fetchApi('/api/v1/agent', {
        method: 'PUT',
        body: JSON.stringify({
          bolna_agent_id: agentId || null,
          language_mappings: mappings.map((m) => ({
            language: m.language,
            bolna_agent_id: m.bolna_agent_id,
            status: m.status || 'Supported',
          })),
        }),
      });
      alert('Saved.');
    } catch (e: any) {
      alert(e.message || 'Failed');
    } finally {
      setSaving(false);
    }
  };

  const updateMapping = (i: number, field: string, value: string) => {
    setMappings((ms) => ms.map((m, idx) => (idx === i ? { ...m, [field]: value } : m)));
  };

  return (
    <AppLayout title="Agent">
      <section className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
        <div>
          <p className="eyebrow text-primary">Workspace / Agent</p>
          <h1 className="mt-2 text-3xl font-bold tracking-[-0.06em]">Voice Agent</h1>
          <p className="mt-2 text-sm text-muted-foreground">Your company&apos;s dedicated Bolna agent. Calls always use this agent — never a shared one.</p>
        </div>
        <button onClick={save} disabled={saving} className="flex items-center gap-2 rounded-lg bg-primary px-3.5 py-2.5 text-xs font-semibold text-primary-foreground shadow-lg shadow-primary/20 hover:opacity-90 disabled:opacity-50">
          {saving ? <Loader2 size={15} className="animate-spin" /> : <Save size={15} />}Save
        </button>
      </section>

      {loading ? (
        <div className="flex h-[200px] items-center justify-center text-muted-foreground"><Loader2 className="animate-spin" /></div>
      ) : (
        <>
          <section className="rounded-xl border border-border bg-card p-5">
            <div className="flex items-center gap-2">
              <Bot size={16} className="text-primary" />
              <h2 className="text-lg font-bold">Default agent ID</h2>
            </div>
            <input
              value={agentId}
              onChange={(e) => setAgentId(e.target.value)}
              placeholder="Bolna agent id"
              className="mt-3 w-full rounded-lg border border-border bg-background px-3 py-2 font-mono text-sm outline-none focus:border-primary"
            />
            {!agentId && (
              <p className="mt-2 text-xs text-amber-600">No agent configured — outbound calls will fail unless a fallback is enabled by the platform.</p>
            )}
          </section>

          {mappings.length > 0 && (
            <section className="rounded-xl border border-border bg-card p-5">
              <h2 className="text-lg font-bold">Per-language agents</h2>
              <div className="mt-3 space-y-2">
                {mappings.map((m, i) => (
                  <div key={m.language} className="flex items-center gap-3">
                    <span className="w-28 text-sm font-semibold">{m.language}</span>
                    <input
                      value={m.bolna_agent_id || ''}
                      onChange={(e) => updateMapping(i, 'bolna_agent_id', e.target.value)}
                      className="flex-1 rounded-lg border border-border bg-background px-3 py-1.5 font-mono text-xs outline-none focus:border-primary"
                    />
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </AppLayout>
  );
}
