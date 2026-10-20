from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Talkly - Technical Architecture Document', border=False, ln=1, align='C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, border=False, ln=1, fill=True)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('helvetica', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()

pdf = PDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

content = [
    ("1. System Overview", "Talkly is a comprehensive AI Voice Agent platform designed for managing outbound and inbound calls. It enables users to create campaigns, manage leads, configure AI agents, and process audio in real-time. The system comprises a modern web frontend and a robust backend processing engine."),
    ("2. Technology Stack", "- Frontend: Next.js, React, Tailwind CSS\n- Backend: FastAPI (Python), Uvicorn\n- Database: MongoDB\n- Audio Processing: FFmpeg, PyDub\n- AI Integrations: OpenAI (GPT-4o), OpenRouter, Deepgram/ElevenLabs (for STT/TTS)\n- Real-Time Communication: WebRTC / SIP integration"),
    ("3. Architecture Breakdown - Backend (FastAPI)", "- Auth Routes (/api/v1/auth): Handles user authentication, authorization, and multi-tenant access control.\n- Campaign Routes (/api/v1): Management of calling campaigns, scheduling, and linking with agents/leads.\n- Lead Routes (/api/v1): Ingestion, updating, and tracking of customer leads.\n- Agent Routes (/api/v1): Configuration of AI agents, defining prompts, voice characteristics, and intelligence settings.\n- Billing Routes (/api/v1/billing): Tracks usage and calculates costs based on the unit-wise breakdown (Rs 12/minute).\n- Inbound Routes (/api/v1/inbound): Handling incoming calls and routing them to the appropriate AI agent context.\n- Super Admin (/api/v1/admin): Platform-wide administration and analytics."),
    ("4. Services & Processing Engine", "- Audio Processing (process_audio.py): Handles audio file uploads, chunking, and conversion. Integrates with Speech-to-Text APIs.\n- Intelligence Service: Interfaces with LLMs to generate conversational responses.\n- Language Service: Manages multi-lingual capabilities and translation configurations.\n- Billing Service: Calculates deductions based on API usage (STT, LLM, TTS, Telecom)."),
    ("5. Database (MongoDB)", "MongoDB is used as the primary data store. The application uses document collections for:\n- users, companies (Multi-tenant architecture)\n- agents (Configurations for AI bots)\n- campaigns & leads (Outbound marketing data)\n- calls & transcripts (Call logs, analysis, and raw transcript storage)"),
    ("6. Cost Structure & Unit Economics", "The platform operates on a Rs 12 per minute unified charge which covers:\n1. Telecom Connectivity: Rs 2.50\n2. Real-Time STT: Rs 1.50\n3. AI Processing (LLM): Rs 3.50\n4. Text-to-Speech (TTS): Rs 2.50\n5. Platform & Infrastructure: Rs 2.00"),
    ("7. Security & Multi-Tenancy", "- Tenant Isolation: All data operations are filtered by company_id to ensure strict tenant data isolation.\n- Environment Management: API keys (OpenAI, OpenRouter) are securely managed via .env variables and are not exposed to the client."),
    ("8. Deployment & Infrastructure", "- The backend is containerized using Dockerfile.\n- FFmpeg is required on the host/container for media processing.\n- The Next.js frontend is built statically or runs via Node.js server for SSR/ISR.")
]

for title, body in content:
    pdf.chapter_title(title)
    pdf.chapter_body(body)

pdf.output('Talkly_Technical_Document.pdf')
print("PDF created successfully")
