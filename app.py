# app.py — RAG-based Mutual Fund FAQ Chatbot (Groww × HDFC AMC)
# Run with: streamlit run app.py

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Groww — Mutual Fund FAQ Assistant",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Base dark theme */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e2129;
    }
    .sidebar-header {
        font-weight: bold;
        color: white;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    .sidebar-text {
        font-size: 0.85rem;
        color: #d1d5db;
        line-height: 1.5;
        margin-bottom: 15px;
    }
    
    /* Green hero header */
    .hero-container {
        background-color: #00805c;
        border-radius: 12px;
        padding: 24px;
        color: white;
        margin-bottom: 24px;
    }
    .hero-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .hero-subtitle {
        font-size: 0.9rem;
        color: #e0f2fe;
    }
    
    /* Disclaimer alert */
    .alert-box {
        background-color: #1a1a14;
        border-left: 4px solid #eab308;
        border-radius: 8px;
        padding: 16px;
        color: #d1d5db;
        font-size: 0.85rem;
        line-height: 1.5;
        margin-bottom: 30px;
    }
    .alert-box strong {
        color: white;
    }
    
    /* Button styling for examples */
    .stButton > button {
        background-color: transparent;
        border: 1px solid #374151;
        color: #d1d5db;
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        border-color: #6b7280;
        color: white;
    }
    
    /* Chat input styling to match screenshot */
    [data-testid="stChatInput"] {
        border-radius: 12px !important;
        background-color: #1e2129 !important;
        border: 1px solid #374151 !important;
    }
    
    /* Chat message styling */
    .chat-user {
        background-color: #1e2129;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
        color: white;
    }
    .chat-assistant {
        background-color: transparent;
        border-left: 2px solid #00805c;
        padding: 12px 16px;
        margin-bottom: 24px;
        color: #d1d5db;
    }
    .chat-source {
        font-size: 0.8rem;
        color: #9ca3af;
        margin-top: 8px;
    }
    .chat-source a {
        color: #38bdf8;
        text-decoration: none;
    }
    
    /* Bottom footer note */
    .footer-note {
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 40px;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-header">Scope</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text"><strong>AMC:</strong> HDFC Asset Management Company Ltd</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text"><strong>Schemes:</strong> Top 100, Flexi Cap, Mid-Cap Opportunities</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text"><strong>Sources:</strong> Official AMC, AMFI, SEBI pages only</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown('<div class="sidebar-header">Known Limits</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text">No real-time NAV or returns data</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text">No PII collected or stored</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text">No performance comparisons</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="font-size: 0.7rem; color: #6b7280; margin-top: 20px;">Last updated from sources: March 2025</div>', unsafe_allow_html=True)

# ── Main Content Area ─────────────────────────────────────────────────────────

# Hero
st.markdown("""
<div class="hero-container">
    <div class="hero-title">📊 Groww — Mutual Fund FAQ Assistant</div>
    <div class="hero-subtitle">HDFC Asset Management Company • Top 100 • Flexi Cap • Mid-Cap</div>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="alert-box">
    ⚠️ <strong>Facts-only. No investment advice.</strong> This tool provides factual information about mutual fund scheme parameters (expense ratio, exit load, SIP minimum, lock-in, benchmark, riskometer) sourced from official AMC/AMFI/SEBI pages only. It does not provide investment advice, recommendations, or return projections. Please consult a SEBI-registered investment adviser before making any investment decisions.
</div>
""", unsafe_allow_html=True)

# ── Example questions row ─────────────────────────────────────────────────────
st.markdown("💡 **Try these example questions:**")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Exit load — Top 100?", use_container_width=True):
        st.session_state["query_input"] = "What is the exit load for HDFC Top 100 Fund?"
with col2:
    if st.button("Flexi Cap riskometer?", use_container_width=True):
        st.session_state["query_input"] = "What is the riskometer level of HDFC Flexi Cap Fund?"
with col3:
    if st.button("Min SIP — Mid-Cap?", use_container_width=True):
        st.session_state["query_input"] = "What is the minimum SIP for HDFC Mid-Cap Opportunities Fund?"

st.markdown("<br><hr style='border-color: #374151; margin: 0;'><br>", unsafe_allow_html=True)

# ── Initialize session state ──────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "query_input" not in st.session_state:
    st.session_state.query_input = ""

# ── Lazy-load RAG components ──────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_rag():
    from rag_engine import load_index, retrieve
    load_index()  # pre-build index
    return retrieve

retrieve_fn = load_rag()

# ── Chat history display ──────────────────────────────────────────────────────
for item in reversed(st.session_state.chat_history):
    q = item["query"]
    r = item["result"]
    refused = r.get("refused", False)
    
    st.markdown(f'<div class="chat-user">{q}</div>', unsafe_allow_html=True)
    
    if refused:
        st.markdown(
            f'<div class="chat-assistant">⚠️ {r["answer"]}<div class="chat-source">📎 Learn more: <a href="{r["source"]}" target="_blank">{r["source"]}</a></div></div>',
            unsafe_allow_html=True,
        )
    else:
        ans = r["answer"]
        if "source:" in ans.lower():
            # If LLM included source, just display it
            st.markdown(f'<div class="chat-assistant">🤖 {ans.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="chat-assistant">🤖 {ans}<div class="chat-source">📎 Source: <a href="{r["source"]}" target="_blank">{r["source"]}</a></div></div>',
                unsafe_allow_html=True,
            )

# ── Input (st.chat_input) ─────────────────────────────────────────────────────
# We check if there's a pre-filled query from the buttons, otherwise use chat_input
prompt = st.chat_input("Ask a factual question about an HDFC fund...")

# Handle default query injection
submit_query = prompt
if st.session_state.get("query_input"):
    submit_query = st.session_state["query_input"]
    st.session_state["query_input"] = "" # clear it

if submit_query:
    st.markdown(f'<div class="chat-user">{submit_query}</div>', unsafe_allow_html=True)
    with st.spinner("Searching knowledge base…"):
        from llm import get_answer
        chunks = retrieve_fn(submit_query, top_k=3)
        result = get_answer(submit_query, chunks)
    
    st.session_state.chat_history.insert(0, {"query": submit_query, "result": result})
    st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-note">
    📌 This assistant uses publicly available information from HDFC AMC (hdfcfund.com), AMFI (amfiindia.com), and SEBI (sebi.gov.in). No PII is collected or stored. | Mutual Fund investments are subject to market risks. Please read all scheme related documents carefully.
</div>
""", unsafe_allow_html=True)
