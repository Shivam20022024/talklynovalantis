'use client'

import { useEffect, useState } from 'react'
import {
  PhoneIncoming,
  Search,
  MoreHorizontal,
  X,
  User,
  Sparkles,
  MessageSquare,
  Clock,
  Activity,
  PhoneMissed,
  Users,
  CalendarDays,
  Download
} from 'lucide-react'
import AppLayout from '@/components/layout/AppLayout'
import { fetchApi, fetchBlob, downloadBlob } from '@/lib/api'

interface CallStats {
  total_calls: number
  answered_calls: number
  missed_calls: number
  calls_today: number
  avg_duration_seconds: number
  unique_callers: number
}

export default function InboundCallsPage() {
  const [calls, setCalls] = useState<any[]>([])
  const [stats, setStats] = useState<CallStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(0)
  const [selectedCall, setSelectedCall] = useState<any>(null)
  const [hasMore, setHasMore] = useState(true)
  const [exporting, setExporting] = useState(false)
  const LIMIT = 20

  const handleExport = async () => {
    setExporting(true)
    try {
      const blob = await fetchBlob('/api/v1/calls/export?direction=inbound')
      downloadBlob(blob, 'talkly_inbound_calls.xlsx')
    } catch (e: any) {
      alert(e.message || 'Failed to export inbound calls')
    } finally {
      setExporting(false)
    }
  }

  const loadCalls = async (pageNum: number) => {
    if (pageNum === 0) setLoading(true)
    try {
      const data = await fetchApi(`/api/v1/calls?direction=inbound&limit=${LIMIT}&skip=${pageNum * LIMIT}`)
      if (data && data.length > 0) {
        if (pageNum === 0) setCalls(data)
        else setCalls(prev => [...prev, ...data])
        if (data.length < LIMIT) setHasMore(false)
      } else {
        if (pageNum === 0) setCalls([])
        setHasMore(false)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const data = await fetchApi('/api/v1/calls/stats?direction=inbound')
      if (data) setStats(data)
    } catch (e) {
      console.error('Failed to load inbound call stats', e)
    }
  }

  useEffect(() => {
    loadCalls(page)
  }, [page])

  useEffect(() => {
    loadStats()
  }, [])

  const visibleCalls = calls.filter((c) =>
    (c.customer_name || '').toLowerCase().includes(query.toLowerCase()) ||
    String(c.customer_id || '').includes(query)
  )

  const formatDuration = (secs: number) => {
    const m = Math.floor(secs / 60)
    const s = Math.round(secs % 60)
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }

  return (
    <AppLayout title="Inbound Calls">
      <section className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
        <div>
          <p className="eyebrow text-primary">Workspace / Inbound Calls</p>
          <h1 className="mt-2 text-3xl font-bold tracking-[-0.06em] sm:text-[34px]">Inbound Call Log</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Calls customers placed directly to your Talkly number - answered by your AI agent.
          </p>
        </div>
        <button
          onClick={handleExport}
          disabled={exporting}
          className="flex h-9 items-center gap-2 rounded-lg border border-border bg-card px-3.5 text-xs font-semibold text-muted-foreground hover:bg-muted hover:text-foreground transition-colors disabled:opacity-50"
        >
          <Download size={14} />{exporting ? 'Exporting...' : 'Export Excel'}
        </button>
      </section>

      {/* KPI Cards */}
      <section className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold tracking-wider text-muted-foreground uppercase">Total Inbound Calls</span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-500/10 text-violet-600 dark:text-violet-400">
              <PhoneIncoming size={16} />
            </div>
          </div>
          <div className="mt-3 text-3xl font-extrabold tracking-tight text-foreground">{stats?.total_calls ?? 0}</div>
          <p className="mt-2 text-xs text-muted-foreground">{stats?.calls_today ?? 0} today</p>
        </div>

        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold tracking-wider text-muted-foreground uppercase">Answered</span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
              <Activity size={16} />
            </div>
          </div>
          <div className="mt-3 text-3xl font-extrabold tracking-tight text-foreground">{stats?.answered_calls ?? 0}</div>
          <p className="mt-2 text-xs text-muted-foreground">by your AI agent</p>
        </div>

        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold tracking-wider text-muted-foreground uppercase">Missed / Incomplete</span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400">
              <PhoneMissed size={16} />
            </div>
          </div>
          <div className="mt-3 text-3xl font-extrabold tracking-tight text-foreground">{stats?.missed_calls ?? 0}</div>
          <p className="mt-2 text-xs text-muted-foreground">avg duration {formatDuration(stats?.avg_duration_seconds ?? 0)}</p>
        </div>

        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold tracking-wider text-muted-foreground uppercase">Unique Callers</span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-400">
              <Users size={16} />
            </div>
          </div>
          <div className="mt-3 text-3xl font-extrabold tracking-tight text-foreground">{stats?.unique_callers ?? 0}</div>
          <p className="mt-2 text-xs text-muted-foreground">distinct phone numbers</p>
        </div>
      </section>

      <section className="mt-6 rounded-xl border border-border bg-card p-5">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 text-primary" size={14} />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by caller name or phone"
              className="h-9 w-64 rounded-lg border border-primary ring-1 ring-primary/20 bg-background pl-9 pr-3 text-xs outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
        </div>

        <div className="mt-5 overflow-x-auto">
          {loading ? (
            <div className="py-10 text-center text-sm text-muted-foreground">Loading inbound calls...</div>
          ) : visibleCalls.length === 0 ? (
            <div className="py-10 text-center text-sm text-muted-foreground">
              No inbound calls yet. Calls customers place to your Talkly number will show up here.
            </div>
          ) : (
            <table className="w-full min-w-[720px] text-left">
              <thead>
                <tr className="border-b border-border h-12 text-sm font-bold uppercase tracking-wider text-foreground">
                  <th className="pb-3 pl-4 font-semibold w-[22%]">Caller</th>
                  <th className="pb-3 px-2 font-semibold w-[16%]">Phone</th>
                  <th className="pb-3 px-2 font-semibold text-center w-[12%]">Language</th>
                  <th className="pb-3 px-2 font-semibold text-center w-[11%]">Duration</th>
                  <th className="pb-3 px-2 font-semibold w-[14%]">Status</th>
                  <th className="pb-3 px-2 font-semibold w-[18%]">Date</th>
                  <th className="pb-3 pr-4 text-right font-semibold w-[7%]">Actions</th>
                </tr>
              </thead>
              <tbody>
                {visibleCalls.map((call, idx) => {
                  const durationSecs = call.duration_seconds || 0
                  const hasDuration = !!call.duration || durationSecs > 0
                  // Missing duration alone doesn't mean the call wasn't
                  // answered - Plivo's hangup webhook can't fire for inbound
                  // calls (see finalize_plivo_call), so older records may
                  // have a real transcript/analysis but no duration. Only
                  // call it "Not Answered" when there's no other evidence
                  // the call actually connected.
                  const wasAnswered = hasDuration || !!call.transcript || ['Analyzed', 'Completed', 'In Progress'].includes(call.status)
                  const isNotReceived = !wasAnswered
                  const displayStatus = isNotReceived ? 'Not Answered' : call.status
                  const isKnownCaller = call.customer_name && call.customer_name !== 'Inbound Caller'

                  return (
                    <tr key={`${call._id || call.call_id || 'call'}-${idx}`} className="border-b border-border/50 h-16 last:border-0 hover:bg-muted/30">
                      <td className="pl-4">
                        <div className="flex items-center gap-3">
                          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-violet-500/10 text-violet-600 dark:text-violet-400">
                            <PhoneIncoming size={13} />
                          </span>
                          <div className="flex flex-col">
                            <p className={`text-sm truncate max-w-[160px] ${!isKnownCaller ? 'text-muted-foreground font-medium' : 'text-foreground font-semibold'}`}>
                              {call.customer_name || 'Inbound Caller'}
                            </p>
                            {!isKnownCaller && (
                              <span className="text-[10px] font-semibold uppercase tracking-wide text-violet-500">New caller</span>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-2">
                        <div className="truncate text-xs font-medium text-muted-foreground" title={call.customer_id}>{call.customer_id}</div>
                      </td>
                      <td className="px-2 text-center text-xs font-medium text-foreground">{call.language || 'English'}</td>
                      <td className="px-2 text-center text-xs font-medium text-foreground">{isNotReceived ? '--:--' : (call.duration || formatDuration(durationSecs))}</td>
                      <td className="px-2">
                        <div className="flex items-center gap-2">
                          <div className={`h-1.5 w-1.5 rounded-full shrink-0
                            ${displayStatus === 'Completed' || displayStatus === 'completed' ? 'bg-emerald-500' : ''}
                            ${displayStatus === 'Failed' || displayStatus === 'failed' ? 'bg-destructive' : ''}
                            ${displayStatus === 'In Progress' ? 'bg-blue-500' : ''}
                            ${displayStatus === 'Not Answered' ? 'bg-orange-400' : ''}
                            ${displayStatus === 'Analyzed' ? 'bg-purple-500' : 'bg-muted-foreground'}
                          `} />
                          <span className="text-[11px] font-medium text-foreground">{displayStatus}</span>
                        </div>
                      </td>
                      <td className="px-2 text-[11px] font-medium text-muted-foreground">
                        {call.created_at ? new Date(call.created_at).toLocaleString('en-US', {
                          month: 'numeric', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true
                        }) : '-'}
                      </td>
                      <td className="pr-4 text-right">
                        <button onClick={() => setSelectedCall(call)} className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground">
                          <MoreHorizontal size={15} />
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}

          {calls.length > 0 && hasMore && (
            <div className="mt-6 flex justify-center pb-4">
              <button
                onClick={() => setPage(p => p + 1)}
                className="rounded-lg border border-border bg-card px-4 py-2 text-sm font-semibold text-muted-foreground hover:bg-muted"
              >
                Load More
              </button>
            </div>
          )}
        </div>
      </section>

      {selectedCall && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="w-full max-w-2xl rounded-2xl border border-border/50 bg-background/95 backdrop-blur-md shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">

            <div className="relative border-b border-border/50 bg-muted/30 px-6 py-5 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-violet-500/10 text-violet-600 dark:text-violet-400 ring-1 ring-violet-500/20 shadow-sm">
                  <PhoneIncoming size={22} />
                </div>
                <div>
                  <h2 className="text-xl font-bold tracking-tight text-foreground">{selectedCall.customer_name || 'Inbound Caller'}</h2>
                  <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
                    <span className="font-medium">{selectedCall.customer_id}</span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setSelectedCall(null)}
                className="absolute right-4 top-4 rounded-full p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="rounded-xl border border-border/50 bg-card p-4 shadow-sm">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                    <Clock size={14} className="text-primary" /> Duration
                  </div>
                  <div className="text-sm font-medium">{selectedCall.duration_seconds ? formatDuration(selectedCall.duration_seconds) : '--:--'}</div>
                </div>

                <div className="rounded-xl border border-border/50 bg-card p-4 shadow-sm">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                    <MessageSquare size={14} className="text-primary" /> Language
                  </div>
                  <div className="text-sm font-medium">{selectedCall.language || 'English'}</div>
                </div>

                <div className="rounded-xl border border-border/50 bg-card p-4 shadow-sm">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                    <Activity size={14} className="text-blue-500" /> Status
                  </div>
                  <div className="text-sm font-bold text-foreground capitalize">{selectedCall.status}</div>
                </div>

                <div className="rounded-xl border border-border/50 bg-card p-4 shadow-sm">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                    <CalendarDays size={14} className="text-amber-500" /> Called On
                  </div>
                  <div className="text-xs font-bold text-foreground">
                    {selectedCall.created_at ? new Date(selectedCall.created_at).toLocaleString() : '-'}
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="mb-3 flex items-center gap-2 text-sm font-bold tracking-tight text-foreground">
                    <Sparkles size={16} className="text-primary" /> Call Summary
                  </h3>
                  <div className="rounded-xl border border-border/50 bg-card p-4 text-sm leading-relaxed text-muted-foreground shadow-sm">
                    {selectedCall.summary || selectedCall.analysis?.summary || 'No summary available.'}
                  </div>
                </div>

                {selectedCall.transcript && (
                  <div>
                    <h3 className="mb-3 flex items-center gap-2 text-sm font-bold tracking-tight text-foreground">
                      <MessageSquare size={16} className="text-primary" /> Transcript
                    </h3>
                    <div className="rounded-xl border border-border/50 bg-card p-4 text-sm leading-relaxed text-muted-foreground shadow-sm max-h-[250px] overflow-y-auto whitespace-pre-wrap">
                      {selectedCall.transcript}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  )
}
