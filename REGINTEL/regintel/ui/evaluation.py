"""
evaluation.py — Streamlit Evaluation page for TRACECHO.

Rendered by ui/app.py when the user navigates to "System/Evaluation".
Calls the FastAPI /api/eval/* endpoints.

Never displays fabricated or hardcoded metrics.
Clearly distinguishes unavailable metrics from zero scores.
Does NOT trigger evaluation automatically on page load.
"""

from __future__ import annotations

import time
import streamlit as st
import requests
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Theme (mirrors app.py CSS)
# ---------------------------------------------------------------------------
_BG     = "#050505"
_PANEL  = "#0B1F3A"
_BORDER = "#1E3A5F"
_ACCENT = "#2563EB"
_TEXT   = "#F3F4F6"
_TEXT2  = "#9CA3AF"
_GREEN  = "#16a34a"
_RED    = "#dc2626"
_AMBER  = "#d97706"

_CHART_LAYOUT = dict(
    paper_bgcolor=_BG,
    plot_bgcolor=_PANEL,
    font=dict(color=_TEXT, family="Inter, Segoe UI, Roboto, sans-serif"),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor=_BORDER, zerolinecolor=_BORDER),
    yaxis=dict(gridcolor=_BORDER, zerolinecolor=_BORDER),
)

METHOD_ORDER = ["vector", "bm25", "hybrid", "hybrid_reranking", "agentic"]
METHOD_COLOURS = {
    "vector":           "#60a5fa",
    "bm25":             "#a78bfa",
    "hybrid":           "#34d399",
    "hybrid_reranking": "#2563EB",
    "agentic":          "#f59e0b",
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
        return {"_error": "Request timed out."}
    except requests.exceptions.HTTPError as exc:
        try:
            detail = exc.response.json().get("detail", str(exc))
        except Exception:
            detail = str(exc)
        return {"_error": detail}
    except Exception as exc:
        return {"_error": str(exc)}


def _post(url: str) -> dict | None:
    try:
        r = requests.post(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        return {"_error": str(exc)}


def _error_card(msg: str) -> None:
    st.markdown(
        f"""<div style="background:#1a0a0a;border:1px solid #7f1d1d;border-radius:8px;
            padding:14px 18px;color:#fca5a5;font-size:0.9rem;margin:8px 0;">
            ⚠️ {msg}</div>""",
        unsafe_allow_html=True,
    )


def _info_card(msg: str) -> None:
    st.markdown(
        f"""<div style="background:{_PANEL};border:1px solid {_BORDER};border-radius:8px;
            padding:14px 18px;color:{_TEXT2};font-size:0.9rem;margin:8px 0;">
            ℹ️ {msg}</div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Section: benchmark overview
# ---------------------------------------------------------------------------

def _render_benchmark(bench: dict) -> None:
    if not bench.get("available"):
        _info_card("Benchmark dataset not found.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Questions", bench.get("total", "—"))
    c2.metric("Answerable",      bench.get("answerable", "—"))
    c3.metric("Out-of-domain",   bench.get("out_of_domain", "—"))

    col_a, col_b = st.columns(2)
    with col_a:
        cats = bench.get("categories", {})
        if cats:
            st.markdown(f"<p style='color:{_TEXT2};font-size:0.85rem;margin-bottom:4px;'>Category breakdown</p>", unsafe_allow_html=True)
            for cat, cnt in sorted(cats.items(), key=lambda x: -x[1]):
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;padding:4px 0;"
                    f"border-bottom:1px solid {_BORDER};font-size:0.88rem;'>"
                    f"<span style='color:{_TEXT};'>{cat}</span>"
                    f"<span style='color:{_ACCENT};font-weight:600;'>{cnt}</span></div>",
                    unsafe_allow_html=True,
                )
    with col_b:
        diffs = bench.get("difficulties", {})
        regs  = bench.get("regulators", {})
        if diffs:
            st.markdown(f"<p style='color:{_TEXT2};font-size:0.85rem;margin-bottom:4px;'>Difficulty</p>", unsafe_allow_html=True)
            for d, cnt in sorted(diffs.items()):
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;padding:4px 0;"
                    f"border-bottom:1px solid {_BORDER};font-size:0.88rem;'>"
                    f"<span style='color:{_TEXT};'>{d}</span>"
                    f"<span style='color:{_ACCENT};font-weight:600;'>{cnt}</span></div>",
                    unsafe_allow_html=True,
                )
        if regs:
            st.markdown(f"<p style='color:{_TEXT2};font-size:0.85rem;margin-top:12px;margin-bottom:4px;'>Regulator</p>", unsafe_allow_html=True)
            for reg, cnt in sorted(regs.items()):
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;padding:4px 0;"
                    f"border-bottom:1px solid {_BORDER};font-size:0.88rem;'>"
                    f"<span style='color:{_TEXT};'>{reg}</span>"
                    f"<span style='color:{_ACCENT};font-weight:600;'>{cnt}</span></div>",
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Section: metric summary cards
# ---------------------------------------------------------------------------

def _render_summary_cards(methods: dict, k_ref: int = 5) -> None:
    ordered = [m for m in METHOD_ORDER if m in methods] + \
              [m for m in methods if m not in METHOD_ORDER]

    cols = st.columns(len(ordered))
    for col, method in zip(cols, ordered):
        m = methods[method]
        label   = m.get("label", method)
        recall  = m.get(f"Recall@{k_ref}")
        mrr_val = m.get(f"MRR@{k_ref}")
        colour  = METHOD_COLOURS.get(method, _ACCENT)

        recall_str = f"{recall:.1%}" if recall is not None else "—"
        mrr_str    = f"{mrr_val:.4f}" if mrr_val is not None else "—"

        col.markdown(
            f"""<div style="background:{_PANEL};border:1px solid {_BORDER};
                border-top:3px solid {colour};border-radius:8px;padding:14px 16px;text-align:center;">
              <div style="color:{_TEXT2};font-size:0.78rem;font-weight:600;text-transform:uppercase;
                          letter-spacing:0.06em;margin-bottom:6px;">{label}</div>
              <div style="color:{colour};font-size:1.6rem;font-weight:800;">{recall_str}</div>
              <div style="color:{_TEXT2};font-size:0.78rem;">Recall@{k_ref}</div>
              <div style="color:{_TEXT};font-size:1rem;font-weight:600;margin-top:6px;">{mrr_str}</div>
              <div style="color:{_TEXT2};font-size:0.78rem;">MRR@{k_ref}</div>
            </div>""",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Section: MRR & Recall@K charts
# ---------------------------------------------------------------------------

def _render_charts(methods: dict, k_values: list[int]) -> None:
    ordered = [m for m in METHOD_ORDER if m in methods] + \
              [m for m in methods if m not in METHOD_ORDER]
    labels  = [methods[m].get("label", m) for m in ordered]
    colours = [METHOD_COLOURS.get(m, _ACCENT) for m in ordered]

    col_left, col_right = st.columns(2)

    # --- Recall@K grouped bar ---
    with col_left:
        st.markdown(f"<h4 style='color:{_TEXT};margin-bottom:8px;'>Recall@K</h4>", unsafe_allow_html=True)
        fig = go.Figure()
        for k in k_values:
            vals = [methods[m].get(f"Recall@{k}") for m in ordered]
            if any(v is not None for v in vals):
                fig.add_trace(go.Bar(
                    name=f"@{k}",
                    x=labels,
                    y=[v if v is not None else 0 for v in vals],
                    text=[f"{v:.1%}" if v is not None else "—" for v in vals],
                    textposition="outside",
                ))
        fig.update_layout(
            **{**_CHART_LAYOUT, "yaxis": dict(range=[0, 1.1], gridcolor=_BORDER, zerolinecolor=_BORDER, tickformat=".0%")},
            barmode="group",
            height=340,
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- MRR@K grouped bar ---
    with col_right:
        st.markdown(f"<h4 style='color:{_TEXT};margin-bottom:8px;'>MRR@K</h4>", unsafe_allow_html=True)
        fig2 = go.Figure()
        for k in k_values:
            vals = [methods[m].get(f"MRR@{k}") for m in ordered]
            if any(v is not None for v in vals):
                fig2.add_trace(go.Bar(
                    name=f"@{k}",
                    x=labels,
                    y=[v if v is not None else 0 for v in vals],
                    text=[f"{v:.4f}" if v is not None else "—" for v in vals],
                    textposition="outside",
                ))
        fig2.update_layout(
            **{**_CHART_LAYOUT, "yaxis": dict(range=[0, 1.1], gridcolor=_BORDER, zerolinecolor=_BORDER)},
            barmode="group",
            height=340,
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- HitRate@5 horizontal bar (single K for readability) ---
    k_ref = 5 if 5 in k_values else k_values[0]
    hr_vals = [methods[m].get(f"HitRate@{k_ref}") for m in ordered]
    if any(v is not None for v in hr_vals):
        st.markdown(f"<h4 style='color:{_TEXT};margin-bottom:8px;'>Hit Rate@{k_ref}</h4>", unsafe_allow_html=True)
        fig3 = go.Figure(go.Bar(
            y=labels,
            x=[v if v is not None else 0 for v in hr_vals],
            orientation="h",
            marker_color=colours,
            text=[f"{v:.1%}" if v is not None else "—" for v in hr_vals],
            textposition="outside",
        ))
        fig3.update_layout(
            **{**_CHART_LAYOUT, "xaxis": dict(range=[0, 1.1], gridcolor=_BORDER, zerolinecolor=_BORDER, tickformat=".0%")},
            height=max(200, 60 * len(ordered)),
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)


# ---------------------------------------------------------------------------
# Section: full metrics table
# ---------------------------------------------------------------------------

def _render_metrics_table(methods: dict, k_values: list[int]) -> None:
    ordered = [m for m in METHOD_ORDER if m in methods] + \
              [m for m in methods if m not in METHOD_ORDER]

    # Build header
    k_headers = "".join(
        f"<th style='padding:8px 12px;text-align:right;'>Recall@{k}</th>"
        f"<th style='padding:8px 12px;text-align:right;'>MRR@{k}</th>"
        for k in k_values
    )
    header_html = (
        f"<thead><tr style='background:{_BORDER};color:{_TEXT2};font-size:0.8rem;'>"
        f"<th style='padding:8px 12px;text-align:left;'>Method</th>"
        f"{k_headers}"
        f"</tr></thead>"
    )

    rows_html = ""
    for method in ordered:
        m = methods[method]
        label  = m.get("label", method)
        colour = METHOD_COLOURS.get(method, _ACCENT)
        cells = "".join(
            f"<td style='padding:8px 12px;text-align:right;'>"
            f"{m[f'Recall@{k}']:.1%}" if m.get(f"Recall@{k}") is not None else "<td style='padding:8px 12px;text-align:right;'>—"
            f"</td>"
            f"<td style='padding:8px 12px;text-align:right;'>"
            f"{m[f'MRR@{k}']:.4f}" if m.get(f"MRR@{k}") is not None else "—"
            f"</td>"
            for k in k_values
        )
        rows_html += (
            f"<tr style='border-bottom:1px solid {_BORDER};'>"
            f"<td style='padding:8px 12px;'>"
            f"<span style='background:{colour};color:white;border-radius:4px;"
            f"padding:2px 8px;font-size:0.78rem;font-weight:700;'>{label}</span>"
            f"</td>{cells}</tr>"
        )

    table_html = (
        f"<table style='width:100%;border-collapse:collapse;font-size:0.9rem;"
        f"background:{_PANEL};color:{_TEXT};border-radius:8px;overflow:hidden;'>"
        f"{header_html}<tbody>{rows_html}</tbody></table>"
    )
    st.markdown(table_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section: per-question detail table
# ---------------------------------------------------------------------------

def _render_per_question(per_question: list[dict]) -> None:
    if not per_question:
        _info_card("No per-question data available.")
        return

    rows_html = ""
    for q in per_question:
        answerable = q.get("answerable", True)
        hit        = q.get("hit_at_5")
        rank       = q.get("first_rank")
        rr         = q.get("reciprocal_rank")

        hit_badge = ""
        if answerable:
            if hit is True:
                hit_badge = f"<span style='color:{_GREEN};font-weight:700;'>✓ Hit</span>"
            elif hit is False:
                hit_badge = f"<span style='color:{_RED};font-weight:700;'>✗ Miss</span>"
            else:
                hit_badge = f"<span style='color:{_TEXT2};'>—</span>"
        else:
            hit_badge = f"<span style='color:{_AMBER};'>OOD</span>"

        rank_str = str(rank) if rank is not None else "—"
        rr_str   = f"{rr:.4f}" if rr is not None else "—"

        rows_html += (
            f"<tr style='border-bottom:1px solid {_BORDER};font-size:0.85rem;'>"
            f"<td style='padding:7px 10px;color:{_TEXT2};'>{q.get('question_id','')}</td>"
            f"<td style='padding:7px 10px;color:{_TEXT};max-width:400px;'>{q.get('question','')[:100]}</td>"
            f"<td style='padding:7px 10px;text-align:center;'>{hit_badge}</td>"
            f"<td style='padding:7px 10px;text-align:right;color:{_TEXT};'>{rank_str}</td>"
            f"<td style='padding:7px 10px;text-align:right;color:{_ACCENT};'>{rr_str}</td>"
            f"</tr>"
        )

    table_html = (
        f"<div style='overflow-x:auto;'>"
        f"<table style='width:100%;border-collapse:collapse;background:{_PANEL};"
        f"color:{_TEXT};border-radius:8px;overflow:hidden;'>"
        f"<thead><tr style='background:{_BORDER};color:{_TEXT2};font-size:0.78rem;'>"
        f"<th style='padding:8px 10px;text-align:left;'>ID</th>"
        f"<th style='padding:8px 10px;text-align:left;'>Question</th>"
        f"<th style='padding:8px 10px;text-align:center;'>Hit@5</th>"
        f"<th style='padding:8px 10px;text-align:right;'>Rank</th>"
        f"<th style='padding:8px 10px;text-align:right;'>RR</th>"
        f"</tr></thead>"
        f"<tbody>{rows_html}</tbody></table></div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Run trigger section
# ---------------------------------------------------------------------------

def _render_run_section(api_url: str) -> None:
    st.markdown(
        f"<h4 style='color:{_TEXT};margin-bottom:4px;'>Run Evaluation Pipeline</h4>"
        f"<p style='color:{_TEXT2};font-size:0.88rem;margin-bottom:12px;'>"
        f"Triggers the full retrieval evaluation over the benchmark dataset. "
        f"This can take several minutes. Results are saved automatically."
        f"</p>",
        unsafe_allow_html=True,
    )

    # Check current run status
    status_data = _get(f"{api_url}/eval/run/status") or {}
    run_status  = status_data.get("status", "idle")
    run_message = status_data.get("message", "")

    if run_status == "running" or run_status == "starting":
        st.markdown(
            f"""<div style="background:{_PANEL};border:1px solid {_AMBER};border-radius:8px;
                padding:12px 16px;color:{_AMBER};font-size:0.9rem;">
                ⏳ {run_message or 'Evaluation is running…'}</div>""",
            unsafe_allow_html=True,
        )
        if st.button("↻ Refresh status", key="refresh_run_status"):
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
        return

    if run_status == "done":
        st.success(f"✓ {run_message}")

    if run_status == "error":
        _error_card(f"Run failed: {run_message}")

    if st.button("▶ Run Evaluation Now", key="trigger_eval", type="primary"):
        resp = _post(f"{api_url}/eval/run")
        if resp and "_error" not in resp:
            st.info("Evaluation queued. This will take several minutes. Refresh the page to check status.")
        elif resp:
            _error_card(resp.get("_error", "Failed to queue evaluation."))
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def render(api_url: str) -> None:
    """Render the full System/Evaluation page."""
    st.markdown(
        '<h1 class="tracecho-title">System · Evaluation</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="tracecho-subtitle" style="margin-bottom:1.5rem;">'
        "Retrieval metrics · Agent performance · Benchmark overview"
        "</p>",
        unsafe_allow_html=True,
    )

    tab_results, tab_benchmark, tab_run = st.tabs(
        ["📊 Retrieval Metrics", "📋 Benchmark Dataset", "⚙️ Run Evaluation"]
    )

    # ----------------------------------------------------------------
    # Tab 1 — Retrieval Metrics
    # ----------------------------------------------------------------
    with tab_results:
        # K selector and timestamp selector in one row
        ctrl_left, ctrl_mid, ctrl_right = st.columns([2, 2, 2])

        with ctrl_left:
            k_choices = st.multiselect(
                "K values",
                options=[1, 3, 5, 10, 15],
                default=[3, 5, 10],
                key="eval_k_values",
            )
            if not k_choices:
                k_choices = [5]
            k_choices = sorted(set(k_choices))

        # Load available timestamps first (lightweight call)
        with st.spinner("Loading evaluation results…"):
            results = _get(f"{api_url}/eval/results", params={"k": k_choices})

        if results is None or "_error" in results:
            _error_card((results or {}).get("_error", "No response from server."))
            return

        timestamps = results.get("timestamps", [])

        with ctrl_mid:
            if len(timestamps) > 1:
                ts_display = {ts: ts for ts in timestamps}
                selected_ts = st.selectbox(
                    "Result run",
                    options=timestamps,
                    index=0,
                    key="eval_ts_selector",
                )
                if selected_ts != results.get("timestamp"):
                    with st.spinner("Loading selected run…"):
                        results = _get(
                            f"{api_url}/eval/results/{selected_ts}",
                            params={"k": k_choices},
                        ) or results
            else:
                st.markdown(
                    f"<p style='color:{_TEXT2};font-size:0.85rem;padding-top:28px;'>"
                    f"{len(timestamps)} run(s) available</p>",
                    unsafe_allow_html=True,
                )

        with ctrl_right:
            display_ts = results.get("display_ts", results.get("timestamp", "—"))
            st.markdown(
                f"<p style='color:{_TEXT2};font-size:0.85rem;padding-top:28px;'>"
                f"Run: <b style='color:{_TEXT};'>{display_ts}</b></p>",
                unsafe_allow_html=True,
            )

        if not results.get("available"):
            _info_card(results.get("message", "No evaluation results found. Run the pipeline first."))

        else:
            methods   = results.get("methods", {})
            k_values  = results.get("k_values", k_choices)
            k_ref     = 5 if 5 in k_values else k_values[0]

            st.markdown("<br/>", unsafe_allow_html=True)

            # Summary cards
            _render_summary_cards(methods, k_ref=k_ref)
            st.markdown("<br/>", unsafe_allow_html=True)

            # Charts
            _render_charts(methods, k_values)
            st.markdown("<br/>", unsafe_allow_html=True)

            # Full metrics table
            st.markdown(
                f"<h4 style='color:{_TEXT};'>All Metrics</h4>",
                unsafe_allow_html=True,
            )
            _render_metrics_table(methods, k_values)
            st.markdown("<br/>", unsafe_allow_html=True)

            # Per-question detail
            per_q = results.get("per_question", [])
            if per_q:
                with st.expander(f"Per-question detail ({len(per_q)} questions) — Hybrid+Reranking method"):
                    _render_per_question(per_q)

    # ----------------------------------------------------------------
    # Tab 2 — Benchmark Dataset
    # ----------------------------------------------------------------
    with tab_benchmark:
        bench_data = _get(f"{api_url}/eval/benchmark")
        if bench_data and "_error" not in bench_data:
            _render_benchmark(bench_data)
        elif bench_data:
            _error_card(bench_data.get("_error", "Could not load benchmark data."))

    # ----------------------------------------------------------------
    # Tab 3 — Run Evaluation
    # ----------------------------------------------------------------
    with tab_run:
        _render_run_section(api_url)

