'use client'

import { useEffect, useState } from 'react'
import {
  Save,
  Play,
  CheckCircle2,
  X,
  Phone,
} from 'lucide-react'
import AppLayout from '@/components/layout/AppLayout'

import { fetchApi } from '@/lib/api'

export default function PromptPage() {
  const [promptText, setPromptText] = useState("Loading...")
  const [welcomeMessage, setWelcomeMessage] = useState("Loading...")
  const [saving, setSaving] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [promptStatus, setPromptStatus] = useState<string>('Draft')
  const [showTestModal, setShowTestModal] = useState(false)
  const [testPhone, setTestPhone] = useState('')

  useEffect(() => {
    const fetchPrompt = async () => {
      try {
        const data = await fetchApi('/api/v1/prompt')
        if (data) {
          if (data.prompt) setPromptText(data.prompt)
          if (data.welcome_message) setWelcomeMessage(data.welcome_message)
          else setWelcomeMessage("नमस्ते, मैं TalklyAI की तरफ से बोल रहा हूँ। आपकी property requirement के बारे में बात करने के लिए कॉल किया है। क्या अभी बात करना convenient है?")
          if (data.prompt_status) setPromptStatus(data.prompt_status)
        }
      } catch (e) {
        console.error("Failed to load prompt")
      }
    }
    fetchPrompt()
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await fetchApi('/api/v1/prompt', {
        method: 'POST',
        body: JSON.stringify({ prompt: promptText, welcome_message: welcomeMessage })
      })
      setPromptStatus('Draft')
      alert("Draft saved.")
    } catch (e) {
      alert("Failed to save prompt.")
    } finally {
      setSaving(false)
    }
  }

  const handlePublish = async () => {
    if (!confirm('Publish this prompt to your company’s live AI agent?')) return
    setPublishing(true)
    try {
      await fetchApi('/api/v1/prompt', {
        method: 'POST',
        body: JSON.stringify({ prompt: promptText, welcome_message: welcomeMessage })
      })
      const res = await fetchApi('/api/v1/prompt/publish', { method: 'POST', body: JSON.stringify({}) })
      setPromptStatus('Published')
      alert(res.bolna_synced ? 'Published and synced to your Bolna agent.' : 'Published (Bolna sync skipped — check agent config).')
    } catch (e: any) {
      alert(e.message || 'Failed to publish.')
    } finally {
      setPublishing(false)
    }
  }

  const handleTestCall = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!testPhone) return
    try {
      await fetchApi('/api/v1/calls/trigger', {
        method: 'POST',
        body: JSON.stringify({
          phone_number: testPhone,
          lead_id: 'test-agent-call',
          campaign_language: 'English'
        })
      })
      alert("Test call initiated successfully! Your phone should ring shortly.")
      setShowTestModal(false)
    } catch (e) {
      alert("Failed to initiate test call")
    }
  }

  return (
    <AppLayout title="AI Prompt">
      <section className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
        <div>
          <p className="eyebrow text-primary">Workspace / AI Prompt</p>
          <h1 className="mt-2 text-3xl font-bold tracking-[-0.06em] sm:text-[34px]">Agent Configuration</h1>
          <p className="mt-2 text-sm text-muted-foreground">Manage your AI agent's instructions and behavior.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowTestModal(true)} className="flex items-center gap-2 rounded-lg border border-border bg-card px-3.5 py-2.5 text-xs font-semibold hover:bg-muted">
            <Play size={15} />Test Agent
          </button>
          <button onClick={handleSave} disabled={saving} className="flex items-center gap-2 rounded-lg border border-border bg-card px-3.5 py-2.5 text-xs font-semibold hover:bg-muted disabled:opacity-50">
            <Save size={15} />{saving ? "Saving..." : "Save Draft"}
          </button>
          <button onClick={handlePublish} disabled={publishing} className="flex items-center gap-2 rounded-lg bg-primary px-3.5 py-2.5 text-xs font-semibold text-primary-foreground shadow-lg shadow-primary/20 hover:opacity-90 disabled:opacity-50">
            <CheckCircle2 size={15} />{publishing ? "Publishing..." : "Publish"}
          </button>
        </div>
      </section>

      <div className="grid gap-5 lg:grid-cols-[1fr_300px]">
        <section className="rounded-xl border border-border bg-card p-5">
          <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
            <div>
              <h2 className="text-lg font-bold">Agent Configuration</h2>
              <p className="mt-1 text-xs text-muted-foreground">Setup the welcome message and system prompt for your agent.</p>
            </div>
            <span className={`inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-[10px] font-semibold ${promptStatus === 'Published' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}`}>
              <CheckCircle2 size={12} />{promptStatus === 'Published' ? 'Published' : 'Draft — not published'}
            </span>
          </div>

          <div className="mt-5 space-y-6">
            
            {/* Welcome Message Section */}
            <div>
              <h2 className="text-lg font-bold">Agent Welcome Message</h2>
              <p className="mt-1 mb-3 text-xs text-muted-foreground">The very first thing your AI agent will say when the user answers the phone.</p>
              <textarea
                value={welcomeMessage}
                onChange={(e) => setWelcomeMessage(e.target.value)}
                className="w-full resize-y rounded-xl border border-border bg-background p-4 text-sm font-mono leading-relaxed outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 min-h-[80px]"
                placeholder="e.g. Hi, this is TalklyAI. How can I help you today?"
              />
            </div>

            {/* System Prompt Section */}
            <div className="border-t border-border pt-6">
              <h2 className="text-lg font-bold">System Prompt</h2>
              <p className="mt-1 mb-3 text-xs text-muted-foreground">The core instructions that guide your AI agent's conversation.</p>
              <textarea
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                className="w-full h-[400px] resize-none rounded-lg border border-border bg-background p-4 text-sm font-mono outline-none focus:ring-2 focus:ring-primary"
                placeholder="Enter your system prompt here..."
              />
            </div>
          </div>
        </section>

        <section className="rounded-xl border border-border bg-card p-5 h-fit">
          <h2 className="text-lg font-bold">Variables</h2>
          <p className="mt-1 text-xs text-muted-foreground mb-4">Use these variables in your prompt to inject dynamic data.</p>
          
          <div className="space-y-3">
            {[
              '{{company_name}}',
              '{{customer_name}}',
              '{{property_name}}',
              '{{property_location}}',
              '{{budget}}',
              '{{lead_source}}',
              '{{campaign_name}}'
            ].map(v => (
              <div key={v} className="flex items-center justify-between rounded-lg bg-muted/50 px-3 py-2">
                <span className="font-mono text-xs font-semibold text-primary">{v}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Test Call Modal */}
      {showTestModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-xl bg-card p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Test Agent</h2>
              <button onClick={() => setShowTestModal(false)} className="text-muted-foreground hover:text-foreground">
                <X size={20} />
              </button>
            </div>
            <p className="text-sm text-muted-foreground mb-4">Enter your phone number to receive a test call from the AI agent using your saved prompt.</p>
            <form onSubmit={handleTestCall} className="space-y-4">
              <div>
                <label className="mb-2 block text-xs font-semibold text-muted-foreground">Phone Number</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-2.5 text-muted-foreground" size={14} />
                  <input
                    required
                    type="text"
                    value={testPhone}
                    onChange={(e) => setTestPhone(e.target.value)}
                    placeholder="+919876543210"
                    className="w-full rounded-lg border border-border bg-background p-2.5 pl-9 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                </div>
              </div>
              <button type="submit" className="w-full rounded-lg bg-primary py-2.5 text-sm font-semibold text-primary-foreground hover:opacity-90">
                Call Me Now
              </button>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  )
}
