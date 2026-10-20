# Fact-Check: "TalklyAI Analysis" (ChatGPT Competitive Report)

A review of `TalklyAi Analysis.pdf` against the actual Talkly codebase (`server.py`, `routes/`, `services/`,
`requirements.txt`, `technical_document.md`) — not against Novalantis' marketing site or demo, which is
what the original report was built from.

## Bottom line

The original report's competitor data (Aircall, Solvea, ElevenLabs Agents, Jotform, Rosie, Yellow.ai) is
probably usable as a rough landscape scan. **Its description of Talkly itself is not usable as-is** — it was
assembled from product-page and demo-site marketing claims, not from the code, and describes features
that don't exist in the repository. Using it for pricing or GTM decisions risks committing to positioning the
product can't back up the moment a prospect or investor asks a specific technical question.

## Claim-by-claim: what the report says vs. what's actually built

| Claim in the report | What's actually in the codebase |
|---|---|
| Omnichannel — voice, SMS, WhatsApp, email, web chat, Slack/Teams/Zoom | Voice only, via Twilio (inbound) + Bolna. Email exists solely as Gmail SMTP for account-activation links — not a customer conversation channel. No SMS, WhatsApp, web chat, or Slack/Teams/Zoom integration anywhere in the code. |
| Multilingual, 100+ languages, auto-detect | 13 languages, hardcoded in `language_service.py`'s `SUPPORTED_LANGUAGES` list (English plus 12 Indian languages). Off by roughly 8x. |
| Connects to CRM/ERP — Salesforce, HubSpot, Zendesk | `crm_service.py` is a mock stub: it calls `asyncio.sleep(1)` and sets a `crm_synced` boolean. There is no real CRM integration of any kind, named or otherwise. |
| Integrated with Vertex AI Search for knowledge-grounding | No Google Cloud or Vertex AI dependency exists in `requirements.txt` or anywhere in the code. No RAG/knowledge-grounding layer is implemented. |
| Softphone GUI — real-time transcription, knowledge-base suggestions, auto-extraction | The dashboard is post-call analytics (campaigns, leads, calls, billing), not a live agent softphone interface. Transcript analysis happens after the call ends, via `process_audio.py` — not in real time during it. |
| Sub-400ms latency; 99.9% SLA | Neither metric is measured, logged, or guaranteed anywhere in the code. Reads as a generic enterprise-SaaS claim, not something grounded in Talkly's own stack. |
| Built on ElevenLabs TTS and Google STT (Chirp3) | Talkly never touches STT/TTS directly — the entire voice stack (ASR/LLM/TTS, per agent) is configured on Bolna's own dashboard, outside this repo (`technical_document.md` §11: "Bolna voice-stack config isn't in this repo"). Talkly has no visibility into which providers Bolna uses underneath. |
| Target segments: BFSI, retail, services | The domain model says otherwise: `leads` has `property`/`location` fields, `campaigns` has a `property` field, and the team's own technical document states Novalantis already runs TalklyAI in production "for Real State" (real estate). The evidence points to real estate as the actual vertical, not BFSI/retail. |

## Is the competitor data trustworthy?

More reliable than the Talkly column, but still worth spot-checking before quoting externally — it's the
same ChatGPT-browsing methodology applied to other vendors' marketing pages:

- **Lower risk**: concrete, vendor-published numbers like Rosie's $49/mo flat rate and ElevenLabs' $0.08/min
  usage pricing — these are checkable facts, not characterizations.
- **Higher risk**: round, marketing-flavored claims like Aircall's "250+ integrations" or Yellow.ai's "135+
  languages" — plausible, but repeated uncritically from vendor copy rather than independently verified.

## Does the gap analysis still hold up?

Partly — but it's reasoning from the wrong baseline for Talkly, so some items land differently once you
correct for what's real:

- **Still valid as-is**: "Lack of self-serve/free trial" and "pricing transparency" (items 1–2). These are true
  of the real Talkly regardless of the capability-table errors, and worth acting on.
- **Needs a second look**: "Human-in-the-Loop Options... adding optional human-backup could improve
  healthcare/legal adoption" (item 4). The real Talkly already has a *partial* version of this —
  `transfer_service.py` exists specifically to escalate a call to a human — just weaker than the gap
  analysis assumes (a post-call heuristic, not a live mid-call handoff). The report doesn't know this exists
  because it never inspected the code, so it's recommending something that's partially already in progress
  rather than wholly missing.

## Recommendation

Don't circulate the original report's capability table externally or use it as the basis for pricing/positioning
without correcting it first. The gap-analysis and recommendations sections (self-serve trial, pricing
transparency, SMB packaging) are more salvageable than the capability table, since they're about strategic
direction rather than specific feature claims that a technical follow-up question could immediately disprove.
Before using any of this for an investor or customer conversation, rewrite the "what Talkly has today" column
from the actual repository, not from the product page or demo site.
