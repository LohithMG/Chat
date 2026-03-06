# RAG-based Mutual Fund FAQ Chatbot
**Product:** Groww &nbsp;|&nbsp; **AMC:** HDFC Asset Management Company Ltd  
**Milestone 1** — Facts-Only Mutual Fund FAQ Assistant

---

## 📌 Scope

| Attribute | Value |
|-----------|-------|
| **AMC** | HDFC Asset Management Company Limited |
| **Platform** | Groww |
| **Schemes** | HDFC Top 100 Fund (Large-cap), HDFC Flexi Cap Fund, HDFC Mid-Cap Opportunities Fund |
| **Source corpus** | 25 public pages from HDFC AMC, AMFI, SEBI, and Groww |
| **LLM** | Google Gemini 1.5 Flash (free tier) — falls back to template if no API key |
| **Embeddings** | `all-MiniLM-L6-v2` via sentence-transformers (local, free) |
| **Vector Store** | FAISS (CPU, local — no server needed) |

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. (Optional) Set Gemini API key for LLM-quality answers
```bash
export GEMINI_API_KEY="your-key-here"
```
Get a free key at: https://aistudio.google.com/app/apikey  
If not set, the app uses template-based retrieval (still fully functional for facts).

### 3. Run the app
```bash
streamlit run app.py
```

The app will auto-build the FAISS index on first launch (~10 seconds).

---

## 🏗️ Architecture

```
User Query
    │
    ▼
[Refusal Filter]  ─── advice/performance query? ──► Polite Refusal + AMFI link
    │
    ▼
[RAG Retrieval]   ─── sentence-transformers + FAISS → top 3 chunks
    │
    ▼
[LLM / Template]  ─── Gemini 1.5 Flash (or template fallback)
    │
    ▼
[Answer + Source Link]  ──► Streamlit UI
```

### Files
| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI |
| `rag_engine.py` | Embedding + FAISS index + retrieval |
| `llm.py` | Answer generation, refusal logic |
| `data/corpus.py` | 30 curated factual chunks from public sources |
| `requirements.txt` | Python dependencies |
| `sources.md` | All 25 source URLs |
| `sample_qa.md` | 10 sample Q&A pairs |

---

## ⚠️ Disclaimer (used in UI)

> This assistant provides factual information only from public HDFC AMC, AMFI, and SEBI sources. It does **not** offer investment advice, recommendations, or return predictions. Mutual fund investments are subject to market risks. Read all scheme-related documents carefully before investing. For investment decisions, consult a SEBI-registered investment advisor (RIA). Data sourced from official public pages; verify current figures at [hdfcfund.com](https://www.hdfcfund.com) or [amfiindia.com](https://www.amfiindia.com).

---

## ✅ What the assistant answers

- Expense ratio (Direct / Regular plan)
- Exit load and holding period
- Minimum SIP and lump-sum investment
- Lock-in period
- Riskometer / risk category
- Benchmark index
- Fund manager name and launch date
- How to download capital gains statement / CAS
- Direct vs Regular plan difference
- NAV definition and where to find it
- Tax on equity mutual funds (factual, not personalized)

## ❌ What the assistant refuses

- Investment recommendations ("Should I buy X?")
- Return comparisons or predictions
- Portfolio advice
- "Best fund" queries

---

## ⚠️ Known Limits

1. **Corpus is static.** Expense ratios and other figures may change. Users are always directed to verify at official sources.
2. **No real-time data.** The app does not scrape live NAVs or factsheets.
3. **No PII accepted.** The app does not ask for or store PAN, Aadhaar, phone, email, or account numbers.
4. **No performance data.** Historical returns are not computed or displayed.
5. **Gemini dependency.** LLM-quality answers require a free Gemini API key. Without it, the app returns direct corpus text (accurate but less fluent).
6. **3 schemes only.** Coverage is limited to HDFC Top 100, Flexi Cap, and Mid-Cap Opportunities funds.
