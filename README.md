# 🏦 FinRAG — Financial Document Q&A with RAG

> A Retrieval-Augmented Generation (RAG) chatbot that answers questions about banking products, loan policies, and financial services — grounded in real documents, not hallucinations.

---

## 🎯 Motivation

Large Language Models (LLMs) often hallucinate when asked about specific financial figures (interest rates, fees, limits). In fintech, accuracy is critical.

**FinRAG solves this** by combining document retrieval with LLM generation:
- Retrieves the most relevant document chunks for each query
- Passes them as context to the LLM
- Answers are always grounded in real source documents

---

## 🏗️ Architecture

```
User Query
    │
    ▼
Embedding Model (HuggingFace all-MiniLM-L6-v2)
    │
    ▼
FAISS Vector Search → Top-4 relevant chunks
    │
    ▼
Prompt = chunks + query
    │
    ▼
Groq LLM (Llama-3.1-8b-instant)
    │
    ▼
Answer + Source Documents
```

**Why RAG over pure LLM?**
| | Pure LLM | RAG |
|---|---|---|
| Accuracy on specific facts | ❌ May hallucinate | ✅ Grounded in docs |
| Updatable knowledge | ❌ Retrain required | ✅ Add docs, re-index |
| Source attribution | ❌ None | ✅ Shows source file |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Llama-3.1-8b-instant via [Groq](https://groq.com) |
| Embeddings | `all-MiniLM-L6-v2` (HuggingFace) |
| Vector Store | FAISS (local, no server needed) |
| RAG Framework | LangChain |
| UI | Streamlit |
| Document Support | `.txt`, `.pdf` |

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/FinRAG.git
cd FinRAG
pip install -r requirements.txt
```

### 2. Get free Groq API key

Go to [console.groq.com](https://console.groq.com) → Sign up → Create API Key (free, no credit card)

```bash
cp .env.example .env
# Edit .env and paste your key:
# GROQ_API_KEY=gsk_xxxxxxxxxxxx
```

### 3. Build the vector index

```bash
python ingest.py
```

Output:
```
✅ Loaded 2 documents
✅ Split into 47 chunks
⏳ Loading embedding model...
⏳ Building FAISS index...
✅ FAISS index saved to ./faiss_index/
🎉 Done! Run: streamlit run app.py
```

### 4. Run the app

```bash
streamlit run app.py
```

Open browser at `http://localhost:8501` 🎉

---

## 💬 Example Queries

```
"What is the 12-month savings interest rate?"
"What are the requirements for a consumer loan?"
"What is the transaction limit for international cards?"
"How is AI used in fraud detection?"
"How can I improve my CIC credit score?"
```

---

## 📁 Project Structure

```
FinRAG/
├── app.py              # Streamlit chat UI
├── rag_pipeline.py     # RAG chain (retriever + LLM)
├── ingest.py           # Document loading, chunking, indexing
├── data/
│   └── docs/           # Put your .txt or .pdf documents here
│       ├── banking_faq.txt
│       └── loan_products.txt
├── faiss_index/        # Auto-generated, gitignored
├── .env.example        # API key template
├── requirements.txt
└── README.md
```

---

## ➕ Add Your Own Documents

Drop any `.txt` or `.pdf` file into `data/docs/`, then re-run:

```bash
python ingest.py
```

Good sources for fintech documents:

- Bank annual reports (Vietcombank, Techcombank...)
- State Bank of Vietnam policy documents at [sbv.gov.vn](https://sbv.gov.vn)
- Product FAQs from bank websites

---

## 🔧 Configuration

Edit `rag_pipeline.py` to tune:

```python
# Number of retrieved chunks
search_kwargs={"k": 4}          # increase for more context

# LLM model (all free on Groq)
model="llama-3.1-8b-instant"    # fastest
model="llama-3.1-70b-versatile" # more capable
model="mixtral-8x7b-32768"      # long context
```

Edit `ingest.py` to tune chunking:

```python
chunk_size=500      # larger = more context per chunk
chunk_overlap=80    # higher = less info loss at boundaries
```

---

## 📝 License

MIT License — free to use and modify.

---

*Built as part of a portfolio project exploring RAG applications in Vietnamese fintech.*
