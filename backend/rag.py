import os
import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Storage
chunks = []
chunk_metadata = []  # stores page number and source file for each chunk
index = None

def extract_text_from_pdf(pdf_path: str) -> tuple[str, list[dict]]:
    doc = fitz.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if text.strip():
            pages.append({"text": text, "page": page_num})
    return pages

def chunk_text(pages: list[dict], chunk_size: int = 500, overlap: int = 50) -> tuple[list[str], list[dict]]:
    result_chunks = []
    result_metadata = []
    for page_data in pages:
        words = page_data["text"].split()
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                result_chunks.append(chunk)
                result_metadata.append({"page": page_data["page"]})
    return result_chunks, result_metadata

def build_index(pdf_path: str, filename: str):
    global chunks, chunk_metadata, index

    pages = extract_text_from_pdf(pdf_path)
    new_chunks, new_metadata = chunk_text(pages)

    # Add source filename to metadata
    for m in new_metadata:
        m["source"] = filename

    chunks.extend(new_chunks)
    chunk_metadata.extend(new_metadata)

    embeddings = embedder.encode(chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return len(chunks)

def retrieve(query: str, top_k: int = 5) -> list[dict]:
    query_vec = embedder.encode([query]).astype("float32")
    _, indices = index.search(query_vec, top_k)
    results = []
    for i in indices[0]:
        if i < len(chunks):
            results.append({
                "text": chunks[i],
                "page": chunk_metadata[i]["page"],
                "source": chunk_metadata[i]["source"]
            })
    return results

def answer_question(query: str) -> dict:
    retrieved = retrieve(query)
    context = "\n\n".join([r["text"] for r in retrieved])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are a helpful assistant. Answer the question based only on the context below.
If the answer isn't in the context, say "I couldn't find that in the document."

Context:
{context}

Question: {query}

Answer:"""
            }
        ]
    )

    # Build unique citations
    seen = set()
    citations = []
    for r in retrieved:
        key = (r["source"], r["page"])
        if key not in seen:
            seen.add(key)
            citations.append({"source": r["source"], "page": r["page"]})

    return {
        "answer": response.content[0].text,
        "citations": citations
    }