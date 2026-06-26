import os
import numpy as np
from typing import List, Dict, Optional

EMBEDDING_DIM = 384

class EmbeddingModel:
    def __init__(self):
        self.model = None

    def load(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            self.model = None

    def encode(self, texts: List[str]) -> np.ndarray:
        if self.model:
            return self.model.encode(texts)
        return np.random.randn(len(texts), EMBEDDING_DIM).astype(np.float32)

embedder = EmbeddingModel()

class FAISSIndex:
    def __init__(self):
        self.index = None
        self.documents: List[Dict] = []

    def build(self, documents: List[Dict]):
        try:
            import faiss
        except ImportError:
            self.documents = documents
            return
        self.documents = documents
        texts = [f"{d['crime_type']}: {d['description']} Location: {d['location']}" for d in documents]
        embeddings = embedder.encode(texts)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings.astype(np.float32))

    def search(self, query: str, k: int = 3) -> List[Dict]:
        query_embedding = embedder.encode([query])
        if self.index and self.index.ntotal > 0:
            distances, indices = self.index.search(query_embedding.astype(np.float32), k)
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents):
                    doc = dict(self.documents[idx])
                    doc["score"] = float(distances[0][i])
                    results.append(doc)
            return results
        texts = [f"{d['crime_type']}: {d['description']} Location: {d['location']}" for d in self.documents]
        query_vec = query_embedding[0]
        scored = []
        for i, doc in enumerate(self.documents):
            doc_vec = embedder.encode(["dummy"])[0] if not self.model else embedder.encode([texts[i]])[0]
            sim = float(np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec) + 1e-8))
            scored.append((sim, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{**doc, "score": sim} for sim, doc in scored[:k]]

vector_index = FAISSIndex()

def initialize_index():
    from . import database
    docs = database.get_all_descriptions()
    vector_index.build(docs)

def retrieve_context(query: str, k: int = 3) -> List[Dict]:
    results = vector_index.search(query, k)
    return results

def generate_answer(question: str, context: List[Dict], llm_mode: str = "mock") -> str:
    if not context:
        return "I couldn't find any relevant crime records matching your query."

    context_str = "\n".join([
        f"FIR {d['fir_id']}: {d['crime_type']} - {d['description']} (Location: {d['location']})"
        for d in context
    ])
    source_ids = [d["fir_id"] for d in context]

    if llm_mode == "openai":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are a law enforcement data assistant. Based on the following crime reports, answer the question concisely and cite relevant case IDs.\n\nCrime Reports:\n{context_str}"},
                    {"role": "user", "content": question}
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[LLM Error: {str(e)}]. Context retrieved: {context_str}"

    if llm_mode == "gemini":
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = f"You are a law enforcement data assistant. Based on the following crime reports, answer the question concisely and cite relevant case IDs.\n\nCrime Reports:\n{context_str}\n\nUser Question: {question}"
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"[LLM Error: {str(e)}]. Context retrieved: {context_str}"

    source_str = ", ".join([f"#{s}" for s in source_ids[:3]])
    return f"Based on the crime records, I found the following relevant cases: {source_str}. The retrieved information shows: {context_str[:300]}..."
