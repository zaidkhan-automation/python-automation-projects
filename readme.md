RAG Chatbot — FastAPI + CHROMA + OpenAI
=====================================

1) Setup
   - Copy files into a folder.
   - Create a virtualenv: python -m venv venv && source venv/bin/activate
   - Install: pip install -r requirements.txt
   - Create .env or set env vars:
       export OPENAI_API_KEY="sk-..."
       export ADMIN_API_KEY="adminsecret"
   - Optional: adjust CHUNK_SIZE in env.

2) Run (dev)
   uvicorn app:app --reload --host 0.0.0.0 --port 8000

3) Ingest docs
   - Use the /ingest/text endpoint (POST) with header X-API-KEY: adminsecret
   - Example curl:
     curl -X POST "http://localhost:8000/ingest/text" -H "X-API-KEY: adminsecret" -H "Content-Type: application/json" -d '{"texts":["your text..."]}'

   - Or upload PDF/text:
     curl -X POST -F "file=@./manual.pdf" -F "namespace=docs" -H "X-API-KEY: adminsecret" http://localhost:8000/ingest/upload

4) Query
   - POST /query with JSON {"query":"How do you onboard?"}
   - Header: X-API-KEY: adminsecret

5) Frontend
   - Place index.html next to backend or serve separately. If backend and frontend on same host, open index.html in browser.