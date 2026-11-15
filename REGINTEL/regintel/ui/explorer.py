"""
explorer.py — Streamlit Document Explorer page for TRACECHO.

Rendered by ui/app.py when the user navigates to "Document Explorer".
Calls the FastAPI /api/explorer/* endpoints.

Layout
------
Sidebar controls: regulator tab, search, doc-type filter, validity filter, page size
Main area:        results list → click a row → document detail panel
"""

from __future__ import annotations

import streamlit as st
import requests

# ---------------------------------------------------------------------------
# Theme constants (mirror app.py CSS variables)
# ---------------------------------------------------------------------------
_BG = "#050505"
_PANEL = "#0B1F3A"
_BORDER = "#1E3A5F"
_ACCENT = "#2563EB"
_TEXT = "#F3F4F6"
_TEXT2 = "#9CA3AF"
_GREEN = "#16a34a"
_RED = "#dc2626"
_AMBER = "#d97706"

# ---------------------------------------------------------------------------
# Validity badge colours
# ---------------------------------------------------------------------------
_VALIDITY_COLOURS = {
    "current": _GREEN,
    "versioned": _GREEN,
    "superseded": _RED,
    "partially_superseded": _AMBER,
    "unknown": _TEXT2,
}


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _get(url: str, params: dict | None = None) -> dict | None:
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"_error": "Cannot reach the API server. Is it running on port 8000?"}
    except requests.exceptions.Timeout:
        return {"_error": "Request timed out — the corpus may still be loading on first use."}
    except requests.exceptions.HTTPError as exc:
        try:
            detail = exc.response.json().get("detail", str(exc))
        except Exception:
            detail = str(exc)
        return {"_error": detail}
    except Exception as exc:
        return {"_error": str(exc)}


def _error_card(msg: str) -> None:
    st.markdown(
        f"""<div style="background:#1a0a0a;border:1px solid #7f1d1d;border-radius:8px;
            padding:14px 18px;color:#fca5a5;font-size:0.9rem;margin:8px 0;">
            ⚠️ {msg}</div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Document card (catalog list row)
# ---------------------------------------------------------------------------

def _validity_badge(status: str) -> str:
    colour = _VALIDITY_COLOURS.get(status.lower(), _TEXT2)
    label = status.replace("_", " ").title() if status else "Unknown"
    return (
        f'<span style="background:{colour}22;color:{colour};border:1px solid {colour}66;'
        f'border-radius:4px;padding:2px 7px;font-size:0.75rem;font-weight:600;'
        f'white-space:nowrap;">{label}</span>'
    )


def _reg_badge(reg: str) -> str:
    colour = _ACCENT if reg == "RBI" else "#7C3AED"
    return (
        f'<span style="background:{colour};color:white;border-radius:4px;'
        f'padding:2px 8px;font-size:0.75rem;font-weight:700;">{reg}</span>'
    )


def _render_doc_card(doc: dict, idx: int) -> bool:
    """Render one document card. Returns True if the user clicked 'View'."""
    reg = doc.get("regulator", "")
    doc_type = doc.get("document_type", "—")
    circ = doc.get("circular_number", "")
    date = doc.get("issue_date", "")
    title = doc.get("display_title") or doc.get("subject", "Untitled")[:160]
    validity = doc.get("validity_status", "unknown")

    meta_parts = []
    if doc_type:
        meta_parts.append(doc_type)
    if circ:
        meta_parts.append(f"<code style='font-size:0.78rem;color:{_TEXT2};'>{circ}</code>")
    if date:
        meta_parts.append(date)
    meta_line = " &nbsp;·&nbsp; ".join(meta_parts)

    card_html = f"""
    <div style="background:{_PANEL};border:1px solid {_BORDER};border-radius:8px;
                padding:12px 16px;margin-bottom:8px;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
        <div style="flex:1;min-width:0;">
          <div style="margin-bottom:4px;">
            {_reg_badge(reg)}&nbsp;&nbsp;{_validity_badge(validity)}
          </div>
          <div style="color:{_TEXT};font-size:0.95rem;font-weight:500;margin:4px 0;
                      overflow:hidden;text-overflow:ellipsis;">
            {title}
          </div>
          <div style="color:{_TEXT2};font-size:0.82rem;">{meta_line}</div>
        </div>
      </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    return st.button("View document →", key=f"view_{idx}_{doc.get('document_id','')}")


# ---------------------------------------------------------------------------
# Document detail panel
# ---------------------------------------------------------------------------

def _render_detail(api_url: str, document_id: str) -> None:
    if st.button("← Back to results", key="back_btn"):
        st.session_state.pop("explorer_doc_id", None)
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()
        return

    with st.spinner("Loading document…"):
        data = _get(f"{api_url}/explorer/document/{document_id}")

    if data is None or "_error" in data:
        _error_card((data or {}).get("_error", "No response from server."))
        return

    if not data:
        st.warning("Document not found.")
        return

    reg = data.get("regulator", "")
    validity = data.get("validity_status", "unknown")
    chunks = data.get("chunks", [])
    chunk_count = data.get("chunk_count", len(chunks))

    # --- Header ---
    st.markdown(
        f"""<div style="background:{_PANEL};border:1px solid {_BORDER};border-radius:10px;
            padding:20px 24px;margin-bottom:16px;">
          <div style="margin-bottom:8px;">
            {_reg_badge(reg)}&nbsp;&nbsp;{_validity_badge(validity)}
          </div>
          <h2 style="color:{_TEXT};font-size:1.3rem;font-weight:700;margin:8px 0;">
            {data.get('display_title') or data.get('subject','Untitled')}
          </h2>
          <p style="color:{_TEXT2};font-size:0.88rem;margin:0;">
            {data.get('subject','')[:300]}
          </p>
        </div>""",
        unsafe_allow_html=True,
    )

    # --- Metadata grid ---
    meta_items = [
        ("Document ID", data.get("document_id", "—")),
        ("Circular / Ref No.", data.get("circular_number", "—") or "—"),
        ("Document Type", data.get("document_type", "—") or "—"),
        ("Issue Date", data.get("issue_date", "—") or "—"),
        ("Validity", validity.replace("_", " ").title()),
        ("Text Chunks", str(chunk_count)),
    ]
    cols = st.columns(3)
    for i, (label, value) in enumerate(meta_items):
        with cols[i % 3]:
            st.markdown(
                f"""<div style="background:{_PANEL};border:1px solid {_BORDER};border-radius:6px;
                    padding:10px 14px;margin-bottom:8px;">
                  <div style="color:{_TEXT2};font-size:0.78rem;font-weight:600;
                              text-transform:uppercase;letter-spacing:0.05em;">{label}</div>
                  <div style="color:{_TEXT};font-size:0.9rem;margin-top:4px;
                              word-break:break-all;">{value}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<br/>", unsafe_allow_html=True)

    # --- Chunk viewer ---
    if not chunks:
        st.info("No text chunks available for this document.")
        return

    st.markdown(
        f"<h4 style='color:{_TEXT};'>Document Text &nbsp;"
        f"<span style='color:{_TEXT2};font-size:0.85rem;font-weight:400;'>"
        f"({chunk_count} chunk{'s' if chunk_count != 1 else ''})</span></h4>",
        unsafe_allow_html=True,
    )

    # Warn if SEBI single-chunk documents are very long
    if len(chunks) == 1 and len(chunks[0].get("text", "")) > 50_000:
        st.info(
            f"This document contains a single large chunk "
            f"({len(chunks[0]['text']):,} characters). "
            "Showing first 5,000 characters."
        )
        preview_text = chunks[0]["text"][:5_000] + "\n\n[… truncated …]"
        st.text_area(
            label="Full text (truncated)",
            value=preview_text,
            height=400,
            disabled=True,
            key="chunk_text_single",
        )
        return

    # Multi-chunk: accordion per chunk
    for i, chunk in enumerate(chunks):
        chunk_id = chunk.get("chunk_id", f"chunk-{i}")
        text = chunk.get("text", "").strip()
        if not text:
            continue
        label = f"Chunk {i + 1}  —  `{chunk_id}`  ({len(text):,} chars)"
        with st.expander(label, expanded=(i == 0 and len(chunks) == 1)):
            st.markdown(
                f"""<div style="background:{_BG};border:1px solid {_BORDER};border-radius:6px;
                    padding:14px;font-size:0.88rem;color:{_TEXT};line-height:1.6;
                    white-space:pre-wrap;max-height:400px;overflow-y:auto;">
                    {text[:4000]}{"…" if len(text) > 4000 else ""}
                </div>""",
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Main entry point — called by ui/app.py
# ---------------------------------------------------------------------------

def render(api_url: str) -> None:
    """Render the full Document Explorer page."""

    st.markdown(
        '<h1 class="tracecho-title">Document Explorer</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="tracecho-subtitle" style="margin-bottom:1rem;">'
        "Browse the processed RBI &amp; SEBI regulatory corpus"
        "</p>",
        unsafe_allow_html=True,
    )

    # --- If a document detail view is requested, render it and stop ---
    if "explorer_doc_id" in st.session_state and st.session_state["explorer_doc_id"]:
        _render_detail(api_url, st.session_state["explorer_doc_id"])
        return

    # --- Load filter options once per session ---
    if "explorer_filters" not in st.session_state:
        with st.spinner("Loading corpus index…"):
            opts = _get(f"{api_url}/explorer/filters")
        if opts and "_error" not in opts:
            st.session_state["explorer_filters"] = opts
        else:
            st.session_state["explorer_filters"] = {}
            if opts and "_error" in opts:
                _error_card(opts["_error"])
                return

    filters = st.session_state.get("explorer_filters", {})
    rbi_opts = filters.get("rbi", {})
    sebi_opts = filters.get("sebi", {})

    # --- Corpus summary stats ---
    rbi_total = rbi_opts.get("total_docs", 0)
    sebi_total = sebi_opts.get("total_docs", 0)
    c1, c2, c3 = st.columns(3)
    c1.metric("RBI Documents", rbi_total)
    c2.metric("SEBI Documents", sebi_total)
    c3.metric("Total Corpus", rbi_total + sebi_total)

    st.markdown("<hr style='border-color:{};margin:1rem 0;'/>".format(_BORDER), unsafe_allow_html=True)

    # --- Search & filter controls ---
    fc1, fc2, fc3, fc4, fc5 = st.columns([3, 1.5, 1.5, 1.5, 1])

    with fc1:
        search = st.text_input(
            "🔍 Search",
            placeholder="Title, circular number, keywords…",
            key="explorer_search",
            label_visibility="collapsed",
        )

    with fc2:
        regulator = st.selectbox(
            "Regulator", ["Both", "RBI", "SEBI"],
            key="explorer_reg",
            label_visibility="collapsed",
        )

    with fc3:
        # Build doc-type options from both regulators
        all_types = sorted(set(
            rbi_opts.get("document_types", []) + sebi_opts.get("document_types", [])
        ))
        type_options = ["All types"] + all_types
        doc_type_sel = st.selectbox(
            "Type", type_options,
            key="explorer_type",
            label_visibility="collapsed",
        )
        doc_type = "" if doc_type_sel == "All types" else doc_type_sel

    with fc4:
        all_validity = sorted(set(
            rbi_opts.get("validity_statuses", []) + sebi_opts.get("validity_statuses", [])
        ))
        validity_options = ["All statuses"] + all_validity
        validity_sel = st.selectbox(
            "Status", validity_options,
            key="explorer_validity",
            label_visibility="collapsed",
        )
        validity = "" if validity_sel == "All statuses" else validity_sel

    with fc5:
        page_size = st.selectbox(
            "Per page", [10, 20, 50],
            index=1,
            key="explorer_page_size",
            label_visibility="collapsed",
        )

    # --- Pagination state ---
    if "explorer_page" not in st.session_state:
        st.session_state["explorer_page"] = 1

    # Reset to page 1 when filters change
    filter_sig = (search, regulator, doc_type, validity, page_size)
    if st.session_state.get("_explorer_last_filter") != filter_sig:
        st.session_state["explorer_page"] = 1
        st.session_state["_explorer_last_filter"] = filter_sig

    page = st.session_state["explorer_page"]

    # --- Fetch results ---
    with st.spinner("Searching corpus…"):
        result = _get(
            f"{api_url}/explorer/catalog",
            params={
                "regulator": regulator,
                "doc_type": doc_type,
                "validity": validity,
                "search": search,
                "page": page,
                "page_size": page_size,
            },
        )

    if result is None or "_error" in result:
        _error_card((result or {}).get("_error", "No response from server."))
        return

    total = result.get("total", 0)
    total_pages = result.get("total_pages", 1)
    documents = result.get("documents", [])

    # --- Results header ---
    st.markdown(
        f"<p style='color:{_TEXT2};font-size:0.9rem;margin-bottom:12px;'>"
        f"<b style='color:{_TEXT};'>{total:,}</b> document{'s' if total != 1 else ''} found"
        f"&nbsp;·&nbsp;Page {page} of {total_pages}"
        f"</p>",
        unsafe_allow_html=True,
    )

    if not documents:
        st.info("No documents match your search. Try broadening the filters.")
        return

    # --- Document cards ---
    for i, doc in enumerate(documents):
        clicked = _render_doc_card(doc, (page - 1) * page_size + i)
        if clicked:
            st.session_state["explorer_doc_id"] = doc.get("document_id", "")
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()

    # --- Pagination controls ---
    st.markdown("<br/>", unsafe_allow_html=True)
    pc1, pc2, pc3 = st.columns([1, 2, 1])

    with pc1:
        if page > 1:
            if st.button("← Previous", key="prev_page"):
                st.session_state["explorer_page"] = page - 1
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()

    with pc2:
        st.markdown(
            f"<div style='text-align:center;color:{_TEXT2};font-size:0.88rem;padding-top:8px;'>"
            f"Page {page} / {total_pages}</div>",
            unsafe_allow_html=True,
        )

    with pc3:
        if page < total_pages:
            if st.button("Next →", key="next_page"):
                st.session_state["explorer_page"] = page + 1
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()

