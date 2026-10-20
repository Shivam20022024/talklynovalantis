# MediSaarthi — Build Plan

Status: draft v1 · scope: grant-funded POC (₹10L, 6 months, 1–2 NCR pilot sites)
Companion to: `MediSaarthi___Pitch_Deck_20261014-Updated.pdf`, `technical_document.md` (Talkly architecture)

This document is written to be built against. It assumes MediSaarthi ships as a healthcare
vertical inside the existing Talkly codebase (FastAPI + MongoDB backend, Next.js frontend,
Bolna for voice), not a rewrite. Every claim about what's reusable is checked against the
actual code, not the pitch deck's framing of it.

---

## 1. Product Requirements

### 1.1 Personas

| Persona | Who | Primary need |
|---|---|---|
| Patient | OPD patient, any literacy/language level, calling or being called | Get triaged, booked, reminded, followed up — in their own language, without waiting on hold |
| Supervisor | Clinic/hospital staff (receptionist, nurse, call-center agent) | Live visibility into AI conversations; instant handoff when a patient needs a human; manage the day's queue |
| Hospital admin | Practice manager / hospital ops lead (tenant admin) | Configure the hospital's protocols, schedules, languages; see no-show/adherence metrics; control billing |
| Novalantis ops | Internal (incl. Shivam's role per the deck: hospital operations, clinical workflows, regulatory) | Onboard pilot sites, tune protocols, monitor red-flag handling, produce grant close-out evidence |

### 1.2 Core flows (POC scope)

These map directly to pitch deck p.4 ("Every patient, end to end"). Each flow below states
what "done" means — use these as acceptance criteria, not the deck's marketing language.

**Flow 1 — Incoming / outbound trigger**
- Patient calls the hospital's published number (inbound), or the clinic triggers a scheduled
  outbound call (reminder, adherence check, post-discharge follow-up).
- System resolves the correct Bolna agent for the hospital + language (reuse `language_service.py`'s
  `resolve_bolna_agent_id`), reuses the inbound Twilio→Bolna SIP path already built for inbound,
  and the existing bulk-trigger endpoint pattern in `server.py` for outbound.
- Done when: a call is logged against the correct `company_id` (hospital) and `patient_id` within
  2s of pickup, in the patient's detected/selected language.

**Flow 2 — Triage**
- Conversational intake (admin questions only — never diagnosis): reason for visit, department,
  existing patient vs. new, preferred slot.
- Red-flag keyword/symptom detection runs **during** the call, not after.
- Done when: a red-flag utterance triggers a live transfer to a supervisor within one conversation
  turn, with the call context (transcript-so-far, detected symptom, patient ID) delivered to the
  supervisor before or at the moment the call lands with them.

**Flow 3 — Booking**
- Confirm, reschedule, or book against the hospital's live slot calendar; recover a cancellation
  by offering the freed slot to a waitlisted patient while the current caller is still on the line.
- Done when: a booked/rescheduled/cancelled appointment is reflected in `appointments` and visible
  on the supervisor dashboard within the same call, with no double-booking under concurrent calls.

**Flow 4 — Reminders**
- Day-before and day-of voice reminders in the patient's chosen language; capture
  confirm/reschedule/cancel inline.
- Done when: a scheduled reminder job fires within the configured window, and a patient's inline
  response updates the appointment without a second call.

**Flow 5 — Follow-up / adherence**
- Scheduled adherence calls (medication reminders) and post-discharge check-ins on a recurring
  cadence tied to the care plan, closing the loop by logging adherence status.
- Done when: a missed adherence call auto-retries per policy and a logged non-response surfaces
  on the supervisor dashboard, not silently drops.

### 1.3 Functional requirements by module

- **Patient & consent**: capture DPDP-compliant consent before the first AI-handled call touches
  PII; store consent state per patient, queryable, revocable.
- **Protocol / knowledge grounding**: each hospital uploads its own schedules, department
  directory, red-flag symptom list, and discharge-instruction templates; the agent answers only
  from this grounded set — no off-script clinical content.
- **Red-flag guardrail**: a deterministic (not purely LLM-judgment) rule layer evaluates
  transcript-in-progress against the hospital's red-flag symptom list; on match, stops the
  scripted flow and transfers live.
- **Supervisor dashboard**: live queue of in-progress calls, pending transfers, today's
  no-show/adherence numbers; this is additive to the existing post-call analytics dashboard,
  not a replacement.
- **Audit log**: immutable, per-conversation record (who/what/when/consent-state/red-flag
  events) retained per DPDP requirements, separate from normal application logs.
- **Billing**: two streams per the deck — per-facility annual SaaS + per-call usage pricing.
  This is structurally the same shape as Talkly's existing wallet + `company_subscriptions`
  dual model (§9 of `technical_document.md`) — reuse, don't rebuild.

### 1.4 Non-functional requirements

- Multilingual: Hindi at POC launch; the language-switch detection and per-language agent
  routing already exist (`language_service.py`) and extend directly.
- Latency: red-flag transfer must happen inside the live call, not on a post-call webhook —
  see §2.3, this is the POC's hardest technical requirement.
- Data residency: in-India hosting, DPDP-compliant consent and audit trail — new work, not
  present in Talkly today (see §2.4).
- Never diagnoses: the agent's prompt/tooling must be structurally incapable of returning a
  diagnosis — enforced in the protocol-grounding layer, not just a system-prompt instruction.

### 1.5 Explicitly out of scope for the POC

- Full ABDM write-back / health-record exchange (only "building blocks" — i.e. consent-artifact
  and facility-registry alignment — per the deck's own phase 2 framing).
- Insurance/claims integration.
- Any clinical decision support or diagnosis.
- Multi-hospital HIS integration beyond 1–2 pilot sites' specific systems.

---

## 2. Architecture

### 2.1 What's genuinely reusable from Talkly today

Verified against the actual code (not the pitch deck's "adapted from the production engine"
framing, which overstates how much is drop-in):

| Capability | Source | Reuse plan |
|---|---|---|
| Multi-tenant isolation | `auth.py` (`tenant_filter`, `require_company_access`, `enforce_no_foreign_company`, `assert_owned`) | Each hospital/clinic = a `company` tenant. No changes needed — this is the one piece that's genuinely production-hardened and directly portable. |
| Inbound call handling | `inbound/` (Twilio webhook → TwiML `<Dial><Sip>` → Bolna) | Reuse as-is for patient-initiated calls. |
| Outbound bulk trigger | inline logic in `server.py` | Reuse the trigger pattern for scheduled reminders/adherence calls; needs a scheduler on top (new, see §2.3). |
| Per-company, per-language agent routing | `language_service.py` (`resolve_bolna_agent_id`, `SUPPORTED_LANGUAGES`, language-switch detection) | Reuse directly; already covers Hindi + 12 other Indian languages. |
| Billing (two-stream model) | `billing_service.py`, `wallets`, `company_subscriptions`/`subscription_plans` | Reuse directly — this already matches the deck's "SaaS base + per-call usage" shape. |
| Post-call transcript analysis | `process_audio.py`, `intelligence_service.py` | Reuse as the base for adherence/outcome logging; will need healthcare-specific extraction fields (symptom flags, adherence confirmation) added to the prompt/schema. |
| Lead/campaign data pattern | `lead_routes.py`, `campaign_routes.py`, `leads`/`campaigns` collections | Reuse the *pattern* (bulk upload, per-campaign stats via aggregation) for patient rosters and adherence cohorts — not a literal reuse, needs a parallel `patients`/`appointments` domain (§2.2). |

### 2.2 What the deck implies is reused but is not — net-new work

This is the gap between the pitch deck's "full-stack deeptech, adapted from production" framing
and what's actually in the repo. Scoping these honestly now avoids a mid-POC surprise.

- **`transfer_service.py` is a 41-line post-call heuristic** (`evaluate_transfer_need` runs on
  `analysis_result`, i.e. *after* the call ends) — not a live mid-call escalation mechanism.
  Real-time red-flag transfer (Flow 2's hardest requirement) does not exist today and is the
  single biggest net-new build item in this plan (§2.3).
- **`followup_service.py` only drafts a follow-up *email*** via LLM, for the real-estate use
  case — it has no concept of a scheduled, recurring, voice-based adherence call. Needs a real
  scheduler + recurrence model, not a prompt swap.
- **`crm_service.py` is a mock stub** (`asyncio.sleep(1)`, sets a `crm_synced` flag) — there is
  no real CRM/HIS integration anywhere in the codebase today. HIS/CRM + ABDM connectors are
  100% new build.
- **No knowledge-grounding/RAG layer exists.** Nothing in the repo retrieves from
  hospital-supplied documents; the agent prompt is a flat per-company template
  (`prompts` collection: draft/published system prompt + welcome message). Grounding on
  schedules/protocols/discharge instructions is new.
- **No audit-log collection** separate from normal app data — DPDP-grade immutable per-conversation
  audit trail is new.
- **No consent-capture model** — new.
- **No live/streaming webhook path.** Every Bolna webhook handler in the repo
  (`inbound/webhook.py::process_inbound_post_call`, the main webhook in `server.py`) fires
  **after** the call completes. There is currently zero mid-call hook.

### 2.3 Real-time red-flag escalation — the critical design decision

This is the riskiest, most safety-critical piece, and the deck's "stops the script and hands the
call to a human in real time" claim has no existing implementation to point to. Two viable
approaches, to be resolved in Phase 0 against Bolna's actual API surface (not assumed):

1. **Bolna-native approach (preferred, verify first):** most voice-AI platforms, Bolna included,
   support agent-side function/tool-calling mid-conversation — e.g. a `transfer_call` tool the
   LLM can invoke when its own prompt-level instructions detect a red-flag symptom, which Bolna
   then executes as a live SIP transfer to a supervisor number. If Bolna exposes this, the work
   is: (a) define the red-flag symptom list and transfer-tool contract per hospital, (b) build the
   receiving side — a supervisor on-call number/queue that gets the call *and* a simultaneous
   context payload (patient ID, transcript-so-far, matched symptom) via a webhook fired at the
   same moment. This is additive to the existing `inbound/session_manager.py` pattern.
2. **Fallback — streaming transcript tap:** if Bolna doesn't expose a live transfer tool, MediSaarthi
   would need to consume a live transcript/event stream (if Bolna offers one) and trigger transfer
   via Bolna's call-control API mid-call. Meaningfully more engineering than (1); should only be
   pursued if (1) is confirmed unavailable.

**Action item for week 1 of Phase 0**: confirm with Bolna's API docs/support which of these is
actually available before committing engineering budget — this determines whether §2 Engineering
(40% of grant) is sized correctly.

### 2.4 New data model (additive to existing collections)

| Collection | Key fields | Notes |
|---|---|---|
| `patients` | `patient_id`, `company_id`, `name`, `phone`, `preferred_language`, `consent_state` | Parallel to `leads`, but PII-sensitive — needs tighter field-level access control than leads currently get. |
| `appointments` | `appointment_id`, `patient_id`, `company_id`, `slot_time`, `department`, `status` (booked/rescheduled/cancelled/completed/no-show) | New domain object; no calendar/slot concept exists in Talkly today. |
| `protocols` | `company_id`, `doc_type` (schedule/directory/redflag_list/discharge_template), `content`, `version` | Backing store for the RAG/grounding layer. |
| `redflag_events` | `call_id`, `patient_id`, `matched_symptom`, `transferred_at`, `supervisor_id`, `outcome` | Safety audit trail — also doubles as the grant close-out evidence for "zero missed escalations." |
| `consent_records` | `patient_id`, `company_id`, `consent_type`, `granted_at`, `revoked_at` | DPDP requirement. |
| `audit_logs` | `conversation_id`, `event_type`, `actor`, `timestamp`, immutable | Append-only; separate from app logs, separate retention policy. |

### 2.5 Integration points, by confidence

- **High confidence, start immediately**: Bolna (existing integration, extend), Twilio (existing),
  multilingual agent routing (existing).
- **Needs validation before committing scope**: Bolna's mid-call transfer/function-calling support
  (§2.3) — gates the whole triage flow's safety story.
- **New, hospital-specific, expect bespoke work per pilot site**: HIS/CRM connector — there is no
  "generic hospital CRM API," so budget this as 1 integration per pilot site, not a reusable
  connector, for the POC.
- **New, external dependency on availability**: ABDM building blocks — confirm sandbox/API access
  timeline with ABDM before committing Phase 2 dates; this is outside Novalantis's control.

---

## 3. Phased roadmap (maps to grant budget, pitch deck p.12)

| Phase | Weeks | Grant line item | Deliverable |
|---|---|---|---|
| **0 — Foundation** | 1–4 | Engineering (part of ₹4.0L/40%) | Hospital-as-tenant onboarding reusing `auth.py`; `patients`/`appointments`/`consent_records` collections; confirm Bolna mid-call transfer capability (§2.3 action item); basic booking flow reusing the campaign/lead upload pattern. |
| **1 — Triage + red-flag guardrails** | 5–9 | Engineering (₹4.0L/40%) | Deterministic red-flag rule layer; live transfer mechanism per §2.3's chosen approach; supervisor live-queue dashboard (additive to existing analytics UI); `redflag_events` audit trail. This is the phase that proves the deck's core safety claim — budget the most scrutiny here. |
| **2 — Reminders + adherence** | 10–14 | Pilots (₹2.5L/25%) begins here | Scheduler for day-before/day-of reminders and recurring adherence calls (new — `followup_service.py` doesn't cover this); inline confirm/reschedule capture; adherence non-response surfacing on dashboard. First live pilot calls start. |
| **3 — Knowledge grounding + ABDM/HIS hooks** | 15–19 | Indic data (₹2.0L/20%) + Compliance (₹1.5L/15%) | RAG layer over `protocols` collection; ABDM building-block integration (pending external access, §2.5); first pilot site's HIS/CRM connector; ASR/TTS tuning on collected pilot call audio. |
| **4 — Pilot hardening + close-out** | 20–24 | remaining Pilots + Compliance budget | DPDP compliance pass (consent flows, PII minimisation, audit-log completeness); second pilot site onboarding; grant close-out evidence package (no-show reduction, adherence completion rate, red-flag escalation accuracy — see §4). |

Weeks 25–26 held as buffer before the 6-month grant window closes, not allocated to new scope.

---

## 4. POC acceptance criteria (grant close-out evidence)

Define these now so pilot data collection (Phase 2 onward) captures the right fields from day one:

- **Red-flag recall**: 0 missed escalations against the hospital's red-flag symptom list, measured
  against `redflag_events` + a manual review sample — this is the non-negotiable safety metric.
- **No-show reduction**: compare pre-pilot no-show rate at the pilot site(s) to in-pilot rate,
  attributable to reminder/recovery calls.
- **Adherence completion rate**: % of scheduled adherence calls that reach a logged outcome
  (confirmed / rescheduled / genuinely unreachable) vs. silently dropped.
- **Audit completeness**: 100% of AI-handled conversations have a corresponding `audit_logs` entry
  and, where applicable, a `consent_records` entry predating the call.
- **Language coverage**: % of pilot-site calls successfully handled in the patient's preferred
  language without a human fallback solely due to language.

---

## 5. Open risks carried into this plan

- Bolna's mid-call transfer capability is unconfirmed — §2.3 flags this as the Phase 0 gating item.
  If unavailable, Phase 1's timeline and the 40% engineering budget both need revisiting.
- No named clinical advisor on the team (per the deck's team slide) to validate the red-flag
  symptom list and escalation thresholds — recommend sourcing this before Phase 1 starts, since
  the guardrail's correctness is a clinical-safety question, not an engineering one.
- HIS/CRM integration is bespoke per hospital — treat each pilot site's integration as its own
  scoped task, not a reusable module, for POC purposes.
- ABDM building-block timeline depends on external API/sandbox access outside Novalantis's control
  — confirm access before locking Phase 3 dates.
