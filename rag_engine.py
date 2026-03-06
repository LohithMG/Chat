# rag_engine.py — Builds FAISS index and retrieves relevant chunks

import os
import pickle
import numpy as np
import sys

sys.path.insert(0, os.path.dirname(__file__))
from corpus import CORPUS

# ── Lazy imports so Streamlit doesn't break if packages aren't installed ──────
def _load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

def _load_faiss():
    import faiss
    return faiss

INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index.pkl")


def build_index():
    """Embed all corpus chunks and build a FAISS index. Saves to disk."""
    model = _load_model()
    faiss = _load_faiss()

    texts = [c["text"] for c in CORPUS]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    embeddings = embeddings.astype(np.float32)

    # Normalize for cosine similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / norms

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner product = cosine after normalization
    index.add(embeddings)

    with open(INDEX_PATH, "wb") as f:
        pickle.dump({"index": index, "corpus": CORPUS, "embeddings": embeddings}, f)

    print(f"✅ Index built: {len(CORPUS)} chunks indexed.")
    return index, CORPUS


def load_index():
    """Load pre-built FAISS index from disk, or build if missing."""
    if not os.path.exists(INDEX_PATH):
        return build_index()
    with open(INDEX_PATH, "rb") as f:
        data = pickle.load(f)
    return data["index"], data["corpus"]


def retrieve(query: str, top_k: int = 3):
    """Return top_k most relevant chunks for the query."""
    model = _load_model()
    faiss = _load_faiss()

    index, corpus = load_index()

    q_emb = model.encode([query], convert_to_numpy=True).astype(np.float32)
    q_emb = q_emb / np.linalg.norm(q_emb, axis=1, keepdims=True)

    scores, indices = index.search(q_emb, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(corpus):
            results.append({
                "text": corpus[idx]["text"],
                "source": corpus[idx]["source"],
                "scheme": corpus[idx]["scheme"],
                "score": float(score),
            })
    return results


if __name__ == "__main__":
    build_index()
