from fpdf import FPDF

# Function to clean text (Removes characters that break the PDF)
def clean_text(text):
    replacements = {
        '\u2014': '-',  # Em-dash -> Hyphen
        '\u2013': '-',  # En-dash -> Hyphen
        '\u2018': "'",  # Left single quote -> '
        '\u2019': "'",  # Right single quote -> '
        '\u201c': '"',  # Left double quote -> "
        '\u201d': '"',  # Right double quote -> "
        '\u2026': '...' # Ellipsis
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text.encode('latin-1', 'replace').decode('latin-1')

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'Project Report: Aadhaar Drishti', 0, 0, 'C')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def chapter_title(self, num, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, f'{num} : {label}', 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        # Clean the text before adding it
        cleaned_body = clean_text(body)
        self.multi_cell(0, 5, cleaned_body)
        self.ln()

# Create PDF object
pdf = PDF()
pdf.alias_nb_pages()
pdf.add_page()

# --- TITLE PAGE ---
pdf.set_font('Arial', 'B', 24)
pdf.ln(50)
pdf.cell(0, 10, 'Aadhaar Drishti', 0, 1, 'C')
pdf.set_font('Arial', '', 16)
pdf.cell(0, 10, 'National Governance Intelligence Platform', 0, 1, 'C')
pdf.ln(20)
pdf.set_font('Arial', '', 12)
pdf.cell(0, 10, 'Submitted By: Team Aadhaar Drishti', 0, 1, 'C')
pdf.cell(0, 10, 'Date: January 2026', 0, 1, 'C')
pdf.cell(0, 10, 'Version: 1.0 (Policy Release)', 0, 1, 'C')
pdf.add_page()

# --- 1. EXECUTIVE SUMMARY ---
pdf.chapter_title('1', 'Executive Summary')
text_exec = """Aadhaar Drishti is a predictive governance intelligence platform designed to transform the administration of India's digital identity framework from a reactive operational model to a proactive one.

Currently, government interventions - whether for fraud detection, infrastructure scaling, or welfare inclusion - often lag behind on-ground realities. Audits are triggered only after suspicious spikes occur, and enrollment camps are deployed only after exclusion complaints arise.

Aadhaar Drishti solves this by treating anonymized enrollment logs as real-time societal signals. The platform integrates three specialized, time-aware intelligence engines:
1. Integrity Shield (Fraud): Detects anomalies while suppressing false positives.
2. Migration Tracker (Infrastructure): Predicts rapid population influxes.
3. Demographic Scanner (Inclusion): Identifies 'Ghost Villages' and 'Digital Dark Zones'.

Strategic Outcome: Moves decision-making from Crisis Management to Predictive Governance."""
pdf.chapter_body(text_exec)

# --- 2. PROBLEM STATEMENT ---
pdf.chapter_title('2', 'Problem Statement')
text_prob = """The Governance Gap:
Despite Aadhaar being the world's largest digital identity system, decision-making often relies on static, fragmented, and delayed data.

1. Reactive Operations: Fraud and exclusion trends are identified weeks late.
2. The 'False Positive' Trap: Standard fraud rules flag legitimate migration spikes as fraud, harassing workers.
3. One-Size-Fits-All Policy: Resources are distributed evenly rather than based on dynamic demand.

Who Is Affected?
- Citizens: Elderly pensioners face service denial; migrant workers face delays.
- Government Officers: Burdened with manual reporting.
- Policy Planners: Lack real-time visibility into demographic shifts."""
pdf.chapter_body(text_prob)

# --- 3. SYSTEM OVERVIEW ---
pdf.chapter_title('3', 'System Overview')
text_sys = """Aadhaar Drishti is a decision intelligence platform that converts raw data into actionable governance signals.

Core Architecture:
The system is built on a Multi-Horizon Time-Series Architecture:
1. Short-Term (30 Days): For immediate fraud detection.
2. Medium-Term (180 Days): For tracking migration trends.
3. Long-Term (3 Years): For monitoring demographic shifts.

The Three Intelligence Engines:
- Engine 1: Integrity Shield (Safeguards ecosystem).
- Engine 2: Migration Tracker (Optimizes infrastructure).
- Engine 3: Demographic Scanner (Ensures inclusion)."""
pdf.chapter_body(text_sys)

# --- 4. SYSTEM FLOWCHART ---
pdf.chapter_title('4', 'System Flowchart')
text_flow = """Data-to-Decision Logic Flow:

1. Raw Data Ingestion: Anonymized logs containing timestamp, pincode, operator ID.
2. Feature Engineering: Data split into rolling windows (30-day, 180-day).
3. Parallel Intelligence Processing:
   - Integrity Shield runs Isolation Forest.
   - Migration Tracker calculates enrollment velocity.
   - Demographic Scanner correlates age data.
4. Cross-Engine Context Layer: Engines share intelligence (e.g., Migration data suppresses Fraud alerts).
5. Decision Dashboard: Prioritized 'Action Lists' for District Collectors.
6. Policy Actions: Deploy Digital Sahayak, Audit Operator, or Scale Infrastructure."""
pdf.chapter_body(text_flow)

# --- 5. DASHBOARD SECTIONS ---
pdf.chapter_title('5', 'Dashboard Sections & Government Questions')

pdf.set_font('Arial', 'B', 11)
pdf.cell(0, 10, '5.1 National Command Center', 0, 1)
pdf.set_font('Arial', '', 11)
pdf.multi_cell(0, 5, clean_text("Question: Where does the government need to act right now?\nSystem Analyzes: Aggregates critical alerts from all three engines.\nDecision Enabled: Immediate prioritization of resources to critical districts."))
pdf.ln(5)

pdf.set_font('Arial', 'B', 11)
pdf.cell(0, 10, '5.2 Integrity Shield (Fraud)', 0, 1)
pdf.set_font('Arial', '', 11)
pdf.multi_cell(0, 5, clean_text("Question: Which centers require audit, and which alerts are false?\nSystem Analyzes: Enrollment velocity and calendar anomalies.\nDecision Enabled: Targeted dispatch of vigilance teams; suppression of false alerts."))
pdf.ln(5)

pdf.set_font('Arial', 'B', 11)
pdf.cell(0, 10, '5.3 Migration Tracker', 0, 1)
pdf.set_font('Arial', '', 11)
pdf.multi_cell(0, 5, clean_text("Question: Where is population pressure increasing due to migration?\nSystem Analyzes: 180-day enrollment velocity and demographics.\nDecision Enabled: Preemptive scaling of Aadhaar Seva Kendras (ASKs)."))
pdf.ln(5)

pdf.set_font('Arial', 'B', 11)
pdf.cell(0, 10, '5.4 Demographic Scanner', 0, 1)
pdf.set_font('Arial', '', 11)
pdf.multi_cell(0, 5, clean_text("Question: Which regions are aging and losing their working population?\nSystem Analyzes: Long-term activity trends vs age brackets.\nDecision Enabled: Deployment of Mobile Aadhaar Vans."))
pdf.ln(5)

pdf.set_font('Arial', 'B', 11)
pdf.cell(0, 10, '5.5 Digital Divide Overlay', 0, 1)
pdf.set_font('Arial', '', 11)
pdf.multi_cell(0, 5, clean_text("Question: Where will digital-only services fail?\nSystem Analyzes: Biometric authentication failure rates.\nDecision Enabled: Targeted deployment of assisted-service models (Digital Sahayaks)."))
pdf.ln(5)

pdf.set_font('Arial', 'B', 11)
pdf.cell(0, 10, '5.6 Impact & Outcomes', 0, 1)
pdf.set_font('Arial', '', 11)
pdf.multi_cell(0, 5, clean_text("Question: Is the system actually improving governance?\nSystem Analyzes: Operational efficiency metrics and ROI.\nDecision Enabled: Data-backed validation for budget allocation."))
pdf.ln()

# --- 6. POLICY IMPACT ---
pdf.chapter_title('6', 'Policy Impact & Benefits')
text_impact = """For Citizens:
- Inclusion: No elderly citizen left behind.
- Dignity: Migrant workers recognized, not harassed.

For Government:
- Cost Efficiency: Elimination of wasteful camps.
- Fraud Prevention: Faster identification of synthetic fraud.

For Administrators:
- Clarity: Automated prioritization replaces manual data crunching.
- Accountability: Every alert comes with a traceable explanation."""
pdf.chapter_body(text_impact)

# --- 7. CONCLUSION ---
pdf.chapter_title('7', 'Conclusion')
text_conc = """Aadhaar Drishti does not just display data. It enables decisions, accountability, and proactive governance.

By bridging the gap between raw data and policy action, it ensures that the Aadhaar ecosystem evolves from a static registry into a dynamic, intelligent framework that serves the changing needs of 1.4 billion citizens."""
pdf.chapter_body(text_conc)

# Output
pdf.output('Aadhaar_Drishti_Project_Report.pdf', 'F')
print("PDF Generated Successfully: Aadhaar_Drishti_Project_Report.pdf")