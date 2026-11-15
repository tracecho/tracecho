"""
dashboard.py — Streamlit page for the Intelligence Dashboard.

Rendered by ui/app.py when the user navigates to "Intelligence Dashboard".
Self-contained: imports only standard libs, requests, streamlit, plotly.
Calls the FastAPI dashboard router at API_URL (passed in by app.py).
"""

from __future__ import annotations

import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# Shared chart theme — matches the existing dark CSS in app.py
# ---------------------------------------------------------------------------
_PLOTLY_THEME = "plotly_dark"
_BG = "#050505"
_PANEL = "#0B1F3A"
_BORDER = "#1E3A5F"
_ACCENT = "#2563EB"
_TEXT = "#F3F4F6"
_TEXT2 = "#9CA3AF"

_CHART_LAYOUT = dict(
    paper_bgcolor=_BG,
    plot_bgcolor=_PANEL,
    font=dict(color=_TEXT, family="Inter, Segoe UI, Roboto, sans-serif"),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor=_BORDER, zerolinecolor=_BORDER),
    yaxis=dict(gridcolor=_BORDER, zerolinecolor=_BORDER),
)

# ---------------------------------------------------------------------------
# Sector list (must match services/market_data.py SECTOR_SYMBOLS keys)
# ---------------------------------------------------------------------------
SECTORS = ["Banking", "IT", "FMCG", "Auto", "Pharma", "Realty", "Metal", "Energy"]

SECTOR_SYMBOL_MAP: dict[str, str] = {
    "Banking": "^NSEBANK",
    "IT": "^CNXIT",
    "FMCG": "^CNXFMCG",
    "Auto": "^CNXAUTO",
    "Pharma": "^CNXPHARMA",
    "Realty": "^CNXREALTY",
    "Metal": "^CNXMETAL",
    "Energy": "^CNXENERGY",
}

INDEX_SYMBOL_MAP: dict[str, str] = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY Bank": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY Midcap 100": "NIFTYMIDCAP100.NS",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get(url: str, params: dict | None = None) -> dict | None:
    """HTTP GET with timeout, returns None on failure."""
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"_error": "Cannot connect to the API server. Is it running?"}
    except requests.exceptions.Timeout:
        return {"_error": "Request timed out. The market data feed may be slow."}
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
        f"""<div style="
            background:#1a0a0a; border:1px solid #7f1d1d; border-radius:8px;
            padding:14px 18px; color:#fca5a5; font-size:0.9rem; margin:8px 0;
        ">⚠️ {msg}</div>""",
        unsafe_allow_html=True,
    )


def _loading_note(msg: str = "Fetching live market data…") -> None:
    st.markdown(
        f"""<div style="
            background:{_PANEL}; border:1px solid {_BORDER}; border-radius:8px;
            padding:10px 16px; color:{_TEXT2}; font-size:0.88rem; margin:8px 0;
        ">⏳ {msg}</div>""",
        unsafe_allow_html=True,
    )


def _section_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"<h3 style='margin-bottom:0; color:{_TEXT};'>{title}</h3>",
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f"<p style='color:{_TEXT2}; margin-top:2px; font-size:0.9rem;'>{subtitle}</p>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _render_market_overview(api_url: str) -> None:
    _section_header("Market Overview", "Live snapshot — NIFTY, SENSEX and key indices")

    with st.spinner("Fetching index data…"):
        data = _get(f"{api_url}/dashboard/market")

    if data is None or "_error" in data:
        _error_card(data.get("_error", "Unknown error") if data else "No response from server.")
        return

    indices = data.get("indices", [])
    if not indices:
        st.info("No index data available right now.")
        return

    # Metric cards row
    cols = st.columns(len(indices))
    for col, idx in zip(cols, indices):
        if idx.get("error"):
            col.metric(idx["name"], "—", help=idx["error"])
            continue
        price = idx.get("price")
        chg = idx.get("change_pct")
        col.metric(
            label=idx["name"],
            value=f"₹{price:,.2f}" if price is not None else "—",
            delta=f"{chg:+.2f}%" if chg is not None else None,
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    # Bar chart — daily change %
    valid = [i for i in indices if i.get("change_pct") is not None and not i.get("error")]
    if valid:
        fig = go.Figure(
            go.Bar(
                x=[i["name"] for i in valid],
                y=[i["change_pct"] for i in valid],
                marker_color=[
                    "#16a34a" if v["change_pct"] >= 0 else "#dc2626" for v in valid
                ],
                text=[f"{v['change_pct']:+.2f}%" for v in valid],
                textposition="outside",
            )
        )
        fig.update_layout(
            **_CHART_LAYOUT,
            title="Daily Change (%)",
            yaxis_title="Change (%)",
            showlegend=False,
            height=320,
        )
        st.plotly_chart(fig, use_container_width=True)


def _render_sector_analysis(api_url: str) -> None:
    _section_header("Sector Analysis", "Performance comparison across Indian equity sectors")

    period = st.select_slider(
        "Look-back period",
        options=[7, 14, 30, 60, 90, 180],
        value=30,
        key="sector_period",
        label_visibility="collapsed",
    )
    st.caption(f"Showing {period}-day % change per sector")

    with st.spinner("Fetching sector data…"):
        data = _get(f"{api_url}/dashboard/sectors", params={"period": period})

    if data is None or "_error" in data:
        _error_card(data.get("_error", "Unknown error") if data else "No response.")
        return

    sectors = data.get("sectors", [])
    valid = [s for s in sectors if s.get("pct_change") is not None and not s.get("error")]
    errors = [s for s in sectors if s.get("error")]

    if errors:
        with st.expander(f"⚠️ {len(errors)} sector(s) unavailable"):
            for s in errors:
                st.caption(f"**{s['sector']}**: {s['error']}")

    if not valid:
        st.info("No sector data could be retrieved.")
        return

    valid.sort(key=lambda x: x["pct_change"], reverse=True)

    # Horizontal bar
    fig = go.Figure(
        go.Bar(
            y=[s["sector"] for s in valid],
            x=[s["pct_change"] for s in valid],
            orientation="h",
            marker_color=[
                "#16a34a" if s["pct_change"] >= 0 else "#dc2626" for s in valid
            ],
            text=[f"{s['pct_change']:+.2f}%" for s in valid],
            textposition="outside",
        )
    )
    fig.update_layout(
        **_CHART_LAYOUT,
        title=f"{period}-Day Sector Performance (%)",
        xaxis_title="% Change",
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Colour-coded table
    rows_html = ""
    for s in valid:
        clr = "#16a34a" if s["pct_change"] >= 0 else "#dc2626"
        arrow = "▲" if s["pct_change"] >= 0 else "▼"
        rows_html += (
            f"<tr>"
            f"<td style='padding:8px 12px;'>{s['sector']}</td>"
            f"<td style='padding:8px 12px; text-align:right;'>₹{s.get('price', 0):,.2f}</td>"
            f"<td style='padding:8px 12px; text-align:right; color:{clr};'>"
            f"{arrow} {s['pct_change']:+.2f}%</td>"
            f"</tr>"
        )
    table_html = f"""
    <table style="width:100%; border-collapse:collapse; font-size:0.9rem;
                  background:{_PANEL}; color:{_TEXT}; border-radius:8px; overflow:hidden;">
      <thead>
        <tr style="background:{_BORDER}; color:{_TEXT2};">
          <th style="padding:10px 12px; text-align:left;">Sector</th>
          <th style="padding:10px 12px; text-align:right;">Last Price</th>
          <th style="padding:10px 12px; text-align:right;">{period}d Change</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)


def _render_time_series(api_url: str) -> None:
    _section_header("Time-Series Analysis", "Historical price, moving averages & volatility")

    col1, col2 = st.columns([2, 1])
    with col1:
        all_names = list(INDEX_SYMBOL_MAP.keys()) + [
            f"Sector — {s}" for s in SECTORS
        ]
        selected_name = st.selectbox("Select index / sector", all_names, key="ts_symbol")
    with col2:
        period = st.selectbox(
            "Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2, key="ts_period"
        )

    # Resolve symbol
    symbol = INDEX_SYMBOL_MAP.get(selected_name) or SECTOR_SYMBOL_MAP.get(
        selected_name.replace("Sector — ", "")
    )
    if not symbol:
        st.warning("Unknown symbol selected.")
        return

    with st.spinner(f"Fetching history for {selected_name}…"):
        data = _get(f"{api_url}/dashboard/history/{symbol}", params={"period": period})

    if data is None or "_error" in data:
        _error_card(data.get("_error", "Unknown error") if data else "No response.")
        return

    dates = data.get("dates", [])
    close = data.get("close", [])

    if not dates or not close:
        st.info("No historical data available.")
        return

    # --- Candlestick + moving averages ---
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.20, 0.25],
        vertical_spacing=0.04,
        subplot_titles=["Price & Moving Averages", "Volume", "Annualised Volatility (20d, %)"],
    )

    fig.add_trace(
        go.Candlestick(
            x=dates,
            open=data.get("open"),
            high=data.get("high"),
            low=data.get("low"),
            close=close,
            name="Price",
            increasing_line_color="#16a34a",
            decreasing_line_color="#dc2626",
        ),
        row=1, col=1,
    )

    ma20 = data.get("ma_20", [])
    ma50 = data.get("ma_50", [])
    if any(v is not None for v in ma20):
        fig.add_trace(
            go.Scatter(x=dates, y=ma20, name="MA 20", line=dict(color="#facc15", width=1.5)),
            row=1, col=1,
        )
    if any(v is not None for v in ma50):
        fig.add_trace(
            go.Scatter(x=dates, y=ma50, name="MA 50", line=dict(color="#fb923c", width=1.5)),
            row=1, col=1,
        )

    vol = data.get("volume", [])
    if any(v is not None for v in vol):
        fig.add_trace(
            go.Bar(x=dates, y=vol, name="Volume", marker_color=_ACCENT, opacity=0.6),
            row=2, col=1,
        )

    volatility = data.get("volatility_20", [])
    if any(v is not None for v in volatility):
        fig.add_trace(
            go.Scatter(
                x=dates, y=volatility, name="Volatility",
                line=dict(color="#c084fc", width=1.5), fill="tozeroy",
                fillcolor="rgba(192,132,252,0.08)",
            ),
            row=3, col=1,
        )

    fig.update_layout(
        **_CHART_LAYOUT,
        height=620,
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
        title=f"{selected_name} — {period}",
    )
    for axis in ["xaxis", "xaxis2", "xaxis3", "yaxis", "yaxis2", "yaxis3"]:
        fig.update_layout(**{axis: {"gridcolor": _BORDER, "zerolinecolor": _BORDER}})

    st.plotly_chart(fig, use_container_width=True)


def _render_regulatory_insights(api_url: str) -> None:
    _section_header(
        "Regulatory Insights",
        "RBI & SEBI documents relevant to the selected sector",
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        sector = st.selectbox("Sector", SECTORS, key="reg_sector")
    with col2:
        top_k = st.number_input("Max documents", min_value=1, max_value=20, value=5, key="reg_topk")

    with st.spinner("Matching regulatory corpus…"):
        data = _get(
            f"{api_url}/dashboard/regulatory-insights",
            params={"sector": sector, "top_k": top_k},
        )

    if data is None or "_error" in data:
        _error_card(data.get("_error", "Unknown error") if data else "No response.")
        return

    docs = data.get("documents", [])
    if not docs:
        st.info(
            f"No regulatory documents found matching the **{sector}** sector in the indexed corpus. "
            "This may mean the sector's keywords are not well represented in the current document set."
        )
        return

    st.caption(f"Found **{len(docs)}** relevant document(s) in the RBI/SEBI corpus:")
    for doc in docs:
        reg = doc.get("regulator", "")
        badge_color = "#1D4ED8" if reg == "RBI" else "#7C3AED"
        url = doc.get("source_url", "")
        title_html = (
            f'<a href="{url}" target="_blank" style="color:{_TEXT};">'
            f'{doc.get("document_title", "Untitled")}</a>'
            if url
            else doc.get("document_title", "Untitled")
        )
        st.markdown(
            f"""<div class="citation-card">
                <span style="background:{badge_color}; color:white; border-radius:4px;
                             padding:2px 8px; font-size:0.78rem; font-weight:600;">{reg}</span>
                &nbsp;&nbsp;{title_html}<br/>
                <span style="color:{_TEXT2}; font-size:0.82rem;">
                    {doc.get('document_type', '')}
                    {"&nbsp;•&nbsp;" + doc.get('issue_date', '') if doc.get('issue_date', 'N/A') != 'N/A' else ''}
                </span>
            </div>""",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Main entry point — called from ui/app.py
# ---------------------------------------------------------------------------

def render(api_url: str) -> None:
    """Render the full Intelligence Dashboard page."""
    st.markdown(
        '<h1 class="tracecho-title">Intelligence Dashboard</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="tracecho-subtitle" style="margin-bottom:1.5rem;">'
        "Market Overview · Sector Analysis · Time-Series · Regulatory Insights"
        "</p>",
        unsafe_allow_html=True,
    )

    tab_market, tab_sector, tab_ts, tab_reg = st.tabs(
        ["📈 Market Overview", "🏭 Sector Analysis", "📊 Time-Series", "📋 Regulatory Insights"]
    )

    with tab_market:
        _render_market_overview(api_url)

    with tab_sector:
        _render_sector_analysis(api_url)

    with tab_ts:
        _render_time_series(api_url)

    with tab_reg:
        _render_regulatory_insights(api_url)

