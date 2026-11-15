"""
market_data.py — Market & sector data fetcher for the Intelligence Dashboard.

Data source: Yahoo Finance via yfinance (no API key required).
All public symbols are freely available through the yfinance library.

Returns plain dicts so callers have no yfinance dependency in their type
signatures.  Every public function raises MarketDataError on failure so the
caller can surface a clear error state without crashing.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    _env: Path | None = None
    for _p in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (_p / ".env").exists():
            _env = _p / ".env"
            break
    if _env:
        load_dotenv(dotenv_path=str(_env), override=False)
except Exception:
    pass


class MarketDataError(RuntimeError):
    """Raised when market data cannot be fetched."""


# ---------------------------------------------------------------------------
# Indian market indices tracked on the dashboard
# ---------------------------------------------------------------------------
INDEX_SYMBOLS: dict[str, str] = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY Bank": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY Midcap 100": "NIFTYMIDCAP100.NS",
}

# Indian sector ETF / index proxies available on Yahoo Finance
SECTOR_SYMBOLS: dict[str, str] = {
    "Banking": "^NSEBANK",
    "IT": "^CNXIT",
    "FMCG": "^CNXFMCG",
    "Auto": "^CNXAUTO",
    "Pharma": "^CNXPHARMA",
    "Realty": "^CNXREALTY",
    "Metal": "^CNXMETAL",
    "Energy": "^CNXENERGY",
}

# Regulatory keyword → (regulator, search terms) for RAG cross-reference
SECTOR_REGULATORY_TAGS: dict[str, tuple[str, list[str]]] = {
    "Banking": ("RBI", ["bank", "NBFC", "CRR", "SLR", "prudential", "credit"]),
    "IT": ("SEBI", ["technology", "data", "cyber", "digital", "fintech"]),
    "FMCG": ("SEBI", ["consumer", "disclosure", "listing"]),
    "Auto": ("SEBI", ["automobile", "EV", "emission", "disclosure"]),
    "Pharma": ("SEBI", ["pharmaceutical", "drug", "pricing", "disclosure"]),
    "Realty": ("SEBI", ["real estate", "REIT", "housing", "mortgage"]),
    "Metal": ("SEBI", ["commodity", "mining", "steel", "disclosure"]),
    "Energy": ("RBI", ["energy", "green bond", "infrastructure", "credit"]),
}


def _import_yfinance():
    try:
        import yfinance as yf  # noqa: PLC0415
        return yf
    except ImportError as exc:
        raise MarketDataError(
            "yfinance is not installed. Run: pip install yfinance"
        ) from exc


# ---------------------------------------------------------------------------
# Market overview
# ---------------------------------------------------------------------------

def fetch_market_overview() -> list[dict[str, Any]]:
    """Return current snapshot for all tracked indices.

    Each entry:
        name, symbol, price, change, change_pct, prev_close, volume, currency
    """
    yf = _import_yfinance()
    results: list[dict[str, Any]] = []

    for name, sym in INDEX_SYMBOLS.items():
        try:
            ticker = yf.Ticker(sym)
            info = ticker.fast_info
            price = float(getattr(info, "last_price", None) or 0)
            prev_close = float(getattr(info, "previous_close", None) or 0)
            change = price - prev_close if price and prev_close else 0.0
            change_pct = (change / prev_close * 100) if prev_close else 0.0
            results.append(
                {
                    "name": name,
                    "symbol": sym,
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "prev_close": round(prev_close, 2),
                    "currency": getattr(info, "currency", "INR"),
                }
            )
        except Exception as exc:
            results.append(
                {
                    "name": name,
                    "symbol": sym,
                    "error": str(exc),
                    "price": None,
                    "change": None,
                    "change_pct": None,
                }
            )

    if not results:
        raise MarketDataError("No market data could be retrieved.")
    return results


# ---------------------------------------------------------------------------
# Sector performance
# ---------------------------------------------------------------------------

def fetch_sector_performance(period_days: int = 30) -> list[dict[str, Any]]:
    """Return % change over `period_days` for each tracked sector."""
    yf = _import_yfinance()
    end = datetime.utcnow()
    start = end - timedelta(days=period_days + 5)  # extra buffer for weekends

    results: list[dict[str, Any]] = []
    for sector, sym in SECTOR_SYMBOLS.items():
        try:
            df = yf.download(
                sym,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
                progress=False,
                auto_adjust=True,
            )
            if df.empty or len(df) < 2:
                results.append({"sector": sector, "symbol": sym, "error": "No data"})
                continue

            close = df["Close"].squeeze()
            first_val = float(close.iloc[0])
            last_val = float(close.iloc[-1])
            pct_change = ((last_val - first_val) / first_val * 100) if first_val else 0.0
            current_price = last_val
            results.append(
                {
                    "sector": sector,
                    "symbol": sym,
                    "price": round(current_price, 2),
                    "pct_change": round(pct_change, 2),
                    "period_days": period_days,
                }
            )
        except Exception as exc:
            results.append({"sector": sector, "symbol": sym, "error": str(exc)})

    return results


# ---------------------------------------------------------------------------
# Historical time-series
# ---------------------------------------------------------------------------

def fetch_historical(symbol: str, period: str = "6mo") -> dict[str, Any]:
    """Return OHLCV + rolling averages for `symbol`.

    period: yfinance period string — 1mo 3mo 6mo 1y 2y
    """
    yf = _import_yfinance()
    VALID_PERIODS = {"1mo", "3mo", "6mo", "1y", "2y"}
    if period not in VALID_PERIODS:
        period = "6mo"

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, auto_adjust=True)
    except Exception as exc:
        raise MarketDataError(f"Failed to fetch history for {symbol}: {exc}") from exc

    if df.empty:
        raise MarketDataError(f"No historical data returned for {symbol}.")

    df = df.reset_index()
    df["MA_20"] = df["Close"].rolling(20).mean()
    df["MA_50"] = df["Close"].rolling(50).mean()
    df["Volatility_20"] = df["Close"].pct_change().rolling(20).std() * (252 ** 0.5) * 100  # annualised %

    # Serialise to plain lists for JSON / Plotly
    dates = df["Date"].dt.strftime("%Y-%m-%d").tolist()
    return {
        "symbol": symbol,
        "period": period,
        "dates": dates,
        "open": _safe_list(df["Open"]),
        "high": _safe_list(df["High"]),
        "low": _safe_list(df["Low"]),
        "close": _safe_list(df["Close"]),
        "volume": _safe_list(df["Volume"]),
        "ma_20": _safe_list(df["MA_20"]),
        "ma_50": _safe_list(df["MA_50"]),
        "volatility_20": _safe_list(df["Volatility_20"]),
    }


def _safe_list(series) -> list:
    import math
    return [None if (v is None or (isinstance(v, float) and math.isnan(v))) else round(float(v), 2)
            for v in series]


# ---------------------------------------------------------------------------
# Regulatory insights — keyword match against faiss_meta corpus
# ---------------------------------------------------------------------------

def fetch_regulatory_insights(sector: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Return relevant document metadata from the indexed corpus for the given sector.

    Data layout (actual on-disk format):
      - faiss_meta.json  : list of chunk-ID strings, e.g. "RBI-RBI_0001.txt-0"
      - metadata.json    : dict keyed by those same chunk IDs; each value is a dict
                           with keys: document_id, regulator, subject, document_type,
                           issue_date, text, validity_status, document_origin

    The function loads both files, looks up each chunk ID in the metadata dict,
    then keyword-scans the rich fields to find sector-relevant documents.
    One result entry per unique document_id (deduplicated).
    """
    import json

    tags = SECTOR_REGULATORY_TAGS.get(sector)
    if not tags:
        return []

    regulator, keywords = tags
    data_dir = Path(__file__).resolve().parent.parent / "data" / "processed"

    # --- Load chunk-ID index (list of strings) ---
    chunk_id_path = data_dir / "faiss_meta.json"
    if not chunk_id_path.exists():
        return []
    try:
        with open(chunk_id_path, "r", encoding="utf-8") as fh:
            chunk_ids: list = json.load(fh)
    except Exception:
        return []

    # Validate: must be a list of strings
    if not isinstance(chunk_ids, list) or (chunk_ids and not isinstance(chunk_ids[0], str)):
        return []

    # --- Load rich metadata (dict keyed by chunk ID) ---
    meta_path = data_dir / "metadata.json"
    if not meta_path.exists():
        return []
    try:
        with open(meta_path, "r", encoding="utf-8") as fh:
            metadata: dict = json.load(fh)
    except Exception:
        return []

    if not isinstance(metadata, dict):
        return []

    seen_docs: set[str] = set()
    results: list[dict[str, Any]] = []

    for chunk_id in chunk_ids:
        # chunk_id is a plain string; look it up in the metadata dict
        if not isinstance(chunk_id, str):
            continue

        chunk = metadata.get(chunk_id)
        if not isinstance(chunk, dict):
            continue  # missing or malformed entry — skip safely

        # Regulator filter — field is "regulator" in the metadata
        reg = str(chunk.get("regulator", "")).strip().upper()
        if regulator != "Both" and reg != regulator:
            continue

        # "subject" is the document title equivalent in this corpus
        subject = str(chunk.get("subject", "")).strip()
        doc_id = str(chunk.get("document_id", chunk_id)).strip()
        doc_type = str(chunk.get("document_type", "")).strip()
        issue_date = str(chunk.get("issue_date", "N/A")).strip()
        text_body = str(chunk.get("text", ""))

        # Keyword scan across title + type + body
        searchable = " ".join([subject, doc_type, text_body]).lower()
        if not any(kw.lower() in searchable for kw in keywords):
            continue

        # Deduplicate by document_id (many chunks share one document)
        dedup_key = doc_id or chunk_id
        if dedup_key in seen_docs:
            continue
        seen_docs.add(dedup_key)

        # Truncate subject to a readable length
        display_title = subject[:120] + "…" if len(subject) > 120 else subject
        if not display_title:
            display_title = doc_id

        results.append(
            {
                "regulator": reg,
                "document_title": display_title,
                "document_type": doc_type,
                "issue_date": issue_date,
                "source_url": chunk.get("source_url", ""),
            }
        )
        if len(results) >= top_k:
            break

    return results

