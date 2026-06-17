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
    page_title="JusticePath | AI Legal Navigator",
    page_icon="⚖️",
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
        content: "⚡";
        margin-right: 12px;
        font-size: 0.9rem;
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
            keyword in item["right_name"].lower()
            or
            keyword in item["description"].lower()
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
# COMPLAINT GENERATOR
# =====================================================

def generate_complaint(user_issue):
    category = classify_issue(user_issue)
    authorities = find_relevant_authorities(user_issue)
    authority = authorities[0] if authorities else "Concerned Authority"

    complaint = f"""To,
{authority}

Subject: Complaint regarding {category}

Respected Sir/Madam,

I wish to submit a complaint regarding the following issue:

{user_issue}

I request your office to examine the matter and take appropriate action as per applicable laws.

I am willing to provide supporting evidence and cooperate fully with any investigation.

Thank you.

Sincerely,
Citizen"""
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
# SIDEBAR NAVIGATION
# =====================================================

with st.sidebar:
    st.markdown('<h1 class="gradient-text" style="font-size: 2.2rem; margin-bottom: 0.5rem;">JusticePath</h1>', unsafe_allow_html=True)
    st.caption("AI-Powered Citizens' Legal Co-Pilot")
    st.markdown("---")
    
    page = st.radio(
        "Navigate Platform",
        [
            "🏠 Home",
            "🔍 Rights Explorer",
            "🛡️ Legal Problem Analyzer",
            "📝 Complaint Generator",
            "💡 Legal Simplifier",
            "🤖 RAG Legal Assistant"
        ]
    )

# =====================================================
# MODULE 1: HOME
# =====================================================

if "Home" in page:
    st.markdown('<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 0px;">JusticePath</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.3rem; color: #8b949e; margin-top: 5px;">AI-Powered Legal Navigation & Awareness Framework</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #58a6ff; margin-top:0;">Empowering Citizen Rights</h3>
            <p style="color: #c9d1d9;">JusticePath bridges the gap between complex constitutional legal frameworks and everyday citizens, giving you tools to navigate unexpected legal problems easily.</p>
            <ul class="feature-list">
                <li>Instantly query & filter constitutional and consumer rights.</li>
                <li>Analyze real-world situations to extract clear legal categorization.</li>
                <li>Identify exact governing authorities for faster reporting lines.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #bc8cff; margin-top:0;">Automation Engine Capabilities</h3>
            <p style="color: #c9d1d9;">Harness optimized intelligence features to bypass manual legal document processing stress:</p>
            <ul class="feature-list">
                <li>Build structural action roadmaps instantly.</li>
                <li>Auto-generate legal standard complaint letters seamlessly.</li>
                <li>Deconstruct confusing dense legal paperwork into simple terms.</li>
                <li>RAG-augmented answers grounded strictly in master knowledge base vectors.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-text">
        <strong>Disclaimer Notice:</strong> This software architecture platform provides educational, general knowledge resources compiled programmatically via retrieval models. It does not provide actionable legal representation, certified legal advice, or professional corporate counsel under judicial practice standards.
    </div>
    """, unsafe_html=True)

# =====================================================
# MODULE 2: RIGHTS EXPLORER
# =====================================================

elif "Rights Explorer" in page:
    st.markdown('<h1 class="gradient-text">🔍 Rights Explorer</h1>', unsafe_allow_html=True)
    st.markdown("Select a legal category below to browse through indexed citizen rights and regulatory bodies.")
    
    categories = get_categories()
    selected_category = st.selectbox("Filter by Category Focus", categories)
    
    st.markdown("---")
    rights = get_rights_by_category(selected_category)
    
    for item in rights:
        with st.expander(f"📋 {item['right_name']}", expanded=False):
            st.markdown(f"**Description:** \n{item['description']}")
            st.markdown(f"📌 **Primary Enforcement Authority:** `{item['authority']}`")
            
            if "laws" in item and item["laws"]:
                st.markdown("**Statutory Frameworks & Laws:**")
                for law in item["laws"]:
                    st.markdown(f"- `<code style='color:#ff7b72'>{law}</code>`", unsafe_allow_html=True)

# =====================================================
# MODULE 3: LEGAL PROBLEM ANALYZER
# =====================================================

elif "Legal Problem Analyzer" in page:
    st.markdown('<h1 class="gradient-text">🛡️ Legal Problem Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("Input your current circumstances or problem details below. The heuristic model will classify the focus and generate structured preparation strategies.")

    issue = st.text_area("Describe the dispute context or incident thoroughly:", placeholder="Ex: My landlord is forcing immediate eviction notice without paying back security deposits...")
    
    if st.button("Execute Diagnostic Analysis", type="primary"):
        if issue.strip():
            with st.spinner("Classifying contexts & generating roadmaps..."):
                category = classify_issue(issue)
                evidence = generate_evidence_checklist(issue)
                authorities = find_relevant_authorities(issue)
                roadmap = generate_action_roadmap(issue)
                
            st.toast("Analysis Completed Successfully!", icon="✅")
            
            col_left, col_right = st.columns([1, 2])
            with col_left:
                st.markdown("### Classified Category")
                st.info(f"⚖️ {category}")
                
                st.markdown("### Relevant Authorities")
                for item in authorities:
                    st.markdown(f"🏛️ **{item}**")
            
            with col_right:
                tab1, tab2 = st.tabs(["📋 Vital Evidence Checklist", "🗺️ Action Roadmap"])
                
                with tab1:
                    st.markdown("Ensure you collect and safeguard the following records:")
                    for item in evidence:
                        st.checkbox(item, key=f"ev_{item}")
                        
                with tab2:
                    st.markdown("Recommended linear resolution steps:")
                    for idx, item in enumerate(roadmap, 1):
                        st.markdown(f"**Step {idx}:** {item}")
        else:
            st.warning("Please type some case details before initializing analysis workflows.")

# =====================================================
# MODULE 4: COMPLAINT GENERATOR
# =====================================================

elif "Complaint Generator" in page:
    st.markdown('<h1 class="gradient-text">📝 Formal Complaint Generator</h1>', unsafe_allow_html=True)
    st.markdown("Draft structured legal complaint templates automatically according to your specific grievance variables.")

    issue = st.text_area("Provide specific details for the complaint draft:", placeholder="Ex: Defective transmission delivered on ecommerce invoice order #902341...")
    
    if st.button("Generate Document Package", type="primary"):
        if issue.strip():
            with st.spinner("Drafting standard grievance templates..."):
                complaint = generate_complaint(issue)
                pdf_file = export_complaint_pdf(complaint)
            
            st.subheader("Generated Grievance Correspondence")
            st.text_area("Draft Output Preview", complaint, height=350)
            
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="📥 Download Ready-To-Print PDF Document",
                    data=file,
                    file_name="JusticePath_Official_Complaint.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.warning("Grievance context field cannot be left blank.")

# =====================================================
# MODULE 5: LEGAL SIMPLIFIER
# =====================================================

elif "Legal Simplifier" in page:
    st.markdown('<h1 class="gradient-text">💡 Legal Language Simplifier</h1>', unsafe_allow_html=True)
    st.markdown("Deconstruct dense multi-layered legal terminology or regulatory briefs into scannable clear takeaways instantly.")

    u1, u2 = st.columns(2)
    with u1:
        uploaded_file = st.file_uploader("Option A: Upload Source PDF File Document", type=["pdf"])
    with u2:
        pasted_text = st.text_area("Option B: Paste Raw Legal Contracts/Clauses here", height=125)

    if st.button("Simplify Language Structure", type="primary"):
        text = ""
        if uploaded_file:
            with st.spinner("Parsing PDF content matrices..."):
                text = read_pdf_text(uploaded_file)
        elif pasted_text:
            text = pasted_text
            
        if text:
            with st.spinner("Processing plain language transcription..."):
                result = simplify_legal_text(text)
                
            st.markdown("### ✨ Translated Plain English Summary")
            st.markdown(f'<div class="feature-card">{result}</div>', unsafe_allow_html=True)
        else:
            st.error("Please supply text variables through either the file upload utility or copy-paste field parameters.")

# =====================================================
# MODULE 6: RAG LEGAL ASSISTANT
# =====================================================

elif "RAG Legal Assistant" in page:
    st.markdown('<h1 class="gradient-text">🤖 Vector-Grounded RAG Legal Assistant</h1>', unsafe_allow_html=True)
    st.markdown("Query the active context vectors seamlessly. Answers are mapped directly to corresponding database elements to guarantee validation accuracy.")

    query = st.text_input("Enter your direct legal query:", placeholder="Ex: What fallback options exist if an online portal scams payment profiles?")
    
    if st.button("Query Knowledge Vectors", type="primary"):
        if query.strip():
            with st.spinner("Scanning dense FAISS index vectors & computing contextual frames..."):
                answer = rag_legal_analyzer(query)
                
            st.markdown("### System Response Guidance")
            st.markdown(f'<div class="feature-card" style="border-left: 4px solid #58a6ff;">{answer}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please type a clear operational question phrase.")
