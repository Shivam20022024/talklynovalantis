from fpdf import FPDF
from fpdf.enums import XPos, YPos

class ManagerSprintPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_margins(16, 16, 16)
        self.set_auto_page_break(auto=True, margin=16)

    def header(self):
        self.set_font('helvetica', 'B', 8)
        self.set_text_color(120, 130, 145)
        self.cell(0, 6, 'TALKLY AI - PRODUCT SPRINT & ROADMAP STATUS REPORT', new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(0, 6, 'OCTOBER 2026', align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(215, 225, 238)
        self.set_line_width(0.3)
        self.line(16, 18, 194, 18)
        self.ln(3)

    def footer(self):
        self.set_y(-14)
        self.set_font('helvetica', '', 8)
        self.set_text_color(140, 150, 165)
        self.set_draw_color(215, 225, 238)
        self.set_line_width(0.3)
        self.line(16, 283, 194, 283)
        self.cell(0, 8, 'Confidential - Prepared for Executive & Management Review', align='L', new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(0, 8, f'Page {self.page_no()} of {{nb}}', align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def section_header(self, title):
        self.ln(2)
        self.set_font('helvetica', 'B', 10.5)
        self.set_text_color(18, 38, 74)
        self.set_fill_color(234, 242, 253)
        self.cell(0, 7, f'  {title}', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

def generate_pdf():
    pdf = ManagerSprintPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Executive Banner
    pdf.set_fill_color(245, 248, 253)
    pdf.set_draw_color(200, 215, 235)
    pdf.rect(16, pdf.get_y(), 178, 28, 'FD')
    
    pdf.set_xy(20, pdf.get_y() + 3.5)
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(18, 38, 74)
    pdf.cell(0, 6.5, 'Product Sprint Plan: Multi-Use-Case & Self-Serve Growth', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_x(20)
    pdf.set_font('helvetica', '', 9)
    pdf.set_text_color(75, 90, 110)
    pdf.cell(0, 5, 'Transitioning TalklyAI from Real Estate Lock-in to Multi-Industry Platform', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_x(20)
    pdf.set_font('helvetica', 'B', 8.5)
    pdf.set_text_color(26, 115, 232)
    pdf.cell(0, 5.5, 'Timeline: Today (Oct 16 Completed) + 5-Day Sprint (Oct 17 - Oct 21, 2026)', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    # 1. Executive Summary
    pdf.section_header('1. Executive Objective')
    pdf.set_font('helvetica', '', 8.5)
    pdf.set_text_color(45, 55, 70)
    exec_summary = (
        "Objective: Rapidly transform Talkly from a demo-only, real-estate-locked tool into a modern, multi-industry AI voice "
        "calling platform (Healthcare, EdTech, BFSI/Loans, B2B Sales, Real Estate) featuring instant self-serve onboarding, "
        "transparent usage pricing, and automated CRM webhook synchronization."
    )
    pdf.multi_cell(0, 4.5, exec_summary)
    pdf.ln(2)

    # 2. Today's Completed Tasks
    pdf.section_header('2. Today\'s Progress & Milestones Completed (Friday, Oct 16, 2026)')
    
    today_items = [
        ("Architecture & Gap Audit", "Reviewed competitive intelligence report against codebase; confirmed key gaps (real-estate hardcoding, lack of self-serve, opaque pricing, missing CRM webhooks)."),
        ("Universal AI Prompt Engine", "Decoupled real estate from backend/process_audio.py. Implemented universal prompt & JSON schema capturing requirements across any vertical with 100% backward compatibility."),
        ("Industry Templates Registry", "Created backend/industry_templates.py with ready-to-use prompt scripts and welcome greetings for Healthcare, EdTech, BFSI, B2B Sales, and Real Estate."),
        ("Dynamic Lead Ingestion", "Updated backend/routes/lead_routes.py & campaign_routes.py to accept arbitrary custom CSV columns into custom_fields and support 'offering' alongside 'property'."),
        ("Outbound Webhook Dispatcher", "Replaced mock CRM stub (crm_service.py) with real async webhook dispatcher for Zapier, Make, and CRMs, plus test ping endpoint."),
        ("Self-Serve & Pricing Foundation", "Built public /register page with automated Rs 100 (10 free mins) wallet credit and created public /pricing page.")
    ]
    
    for title, desc in today_items:
        pdf.set_font('helvetica', 'B', 8.5)
        pdf.set_text_color(30, 120, 80)
        pdf.cell(5, 4.5, chr(149), align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_text_color(18, 38, 74)
        pdf.cell(52, 4.5, f' {title}:', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font('helvetica', '', 8.5)
        pdf.set_text_color(60, 70, 85)
        pdf.multi_cell(121, 4.5, f' {desc}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(0.5)

    # 3. 5-Day Sprint Schedule
    pdf.section_header('3. 5-Day Sprint Execution Schedule (Tomorrow, Oct 17 - Oct 21, 2026)')

    sprint_days = [
        (
            "Day 1",
            "Saturday, Oct 17",
            "Universal AI Engine Decoupling & Follow-up Context",
            [
                "Deploy universal transcript analysis prompt for Healthcare, EdTech, BFSI, Sales, and Real Estate.",
                "Implement dynamic requirements extraction (offering, budget, timeline, location) with temperature scoring.",
                "Deploy context-aware follow-up email drafts adapting to the inquiry topic instead of hardcoded 'property search'."
            ],
            "Universal speech intelligence engine active across all 5 target business verticals."
        ),
        (
            "Day 2",
            "Sunday, Oct 18",
            "Flexible Data Model & Dynamic CSV/Excel Custom Fields",
            [
                "Support industry and offering in campaigns instead of hardcoded property.",
                "Enable CSV uploader to dynamically capture doctor, course, city, or batch into custom_fields.",
                "Enable dynamic prompt variable injection ({{offering}}, {{doctor}}, {{course}}) in single and bulk calls."
            ],
            "Dynamic lead ingestion engine capable of running campaigns for any industry CSV."
        ),
        (
            "Day 3",
            "Monday, Oct 19",
            "Turnkey Industry Prompt Templates & UI Adaptation",
            [
                "Launch 1-click industry template selector bar in Prompt Studio (Healthcare, EdTech, BFSI, Sales, Real Estate).",
                "Update Campaigns table and modal from 'Property' to 'Offering / Product / Service'.",
                "Update Leads table header and detail drawer to display 'Offering / Details'."
            ],
            "Non-technical business owners can configure prompt instructions and launch campaigns in 1 click."
        )
    ]

    for day_label, date_label, title, tasks, deliverable in sprint_days:
        pdf.set_font('helvetica', 'B', 9)
        pdf.set_text_color(26, 115, 232)
        pdf.cell(32, 5.5, f'{day_label} ({date_label}):', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_text_color(18, 38, 74)
        pdf.cell(0, 5.5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        pdf.set_font('helvetica', '', 8)
        pdf.set_text_color(50, 60, 75)
        for t in tasks:
            pdf.cell(5, 4.2, chr(149), align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.multi_cell(173, 4.2, f' {t}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        pdf.set_font('helvetica', 'B', 7.5)
        pdf.set_text_color(30, 120, 80)
        pdf.cell(24, 4.2, 'Deliverable: ', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font('helvetica', '', 7.5)
        pdf.set_text_color(70, 80, 95)
        pdf.cell(0, 4.2, deliverable, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1.5)

    # Add Page 2 for Day 4 & Day 5 + Acceptance Checklist
    pdf.add_page()
    pdf.section_header('3. 5-Day Sprint Execution Schedule (Continued)')

    sprint_days_p2 = [
        (
            "Day 4",
            "Tuesday, Oct 20",
            "Self-Serve Onboarding & Automated Free Trial Credits",
            [
                "Enable instant public self-registration with automated company workspace provisioning.",
                "Auto-credit Rs 100 starter wallet balance (~10 free AI call minutes) upon registration.",
                "Deploy dedicated /register page with '10 Free Minutes - No Card Required' messaging.",
                "Implement GET and PATCH /api/v1/auth/company-settings for self-serve workspace management."
            ],
            "Zero-friction self-serve customer acquisition funnel to eliminate demo-request drop-offs."
        ),
        (
            "Day 5",
            "Wednesday, Oct 21",
            "CRM Webhook Dispatcher, Transparent Pricing & Final QA",
            [
                "Deploy automated outbound webhook engine (posts lead score, sentiment, transcript to Zapier/CRM).",
                "Deploy Workspace Settings page with live Webhook Test Ping verification tool.",
                "Publish transparent /pricing page: Free Trial (Rs 0), Wallet Pay-As-You-Go (Rs 12/min), and Pro Growth.",
                "Execute end-to-end multi-industry call verification: Signup -> 10 Free Mins -> Call -> Webhook received."
            ],
            "Fully production-ready multi-industry AI calling platform with webhook sync and live pricing."
        )
    ]

    for day_label, date_label, title, tasks, deliverable in sprint_days_p2:
        pdf.set_font('helvetica', 'B', 9)
        pdf.set_text_color(26, 115, 232)
        pdf.cell(32, 5.5, f'{day_label} ({date_label}):', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_text_color(18, 38, 74)
        pdf.cell(0, 5.5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        pdf.set_font('helvetica', '', 8)
        pdf.set_text_color(50, 60, 75)
        for t in tasks:
            pdf.cell(5, 4.2, chr(149), align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.multi_cell(173, 4.2, f' {t}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        pdf.set_font('helvetica', 'B', 7.5)
        pdf.set_text_color(30, 120, 80)
        pdf.cell(24, 4.2, 'Deliverable: ', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font('helvetica', '', 7.5)
        pdf.set_text_color(70, 80, 95)
        pdf.cell(0, 4.2, deliverable, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2.5)

    # 4. Summary Matrix
    pdf.section_header('4. Quick Reference Summary Table')
    pdf.set_font('helvetica', 'B', 8)
    pdf.set_fill_color(230, 238, 250)
    pdf.set_text_color(18, 38, 74)
    pdf.cell(30, 6, 'Sprint Day', border=1, fill=True, align='C')
    pdf.cell(60, 6, 'Focus Area', border=1, fill=True)
    pdf.cell(88, 6, 'Primary Output / Impact', border=1, fill=True)
    pdf.ln()

    summary_rows = [
        ("Today (Fri, Oct 16)", "Gap Audit & Core Decoupling", "Foundation built; real estate decoupled from analysis prompt"),
        ("Day 1 (Sat, Oct 17)", "Universal AI Engine", "Speech analysis scores clinic, course, loan & property inquiries"),
        ("Day 2 (Sun, Oct 18)", "Dynamic CSV Model", "Upload CSVs with any custom fields injected into Bolna calls"),
        ("Day 3 (Mon, Oct 19)", "Industry Prompt Studio", "1-click pre-built prompts & bilingual greetings in UI"),
        ("Day 4 (Tue, Oct 20)", "Self-Serve Trial Funnel", "Instant registration with Rs 100 / 10 free minutes credited"),
        ("Day 5 (Wed, Oct 21)", "Webhooks, Pricing & QA", "Outbound CRM webhook sync, public pricing & rollout smoke test")
    ]
    
    pdf.set_font('helvetica', '', 8)
    for d, f, o in summary_rows:
        pdf.set_text_color(40, 50, 65)
        pdf.cell(30, 5.5, d, border=1, align='C')
        pdf.cell(60, 5.5, f' {f}', border=1)
        pdf.set_text_color(26, 115, 232) if 'Day' in d else pdf.set_text_color(30, 120, 80)
        pdf.cell(88, 5.5, f' {o}', border=1)
        pdf.ln()
    pdf.ln(3)

    # 5. Success Metrics & Manager Sign-off
    pdf.section_header('5. Acceptance Checklist for Manager Sign-off')
    pdf.set_font('helvetica', '', 8)
    pdf.set_text_color(50, 60, 75)
    checks = [
        "[x] Multi-Industry Capability: AI qualified across Healthcare, EdTech, BFSI, B2B Sales, and Real Estate.",
        "[x] Zero Friction Signup: Prospective customers can register at /register without sales demo gatekeeping.",
        "[x] Automated Trial Balance: Rs 100 trial balance credited upon signup allowing instant 10-minute trial call.",
        "[x] Transparent Public Pricing: Clear wallet-based pricing (Rs 12/min) and growth bundles published at /pricing.",
        "[x] Real Outbound Webhooks: Automatic lead & transcript dispatch to Zapier, Make.com, or internal CRMs.",
        "[x] Code Stability: Clean TypeScript (tsc: 0 errors) and Python syntax verification across backend & frontend."
    ]
    for c in checks:
        pdf.cell(5, 4.2, chr(149), align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.multi_cell(173, 4.2, f' {c}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Save
    out_path = 'Talkly_Sprint_Plan_Manager.pdf'
    pdf.output(out_path)
    print(f"Manager PDF generated successfully: {out_path}")

if __name__ == '__main__':
    generate_pdf()
