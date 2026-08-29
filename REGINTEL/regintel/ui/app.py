import streamlit as st
import requests

st.set_page_config(page_title="TRACECHO", layout="wide")

# Custom CSS implementation
st.markdown("""
<style>
    /* Dark Theme Setup */
    :root {
        --bg-color: #050505;
        --navy-panel: #0B1F3A;
        --accent-blue: #2563EB;
        --text-primary: #F3F4F6;
        --text-secondary: #9CA3AF;
        --border-color: #1E3A5F;
    }
    
    .stApp, .stApp > header {
        background-color: var(--bg-color) !important;
        color: var(--text-primary) !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--navy-panel) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    
    h1, h2, h3, h4, h5, h6, .markdown-text-container {
        color: var(--text-primary) !important;
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }
    
    /* Input and Buttons */
    .stTextInput>div>div>input, .stChatInput>div {
        background-color: var(--navy-panel) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    .stButton>button {
        background-color: var(--accent-blue) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    .stButton>button:hover {
        background-color: #1D4ED8 !important;
        border: none !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: var(--accent-blue) !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
    }
    [data-testid="stMetric"] {
        background-color: var(--navy-panel) !important;
        padding: 1rem !important;
        border-radius: 0.5rem !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--navy-panel) !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
    }
    div[data-testid="stExpander"] div[role="button"] {
        background-color: var(--navy-panel) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
    }
    
    /* Custom Components */
    .tracecho-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        letter-spacing: 2px !important;
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
        color: var(--text-primary) !important;
    }
    .tracecho-subtitle {
        font-size: 1.2rem !important;
        color: var(--accent-blue) !important;
        margin-top: -10px !important;
        font-weight: 500 !important;
        margin-bottom: 2rem !important;
    }
    
    .citation-card {
        background-color: var(--navy-panel);
        border-left: 4px solid var(--accent-blue);
        padding: 12px 16px;
        margin-bottom: 12px;
        border-radius: 0 6px 6px 0;
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
    }
    
    .evidence-quote {
        background-color: var(--navy-panel);
        border-left: 3px solid #4B5563;
        padding: 10px 16px;
        margin: 10px 0;
        font-style: italic;
        border-radius: 4px;
        color: #D1D5DB;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: var(--navy-panel);
        border: 1px solid var(--accent-blue);
        color: var(--accent-blue);
    }
    
    /* Welcome screen wrapper */
    .welcome-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 65vh;
        text-align: center;
        background-image: linear-gradient(var(--navy-panel) 1px, transparent 1px), linear-gradient(90deg, var(--navy-panel) 1px, transparent 1px);
        background-size: 50px 50px;
        background-position: center;
    }
    
    .welcome-main-title {
        font-size: 5rem !important;
        font-weight: 800 !important;
        letter-spacing: 4px !important;
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
        color: var(--text-primary) !important;
    }
    
    .welcome-sub-title {
        font-size: 1.8rem !important;
        color: var(--text-primary) !important;
        margin-top: -10px !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    .welcome-desc {
        font-size: 1.1rem !important;
        color: var(--text-secondary) !important;
        max-width: 600px !important;
        margin: 0 auto 3rem auto !important;
        line-height: 1.6 !important;
    }
    
    /* Center the button properly */
    div.stButton {
        display: flex;
        justify-content: center;
    }
    
    div.stButton > button {
        padding: 0.75rem 2rem !important;
        font-size: 1.1rem !important;
        border-radius: 4px !important;
        border: 1px solid var(--border-color) !important;
        transition: all 0.2s ease-in-out !important;
        background-color: var(--navy-panel) !important;
        color: var(--text-primary) !important;
    }
    
    div.stButton > button:hover {
        border-color: var(--accent-blue) !important;
        background-color: var(--secondary-navy) !important;
    }
    
    /* Chat message alignment */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse;
        text-align: right;
    }
    
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        max-width: 75%;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] > div {
        background-color: #102A4C !important;
        color: #F1F3F5 !important;
        border-radius: 8px !important;
        padding: 12px 18px !important;
        display: inline-block;
        text-align: left;
    }
    
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageContent"]) .stMarkdown {
        display: flex;
        flex-direction: column;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) .stMarkdown {
        align-items: flex-end;
    }
    
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        max-width: 80%;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContent"] > div {
        background-color: #050505 !important;
        color: #F1F3F5 !important;
        border-radius: 8px !important;
        padding: 12px 18px !important;
        border: 1px solid #1E3A5F !important;
        display: inline-block;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Application logic
st.sidebar.markdown("<h2 style='text-align: center; font-weight: 800; letter-spacing: 1px; font-size: 1.3rem; margin-bottom: 0;'>TRACECHO</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.85rem; margin-top: 0px;'>Regulatory Intelligence</p>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #1E3A5F;'/>", unsafe_allow_html=True)

if st.sidebar.button("New Query", use_container_width=True):
    st.session_state.messages = []
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

st.sidebar.divider()

page = st.sidebar.radio("Navigation", ["Regulatory Assistant", "Intelligence Dashboard", "Document Explorer", "System/Evaluation"])

st.sidebar.divider()
st.sidebar.markdown("<br/>", unsafe_allow_html=True)
regulator_filter = st.sidebar.selectbox("Regulatory Scope", ["Both", "SEBI", "RBI"], index=0)
st.sidebar.markdown("<br/>", unsafe_allow_html=True)

st.sidebar.markdown(
    """
    <div style='background-color:#0B1F3A; padding:10px; border-radius:5px; border:1px solid #1E3A5F; font-size: 0.85rem;'>
        <b style="color:white;">Supported Sources:</b><br/>
        • <b>RBI</b>: Master Directions, Circulars<br/>
        • <b>SEBI</b>: Guidelines, Regulations
    </div>
    """, unsafe_allow_html=True)

API_URL = "http://localhost:8000/api"

def _render_citation_custom(citation: dict) -> None:
    title = citation.get("document_title") or citation.get("chunk_id") or "Unknown document"
    
    meta_parts = []
    if citation.get("regulator"):
        meta_parts.append(f"<b>Regulator:</b> {citation['regulator']}")
    if citation.get("issue_date"):
        meta_parts.append(f"<b>Date:</b> {citation['issue_date']}")
    if citation.get("section"):
        meta_parts.append(f"<b>Section:</b> {citation['section']}")
    if citation.get("chunk_id"):
        meta_parts.append(f"<b>Chunk ID:</b> {citation['chunk_id']}")
        
    meta_html = " | ".join(meta_parts)
    source_link = f"<br/><a href='{citation.get('source_url')}' target='_blank' style='color:#2563EB; text-decoration:none;'>View Source Document</a>" if citation.get("source_url") else ""
    
    st.markdown(f"""
    <div class="citation-card">
        <div style="font-weight: 600; font-size: 1.05rem; margin-bottom: 4px; color: white;">{title}</div>
        <div style="font-size: 0.85rem; color: #9CA3AF;">
            {meta_html}
            {source_link}
        </div>
    </div>
    """, unsafe_allow_html=True)

def _render_assistant_data(data: dict):
    # Verified Answer
    ans = data.get('answer') or 'No answer returned.'
    st.markdown("##### Answer")
    st.markdown(f"<div style='font-size: 1.1rem; color: #F1F3F5;'>{ans}</div>", unsafe_allow_html=True)

    # Verification Status Badge
    status = data.get("verification_status", "")
    if "pass" in status.lower() or "true" in str(status).lower() or status.lower() == "verified":
        st.markdown(f'<div style="display:inline-block; border:1px solid #1E3A5F; background:transparent; color:#9CA3AF; border-radius:4px; padding:2px 8px; font-size:0.75rem; margin-top:10px; margin-bottom:1rem;">Evidence Grounded</div>', unsafe_allow_html=True)
    elif status:
        if "error" in status.lower() or "fail" in status.lower() or status == "unknown":
            st.error(f"Analysis could not be completed: {status}")
        else:
            st.markdown(f'<div style="display:inline-block; border:1px solid #1E3A5F; background:transparent; color:#9CA3AF; border-radius:4px; padding:2px 8px; font-size:0.75rem; margin-top:10px; margin-bottom:1rem;">{status.upper().replace("_", " ")}</div>', unsafe_allow_html=True)
    
    # Regulatory Details
    requirement = data.get("regulatory_requirement")
    applicability = data.get("applicability")
    conditions = data.get("conditions") or []
    exceptions = data.get("exceptions") or []
    
    if requirement or applicability or conditions or exceptions:
        with st.expander("Regulatory Details"):
            if requirement:
                st.write(f"**Requirement:** {requirement}")
                
            if applicability:
                st.markdown("#### Applicability")
                st.write(applicability)
                
            if conditions or exceptions:
                c1, c2 = st.columns(2)
                with c1:
                    if conditions:
                        st.markdown("#### Conditions")
                        for item in conditions:
                            st.write(f"- {item}")
                with c2:
                    if exceptions:
                        st.markdown("#### Exceptions")
                        for item in exceptions:
                            st.write(f"- {item}")
                        
    # Evidence
    evidence_quotes = data.get("evidence") or []
    if evidence_quotes:
        with st.expander("Supporting Evidence"):
            for quote in evidence_quotes:
                st.markdown(f'<div class="evidence-quote">{quote}</div>', unsafe_allow_html=True)
            
    # Citations
    citations = data.get("citations") or []
    if citations:
        with st.expander("Regulatory Basis / Citations"):
            for citation in citations:
                _render_citation_custom(citation)
            
    # Retrieved Chunks
    retrieved = data.get("retrieved_chunks") or []
    if retrieved:
        with st.expander(f"Retrieved Evidence ({len(retrieved)} chunks)"):
            for idx, chunk in enumerate(retrieved):
                title = chunk.get('document_title') or chunk.get('chunk_id')
                regulator = chunk.get('regulator', '—')
                st.markdown(f"**{title}** ({regulator})")
                
                chunk_meta = [f"Chunk: {chunk.get('chunk_id', '—')}"]
                if chunk.get("hybrid_score") is not None:
                    chunk_meta.append(f"Score: {chunk['hybrid_score']}")
                st.caption(" | ".join(chunk_meta))
                
                if chunk.get("source_url"):
                    st.markdown(f"[Source link]({chunk['source_url']})")
                st.write(chunk.get("text", "")[:800] + "...")
                if idx < len(retrieved) - 1:
                    st.divider()


if page == "Regulatory Assistant":
    if "started" not in st.session_state:
        st.session_state.started = False

    if not st.session_state.started:
        st.markdown(
            """
            <div class="welcome-wrapper">
                <h1 class="welcome-main-title">TRACECHO</h1>
                <p class="welcome-sub-title">AI-Powered Regulatory Intelligence</p>
                <p class="welcome-desc">
                    Ask questions across RBI and SEBI regulations using evidence-grounded AI.
                </p>
            </div>
            """, unsafe_allow_html=True
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Get Started", use_container_width=True):
                st.session_state.started = True
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
    else:
        # Subtle header
        st.markdown('<h4 style="text-align:center; font-weight:600; color:var(--text-primary); margin-bottom:0;">TRACECHO</h4>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:var(--text-secondary); margin-bottom:2rem; font-size:0.95rem;">Ask questions across RBI and SEBI regulations.</p>', unsafe_allow_html=True)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        if len(st.session_state.messages) == 0:
            st.markdown('<h3 style="text-align:center; margin-top:3rem; color:var(--text-primary); font-weight: 500;">How can TRACECHO help you today?</h3>', unsafe_allow_html=True)
            st.markdown('<p style="text-align:center; color:var(--text-secondary); margin-bottom: 2rem;">Ask questions and explore evidence across RBI and SEBI regulatory documents.</p>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            
            def set_prompt(text):
                st.session_state.example_prompt = text
                
            with c1:
                st.button("What are the KYC requirements for NBFCs", on_click=set_prompt, args=("What are the KYC requirements for NBFCs",), use_container_width=True)
                st.button("What are cybersecurity requirements for banks", on_click=set_prompt, args=("What are cybersecurity requirements for banks",), use_container_width=True)
            with c2:
                st.button("What are SEBI regulations for mutual funds", on_click=set_prompt, args=("What are SEBI regulations for mutual funds",), use_container_width=True)
                st.button("What are fraud reporting requirements under RBI guidelines", on_click=set_prompt, args=("What are fraud reporting requirements under RBI guidelines",), use_container_width=True)

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "user":
                    st.write(msg["content"])
                else:
                    data = msg.get("data")
                    if data:
                        _render_assistant_data(data)
                    else:
                        st.write(msg.get("content", ""))
        
        prompt = st.chat_input("Ask a regulatory question...")
        
        if hasattr(st.session_state, 'example_prompt') and st.session_state.example_prompt:
            prompt = st.session_state.example_prompt
            st.session_state.example_prompt = None

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Analysing regulatory documents"):
                    try:
                        res = requests.post(f"{API_URL}/ask", json={"query": prompt}, timeout=180)
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.messages.append({"role": "assistant", "data": data})
                            _render_assistant_data(data)
                        else:
                            st.error(f"Analysis could not be completed: Backend error ({res.status_code})")
                            if st.button("Try Again"):
                                pass
                    except Exception as e:
                        st.error(f"Analysis could not be completed: Backend not reachable")
                        if st.button("Try Again"):
                            pass

elif page == "Intelligence Dashboard":
    st.markdown('<h1 class="tracecho-title">Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tracecho-subtitle" style="margin-bottom: 2rem;">System Overview and Metrics</p>', unsafe_allow_html=True)
    
    try:
        res = requests.get(f"{API_URL}/dashboard")
        if res.status_code == 200:
            data = res.json()
            
            st.markdown("### Market & Financial Overview")
            if "market_error" in data:
                st.warning(f"Market Data Unavailable: {data['market_error']}")
            else:
                market_cols = st.columns(len(data.get("market_overview", {})))
                for col, (k, v) in zip(market_cols, data.get("market_overview", {}).items()):
                    with col:
                        st.metric(k, v)
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Document Intelligence Stats")
                stats = data.get("document_stats", {})
                
                inner_c1, inner_c2 = st.columns(2)
                with inner_c1:
                    st.metric("Total Documents", stats.get("total", 0))
                with inner_c2:
                    st.metric("Total Chunks", stats.get("total_chunks", 0))
                    
                st.markdown(f"""
                <div class="metric-card" style="margin-top: 15px; margin-bottom: 15px;">
                    <div><b>RBI Documents:</b> {stats.get('rbi_count', 0)}</div>
                    <div><b>SEBI Documents:</b> {stats.get('sebi_count', 0)}</div>
                </div>
                """, unsafe_allow_html=True)
                
                categories = data.get("categories", {})
                if categories:
                    st.markdown("#### Top Document Categories")
                    cat_html = "".join([f"<li>{cat}: {count}</li>" for cat, count in categories.items()])
                    st.markdown(f"<ul style='color: var(--text-secondary);'>{cat_html}</ul>", unsafe_allow_html=True)

            with col2:
                st.markdown("### Recent Regulatory Documents")
                for doc in data.get("recent_documents", []):
                    st.markdown(f"""
                    <div class="citation-card" style="border-left: 4px solid #0B1F3A; border-top: 2px solid var(--accent-blue);">
                        <b>{doc.get('regulator', 'Unknown')}</b><br/>
                        <span style="color:var(--text-secondary); font-size:0.9rem;">{doc.get('document_title', 'Untitled')}</span><br/>
                        <span style="color:var(--accent-blue); font-size:0.8rem;">Issue Date: {doc.get('issue_date', 'N/A')}</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("Could not load dashboard data.")
    except Exception as e:
        st.error(f"Backend not reachable: {e}")

elif page == "Document Explorer":
    st.markdown('<h1 class="tracecho-title">Explorer</h1>', unsafe_allow_html=True)
    st.write("Browse the processed SEBI and RBI corpus (To Be Implemented)")

elif page == "System/Evaluation":
    st.markdown('<h1 class="tracecho-title">Evaluation</h1>', unsafe_allow_html=True)
    st.write("Retrieve MRR, Recall@K, and Agent metrics here (To Be Implemented)")
