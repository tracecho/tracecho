"""
dashboard.py — FastAPI router for the Intelligence Dashboard.

Endpoints
---------
GET  /api/dashboard/market              — Index snapshots (all tracked indices)
GET  /api/dashboard/sectors?period=30  — Sector % change over N days
GET  /api/dashboard/history/{symbol}?period=6mo  — OHLCV + rolling averages
GET  /api/dashboard/regulatory-insights?sector=Banking&top_k=5

None of these endpoints touch the RAG workflow or /api/ask.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from services.market_data import (
    MarketDataError,
    SECTOR_SYMBOLS,
    fetch_historical,
    fetch_market_overview,
    fetch_regulatory_insights,
    fetch_sector_performance,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# ---------------------------------------------------------------------------
# Market overview
# ---------------------------------------------------------------------------

@router.get("/market")
async def market_overview():
    """Current snapshot for all tracked Indian market indices."""
    try:
        data = fetch_market_overview()
    except MarketDataError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")
    return {"indices": data}


# ---------------------------------------------------------------------------
# Sector performance
# ---------------------------------------------------------------------------

@router.get("/sectors")
async def sector_performance(
    period: int = Query(default=30, ge=5, le=365, description="Look-back period in days")
):
    """Percentage change per sector over the given period."""
    try:
        data = fetch_sector_performance(period_days=period)
    except MarketDataError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")
    return {"period_days": period, "sectors": data}


# ---------------------------------------------------------------------------
# Historical time-series
# ---------------------------------------------------------------------------

SYMBOL_WHITELIST: set[str] = set(
    list(
        {
            "^NSEI", "^BSESN", "^NSEBANK", "^CNXIT", "NIFTYMIDCAP100.NS",
            "^CNXFMCG", "^CNXAUTO", "^CNXPHARMA", "^CNXREALTY",
            "^CNXMETAL", "^CNXENERGY",
        }
    )
)


@router.get("/history/{symbol:path}")
async def historical_data(
    symbol: str,
    period: str = Query(default="6mo", pattern="^(1mo|3mo|6mo|1y|2y)$"),
):
    """OHLCV time-series with 20-day / 50-day moving averages and 20-day rolling volatility."""
    if symbol not in SYMBOL_WHITELIST:
        raise HTTPException(
            status_code=400,
            detail=f"Symbol '{symbol}' is not in the allowed list.",
        )
    try:
        data = fetch_historical(symbol, period=period)
    except MarketDataError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")
    return data


# ---------------------------------------------------------------------------
# Regulatory insights
# ---------------------------------------------------------------------------

@router.get("/regulatory-insights")
async def regulatory_insights(
    sector: str = Query(description="Sector name, e.g. Banking, IT, Pharma"),
    top_k: int = Query(default=5, ge=1, le=20),
):
    """Return relevant RBI/SEBI document metadata matching the given sector."""
    if sector not in SECTOR_SYMBOLS and sector != "All":
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sector '{sector}'. Valid: {sorted(SECTOR_SYMBOLS.keys())}",
        )
    try:
        docs = fetch_regulatory_insights(sector, top_k=top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")
    return {"sector": sector, "documents": docs}

