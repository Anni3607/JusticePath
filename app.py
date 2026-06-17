import streamlit as st
import json
import google.generativeai as genai
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
from fpdf import FPDF
from PyPDF2 import PdfReader

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="JusticePath",
    layout="wide"
)

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


def get_rights_by_category(
    category
):

    return [

        item

        for item in rights_data

        if item["category"] == category
    ]


def search_rights(
    keyword
):

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

def classify_issue(
    user_issue
):

    issue = user_issue.lower()

    if any(
        word in issue
        for word in [
            "fraud",
            "scam",
            "upi",
            "cyber",
            "hack",
            "otp"
        ]
    ):
        return "Cybercrime Rights"

    elif any(
        word in issue
        for word in [
            "salary",
            "employer",
            "job",
            "work",
            "harassment"
        ]
    ):
        return "Employment Rights"

    elif any(
        word in issue
        for word in [
            "product",
            "refund",
            "consumer",
            "defective"
        ]
    ):
        return "Consumer Rights"

    elif any(
        word in issue
        for word in [
            "rent",
            "tenant",
            "landlord",
            "eviction"
        ]
    ):
        return "Tenant Rights"

    elif any(
        word in issue
        for word in [
            "college",
            "school",
            "university",
            "exam"
        ]
    ):
        return "Education Rights"

    return "Constitutional Rights"

# =====================================================
# EVIDENCE CHECKLIST
# =====================================================

evidence_templates = {

    "Cybercrime Rights": [
        "Screenshots",
        "Transaction Records",
        "Bank Statements",
        "Phone Numbers",
        "Emails"
    ],

    "Employment Rights": [
        "Offer Letter",
        "Salary Slips",
        "Employment Contract",
        "Emails",
        "Messages"
    ],

    "Consumer Rights": [
        "Invoice",
        "Receipt",
        "Product Images",
        "Warranty Documents"
    ],

    "Tenant Rights": [
        "Rent Agreement",
        "Rent Receipts",
        "Photos",
        "Communication Records"
    ],

    "Education Rights": [
        "Admission Documents",
        "Fee Receipts",
        "Emails",
        "Academic Records"
    ]
}

def generate_evidence_checklist(
    user_issue
):

    category = classify_issue(
        user_issue
    )

    return evidence_templates.get(
        category,
        []
    )

# =====================================================
# AUTHORITY FINDER
# =====================================================

authority_mapping = {

    "Cybercrime Rights":
    [
        "National Cyber Crime Portal",
        "Cyber Crime Cell"
    ],

    "Employment Rights":
    [
        "Labour Commissioner",
        "HR Department"
    ],

    "Consumer Rights":
    [
        "Consumer Commission"
    ],

    "Tenant Rights":
    [
        "Civil Court"
    ],

    "Education Rights":
    [
        "Education Department"
    ]
}

def find_relevant_authorities(
    user_issue
):

    category = classify_issue(
        user_issue
    )

    return authority_mapping.get(
        category,
        []
    )
# =====================================================
# ACTION ROADMAP
# =====================================================

roadmap_templates = {

    "Cybercrime Rights": [
        "Preserve screenshots",
        "Save transaction details",
        "Contact bank immediately",
        "Report on National Cyber Crime Portal",
        "File FIR if required"
    ],

    "Employment Rights": [
        "Collect salary records",
        "Preserve communication with employer",
        "Submit written complaint",
        "Contact HR or management",
        "Approach Labour Commissioner"
    ],

    "Consumer Rights": [
        "Collect invoice and receipt",
        "Document product issue",
        "Contact seller",
        "Request refund/replacement",
        "File consumer complaint"
    ],

    "Tenant Rights": [
        "Collect rent agreement",
        "Preserve payment records",
        "Document dispute",
        "Issue written notice",
        "Seek civil remedy"
    ],

    "Education Rights": [
        "Collect academic records",
        "Preserve communication",
        "Contact institution",
        "Submit formal representation",
        "Escalate to authority"
    ],

    "Constitutional Rights": [
        "Document incident",
        "Collect evidence",
        "Preserve witness details",
        "Submit representation",
        "Seek legal remedy"
    ]
}

def generate_action_roadmap(
    user_issue
):

    category = classify_issue(
        user_issue
    )

    return roadmap_templates.get(
        category,
        []
    )

# =====================================================
# COMPLAINT GENERATOR
# =====================================================

def generate_complaint(
    user_issue
):

    category = classify_issue(
        user_issue
    )

    authorities = find_relevant_authorities(
        user_issue
    )

    authority = (
        authorities[0]
        if authorities
        else "Concerned Authority"
    )

    complaint = f"""
To,
{authority}

Subject: Complaint regarding {category}

Respected Sir/Madam,

I wish to submit a complaint regarding the following issue:

{user_issue}

I request your office to examine the matter and take appropriate action as per applicable laws.

I am willing to provide supporting evidence and cooperate fully with any investigation.

Thank you.

Sincerely,

Citizen
"""

    return complaint

# =====================================================
# PDF EXPORT
# =====================================================

def export_complaint_pdf(
    complaint_text
):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        size=12
    )

    pdf.multi_cell(
        0,
        10,
        complaint_text
    )

    pdf.output(
        "complaint.pdf"
    )

    return "complaint.pdf"

# =====================================================
# PDF READER
# =====================================================

def read_pdf_text(
    uploaded_file
):

    reader = PdfReader(
        uploaded_file
    )

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted

    return text

# =====================================================
# LEGAL LANGUAGE SIMPLIFIER
# =====================================================

def simplify_legal_text(
    document_text
):

    prompt = f"""
You are a legal language simplifier.

Convert the following legal text into simple English.

Rules:

1. Keep meaning unchanged
2. Use easy language
3. Explain legal terms
4. Use bullet points
5. Maximum 300 words

Document:

{document_text}
"""

    response = model.generate_content(
        prompt
    )

    return response.text

# =====================================================
# FAISS + EMBEDDING MODEL
# =====================================================

@st.cache_resource
def load_embedding_model():

    return SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

embedding_model = load_embedding_model()

# =====================================================
# BUILD DOCUMENTS
# =====================================================

documents = []

for item in rights_data:

    doc = f"""
Category: {item['category']}
Right: {item['right_name']}
Description: {item['description']}
Authority: {item['authority']}
"""

    documents.append(
        doc
    )

# =====================================================
# EMBEDDINGS
# =====================================================

embeddings = embedding_model.encode(
    documents
)

embeddings = np.array(
    embeddings,
    dtype=np.float32
)

# =====================================================
# FAISS INDEX
# =====================================================

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(
    dimension
)

index.add(
    embeddings
)

# =====================================================
# RETRIEVE CONTEXT
# =====================================================

def retrieve_context(
    query,
    top_k=3
):

    query_embedding = embedding_model.encode(
        [query]
    )

    query_embedding = np.array(
        query_embedding,
        dtype=np.float32
    )

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    context = ""

    for idx in indices[0]:

        context += documents[idx]
        context += "\n\n"

    return context

# =====================================================
# RAG LEGAL ANALYZER
# =====================================================

def rag_legal_analyzer(
    user_issue
):

    retrieved_context = retrieve_context(
        user_issue
    )

    prompt = f"""
You are JusticePath.

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

Keep response concise.
"""

    response = model.generate_content(
        prompt
    )

    return response.text

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title(
    "JusticePath"
)

page = st.sidebar.radio(

    "Navigation",

    [
        "Home",
        "Rights Explorer",
        "Legal Problem Analyzer",
        "Complaint Generator",
        "Legal Simplifier",
        "RAG Legal Assistant"
    ]
)

# =====================================================
# HOME
# =====================================================

if page == "Home":

    st.title(
        "JusticePath"
    )

    st.subheader(
        "AI-Powered Legal Navigation and Awareness Platform"
    )

    st.write(
        """
JusticePath helps citizens:

• Understand legal rights

• Identify relevant authorities

• Generate evidence checklists

• Create complaint drafts

• Simplify legal language

• Retrieve legal information using RAG

Disclaimer:
This platform provides educational information only and does not constitute legal advice.
"""
    )

# =====================================================
# RIGHTS EXPLORER
# =====================================================

elif page == "Rights Explorer":

    st.title(
        "Rights Explorer"
    )

    categories = get_categories()

    selected_category = st.selectbox(
        "Select Category",
        categories
    )

    rights = get_rights_by_category(
        selected_category
    )

    for item in rights:

        with st.expander(
            item["right_name"]
        ):

            st.write(
                item["description"]
            )

            st.write(
                f"Authority: {item['authority']}"
            )

            if "laws" in item:

                st.write(
                    "Relevant Laws:"
                )

                for law in item["laws"]:

                    st.write(
                        f"- {law}"
                    )

# =====================================================
# LEGAL PROBLEM ANALYZER
# =====================================================

elif page == "Legal Problem Analyzer":

    st.title(
        "Legal Problem Analyzer"
    )

    issue = st.text_area(
        "Describe your legal issue"
    )

    if st.button(
        "Analyze"
    ):

        category = classify_issue(
            issue
        )

        evidence = generate_evidence_checklist(
            issue
        )

        authorities = find_relevant_authorities(
            issue
        )

        roadmap = generate_action_roadmap(
            issue
        )

        st.subheader(
            "Predicted Category"
        )

        st.success(
            category
        )

        st.subheader(
            "Evidence Checklist"
        )

        for item in evidence:

            st.write(
                f"• {item}"
            )

        st.subheader(
            "Relevant Authorities"
        )

        for item in authorities:

            st.write(
                f"• {item}"
            )

        st.subheader(
            "Recommended Roadmap"
        )

        for item in roadmap:

            st.write(
                f"• {item}"
            )

# =====================================================
# COMPLAINT GENERATOR
# =====================================================

elif page == "Complaint Generator":

    st.title(
        "Complaint Generator"
    )

    issue = st.text_area(
        "Describe the issue"
    )

    if st.button(
        "Generate Complaint"
    ):

        complaint = generate_complaint(
            issue
        )

        st.text_area(
            "Generated Complaint",
            complaint,
            height=300
        )

        pdf_file = export_complaint_pdf(
            complaint
        )

        with open(
            pdf_file,
            "rb"
        ) as file:

            st.download_button(
                label="Download PDF",
                data=file,
                file_name="complaint.pdf",
                mime="application/pdf"
            )

# =====================================================
# LEGAL SIMPLIFIER
# =====================================================

elif page == "Legal Simplifier":

    st.title(
        "Legal Language Simplifier"
    )

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    pasted_text = st.text_area(
        "Or paste legal text"
    )

    if st.button(
        "Simplify"
    ):

        text = ""

        if uploaded_file:

            text = read_pdf_text(
                uploaded_file
            )

        elif pasted_text:

            text = pasted_text

        if text:

            result = simplify_legal_text(
                text
            )

            st.subheader(
                "Simplified Version"
            )

            st.write(
                result
            )

# =====================================================
# RAG LEGAL ASSISTANT
# =====================================================

elif page == "RAG Legal Assistant":

    st.title(
        "RAG Legal Assistant"
    )

    query = st.text_area(
        "Ask a legal question"
    )

    if st.button(
        "Get Guidance"
    ):

        answer = rag_legal_analyzer(
            query
        )

        st.subheader(
            "Response"
        )

        st.write(
            answer
        )
