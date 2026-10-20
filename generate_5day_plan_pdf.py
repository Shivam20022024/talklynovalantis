from fpdf import FPDF
from datetime import datetime

class SprintPlanPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_margins(16, 16, 16)
        self.set_auto_page_break(auto=True, margin=16)

    def header(self):
        self.set_font('helvetica', 'B', 8)
        self.set_text_color(120, 130, 145)
        self.cell(0, 6, 'TALKLY AI - ACCELERATED 5-DAY PRODUCT SPRINT PLAN', align='L')
        self.cell(0, 6, 'OCTOBER 2026', align='R', ln=True)
        self.set_draw_color(220, 226, 235)
        self.set_line_width(0.3)
        self.line(16, 18, 194, 18)
        self.ln(4)

    def footer(self):
        self.set_y(-14)
        self.set_font('helvetica', '', 8)
        self.set_text_color(140, 150, 165)
        self.set_draw_color(220, 226, 235)
        self.set_line_width(0.3)
        self.line(16, 283, 194, 283)
        self.cell(0, 8, 'Confidential - For Internal & Stakeholder Review Only', align='L')
        self.cell(0, 8, f'Page {self.page_no()} of {{nb}}', align='R')

    def title_block(self, main_title, subtitle, start_date):
        self.set_fill_color(244, 247, 252)
        self.set_draw_color(205, 217, 235)
        self.rect(16, self.get_y(), 178, 28, 'FD')
        
        self.set_xy(20, self.get_y() + 4)
        self.set_font('helvetica', 'B', 15)
        self.set_text_color(18, 38, 74)
        self.cell(0, 7, main_title, ln=True)
        
        self.set_x(20)
        self.set_font('helvetica', '', 9.5)
        self.set_text_color(80, 95, 115)
        self.cell(0, 5, subtitle, ln=True)
        
        self.set_x(20)
        self.set_font('helvetica', 'B', 8.5)
        self.set_text_color(26, 115, 232)
        self.cell(0, 6, f'Sprint Duration: 5 Calendar Days | Effective Start: {start_date}', ln=True)
        self.ln(6)

    def section_heading(self, title):
        self.ln(2)
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(18, 38, 74)
        self.set_fill_color(233, 240, 252)
        self.cell(0, 7.5, f'  {title}', fill=True, ln=True)
        self.ln(2)

    def day_card(self, day_num, date_str, title, objective, tasks, deliverables, impacted_files):
        # Header of Day Card
        self.set_fill_color(248, 250, 254)
        self.set_draw_color(210, 222, 238)
        card_start_y = self.get_y()
        
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(26, 115, 232)
        self.cell(32, 7, f'DAY {day_num} ({date_str}):', ln=False)
        
        self.set_text_color(20, 35, 60)
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 7, title, ln=True)
        
        # Objective
        self.set_font('helvetica', 'I', 8.5)
        self.set_text_color(90, 105, 125)
        self.multi_cell(0, 4.5, f'Objective: {objective}')
        self.ln(1.5)
        
        # Tasks
        self.set_font('helvetica', 'B', 8.5)
        self.set_text_color(50, 65, 85)
        self.cell(0, 5, 'Key Implementation Tasks:', ln=True)
        self.set_font('helvetica', '', 8.5)
        self.set_text_color(60, 70, 85)
        for t in tasks:
            self.cell(5, 4.5, chr(149), align='R')
            self.multi_cell(173, 4.5, f' {t}')
        self.ln(1)
        
        # Deliverables & Files
        self.set_font('helvetica', 'B', 8)
        self.set_text_color(30, 120, 80)
        self.cell(30, 4.5, 'Deliverables: ', ln=False)
        self.set_font('helvetica', '', 8)
        self.set_text_color(60, 70, 85)
        self.cell(0, 4.5, deliverables, ln=True)
        
        self.set_font('helvetica', 'B', 8)
        self.set_text_color(100, 110, 125)
        self.cell(30, 4.5, 'Files Impacted: ', ln=False)
        self.set_font('helvetica', '', 7.5)
        self.set_text_color(80, 90, 105)
        self.cell(0, 4.5, impacted_files, ln=True)
        
        self.set_draw_color(225, 232, 242)
        self.line(16, self.get_y() + 2, 194, self.get_y() + 2)
        self.ln(4)

def build_pdf():
    pdf = SprintPlanPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Header block
    pdf.title_block(
        'Talkly AI: 5-Day Accelerated Fast-Track Sprint',
        'Decoupling Real Estate, Enabling Multi-Use-Case AI, Self-Serve Trial & Outbound Webhooks',
        'Tomorrow, Saturday, Oct 17 - Wednesday, Oct 21, 2026'
    )
    
    # Executive Summary
    pdf.section_heading('1. Executive Objective & Strategic Rationale')
    pdf.set_font('helvetica', '', 8.5)
    pdf.set_text_color(50, 60, 75)
    summary_text = (
        "TalklyAI currently faces two major strategic constraints: (1) it is technically hardcoded for real estate, "
        "and (2) it operates on a high-friction, demo-only enterprise onboarding model with opaque pricing. "
        "This 5-Day Accelerated Sprint condenses the original 7-day engineering roadmap into 5 high-impact working days. "
        "By Day 5, Talkly will be fully industry-agnostic (Healthcare, EdTech, BFSI, B2B Sales, Real Estate), offer instant "
        "self-serve signup with 10 free minutes, and sync live call intelligence directly to any CRM via webhooks."
    )
    pdf.multi_cell(0, 4.5, summary_text)
    pdf.ln(3)

    # Comparison Table
    pdf.section_heading('2. Roadmap Condensation: 7-Day Plan vs. 5-Day Fast-Track')
    pdf.set_font('helvetica', 'B', 8)
    pdf.set_fill_color(230, 238, 250)
    pdf.set_text_color(20, 35, 60)
    pdf.cell(20, 6, 'Timeline', border=1, fill=True, align='C')
    pdf.cell(75, 6, 'Original 7-Day Sprint', border=1, fill=True)
    pdf.cell(83, 6, 'Accelerated 5-Day Fast-Track Delivery', border=1, fill=True)
    pdf.ln()

    table_data = [
        ('Day 1', 'Multi-Use-Case AI Engine (process_audio.py)', 'Universal AI Engine + Follow-Up Context Engine'),
        ('Day 2', 'Dynamic CSV & Campaign Data Model', 'Flexible Data Model + Dynamic CSV Custom Fields Ingestion'),
        ('Day 3', 'Prompt Studio Industry Templates', '1-Click Prompt Templates + Generalized Table UI (Campaigns/Leads)'),
        ('Day 4', 'Self-Serve Signup & Free Trial Wallet', 'Public Self-Serve Registration + Automated 10-Min Free Trial'),
        ('Day 5', 'Public Pricing Page', 'Outbound Webhooks / Zapier Sync + Public Pricing + End-to-End QA'),
        ('Days 6-7', 'Outbound Webhooks & Final QA', 'Merged into Days 4 & 5 for immediate market deployment')
    ]
    
    pdf.set_font('helvetica', '', 8)
    for day_col, orig_col, fast_col in table_data:
        pdf.set_text_color(40, 50, 65)
        pdf.cell(20, 5.5, day_col, border=1, align='C')
        pdf.cell(75, 5.5, f' {orig_col}', border=1)
        pdf.set_text_color(26, 115, 232) if 'Merged' not in fast_col else pdf.set_text_color(150, 50, 50)
        pdf.cell(83, 5.5, f' {fast_col}', border=1)
        pdf.ln()
    pdf.ln(4)

    # Detailed Day Breakdown
    pdf.section_heading('3. Detailed Day-by-Day Implementation Breakdown')
    
    # Day 1
    pdf.day_card(
        day_num=1,
        date_str='Sat, Oct 17',
        title='Universal AI Engine & Dynamic Prompt Decoupling',
        objective='Decouple real estate from post-call LLM analysis and follow-up email drafting.',
        tasks=[
            'Replace hardcoded ANALYSIS_SYSTEM_PROMPT with universal multi-industry prompt & JSON schema.',
            'Support both requirements (offering, budget, location, timeline) and backward-compatible property_requirements.',
            'Update sync_lead_status_from_call() in server.py to extract generalized offering and budget.',
            'Upgrade followup_service.py to generate inquiry-specific email drafts instead of "property search".'
        ],
        deliverables='Universal speech analytics engine supporting Healthcare, EdTech, BFSI, Sales, and Real Estate.',
        impacted_files='backend/process_audio.py, backend/server.py, backend/services/followup_service.py'
    )

    # Day 2
    pdf.day_card(
        day_num=2,
        date_str='Sun, Oct 18',
        title='Flexible Data Model & Dynamic CSV/Excel Custom Fields',
        objective='Enable tenant companies to upload contacts with arbitrary custom columns and inject them into AI calls.',
        tasks=[
            'Update backend/routes/lead_routes.py to collect all non-standard CSV/Excel columns into custom_fields.',
            'Update backend/routes/campaign_routes.py to support industry and offering alongside property.',
            'Update trigger_bolna_call and process_bulk_calls in server.py to replace any {{variable}} dynamically from custom_fields.'
        ],
        deliverables='Dynamic CSV lead uploader and multi-variable Bolna prompt injector.',
        impacted_files='backend/routes/lead_routes.py, backend/routes/campaign_routes.py, backend/server.py'
    )

    # Add page 2
    pdf.add_page()
    pdf.section_heading('3. Detailed Day-by-Day Implementation Breakdown (Cont.)')

    # Day 3
    pdf.day_card(
        day_num=3,
        date_str='Mon, Oct 19',
        title='Turnkey Industry Prompt Templates & UI Adaptation',
        objective='Give non-technical business owners 1-click prompt scripts and generalize frontend tables.',
        tasks=[
            'Build backend/industry_templates.py with ready-to-use scripts for Healthcare, EdTech, BFSI, Sales, and Real Estate.',
            'Enhance frontend/app/prompt/page.tsx with 1-click industry template selector bar and dynamic variable chips.',
            'Update frontend/app/campaigns/page.tsx with Industry dropdown and Campaign Offering / Service input.',
            'Generalize frontend/app/leads/page.tsx headers and drawer from "Property" to "Offering / Details".'
        ],
        deliverables='Prompt Studio Template Library + multi-industry campaign & leads views.',
        impacted_files='backend/industry_templates.py, frontend/app/prompt/page.tsx, campaigns/page.tsx, leads/page.tsx'
    )

    # Day 4
    pdf.day_card(
        day_num=4,
        date_str='Tue, Oct 20',
        title='Self-Serve Onboarding & Automated Free Trial Grant',
        objective='Remove demo-only friction: allow users to sign up and test call immediately without manual approval.',
        tasks=[
            'Enable instant self-registration in backend/routes/auth_routes.py without pending super-admin gating.',
            'Automatically grant 100 INR trial credit (~10 free call minutes) to new company wallets via billing_service.',
            'Build dedicated frontend/app/register/page.tsx with instant trial sandbox messaging and industry selector.',
            'Add GET and PATCH /api/v1/auth/company-settings for self-serve workspace configuration.'
        ],
        deliverables='Self-serve signup flow with 10 free minutes automatically credited upon registration.',
        impacted_files='backend/routes/auth_routes.py, frontend/app/register/page.tsx, frontend/app/login/page.tsx'
    )

    # Day 5
    pdf.day_card(
        day_num=5,
        date_str='Wed, Oct 21',
        title='Outbound CRM Webhooks, Transparent Pricing & Rollout QA',
        objective='Solve the ecosystem integration gap, publish clear pricing, and conduct end-to-end smoke testing.',
        tasks=[
            'Upgrade backend/services/crm_service.py to dispatch real HTTP POST webhooks (Zapier, Make, HubSpot).',
            'Auto-dispatch webhook events upon call completion & analysis in server.py.',
            'Build frontend/app/settings/page.tsx with Company Profile, Industry selector, and Live Webhook Test Ping.',
            'Build public frontend/app/pricing/page.tsx detailing Free Starter (Rs 0), Wallet Pay-As-You-Go (Rs 12/min), and Pro Growth.',
            'Execute end-to-end verification: Signup -> 10 Free Minutes -> Healthcare/EdTech call -> Transcript analyzed -> Webhook posted.'
        ],
        deliverables='Production-ready multi-industry AI calling platform with webhooks, pricing, and self-serve onboarding.',
        impacted_files='backend/services/crm_service.py, frontend/app/settings/page.tsx, frontend/app/pricing/page.tsx'
    )

    # Success Criteria & Signoff Block
    pdf.section_heading('4. Sprint Acceptance Criteria & Deliverables Checklist')
    pdf.set_font('helvetica', '', 8)
    pdf.set_text_color(50, 60, 75)
    checklist = [
        '[x] Multi-Industry Speech Analytics: Transcript analysis scores any business inquiry (clinic, course, loan, property).',
        '[x] Flexible Lead Columns: CSV uploads can ingest doctor, course, city, or timeline and inject them into Bolna AI calls.',
        '[x] 1-Click Prompt Templates: Users can switch between Healthcare, EdTech, BFSI, and Sales templates in 1 click.',
        '[x] Zero-Friction Signup: Anyone can register at /register and get 10 free minutes credited to their wallet automatically.',
        '[x] Transparent Pricing: Public /pricing page shows clear per-minute rates (Rs 12/min) and wallet model.',
        '[x] Live Webhook Sync: Completed calls automatically post summary, sentiment, and score to Zapier/CRM.'
    ]
    for item in checklist:
        pdf.cell(5, 4.5, chr(149), align='R')
        pdf.multi_cell(173, 4.5, f' {item}')

    pdf.output('Talkly_5_Day_Sprint_Plan.pdf')
    print("PDF generated successfully: Talkly_5_Day_Sprint_Plan.pdf")

if __name__ == '__main__':
    build_pdf()
