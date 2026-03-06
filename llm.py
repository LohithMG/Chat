# llm.py — Answer generation using Google Gemini 1.5 Flash (free tier)
# Falls back to a template-based answer if API key is not set.

import os
import re

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ── Topics that should be refused (opinionated / advice-seeking) ──────────────
ADVICE_PATTERNS = [
    r"\bshould i\b", r"\bworth (buying|investing)\b", r"\bbetter (than|fund)\b",
    r"\brecommend\b", r"\badvise\b", r"\bwhich fund (to|should)\b",
    r"\bbuy\b", r"\bsell\b", r"\bswitch\b", r"\bportfolio\b",
    r"\bwill (it|the fund) (go up|rise|fall|drop|perform)\b",
    r"\breturn (prediction|forecast|expected)\b",
    r"\bbest fund\b", r"\btop fund\b", r"\bwhere (should|to) invest\b", r"\bwhich.{0,20}better\b", r"\bbetter than\b",
    r"\bcompare returns\b", r"\bhow much (will|can) i (earn|make|get)\b",
]

REFUSAL_MESSAGE = (
    "I'm a facts-only assistant and cannot provide investment advice or recommendations. "
    "For guidance on choosing funds, please consult a SEBI-registered investment advisor (RIA) "
    "or explore AMFI's investor education resources."
)
REFUSAL_LINK = "https://www.amfiindia.com/investor-corner/investor-education"

# ── Performance / returns queries ─────────────────────────────────────────────
PERFORMANCE_PATTERNS = [
    r"\breturns?\b", r"\bperformance\b", r"\bcagr\b", r"\bxirr\b",
    r"\bhow much (did|has|have).{0,20}(return|gain|grow)\b",
    r"\bprofit\b", r"\bgrowth\b",
]


def is_advice_query(query: str) -> bool:
    q = query.lower()
    return any(re.search(p, q) for p in ADVICE_PATTERNS)


def is_performance_query(query: str) -> bool:
    q = query.lower()
    return any(re.search(p, q) for p in PERFORMANCE_PATTERNS)


def _build_prompt(query: str, chunks: list) -> str:
    context_lines = []
    for i, c in enumerate(chunks, 1):
        context_lines.append(f"[Source {i}] ({c['scheme']}): {c['text']}")
    context = "\n\n".join(context_lines)

    return f"""You are a facts-only mutual fund FAQ assistant for Groww users. 
Your knowledge comes only from the provided context. 

Rules:
1. Answer in 2-3 sentences maximum using ONLY the facts in the context.
2. If the user asks a question that is completely unrelated to mutual funds, HDFC, Groww, or finance (e.g. politics, general knowledge, weather), politely state: "I am a mutual fund FAQ assistant and can only answer questions related to HDFC AMC mutual funds based on the provided context."
3. Do NOT provide investment advice, recommendations, or performance predictions.
4. Do NOT compute or compare returns.
5. End your relevant answers with: "Source: [URL]" using the most relevant source URL from the context.
6. If the context does not contain the answer to a mutual fund question, say: "I don't have that information. Please check the official HDFC AMC website: https://www.hdfcfund.com"
7. Today's date context: Sources last indexed March 2025. Always recommend verifying current figures from official sources.

Context:
{context}

Question: {query}

Answer (2-3 sentences, end with Source URL if applicable):"""


def answer_with_gemini(query: str, chunks: list) -> dict:
    """Call Gemini 1.5 Flash to generate a grounded answer."""
    import urllib.request
    import json

    prompt = _build_prompt(query, chunks)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 256},
    }).encode("utf-8")

    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Extract source link from answer
        source = chunks[0]["source"] if chunks else "https://www.hdfcfund.com"
        for line in text.splitlines():
            if line.lower().startswith("source:"):
                source = line.split(":", 1)[1].strip()
        return {"answer": text, "source": source, "chunks": chunks}
    except Exception as e:
        return _template_answer(query, chunks, error=str(e))


def _template_answer(query: str, chunks: list, error: str = "") -> dict:
    """Simple template answer when no API key is set."""
    if not chunks:
        return {
            "answer": "I don't have information about that in my knowledge base. Please check the official HDFC AMC website.",
            "source": "https://www.hdfcfund.com",
            "chunks": [],
        }
    best = chunks[0]
    answer = f"{best['text']} (Last updated from sources: March 2025.)"
    return {"answer": answer, "source": best["source"], "chunks": chunks}


def get_answer(query: str, chunks: list) -> dict:
    """Main entry point. Handles refusals, then calls LLM or template."""

    if is_advice_query(query):
        return {
            "answer": REFUSAL_MESSAGE,
            "source": REFUSAL_LINK,
            "chunks": [],
            "refused": True,
        }

    if is_performance_query(query) and not any(
        kw in query.lower() for kw in ["expense", "exit load", "minimum", "sip", "lock"]
    ):
        return {
            "answer": (
                "I don't provide return calculations or performance comparisons. "
                "For historical performance data, please refer to the official factsheet."
            ),
            "source": "https://www.hdfcfund.com/our-products/equities",
            "chunks": [],
            "refused": True,
        }

    if GEMINI_API_KEY:
        return answer_with_gemini(query, chunks)
    else:
        return _template_answer(query, chunks)
