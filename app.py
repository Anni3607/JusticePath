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
    with open(
        "data/rights/master_rights.json",
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)

rights_data = load_rights()

# =====================================================
# RIGHTS EXPLORER FUNCTIONS
# =====================================================

def get_categories():
    categories = sorted(
        list(
            set(
                item["category"]
                for item in rights_data
            )
        )
    )
    return categories


def get_rights_by_category(category):
    return [
        item
        for item in rights_data
        if item["category"] == category
    ]


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
# ISSUE CLASSIFIER
# =====================================================

def classify_issue(user_issue):
    issue = user_issue.lower()
    if any(
        word in issue
        for word in ["fraud", "scam", "upi", "cyber", "hack", "otp"]
    ):
        return "Cybercrime Rights"
    elif any(
        word in issue
        for word in ["salary", "employer", "job", "work", "harassment"]
    ):
        return "Employment Rights"
    elif any(
        word in issue
        for word in ["product", "refund", "consumer", "defective"]
    ):
        return "Consumer Rights"
    elif any(
        word in issue
        for word in ["rent", "tenant", "landlord", "eviction"]
    ):
        return "Tenant Rights"
    elif any(
        word in issue
        for word in ["college", "school", "university", "exam"]
    ):
        return "Education Rights"
    return "Constitutional Rights"

# =====================================================
# EVIDENCE CHECKLIST
# =====================================================

evidence_templates = {
    "Cybercrime Rights": ["Screenshots", "Transaction Records", "Bank Statements", "Phone Numbers", "Emails"],
    "Employment Rights": ["Offer Letter", "Salary Slips", "Employment Contract", "Emails", "Messages"],
    "Consumer Rights": ["Invoice", "Receipt", "Product Images", "Warranty Documents"],
    "Tenant Rights": ["Rent Agreement", "Rent Receipts", "Photos", "Communication Records"],
    "Education Rights": ["Admission Documents", "Fee Receipts", "Emails", "Academic Records"]
}

def generate_evidence_checklist(user_issue):
    category = classify_issue(user_issue)
    return evidence_templates.get(category, [])

# =====================================================
# AUTHORITY FINDER
# =====================================================

authority_mapping = {
    "Cybercrime Rights": ["National Cyber Crime Portal", "Cyber Crime Cell"],
    "Employment Rights": ["Labour Commissioner", "HR Department"],
    "Consumer Rights": ["Consumer Commission"],
    "Tenant Rights": ["Civil Court"],
    "Education Rights": ["Education Department"]
}

def find_relevant_authorities(user_issue):
    category = classify_issue(user_issue)
    return authority_mapping.get(category, [])

# =====================================================
# ACTION ROADMAP
# =====================================================

roadmap_templates = {
    "Cybercrime Rights": ["Preserve screenshots", "Save transaction details", "Contact bank immediately", "Report on National Cyber Crime Portal", "File FIR if required"],
    "Employment Rights": ["Collect salary records", "Preserve communication with employer", "Submit written complaint", "Contact HR or management", "Approach Labour Commissioner"],
    "Consumer Rights": ["Collect invoice and receipt", "Document product issue", "Contact seller", "Request refund/replacement", "File consumer complaint"],
    "Tenant Rights": ["Collect rent agreement", "Preserve payment records", "Document dispute", "Issue written notice", "Seek civil remedy"],
    "Education Rights": ["Collect academic records", "Preserve communication", "Contact institution", "Submit formal representation", "Escalate to authority"],
    "Constitutional Rights": ["Document incident", "Collect evidence", "Preserve witness details", "Submit representation", "Seek legal remedy"]
}

def generate_action_roadmap(user_issue):
    category = classify_issue(user_issue)
    return roadmap_templates.get(category, [])

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

{citizen_name}{contact_block}
"""
    return complaint

# =====================================================
# PDF EXPORT
# =====================================================

def export_complaint_pdf(complaint_text):
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
    
    # Simplified Navigation Titles for Easy Understanding
    page = st.radio(
        "Navigate Platform",
        [
            "Home Dashboard",
            "Browse Your Rights",
            "Problem Analyzer & Helper",
            "Letter & Complaint Draft Generator",
            "Document Language Simplifier",
            "Smart Legal Question AI"
        ]
    )
    
    # EXPANDED THEMATIC FEATURE: Dictionary Reference Widget (+10 Terms, 15 Total)
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

    # BRAND NEW FEATURE: Preset Dropdown Helper Examples for Naive Users
    st.markdown("**Need help starting? Choose a common scenario example below, or write your own custom case text:**")
    preset_example = st.selectbox(
        "Optional: Click here to view sample scenarios",
        [
            "Custom (Write your own description below)",
            "An online store took my money but never shipped my order or gave a refund.",
            "My boss is withholding my monthly salary and threatening termination without cause.",
            "My landlord is keeping my security deposit and forcing immediate eviction without notice.",
            "I received a fake UPI payment scam text and lost money from my bank account."
        ]
    )

    default_text = "" if preset_example.startswith("Custom") else preset_example
    issue = st.text_area("Type your situation details here:", value=default_text, placeholder="Write what happened in your own words...")
    
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
                st.markdown("### 🏛️ Main Category")
                st.info(category)
                
                st.markdown("### 🏢 Where to File This")
                for item in authorities:
                    st.markdown(f"**{item}**")
            
            with col_right:
                tab1, tab2 = st.tabs(["Proof Items to Keep", "Your Next Action Steps"])
                
                with tab1:
                    st.markdown("Make sure to hold onto these items to protect your claim:")
                    for item in evidence:
                        st.checkbox(item, key=f"ev_{item}")
                        
                with tab2:
                    st.markdown("Follow these steps to resolve your issue:")
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
    
    # BRAND NEW FEATURE: Interactive Customizer Overlays for Official Formatting
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
# MODULE 6: SMART LEGAL QUESTION AI
# =====================================================

elif page == "Smart Legal Question AI":
    st.markdown('<h1 class="gradient-text">Smart Legal Question AI</h1>', unsafe_allow_html=True)
    st.markdown("Ask an open-ended question about rules, processes, or consumer guidelines. The AI will answer based on our stored master laws.")

    query = st.text_input("Ask your question here:", placeholder="Example: What happens if an online site refuses to take back a broken product?")
    
    if st.button("Get My Answer Summary", type="primary"):
        if query.strip():
            with st.spinner("Checking our master guidelines database..."):
                answer = rag_legal_analyzer(query)
                
            st.markdown("### Explanatory AI Guidance Answer")
            st.markdown(f'<div class="feature-card" style="border-left: 4px solid #58a6ff;">{answer}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please write a question phrase first.")
