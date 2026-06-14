import streamlit as st
import requests
import uuid

# ── Configuration ────────────────────────────────────────────────────────────
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="RAG Doc Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Sidebar session buttons */
div[data-testid="stSidebarContent"] .session-btn {
    background: #1e1e2e;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 6px 10px;
    margin-bottom: 4px;
    cursor: pointer;
    font-size: 0.82rem;
    color: #cdd6f4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 100%;
    text-align: left;
}
div[data-testid="stSidebarContent"] .session-btn:hover {
    background: #313244;
}
div[data-testid="stSidebarContent"] .session-btn.active {
    border-color: #89b4fa;
    color: #89b4fa;
}
</style>
""", unsafe_allow_html=True)

# ── Session State Init ────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "token" not in st.session_state:
    try:
        res = requests.post(f"{API_URL}/token", data={"username": "admin", "password": "admin"})
        st.session_state.token = res.json().get("access_token") if res.status_code == 200 else None
    except Exception:
        st.session_state.token = None

# ── API Helpers ───────────────────────────────────────────────────────────────
def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}", "Content-Type": "application/json"}

def get_indexed_documents():
    try:
        res = requests.get(f"{API_URL}/documents/", timeout=5)
        if res.status_code == 200:
            return res.json().get("documents", [])
    except Exception:
        pass
    return []

def get_past_sessions():
    try:
        res = requests.get(f"{API_URL}/sessions/", timeout=5)
        if res.status_code == 200:
            return res.json().get("sessions", [])
    except Exception:
        pass
    return []

def load_session_history(session_id: str):
    try:
        res = requests.get(f"{API_URL}/sessions/{session_id}/history", timeout=5)
        if res.status_code == 200:
            return res.json().get("history", [])
    except Exception:
        pass
    return []

def query_assistant(question: str):
    payload = {"session_id": st.session_state.session_id, "question": question}
    try:
        res = requests.post(f"{API_URL}/query/", headers=auth_headers(), json=payload, timeout=60)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {"answer": "Error connecting to the API.", "sources": [], "hallucination_score": "unknown"}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("💬 RAG Assistant")
    st.caption(f"Session: `{st.session_state.session_id[:8]}...`")

    if st.button("＋  New Chat", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # ── Past Sessions (ChatGPT-style) ─────────────────────────────────────────
    st.subheader("🕘 Recent Sessions")
    past_sessions = get_past_sessions()

    if not past_sessions:
        st.caption("No previous sessions yet.")
    else:
        for s in past_sessions:
            sid = s["session_id"]
            title = s["title"] if s["title"] else "Untitled"
            is_active = sid == st.session_state.session_id
            label = f"{'▶ ' if is_active else ''}{title}"
            if st.button(label, key=f"sess_{sid}", use_container_width=True,
                         help=f"Session: {sid}"):
                if sid != st.session_state.session_id:
                    st.session_state.session_id = sid
                    # Restore history from DB — only user/assistant messages
                    raw = load_session_history(sid)
                    st.session_state.messages = [
                        m for m in raw if m.get("role") in ("user", "assistant")
                    ]
                    st.rerun()

    st.markdown("---")

    # ── Indexed Documents (collapsible dropdown) ───────────────────────────────
    with st.expander("📄 Indexed Documents", expanded=False):
        docs = get_indexed_documents()
        if docs:
            st.caption(f"{len(docs)} document(s) indexed")
            for doc in docs:
                # Show just the filename, not the full path
                label = doc.split("\\")[-1].split("/")[-1]
                st.markdown(f"• `{label}`", help=doc)
        else:
            st.write("No documents indexed yet.")

# ── Main Chat ─────────────────────────────────────────────────────────────────
st.title("RAG Technical Documentation Assistant")

# Render existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant":
            # Sources
            if msg.get("sources"):
                with st.expander("📚 View Sources"):
                    for i, source in enumerate(msg["sources"]):
                        st.markdown(f"**Source {i+1}:** `{source['source']}`")
                        st.text(source.get("content_snippet", ""))

            # Hallucination badge
            score = msg.get("hallucination_score", "unknown")
            color = "green" if score == "pass" else "red" if score == "fail" else "orange"
            icon = "✅" if score == "pass" else "❌" if score == "fail" else "⚠️"
            st.markdown(
                f"<small><span style='color:{color}'>{icon} Hallucination Check: <b>{score.upper()}</b></span></small>",
                unsafe_allow_html=True
            )

# ── Chat Input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a technical question..."):
    # Add & display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = query_assistant(prompt)

        answer = result.get("answer", "")
        sources = result.get("sources", [])
        h_score = result.get("hallucination_score", "unknown")

        st.markdown(answer)

        if sources:
            with st.expander("📚 View Sources"):
                for i, source in enumerate(sources):
                    st.markdown(f"**Source {i+1}:** `{source['source']}`")
                    st.text(source.get("content_snippet", ""))

        color = "green" if h_score == "pass" else "red" if h_score == "fail" else "orange"
        icon = "✅" if h_score == "pass" else "❌" if h_score == "fail" else "⚠️"
        st.markdown(
            f"<small><span style='color:{color}'>{icon} Hallucination Check: <b>{h_score.upper()}</b></span></small>",
            unsafe_allow_html=True
        )

    # Save to local session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "hallucination_score": h_score
    })
