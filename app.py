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
    page_title="FinRAG — Trợ Lý Ngân Hàng AI",
    page_icon="🏦",
    layout="centered",
)

st.title("🏦 FinRAG — Trợ Lý Ngân Hàng AI")
st.caption(
    "Hỏi bất cứ điều gì về sản phẩm, chính sách vay, tài khoản, và dịch vụ ngân hàng."
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
    st.markdown("**Câu hỏi gợi ý:**")
    suggestions = [
        "Lãi suất tiết kiệm 12 tháng là bao nhiêu?",
        "Điều kiện để vay tiêu dùng là gì?",
        "Làm sao để mở tài khoản online?",
        "Hạn mức giao dịch thẻ quốc tế là bao nhiêu?",
        "AI được dùng như thế nào trong ngân hàng?",
    ]
    for s in suggestions:
        if st.button(s, use_container_width=True):
            st.session_state.pending_query = s

# ── Load RAG chain (cached) ───────────────────────────────────────────────────
@st.cache_resource(show_spinner="⏳ Đang tải mô hình AI...")
def get_chain():
    vs = load_vectorstore()
    return build_rag_chain(vs)

try:
    chain = get_chain()
except FileNotFoundError as e:
    st.error(str(e))
    st.info("Chạy lệnh này trước: `python ingest.py`")
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
            with st.expander("📄 Nguồn tài liệu"):
                for src in msg["sources"]:
                    st.caption(f"• {src}")

# ── Handle sidebar suggestion click ──────────────────────────────────────────
user_input = st.chat_input("Nhập câu hỏi của bạn...")
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
        with st.spinner("🔍 Đang tìm kiếm tài liệu..."):
            result = query(chain, user_input)
            answer = result["answer"]
            sources = result["sources"]

        st.markdown(answer)
        if sources:
            with st.expander("📄 Nguồn tài liệu"):
                for src in sources:
                    st.caption(f"• {src}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
