import streamlit as st
import json
import google.generativeai as genai
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
from fpdf import FPDF
from PyPDF2 import PdfReader

# =====================================================
# PAGE CONFIG & CUSTOM THEME INJECTION
# =====================================================

st.set_page_config(
    page_title="JusticePath | Simple AI Legal Guide",
    layout="wide"
)

# Custom CSS for a sleek, modern premium dark theme aesthetic
st.markdown("""
    <style>
    /* Import modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stSidebarNav"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background and Card Aesthetics */
    .stApp {
        background-color: #0d1117;
    }
    
    /* Beautiful UI Content Cards */
    .feature-card {
        background: linear-gradient(145deg, #161b22, #1f242c);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        margin-bottom: 16px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        border-color: #58a6ff;
    }

    /* Output Display Cards */
    .result-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #30363d;
        margin-bottom: 12px;
    }
    .card-label {
        color: #8b949e;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
        font-weight: 600;
    }
    .card-value {
        color: #c9d1d9;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    /* Clean custom list styling */
    .feature-list {
        list-style-type: none;
        padding-left: 0;
    }
    .feature-list li {
        padding: 8px 0;
        font-size: 1.05rem;
        color: #c9d1d9;
        display: flex;
        align-items: center;
    }
    .feature-list li::before {
        content: "-";
        margin-right: 12px;
        font-size: 0.9rem;
        color: #58a6ff;
    }
    
    /* Gradient App Headers */
    .gradient-text {
        background: linear-gradient(90deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    /* Muted Footer Disclaimer text styling */
    .disclaimer-text {
        font-size: 0.85rem;
        color: #8b949e;
        border-left: 3px solid #ff7b72;
        padding-left: 12px;
        margin-top: 30px;
    }

    /* Elegant Custom Badges for Legal Framework Rendering */
    .legal-badge {
        background-color: #1f242c;
        color: #ff7b72;
        padding: 4px 8px;
        border-radius: 6px;
        border: 1px solid #30363d;
        font-family: monospace;
        font-size: 0.9rem;
        display: inline-block;
        margin-top: 4px;
    }
    .authority-badge {
        background-color: #161b22;
        color: #58a6ff;
        padding: 4px 8px;
        border-radius: 6px;
        border: 1px solid #30363d;
        font-weight: 600;
    }

    /* Premium Category Status Badges */
    .category-badge {
        background-color: #1f242c;
        color: #bc8cff;
        padding: 6px 14px;
        border-radius: 20px;
        border: 1px solid #bc8cff;
        font-family: monospace;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 1px;
        display: inline-block;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    /* Premium Platform Statistics Metric Elements */
    .stat-box {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #58a6ff;
        margin-bottom: 2px;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Clean Application Footer Styles */
    .app-footer {
        text-align: center;
        padding: 24px 0;
        margin-top: 60px;
        border-top: 1px solid #30363d;
        color: #8b949e;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# GEMINI SETUP
# =====================================================

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# =====================================================
# LOAD RIGHTS DATABASE
# =====================================================

@st.cache_data
def load_rights():
    try:
        with open(
            "data/rights/master_rights.json",
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)
    except Exception:
        return [
            {"category": "Cybercrime Rights", "right_name": "Online Fraud Reporting", "description": "Protections against online scam losses.", "authority": "National Cyber Crime Portal", "laws": ["Information Technology Act, 2000"]},
            {"category": "Consumer Rights", "right_name": "Right to Refund", "description": "Protections against defective marketplace assets.", "authority": "Consumer Commission", "laws": ["Consumer Protection Act, 2019"]}
        ]

rights_data = load_rights()

# =====================================================
# RIGHTS EXPLORER FUNCTIONS
# =====================================================

def get_categories():
    categories = list(set(item["category"] for item in rights_data))
    extra_categories = ["Women Rights", "Senior Citizen Rights", "Banking Rights", "Digital Privacy Rights"]
    for cat in extra_categories:
        if cat not in categories:
            categories.append(cat)
    return sorted(categories)


def get_rights_by_category(category):
    base_results = [item for item in rights_data if item["category"] == category]
    if not base_results:
        mock_extensions = {
            "Women Rights": [{"right_name": "Protection Against Workplace Harassment", "description": "Ensures safe corporate working frameworks for female professionals.", "authority": "Internal Complaints Committee (ICC)", "laws": ["POSH Act, 2013"]}],
            "Senior Citizen Rights": [{"right_name": "Maintenance Claims", "description": "Legal recourse ensuring welfare allowances from legal heirs.", "authority": "Welfare Tribunal", "laws": ["Maintenance Act, 2007"]}],
            "Banking Rights": [{"right_name": "Unauthorized Transaction Protection", "description": "Zero liability windows for reporting fraudulent account billing.", "authority": "Banking Ombudsman", "laws": ["RBI Consumer Protection Guidelines"]}],
            "Digital Privacy Rights": [{"right_name": "Data Consent Revocation", "description": "The explicit right to mandate deletion of personal telemetry information.", "authority": "Data Protection Board", "laws": ["DPDP Act, 2023"]}]
        }
        return mock_extensions.get(category, [])
    return base_results


def search_rights(keyword):
    keyword = keyword.lower()
    results = []
    for item in rights_data:
        if (
            keyword in item["right_name"].lower() or
            keyword in item["description"].lower() or
            any(keyword in law.lower() for law in item.get("laws", []))
        ):
            results.append(item)
    return results

# =====================================================
# EXTENSIVE ISSUE CLASSIFIER
# =====================================================

def classify_issue(user_issue):
    issue = user_issue.lower()
    if any(word in issue for word in ["fraud", "scam", "upi", "cyber", "hack", "otp"]):
        return "Cybercrime Rights"
    elif any(word in issue for word in ["salary", "employer", "job", "work", "harassment"]):
        return "Employment Rights"
    elif any(word in issue for word in ["product", "refund", "consumer", "defective", "store"]):
        return "Consumer Rights"
    elif any(word in issue for word in ["rent", "tenant", "landlord", "eviction"]):
        return "Tenant Rights"
    elif any(word in issue for word in ["college", "school", "university", "exam"]):
        return "Education Rights"
    elif any(word in issue for word in ["domestic", "harassment", "women", "dowry", "posh"]):
        return "Women Rights"
    elif any(word in issue for word in ["senior", "elderly", "parent", "pension", "old age"]):
        return "Senior Citizen Rights"
    elif any(word in issue for word in ["bank", "atm", "credit card", "loan", "unauthorized"]):
        return "Banking Rights"
    elif any(word in issue for word in ["data", "privacy", "leak", "tracking", "surveillance"]):
        return "Digital Privacy Rights"
    return "Constitutional Rights"

# =====================================================
# EVIDENCE CHECKLIST
# =====================================================

evidence_templates = {
    "Cybercrime Rights": ["Screenshots", "Transaction Records", "Bank Statements", "Phone Numbers", "Emails"],
    "Employment Rights": ["Offer Letter", "Salary Slips", "Employment Contract", "Emails", "Messages"],
    "Consumer Rights": ["Invoice", "Receipt", "Product Images", "Warranty Documents"],
    "Tenant Rights": ["Rent Agreement", "Rent Receipts", "Photos", "Communication Records"],
    "Education Rights": ["Admission Documents", "Fee Receipts", "Emails", "Academic Records"],
    "Women Rights": ["Text Messages", "Witness Accounts", "Incident Timeline Logs", "Official Written Notices"],
    "Senior Citizen Rights": ["Age Proof Certificates", "Bank Passbooks", "Property Ownership Records", "Medical Bills"],
    "Banking Rights": ["Bank Statements", "Dispute Acknowledgment Forms", "Card Block Confirmation SMS"],
    "Digital Privacy Rights": ["Privacy Policy Screenshots", "Consent Logs", "Data Access Request Emails"]
}

def generate_evidence_checklist(user_issue):
    category = classify_issue(user_issue)
    return evidence_templates.get(category, ["Supporting Case Correspondence", "Timeline Documents"])

# =====================================================
# AUTHORITY FINDER
# =====================================================

authority_mapping = {
    "Cybercrime Rights": ["National Cyber Crime Portal", "Cyber Crime Cell"],
    "Employment Rights": ["Labour Commissioner", "HR Department"],
    "Consumer Rights": ["Consumer Commission"],
    "Tenant Rights": ["Civil Court"],
    "Education Rights": ["Education Department"],
    "Women Rights": ["National Commission for Women", "Local Police Station Support Desk"],
    "Senior Citizen Rights": ["Social Welfare Officer", "Maintenance Tribunal"],
    "Banking Rights": ["Banking Ombudsman Office", "Reserve Bank Portal Lines"],
    "Digital Privacy Rights": ["Data Protection Authority Officers", "Cyber Grievance Desks"]
}

def find_relevant_authorities(user_issue):
    category = classify_issue(user_issue)
    return authority_mapping.get(category, ["Concerned Local Regulatory Desk"])

# =====================================================
# ACTION ROADMAP
# =====================================================

roadmap_templates = {
    "Cybercrime Rights": ["Preserve screenshots", "Save transaction details", "Contact bank immediately", "Report on National Cyber Crime Portal", "File FIR if required"],
    "Employment Rights": ["Collect salary records", "Preserve communication with employer", "Submit written complaint", "Contact HR or management", "Approach Labour Commissioner"],
    "Consumer Rights": ["Collect invoice and receipt", "Document product issue", "Contact seller", "Request refund/replacement", "File consumer complaint"],
    "Tenant Rights": ["Collect rent agreement", "Preserve payment records", "Document dispute", "Issue written notice", "Seek civil remedy"],
    "Education Rights": ["Collect academic records", "Preserve communication", "Contact institution", "Submit formal representation", "Escalate to authority"],
    "Women Rights": ["Log specific timeline markers", "Notify internal safety committees", "Escalate to regional commission centers"],
    "Senior Citizen Rights": ["Collate maintenance records", "Submit representation to welfare panels", "Request emergency fast track support status"],
    "Banking Rights": ["Mandate credit account freezing actions", "Log dispute complaints within 72 hour liability windows", "Escalate unresolved tickets to ombudsman paths"],
    "Digital Privacy Rights": ["Submit data clearing demands", "Revoke active cookies or credentials", "File tracking violation reports with authorities"]
}

def generate_action_roadmap(user_issue):
    category = classify_issue(user_issue)
    return roadmap_templates.get(category, ["Document incident events", "Collect primary files", "Submit formal legal summary report"])

# =====================================================
# COMPLAINT GENERATOR WITH INTERACTIVE DATA OVERLAYS
# =====================================================

def generate_complaint(user_issue, citizen_name="Citizen", date_str="As Applicable", contact_info=""):
    category = classify_issue(user_issue)
    authorities = find_relevant_authorities(user_issue)
    authority = authorities[0] if authorities else "Concerned Authority"
    
    contact_block = f"\nContact Info: {contact_info}" if contact_info else ""

    complaint = f"""Date: {date_str}

To,
{authority}

Subject: Formal Grievance and Complaint regarding {category}

Respected Sir/Madam,

I am writing to formally submit a grievance regarding the following event:

{user_issue}

I request your office to look into this matter and take appropriate action as per applicable rules and laws.

I am holding onto supporting proof and evidence and I am ready to cooperate with any check or investigation.

Thank you.

Sincerely,

{citizen_name}{contact_block}"""
    return complaint

# =====================================================
# PDF EXPORT (SANITAION FIXES APPLIED)
# =====================================================

def export_complaint_pdf(complaint_text):
    # Sanitize and replace Unicode characters that crash Latin-1 FPDF encodings
    complaint_text = (
        complaint_text
        .replace("₹", "Rs.")
        .replace("•", "-")
        .replace("—", "-")
        .replace("–", "-")
    )
    
    complaint_text = complaint_text.encode(
        "latin-1", 
        "replace"
    ).decode("latin-1")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, complaint_text)
    pdf.output("complaint.pdf")
    return "complaint.pdf"

# =====================================================
# PDF READER
# =====================================================

def read_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    return text

# =====================================================
# LEGAL LANGUAGE SIMPLIFIER
# =====================================================

def simplify_legal_text(document_text):
    prompt = f"""You are a legal language simplifier.
Convert the following legal text into simple English.

Rules:
1. Keep meaning unchanged
2. Use easy language
3. Explain legal terms
4. Use bullet points
5. Maximum 300 words

Document:
{document_text}"""

    response = model.generate_content(prompt)
    return response.text

# =====================================================
# FAISS + EMBEDDING MODEL
# =====================================================

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

embedding_model = load_embedding_model()

# =====================================================
# BUILD DOCUMENTS
# =====================================================

documents = []
for item in rights_data:
    doc = f"Category: {item['category']}\nRight: {item['right_name']}\nDescription: {item['description']}\nAuthority: {item['authority']}\n"
    documents.append(doc)

# =====================================================
# EMBEDDINGS
# =====================================================

embeddings = embedding_model.encode(documents)
embeddings = np.array(embeddings, dtype=np.float32)

# =====================================================
# FAISS INDEX
# =====================================================

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# =====================================================
# RETRIEVE CONTEXT
# =====================================================

def retrieve_context(query, top_k=3):
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding, dtype=np.float32)
    distances, indices = index.search(query_embedding, top_k)
    
    context = ""
    for idx in indices[0]:
        if idx < len(documents):
            context += documents[idx] + "\n\n"
    return context

# =====================================================
# RAG LEGAL ANALYZER
# =====================================================

def rag_legal_analyzer(user_issue):
    retrieved_context = retrieve_context(user_issue)
    prompt = f"""You are JusticePath.
IMPORTANT:
- Educational information only
- Not legal advice
- Use ONLY the retrieved information

User Issue:
{user_issue}

Retrieved Legal Knowledge:
{retrieved_context}

Provide:
1. Issue Summary
2. Relevant Rights
3. Relevant Authority
4. Evidence To Preserve
5. Suggested Next Steps

Keep response concise."""

    response = model.generate_content(prompt)
    return response.text

# =====================================================
# SIDEBAR NAVIGATION & THEME ADDITIONS
# =====================================================

with st.sidebar:
    st.markdown('<h1 class="gradient-text" style="font-size: 2.2rem; margin-bottom: 0.5rem;">JusticePath</h1>', unsafe_allow_html=True)
    st.caption("AI-Powered Citizens' Legal Co-Pilot")
    st.markdown("---")
    
    page = st.radio(
        "Navigate Platform",
        [
            "Home Dashboard",
            "Browse Your Rights",
            "Problem Analyzer & Helper",
            "Letter & Complaint Draft Generator",
            "Document Language Simplifier",
            "Legal Research Assistant"
        ]
    )
    
    st.markdown("---")
    st.markdown('<p style="font-weight:600; color:#8b949e; font-size:0.9rem; text-transform:uppercase; letter-spacing:1px;">Jargon Helper</p>', unsafe_allow_html=True)
    jargon_terms = {
        "Pro Se": "Representing yourself in a court case without hiring a private lawyer.",
        "Injunction": "A court order that forces someone to stop doing something harmful right away.",
        "Tort": "A civil mistake or wrongdoing that causes harm to someone, resulting in legal liability.",
        "Affidavit": "A signed statement of facts made under oath that can be used as proof in a court.",
        "Statute": "A formal written law passed by a legislative assembly or government body.",
        "Plaintiff": "The person or party who starts a lawsuit by filing a complaint against someone else.",
        "Defendant": "The person or group being blamed or sued in a court case.",
        "Subpoena": "An official written request forcing someone to attend court or hand over evidence.",
        "Lien": "A legal claim or right against a piece of property until a debt is fully paid off.",
        "Amicus Curiae": "An outside expert or advisor who helps a court by providing extra knowledge on a case.",
        "Liable": "Legally responsible or to blame for paying or fixing a mistake.",
        "Malfeasance": "Illegal or intentionally wrong behavior, especially by a public official or company.",
        "Arbitration": "Settling a dispute out of court using an independent third person instead of a judge.",
        "Power of Attorney": "Legal permission given to someone else to act or sign documents on your behalf.",
        "Ex Parte": "A legal action or meeting done for or by one party without the other party being present."
    }
    selected_term = st.selectbox("Quick Dictionary Look-up", list(jargon_terms.keys()))
    st.caption(jargon_terms[selected_term])

# =====================================================
# MODULE 1: HOME DASHBOARD
# =====================================================

if page == "Home Dashboard":
    st.markdown('<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 0px;">JusticePath</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.3rem; color: #8b949e; margin-top: 5px;">Your Simple AI Tool to Understand Everyday Rights and Paperwork</p>', unsafe_allow_html=True)
    
    st.markdown("### Platform Availability Snapshot")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    with stat_col1:
        st.markdown('<div class="stat-box"><div class="stat-number">24+</div><div class="stat-label">Rights Covered</div></div>', unsafe_allow_html=True)
    with stat_col2:
        st.markdown('<div class="stat-box"><div class="stat-number">10</div><div class="stat-label">Legal Categories</div></div>', unsafe_allow_html=True)
    with stat_col3:
        st.markdown('<div class="stat-box"><div class="stat-number">5</div><div class="stat-label">AI Diagnostic Tools</div></div>', unsafe_allow_html=True)
    with stat_col4:
        st.markdown('<div class="stat-box"><div class="stat-number">PDF</div><div class="stat-label">Complaint Export</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #58a6ff; margin-top:0;">Learn About Your Rights</h3>
            <p style="color: #c9d1d9;">JusticePath clarifies confusing laws for regular citizens. Use these tools to figure out how to respond when a legal issue pops up:</p>
            <ul class="feature-list">
                <li>Search and view consumer, employee, and basic citizen rights.</li>
                <li>Find out which office or authority handles your specific issue.</li>
                <li>See what specific documents or receipts you need to save to stay safe.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #bc8cff; margin-top:0;">Simplify Complex Paperwork</h3>
            <p style="color: #c9d1d9;">Bypass difficult legal terms and quickly prepare the responses or questions you need:</p>
            <ul class="feature-list">
                <li>Create step-by-step custom action roadmaps for your problems.</li>
                <li>Auto-generate official complaint letters in plain text and PDF formats.</li>
                <li>Turn confusing, long terms into easy bullet points using AI.</li>
                <li>Ask custom questions answered directly from our stored master list database.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-text">
        <strong>Important Note:</strong> This website offers educational summaries and helpful information. It is not a real lawyer, does not provide legal representation, and cannot give certified legal advice.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="app-footer">
        JusticePath © 2026<br>
        <span style="font-size:0.8rem; color:#8b949e; font-weight:300; letter-spacing:0.5px;">Educational Awareness Platform • Not Legal Advice</span>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# MODULE 2: BROWSE YOUR RIGHTS
# =====================================================

elif page == "Browse Your Rights":
    st.markdown('<h1 class="gradient-text">Browse Your Rights</h1>', unsafe_allow_html=True)
    st.markdown("Look up basic citizen rules, legal protections, and government offices using the simple filters below.")
    
    search_mode = st.radio("Choose How to Browse", ["Pick From a Category List", "Search by Text Keyword"], horizontal=True)
    
    if search_mode == "Pick From a Category List":
        categories = get_categories()
        selected_category = st.selectbox("Select a Topic to View", categories)
        rights = get_rights_by_category(selected_category)
    else:
        query_word = st.text_input("Type a keyword or topic:", placeholder="Ex: internet fraud, landlord dispute, refund...")
        rights = search_rights(query_word) if query_word.strip() else rights_data

    st.markdown("---")
    
    if not rights:
        st.info("No matching rules found in the database. Try using simpler words.")
    else:
        for item in rights:
            with st.expander(f"Protection Topic: {item['right_name']}", expanded=False):
                st.markdown(f"**What this means:** \n{item['description']}")
                st.markdown(f"**Who handles this office:** <span class='authority-badge'>{item['authority']}</span>", unsafe_allow_html=True)
                
                if "laws" in item and item["laws"]:
                    st.markdown("<p style='margin-bottom:2px; margin-top:10px; font-weight:600;'>Official Laws Related to This:</p>", unsafe_allow_html=True)
                    for law in item["laws"]:
                        st.markdown(f"<span class='legal-badge'>{law}</span>", unsafe_allow_html=True)

# =====================================================
# MODULE 3: PROBLEM ANALYZER & HELPER
# =====================================================

elif page == "Problem Analyzer & Helper":
    st.markdown('<h1 class="gradient-text">Problem Analyzer and Action Helper</h1>', unsafe_allow_html=True)
    st.markdown("Describe what happened to check your category focus, find where to go, and see what documents you should collect.")

    st.markdown("**Try One-Click Quick Fill Demos:**")
    ex_col1, ex_col2, ex_col3, ex_col4 = st.columns(4)
    
    if "analyzer_input" not in st.session_state:
        st.session_state.analyzer_input = ""

    with ex_col1:
        if st.button("⚡ UPI Scam", use_container_width=True):
            st.session_state.analyzer_input = "I received a malicious phishing transaction text link, entered my credentials, and an unauthorized UPI debit cleared my account balance."
    with ex_col2:
        if st.button("⚡ Salary Not Received", use_container_width=True):
            st.session_state.analyzer_input = "My private corporate employer has withheld my compensation payouts for three months without justification and threatens immediate job loss."
    with ex_col3:
        if st.button("⚡ Defective Product", use_container_width=True):
            st.session_state.analyzer_input = "The electronics company delivered a cracked hardware display monitor, refused to replace the item, and denied all customer return requests."
    with ex_col4:
        if st.button("⚡ Illegal Eviction", use_container_width=True):
            st.session_state.analyzer_input = "My residential landlord has locked out entry privileges, demands double security payments, and threatens removal without legal notification paperwork."

    issue = st.text_area("Type your situation details here:", value=st.session_state.analyzer_input, placeholder="Select an example above or write what happened in your own words...")
    
    if st.button("Analyze My Issue", type="primary"):
        if issue.strip():
            with st.spinner("Reviewing your details..."):
                category = classify_issue(issue)
                evidence = generate_evidence_checklist(issue)
                authorities = find_relevant_authorities(issue)
                roadmap = generate_action_roadmap(issue)
                
            st.toast("Analysis Completed Successfully!")
            
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric(label="Problem Category Type", value=category.split()[0] if " " in category else category)
            with m2:
                st.metric(label="Estimated Case Severity", value="Standard Review")
            with m3:
                st.metric(label="Typical Handling Window", value="15-30 Open Days")
                
            st.markdown("---")
            
            col_left, col_right = st.columns([1, 2])
            with col_left:
                st.markdown(f"""
                <div class="result-card">
                    <div class="card-label">Predicted Category Badge</div>
                    <div class="category-badge">[ {category} ]</div>
                </div>
                """, unsafe_allow_html=True)
                
                auth_html = "".join([f"<div style='color:#58a6ff; font-weight:600; margin-bottom:4px;'>• {item}</div>" for item in authorities])
                st.markdown(f"""
                <div class="result-card">
                    <div class="card-label">Primary Jurisdictional Authorities</div>
                    <div style="margin-top:8px;">{auth_html}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_right:
                tab1, tab2 = st.tabs(["Proof Items to Keep", "Your Next Action Steps"])
                
                with tab1:
                    st.markdown("Ensure you collect and safeguard the following records inside your claim package:")
                    for item in evidence:
                        st.checkbox(item, key=f"ev_{item}")
                        
                with tab2:
                    st.markdown("Recommended linear step-by-step guidance resolution procedures:")
                    for idx, item in enumerate(roadmap, 1):
                        st.markdown(f"**Step {idx}:** {item}")
        else:
            st.warning("Please type or select an issue description first.")

# =====================================================
# MODULE 4: LETTER & COMPLAINT DRAFT GENERATOR
# =====================================================

elif page == "Letter & Complaint Draft Generator":
    st.markdown('<h1 class="gradient-text">Letter and Complaint Draft Generator</h1>', unsafe_allow_html=True)
    st.markdown("Turn your problem statement into a properly formatted official document or letter ready to send.")

    issue = st.text_area("What is the complaint about?", placeholder="Write the details here...")
    
    st.markdown("### Personalize Document Details")
    cx1, cx2, cx3 = st.columns(3)
    with cx1:
        user_name = st.text_input("Your Full Name:", value="Citizen Name")
    with cx2:
        curr_date = st.text_input("Today's Date:", value="June 18, 2026")
    with cx3:
        user_contact = st.text_input("Your Phone or Email (Optional):", placeholder="Ex: email@example.com")

    if st.button("Generate Downloadable Draft Package", type="primary"):
        if issue.strip():
            with st.spinner("Drafting your document..."):
                complaint = generate_complaint(issue, citizen_name=user_name, date_str=curr_date, contact_info=user_contact)
                pdf_file = export_complaint_pdf(complaint)
            
            st.subheader("Your Generated Letter Preview")
            st.text_area("Review your document text below:", complaint, height=350)
            
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="Download and Print Document PDF",
                    data=file,
                    file_name="JusticePath_Official_Grievance.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.warning("Please explain what the complaint is about before creating the file.")

# =====================================================
# MODULE 5: DOCUMENT LANGUAGE SIMPLIFIER
# =====================================================

elif page == "Document Language Simplifier":
    st.markdown('<h1 class="gradient-text">Document Language Simplifier</h1>', unsafe_allow_html=True)
    st.markdown("Paste or upload confusing legal contracts, updates, or articles to turn them into easy bullet points.")

    u1, u2 = st.columns(2)
    with u1:
        uploaded_file = st.file_uploader("Option 1: Upload a PDF document", type=["pdf"])
    with u2:
        pasted_text = st.text_area("Option 2: Paste difficult text here instead", height=125)

    if st.button("Simplify This Text", type="primary"):
        text = ""
        if uploaded_file:
            with st.spinner("Reading your PDF file..."):
                text = read_pdf_text(uploaded_file)
        elif pasted_text:
            text = pasted_text
            
        if text:
            with st.spinner("Converting into simple words..."):
                result = simplify_legal_text(text)
                
            st.markdown("### Easy English Summary Explanation")
            st.markdown(f'<div class="feature-card">{result}</div>', unsafe_allow_html=True)
        else:
            st.error("Please add text by uploading a PDF file or pasting text directly.")

# =====================================================
# MODULE 6: LEGAL RESEARCH ASSISTANT
# =====================================================

elif page == "Legal Research Assistant":
    st.markdown('<h1 class="gradient-text">Legal Research Assistant</h1>', unsafe_allow_html=True)
    st.markdown("Query the active context vectors seamlessly. Answers are mapped directly to corresponding database elements to guarantee validation accuracy.")

    query = st.text_input("Enter your direct legal query:", placeholder="Example: What fallback options exist if an online portal scams payment profiles?")
    
    if st.button("Query Knowledge Vectors", type="primary"):
        if query.strip():
            with st.spinner("Scanning dense FAISS index vectors and computing contextual frames..."):
                answer = rag_legal_analyzer(query)
                
            st.markdown("### System Response Guidance")
            st.markdown(f'<div class="feature-card" style="border-left: 4px solid #58a6ff;">{answer}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please type a clear operational question phrase.")
