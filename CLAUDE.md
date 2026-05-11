# CLAUDE.md

Notes for future Claude sessions working on this repo.

## What this project is

FinRAG is a Retrieval-Augmented Generation (RAG) demo over SEC 10-K filings of major US banks. Stack: LangChain + FAISS + HuggingFace embeddings + Groq Llama-3.1 + Streamlit. Originally built around toy Vietnamese banking FAQ files, now translated to English and pointed at real SEC data.

## Repo layout that matters

- [app.py](app.py) — Streamlit UI. Has a `check_password()` gate driven by `APP_PASSWORD` env var (no-op if unset). Required for public exposure.
- [rag_pipeline.py](rag_pipeline.py) — Loads FAISS, builds `RetrievalQA` chain with `ChatGroq`. Prompt is in English and tells the LLM to refuse if context is missing.
- [ingest.py](ingest.py) — `DirectoryLoader` over `data/docs/**/*.txt` (and `.pdf` if pypdf installed), splits with `RecursiveCharacterTextSplitter`, embeds with `all-MiniLM-L6-v2`, writes to `faiss_index/`.
- [fetch_sec.py](fetch_sec.py) — Pulls latest 10-K of each bank in the `BANKS` dict from SEC EDGAR, strips HTML with BeautifulSoup, writes to `data/docs/sec/`. Uses `SEC_USER_AGENT` env var (SEC requires real contact email).
- `data/docs/sec/` — Ingested data. SEC 10-Ks (public domain).
- `data/docs_demo/` — Old toy FAQ files. **NOT ingested** (outside `data/docs/`). Kept for reference.
- `faiss_index/` — Gitignored. Rebuild with `python ingest.py`.

## Run notes (Windows specifics)

- Windows console (cp1252) breaks on emoji output → always set `PYTHONIOENCODING=utf-8` before running `python ingest.py` / `fetch_sec.py`.
- Python install on this machine is via `uv` (no global `python` on PATH). Use `.venv/Scripts/python.exe` directly.
- Streamlit binds to all interfaces by default. Use `--server.address=127.0.0.1` so only ngrok (or other explicit tunnel) can reach it.

## Conventions

- Don't commit the FAISS index — it's regeneratable and 20+ MB.
- `.env` is gitignored. `.env.example` is the only source of truth for required vars (`GROQ_API_KEY`, `APP_PASSWORD`, `SEC_USER_AGENT`).
- When adding a new bank to `fetch_sec.py`, look up its CIK on [sec.gov/cgi-bin/browse-edgar](https://www.sec.gov/cgi-bin/browse-edgar) and pad to 10 digits.
- After changing any file in `data/docs/`, **must re-run `python ingest.py`** before the chat reflects the change.

## Security posture

Public exposure (ngrok / tunnel) requires `APP_PASSWORD` set. The password gate uses `hmac.compare_digest`. It is a deterrent, not production-grade auth — for higher-risk use ngrok OAuth, Cloudflare Access, or a real reverse proxy.

## Common tasks

- **Update the dataset**: `python fetch_sec.py && python ingest.py`
- **Add a doc by hand**: drop into `data/docs/`, run `python ingest.py`
- **Change LLM**: edit `model="..."` in [rag_pipeline.py:60](rag_pipeline.py#L60). Supported Groq models listed at [console.groq.com/docs/models](https://console.groq.com/docs/models).
- **Tune retrieval**: `search_kwargs={"k": N}` in [rag_pipeline.py:68](rag_pipeline.py#L68); chunk size in [ingest.py:48](ingest.py#L48).
