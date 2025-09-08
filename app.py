import os
import io
import time
from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import requests

# ChromaDB
import chromadb
from chromadb.utils import embedding_functions

# OpenAI
import openai
from limit import RateLimitMiddleware

# PDF loader
from PyPDF2 import PdfReader

# ---------- Config ----------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "adminsecret")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))
TOP_K = int(os.getenv("TOP_K", "4"))

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not set. Set it in .env or environment variables.")

openai.api_key = OPENAI_API_KEY

app = FastAPI(title="RAG Chatbot (FastAPI + ChromaDB + OpenAI)")
app.add_middleware(
    RateLimitMiddleware,
    daily_limit=int(os.getenv("MAX_DAILY_REQUESTS", 200))
)
# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Simple API Key auth ----------
def require_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-KEY header.")

# ---------- Initialize ChromaDB ----------
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="agency_docs",
    embedding_function=embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name=EMBEDDING_MODEL
    )
)

# ---------- Helpers ----------
def split_text_words(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks


# ---------- Models ----------
class IngestRequest(BaseModel):
    texts: List[str]
    namespace: Optional[str] = "default"

class QueryRequest(BaseModel):
    query: str
    k: Optional[int] = TOP_K
    namespace: Optional[str] = "default"


# ---------- Ingest endpoints ----------
@app.post("/ingest/text", dependencies=[Depends(require_api_key)])
def ingest_texts(req: IngestRequest):
    if not req.texts:
        raise HTTPException(status_code=400, detail="No texts provided.")

    all_chunks, metadatas, ids = [], [], []
    for d_idx, d in enumerate(req.texts):
        chunks = split_text_words(d)
        for c_idx, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            ids.append(f"{req.namespace}{d_idx}{c_idx}_{int(time.time())}")
            metadatas.append({
                "doc_id": d_idx,
                "chunk_id": c_idx,
                "namespace": req.namespace,
                "timestamp": time.time()
            })

    collection.add(documents=all_chunks, ids=ids, metadatas=metadatas)
    return {"status": "ok", "indexed_chunks": len(all_chunks)}


@app.post("/ingest/upload", dependencies=[Depends(require_api_key)])
async def ingest_upload(file: UploadFile = File(...), namespace: Optional[str] = "default"):
    filename = file.filename.lower()
    content = await file.read()
    text = ""

    if filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
    elif filename.endswith(".txt"):
        text = content.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .pdf or .txt")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from file.")

    chunks = split_text_words(text)
    ids = [f"{namespace}{filename}{i}_{int(time.time())}" for i, _ in enumerate(chunks)]
    metadatas = [{"filename": filename, "chunk_id": i, "namespace": namespace, "timestamp": time.time()} for i in range(len(chunks))]

    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    return {"status": "ok", "indexed_chunks": len(chunks), "file": filename}


# ---------- Query endpoint ----------
@app.post("/query", dependencies=[Depends(require_api_key)])
def query(req: QueryRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="Empty query.")

    results = collection.query(query_texts=[req.query], n_results=req.k or TOP_K)

    if not results["documents"] or not results["documents"][0]:
        return {"answer": "I don't know based on provided documents.", "retrieved": []}

    hits = []
    for i, doc in enumerate(results["documents"][0]):
        hits.append({
            "text_preview": doc[:400],
            "metadata": results["metadatas"][0][i]
        })

    context = "\n\n---\n\n".join([f"{h['text_preview']}" for h in hits])

    system_prompt = (
        "You are an assistant that answers using only the provided context. "
        "If the answer can't be found, say 'I don't know based on provided documents'."
    )
    user_prompt = f"Question: {req.query}\n\nContext:\n{context}\n\nAnswer:"

    try:
        resp = openai.ChatCompletion.create(
            model=LLM_MODEL,
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": user_prompt}],
            max_tokens=500,
            temperature=0.0,
        )
        answer = resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {e}")

    return {"answer": answer, "retrieved": hits}


# ---------- Admin endpoints ----------
@app.get("/index/info", dependencies=[Depends(require_api_key)])
def index_info():
    count = collection.count()
    return {"status": "ok", "count": count}


@app.post("/index/clear", dependencies=[Depends(require_api_key)])
def clear_index():
    chroma_client.delete_collection("agency_docs")
    return {"status": "cleared"}


# ---------- Health ----------
@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)