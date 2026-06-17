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
