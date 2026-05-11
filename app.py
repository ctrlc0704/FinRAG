"""
app.py
Streamlit chat UI for FinRAG - Financial Document Q&A
"""

import streamlit as st
from dotenv import load_dotenv
from rag_pipeline import load_vectorstore, build_rag_chain, query

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinRAG — AI Banking Assistant",
    page_icon="🏦",
    layout="centered",
)

st.title("🏦 FinRAG — AI Banking Assistant")
st.caption(
    "Ask anything about products, loan policies, accounts, and banking services."
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ Về FinRAG")
    st.markdown("""
    **Stack:**
    - 🦙 LLM: Llama-3.1-8b (Groq)
    - 🔍 Retrieval: FAISS + HuggingFace Embeddings
    - 🔗 Framework: LangChain
    - 🖥️ UI: Streamlit

    **Architecture:**
    ```
    Query → Embed → FAISS Search
    → Top-4 chunks → LLM → Answer
    ```
    """)

    st.divider()
    st.markdown("**Suggested questions:**")
    suggestions = [
        "What is the 12-month savings interest rate?",
        "What are the requirements for a consumer loan?",
        "How can I open an account online?",
        "What is the transaction limit for international cards?",
        "How is AI used in banking?",
    ]
    for s in suggestions:
        if st.button(s, use_container_width=True):
            st.session_state.pending_query = s

# ── Load RAG chain (cached) ───────────────────────────────────────────────────
@st.cache_resource(show_spinner="⏳ Loading AI model...")
def get_chain():
    vs = load_vectorstore()
    return build_rag_chain(vs)

try:
    chain = get_chain()
except FileNotFoundError as e:
    st.error(str(e))
    st.info("Run this command first: `python ingest.py`")
    st.stop()
except ValueError as e:
    st.error(str(e))
    st.stop()

# ── Chat history ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📄 Source documents"):
                for src in msg["sources"]:
                    st.caption(f"• {src}")

# ── Handle sidebar suggestion click ──────────────────────────────────────────
user_input = st.chat_input("Enter your question...")
if "pending_query" in st.session_state:
    user_input = st.session_state.pop("pending_query")

# ── Chat logic ────────────────────────────────────────────────────────────────
if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get answer
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching documents..."):
            result = query(chain, user_input)
            answer = result["answer"]
            sources = result["sources"]

        st.markdown(answer)
        if sources:
            with st.expander("📄 Source documents"):
                for src in sources:
                    st.caption(f"• {src}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
