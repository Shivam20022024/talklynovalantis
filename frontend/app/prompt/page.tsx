'use client'

import { useEffect, useState } from 'react'
import {
  Save,
  Play,
  CheckCircle2,
  X,
  Phone,
  Sparkles,
  Building2,
  Stethoscope,
  GraduationCap,
  CreditCard,
  Briefcase
} from 'lucide-react'
import AppLayout from '@/components/layout/AppLayout'
import { fetchApi } from '@/lib/api'
import { useAuth } from '@/components/providers/AuthProvider'

interface IndustryTemplate {
  id: string
  name: string
  icon: string
  description: string
  default_offering_label: string
  welcome_message: string
  prompt: string
  variables: string[]
}

const CLIENT_TEMPLATES: Record<string, IndustryTemplate> = {
  real_estate: {
    id: "real_estate",
    name: "Real Estate",
    icon: "Building2",
    description: "Qualify home buyers, check budget & location, schedule site tours.",
    default_offering_label: "Project / Property Name",
    welcome_message: "नमस्ते {{customer_name}}, मैं {{company_name}} की तरफ से बोल रहा हूँ। आपके {{offering}} प्रोजेक्ट की इन्क्वायरी के बारे में बात करने के लिए कॉल किया है। क्या अभी 2 मिनट बात करना convenient है?",
    prompt: `You are an experienced real estate sales consultant representing {{company_name}}.
Your goal is to politely qualify prospective buyers who expressed interest in {{offering}} and schedule an in-person site visit.

Key Objectives:
1. Warm Greeting: Acknowledge the customer's inquiry for {{offering}} in {{location}}.
2. Understand Requirements: Inquire about configuration (e.g. 2BHK, 3BHK, Villa), budget range, and timeline to purchase.
3. Highlight Key Selling Points: Mention location connectivity, luxury amenities, and ongoing spot-booking offers.
4. Schedule Site Visit: Propose a convenient time (e.g., this weekend or tomorrow morning) for a guided site tour.
5. Tone: Polite, consultative, respectful, and persistent without being pushy. Reply naturally in the customer's language (Hindi, English, or Hinglish).`,
    variables: ["{{company_name}}", "{{customer_name}}", "{{offering}}", "{{location}}", "{{budget}}"]
  },
  healthcare: {
    id: "healthcare",
    name: "Healthcare & Clinic",
    icon: "Stethoscope",
    description: "Confirm doctor appointments, clinic timings, and collect visit notes.",
    default_offering_label: "Doctor / Clinic Specialty",
    welcome_message: "Hello {{customer_name}}, I am calling from {{company_name}}. I am reaching out regarding your appointment request for {{offering}}. Is this a good time to speak for a moment?",
    prompt: `You are a compassionate, professional clinic coordinator for {{company_name}}.
Your goal is to assist {{customer_name}} with their medical consultation inquiry for {{offering}}.

Key Objectives:
1. Warm Greeting: Confirm you are speaking with {{customer_name}} regarding their inquiry for {{offering}}.
2. Gather Needs: Inquire politely about their preferred consultation day (weekday or weekend) and time slot (morning/evening).
3. Inform Clinic Policies: Mention doctor availability, clinic location ({{location}}), and consultation charges if asked.
4. Confirm Appointment: Lock in a tentative consultation slot and inform them that an SMS/WhatsApp reminder will follow.
5. Tone: Empathetic, calm, reassuring, and confidential. If the customer reports a medical emergency, immediately advise them to visit the nearest emergency room.`,
    variables: ["{{company_name}}", "{{customer_name}}", "{{offering}}", "{{location}}", "{{doctor_name}}", "{{preferred_time}}"]
  },
  edtech: {
    id: "edtech",
    name: "EdTech & Academy",
    icon: "GraduationCap",
    description: "Qualify student goals, program interests, and book free demo sessions.",
    default_offering_label: "Course / Program Name",
    welcome_message: "Hi {{customer_name}}, this is {{company_name}} calling regarding your inquiry for our {{offering}} program. Do you have a quick minute to chat?",
    prompt: `You are an enthusiastic educational counselor representing {{company_name}}.
Your goal is to understand {{customer_name}}'s learning background and invite them to an upcoming live demo session for {{offering}}.

Key Objectives:
1. Connect: Acknowledge their recent inquiry for the {{offering}} curriculum.
2. Background Discovery: Ask whether they are currently a college student, working professional, or career switcher.
3. Program Value: Highlight industry-led projects, guaranteed placement support, flexible weekend batches, and mentor guidance.
4. Free Demo / Counseling: Invite them to attend a free live workshop or schedule a 1-on-1 career roadmap call this week.
5. Tone: Motivating, encouraging, informative, and professional.`,
    variables: ["{{company_name}}", "{{customer_name}}", "{{offering}}", "{{batch_time}}", "{{current_role}}"]
  },
  bfsi: {
    id: "bfsi",
    name: "BFSI (Loans & Insurance)",
    icon: "CreditCard",
    description: "Check eligibility for personal/business loans or policies and schedule callbacks.",
    default_offering_label: "Financial Product / Loan Type",
    welcome_message: "Hello {{customer_name}}, I am calling from {{company_name}} regarding your recent inquiry for our {{offering}} options. Am I speaking with {{customer_name}}?",
    prompt: `You are a knowledgeable financial advisory agent for {{company_name}}.
Your goal is to qualify {{customer_name}} for {{offering}} and arrange a verification call with a senior loan officer.

Key Objectives:
1. Verification: Confirm the customer applied or checked eligibility for {{offering}}.
2. Preliminary Discovery: Ask about required loan or coverage amount, employment type (Salaried vs. Self-employed), and approximate monthly income.
3. Value Proposition: Mention competitive interest rates, zero foreclosure charges (if applicable), and same-day instant pre-approval.
4. Next Step: Confirm their interest in receiving a customized sanction quote and schedule a documentation callback.
5. Tone: Trustworthy, professional, compliant, and discreet.`,
    variables: ["{{company_name}}", "{{customer_name}}", "{{offering}}", "{{loan_amount}}", "{{tenure}}"]
  },
  general_sales: {
    id: "general_sales",
    name: "B2B Sales & Outbound",
    icon: "Briefcase",
    description: "Cold outreach, qualify pain points, and book 15-minute executive walkthroughs.",
    default_offering_label: "Product / Service Solution",
    welcome_message: "Hi {{customer_name}}, this is {{company_name}} reaching out. I noticed your interest in our {{offering}} solutions. Do you have a brief moment?",
    prompt: `You are an outbound sales development representative (SDR) for {{company_name}}.
Your goal is to uncover business challenges and schedule a 15-minute executive walkthrough of {{offering}}.

Key Objectives:
1. Introduction: Briefly state the purpose of the call and connect it to {{offering}}.
2. Qualification: Ask what solution they are currently using and where they experience workflow bottlenecks.
3. Value Pitch: Explain how {{company_name}} helps businesses increase efficiency and reduce operational costs by up to 40%.
4. Call to Action: Propose a quick 15-minute screen-share demo with your product specialist this Tuesday or Thursday.
5. Tone: Confident, articulate, consultative, and concise.`,
    variables: ["{{company_name}}", "{{customer_name}}", "{{offering}}", "{{company_size}}", "{{industry}}"]
  }
}

export default function PromptPage() {
  const { user } = useAuth()
  const [promptText, setPromptText] = useState("Loading...")
  const [welcomeMessage, setWelcomeMessage] = useState("Loading...")
  const [saving, setSaving] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [promptStatus, setPromptStatus] = useState<string>('Draft')
  const [showTestModal, setShowTestModal] = useState(false)
  const [testPhone, setTestPhone] = useState('')
  const [selectedIndustry, setSelectedIndustry] = useState<string>('healthcare')

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search)
      const t = params.get('template')
      if (t && CLIENT_TEMPLATES[t]) {
        setSelectedIndustry(t)
        return
      }
    }
    if (user?.industry && CLIENT_TEMPLATES[user.industry]) {
      setSelectedIndustry(user.industry)
    }
  }, [user?.industry])

  useEffect(() => {
    const fetchPrompt = async () => {
      try {
        const data = await fetchApi('/api/v1/prompt')
        if (data) {
          if (data.prompt) setPromptText(data.prompt)
          if (data.welcome_message) setWelcomeMessage(data.welcome_message)
          else setWelcomeMessage("नमस्ते {{customer_name}}, मैं {{company_name}} की तरफ से बोल रहा हूँ। क्या अभी 2 मिनट बात करना convenient है?")
          if (data.prompt_status) setPromptStatus(data.prompt_status)
        }
      } catch (e) {
        console.error("Failed to load prompt")
      }
    }
    fetchPrompt()
  }, [])

  const handleApplyTemplate = (key: string) => {
    const tmpl = CLIENT_TEMPLATES[key]
    if (!tmpl) return
    if (confirm(`Load the "${tmpl.name}" preset? This will overwrite your draft prompt and welcome message.`)) {
      setSelectedIndustry(key)
      setPromptText(tmpl.prompt)
      setWelcomeMessage(tmpl.welcome_message)
      setPromptStatus('Draft')
    }
  }

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
          campaign_language: 'English',
          industry: selectedIndustry
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
          <p className="mt-2 text-sm text-muted-foreground">Manage your AI agent's instructions, use-case presets, and behavior.</p>
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

      {/* Multi-Industry Preset Bar */}
      <section className="mt-6 rounded-2xl border-2 border-border bg-card p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 pb-3 border-b border-border">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/15 text-primary">
              <Sparkles size={16} />
            </div>
            <div>
              <h2 className="text-sm font-extrabold uppercase tracking-wider text-foreground">
                LOAD PRE-BUILT INDUSTRY TEMPLATE
              </h2>
              <p className="text-xs font-bold text-muted-foreground">
                Instant one-click setup tailored for your vertical
              </p>
            </div>
          </div>
          <span className="inline-flex items-center self-start sm:self-auto rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary">
            Click to load full prompt &amp; greeting
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {Object.entries(CLIENT_TEMPLATES).map(([key, t]) => {
            const isSelected = selectedIndustry === key
            return (
              <button
                key={key}
                type="button"
                onClick={() => handleApplyTemplate(key)}
                className={`flex flex-col items-start justify-between p-4 rounded-xl border-2 text-left transition-all ${
                  isSelected
                    ? 'border-primary bg-primary/15 shadow-md ring-2 ring-primary/20 scale-[1.02]'
                    : 'border-border/80 bg-background hover:bg-muted/40 hover:border-primary/50 hover:shadow-sm'
                }`}
              >
                <div className="w-full">
                  <div className="flex w-full items-center justify-between gap-1 mb-2">
                    <div className="flex items-center gap-2">
                      <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-muted shrink-0">
                        {key === 'real_estate' && <Building2 size={16} className="text-primary" />}
                        {key === 'healthcare' && <Stethoscope size={16} className="text-emerald-500" />}
                        {key === 'edtech' && <GraduationCap size={16} className="text-blue-500" />}
                        {key === 'bfsi' && <CreditCard size={16} className="text-amber-500" />}
                        {key === 'general_sales' && <Briefcase size={16} className="text-purple-500" />}
                      </div>
                      <span className="font-extrabold text-sm tracking-tight text-foreground">
                        {t.name}
                      </span>
                    </div>
                    {user?.industry === key && (
                      <span className="shrink-0 rounded-full bg-primary px-2 py-0.5 text-[9px] font-black uppercase tracking-wider text-primary-foreground shadow-sm">
                        Default
                      </span>
                    )}
                  </div>
                  <p className="text-xs font-bold text-foreground/80 dark:text-foreground/90 line-clamp-2 leading-relaxed">
                    {t.description}
                  </p>
                </div>
                <div className="mt-3 pt-2 w-full border-t border-border/50 flex items-center justify-between text-[11px] font-extrabold">
                  <span className={isSelected ? 'text-primary' : 'text-muted-foreground'}>
                    {isSelected ? '✓ Currently Loaded' : 'Load Template →'}
                  </span>
                </div>
              </button>
            )
          })}
        </div>
      </section>

      <div className="mt-6 grid gap-5 lg:grid-cols-[1fr_300px]">
        <section className="rounded-xl border border-border bg-card p-5">
          <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
            <div>
              <h2 className="text-lg font-bold">Agent Configuration</h2>
              <p className="mt-1 text-xs text-muted-foreground">Setup the welcome message and system prompt for your agent.</p>
            </div>
            <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold ${promptStatus === 'Published' ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300' : 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300'}`}>
              <CheckCircle2 size={12} />{promptStatus === 'Published' ? 'Published' : 'Draft — not published'}
            </span>
          </div>

          <div className="mt-5 space-y-6">
            
            {/* Welcome Message Section */}
            <div>
              <h2 className="text-sm font-bold text-foreground">Agent Welcome Message</h2>
              <p className="mt-0.5 mb-2.5 text-xs text-muted-foreground">The very first sentence your AI agent speaks when the prospect picks up.</p>
              <textarea
                value={welcomeMessage}
                onChange={(e) => setWelcomeMessage(e.target.value)}
                className="w-full resize-y rounded-xl border border-border bg-background p-4 text-sm font-mono leading-relaxed outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 min-h-[90px]"
                placeholder="e.g. Hello {{customer_name}}, this is {{company_name}} calling regarding {{offering}}..."
              />
            </div>

            {/* System Prompt Section */}
            <div className="border-t border-border pt-6">
              <h2 className="text-sm font-bold text-foreground">System Prompt Instructions</h2>
              <p className="mt-0.5 mb-2.5 text-xs text-muted-foreground">The master AI persona, objection handling scripts, and conversation flow.</p>
              <textarea
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                className="w-full h-[420px] resize-none rounded-lg border border-border bg-background p-4 text-sm font-mono outline-none focus:ring-2 focus:ring-primary leading-relaxed"
                placeholder="Enter your system prompt here..."
              />
            </div>
          </div>
        </section>

        <section className="rounded-xl border border-border bg-card p-5 h-fit">
          <h2 className="text-lg font-bold">Dynamic Variables</h2>
          <p className="mt-1 text-xs text-muted-foreground mb-4">Injected automatically per contact from your uploaded CSV.</p>
          
          <div className="space-y-2.5">
            {[
              { tag: '{{customer_name}}', desc: 'Contact / Lead name' },
              { tag: '{{company_name}}', desc: 'Your company name' },
              { tag: '{{offering}}', desc: 'Product, course, clinic service, or property' },
              { tag: '{{location}}', desc: 'City or branch location' },
              { tag: '{{budget}}', desc: 'Budget range or price' },
              { tag: '{{campaign_name}}', desc: 'Active campaign name' },
              { tag: '{{any_csv_column}}', desc: 'Any extra CSV column (e.g. doctor, date)' }
            ].map(v => (
              <div key={v.tag} className="flex flex-col gap-0.5 rounded-lg bg-muted/40 p-2.5 border border-border/40">
                <span className="font-mono text-xs font-semibold text-primary">{v.tag}</span>
                <span className="text-[11px] text-muted-foreground">{v.desc}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Test Call Modal */}
      {showTestModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-xl bg-card p-6 shadow-2xl border border-border">
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
