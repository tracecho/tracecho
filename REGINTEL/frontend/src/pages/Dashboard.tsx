import React, { useEffect, useState, useCallback } from "react";
import AppShell from "@/components/layout/AppShell";
import api from "@/lib/api";
import {
  RefreshCw,
  TrendingUp,
  TrendingDown,
  ExternalLink,
  AlertCircle,
  FileText,
  Calendar,
  Layers,
  LineChart as LineChartIcon,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from "recharts";

// ─── Whitelist & Constants ───────────────────────────────────────────────────

interface SymbolOption {
  symbol: string;
  name: string;
}

const WHITELISTED_SYMBOLS: SymbolOption[] = [
  { symbol: "^NSEI", name: "NIFTY 50" },
  { symbol: "^BSESN", name: "SENSEX" },
  { symbol: "^NSEBANK", name: "NIFTY Bank" },
  { symbol: "^CNXIT", name: "NIFTY IT" },
  { symbol: "NIFTYMIDCAP100.NS", name: "NIFTY Midcap 100" },
  { symbol: "^CNXFMCG", name: "NIFTY FMCG" },
  { symbol: "^CNXAUTO", name: "NIFTY Auto" },
  { symbol: "^CNXPHARMA", name: "NIFTY Pharma" },
  { symbol: "^CNXREALTY", name: "NIFTY Realty" },
  { symbol: "^CNXMETAL", name: "NIFTY Metal" },
  { symbol: "^CNXENERGY", name: "NIFTY Energy" },
];

const VALID_SECTORS: string[] = [
  "All",
  "Banking",
  "IT",
  "Pharma",
  "Auto",
  "FMCG",
  "Realty",
  "Metal",
  "Energy",
];

// ─── Types ───────────────────────────────────────────────────────────────────

interface MarketCardItem {
  symbol: string;
  name: string;
  price?: number | null;
  change?: number | null;
  change_pct?: number | null;
  volume?: number | null;
  error?: string;
}

interface SectorChartItem {
  name: string;
  symbol: string;
  change_pct: number;
  price?: number;
}

interface HistoryDataPoint {
  date: string;
  close: number | null;
  ma20: number | null;
  ma50: number | null;
}

interface RegulatoryDocItem {
  document_id?: string;
  document_title: string;
  regulator: string;
  document_type: string;
  issue_date: string;
  source_url?: string;
  relevance_note?: string;
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function Dashboard() {
  // --- State: Market Overview ---
  const [marketIndices, setMarketIndices] = useState<MarketCardItem[]>([]);
  const [loadingMarket, setLoadingMarket] = useState<boolean>(true);
  const [errorMarket, setErrorMarket] = useState<string | null>(null);

  // --- State: Sector Performance ---
  const [sectorPeriod, setSectorPeriod] = useState<number>(30); // 7, 30, 90
  const [sectorData, setSectorData] = useState<SectorChartItem[]>([]);
  const [loadingSectors, setLoadingSectors] = useState<boolean>(true);
  const [errorSectors, setErrorSectors] = useState<string | null>(null);

  // --- State: Historical Time Series ---
  const [historySymbol, setHistorySymbol] = useState<string>("^NSEI");
  const [historyPeriod, setHistoryPeriod] = useState<string>("6mo"); // 1mo, 3mo, 6mo, 1y
  const [historyData, setHistoryData] = useState<HistoryDataPoint[]>([]);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(true);
  const [errorHistory, setErrorHistory] = useState<string | null>(null);

  // --- State: Regulatory Insights ---
  const [insightSector, setInsightSector] = useState<string>("Banking");
  const [regulatoryDocs, setRegulatoryDocs] = useState<RegulatoryDocItem[]>([]);
  const [loadingInsights, setLoadingInsights] = useState<boolean>(true);
  const [errorInsights, setErrorInsights] = useState<string | null>(null);

  // ─── Fetchers ───────────────────────────────────────────────────────────────

  const fetchMarket = useCallback(async () => {
    setLoadingMarket(true);
    setErrorMarket(null);
    try {
      const res = await api.get("/api/dashboard/market");
      const list = Array.isArray(res.data)
        ? res.data
        : res.data?.indices || [];
      setMarketIndices(list);
    } catch (err: any) {
      setErrorMarket(
        err?.response?.data?.detail ||
          err?.message ||
          "Failed to load market overview"
      );
    } finally {
      setLoadingMarket(false);
    }
  }, []);

  const fetchSectors = useCallback(async (period: number) => {
    setLoadingSectors(true);
    setErrorSectors(null);
    try {
      const res = await api.get("/api/dashboard/sectors", {
        params: { period },
      });
      const list = Array.isArray(res.data)
        ? res.data
        : res.data?.sectors || [];
      const formatted: SectorChartItem[] = list.map((item: any) => ({
        name: item.sector || item.name || item.symbol || "Unknown",
        symbol: item.symbol || "",
        change_pct:
          typeof item.pct_change === "number"
            ? item.pct_change
            : typeof item.change_pct === "number"
            ? item.change_pct
            : 0,
        price: item.price,
      }));
      setSectorData(formatted);
    } catch (err: any) {
      setErrorSectors(
        err?.response?.data?.detail ||
          err?.message ||
          "Failed to load sector performance"
      );
    } finally {
      setLoadingSectors(false);
    }
  }, []);

  const fetchHistory = useCallback(
    async (symbol: string, period: string) => {
      setLoadingHistory(true);
      setErrorHistory(null);
      try {
        const res = await api.get(`/api/dashboard/history/${encodeURIComponent(symbol)}`, {
          params: { period },
        });
        const raw = res.data;
        let points: HistoryDataPoint[] = [];

        if (raw?.data && Array.isArray(raw.data)) {
          points = raw.data.map((d: any) => ({
            date: d.date || "",
            close: d.close ?? null,
            ma20: d.ma20 ?? d.ma_20 ?? null,
            ma50: d.ma50 ?? d.ma_50 ?? null,
          }));
        } else if (raw?.dates && Array.isArray(raw.dates)) {
          points = raw.dates.map((d: string, i: number) => ({
            date: d,
            close: raw.close?.[i] ?? null,
            ma20: raw.ma_20?.[i] ?? raw.ma20?.[i] ?? null,
            ma50: raw.ma_50?.[i] ?? raw.ma50?.[i] ?? null,
          }));
        }

        setHistoryData(points);
      } catch (err: any) {
        setErrorHistory(
          err?.response?.data?.detail ||
            err?.message ||
            "Failed to load historical data"
        );
      } finally {
        setLoadingHistory(false);
      }
    },
    []
  );

  const fetchInsights = useCallback(async (sector: string) => {
    setLoadingInsights(true);
    setErrorInsights(null);
    try {
      const res = await api.get("/api/dashboard/regulatory-insights", {
        params: { sector, top_k: 5 },
      });
      const list = res.data?.documents || (Array.isArray(res.data) ? res.data : []);
      const formatted: RegulatoryDocItem[] = list.map((doc: any) => ({
        document_id: doc.document_id || doc.id || "",
        document_title: doc.document_title || doc.title || "Untitled Document",
        regulator: doc.regulator || "RBI",
        document_type: doc.document_type || doc.doc_type || "Circular",
        issue_date: doc.issue_date || doc.date || "N/A",
        source_url: doc.source_url || doc.url || "",
        relevance_note: doc.relevance_note || "",
      }));
      setRegulatoryDocs(formatted);
    } catch (err: any) {
      setErrorInsights(
        err?.response?.data?.detail ||
          err?.message ||
          "Failed to load regulatory insights"
      );
    } finally {
      setLoadingInsights(false);
    }
  }, []);

  // ─── Initial Load & Observers ───────────────────────────────────────────────

  useEffect(() => {
    fetchMarket();
  }, [fetchMarket]);

  useEffect(() => {
    fetchSectors(sectorPeriod);
  }, [sectorPeriod, fetchSectors]);

  useEffect(() => {
    fetchHistory(historySymbol, historyPeriod);
  }, [historySymbol, historyPeriod, fetchHistory]);

  useEffect(() => {
    fetchInsights(insightSector);
  }, [insightSector, fetchInsights]);

  // ─── Helper Formatters ──────────────────────────────────────────────────────

  const formatNumber = (num?: number | null) => {
    if (num === undefined || num === null) return "--";
    return num.toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  const selectedSymbolName =
    WHITELISTED_SYMBOLS.find((s) => s.symbol === historySymbol)?.name ||
    historySymbol;

  return (
    <AppShell>
      <div className="space-y-6 max-w-7xl mx-auto pb-12">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-[#E2E9E6]">
          <div>
            <h1 className="text-2xl font-bold text-[#202C2A] tracking-tight">
              Overview Dashboard
            </h1>
            <p className="text-sm text-[#66736F] mt-1">
              Indian market benchmarks, sectoral momentum, and correlated regulatory updates
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-[#167568]/10 text-[#167568] border border-[#167568]/20">
              <span className="w-2 h-2 rounded-full bg-[#167568] animate-pulse"></span>
              Live Intelligence
            </span>
          </div>
        </div>

        {/* ────────────────────────────────────────────────────────────────────
            SECTION A: Market Overview — KPI Cards Row
        ──────────────────────────────────────────────────────────────────── */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-[14px] uppercase tracking-wider text-[#66736F] font-semibold">
              Market Overview
            </h2>
            <button
              onClick={fetchMarket}
              disabled={loadingMarket}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-white text-[#202C2A] border border-[#E2E9E6] hover:bg-slate-50 transition-colors disabled:opacity-50"
              title="Refresh Market Overview"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 text-[#167568] ${
                  loadingMarket ? "animate-spin" : ""
                }`}
              />
              <span>Refresh</span>
            </button>
          </div>

          {/* Error Banner */}
          {errorMarket && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-[#dc2626]">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMarket}</span>
            </div>
          )}

          {/* KPI Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {loadingMarket
              ? Array.from({ length: 5 }).map((_, idx) => (
                  <div
                    key={idx}
                    className="bg-[#FFFFFF] border border-[#E2E9E6] rounded-lg p-4 shadow-sm animate-pulse space-y-3"
                  >
                    <div className="h-3.5 bg-slate-200 rounded w-1/2"></div>
                    <div className="h-7 bg-slate-200 rounded w-3/4"></div>
                    <div className="h-3 bg-slate-200 rounded w-1/3"></div>
                  </div>
                ))
              : marketIndices.map((idxItem) => {
                  const isPositive = (idxItem.change ?? 0) >= 0;
                  return (
                    <div
                      key={idxItem.symbol}
                      className="bg-[#FFFFFF] border border-[#E2E9E6] rounded-lg p-4 shadow-sm transition-all hover:border-[#167568]/40"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-[#66736F] truncate">
                          {idxItem.name || idxItem.symbol}
                        </span>
                        {isPositive ? (
                          <TrendingUp className="w-4 h-4 text-[#16a34a]" />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-[#dc2626]" />
                        )}
                      </div>
                      <div className="mt-2 flex items-baseline justify-between">
                        <span className="text-xl font-bold text-[#202C2A]">
                          {formatNumber(idxItem.price)}
                        </span>
                      </div>
                      <div className="mt-1 flex items-center gap-1.5 text-xs font-medium">
                        <span
                          className={
                            isPositive ? "text-[#16a34a]" : "text-[#dc2626]"
                          }
                        >
                          {isPositive ? "+" : ""}
                          {formatNumber(idxItem.change)} (
                          {isPositive ? "+" : ""}
                          {formatNumber(idxItem.change_pct)}%)
                        </span>
                      </div>
                    </div>
                  );
                })}
          </div>
        </section>

        {/* ────────────────────────────────────────────────────────────────────
            MIDDLE ROW: B. Sector Performance Chart + C. Historical Trends
        ──────────────────────────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* SECTION B: Sector Performance Chart */}
          <section className="bg-[#FFFFFF] border border-[#E2E9E6] rounded-lg p-5 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <h2 className="text-[14px] uppercase tracking-wider text-[#66736F] font-semibold flex items-center gap-2">
                  <Layers className="w-4 h-4 text-[#167568]" />
                  Sector Performance
                </h2>
                <p className="text-xs text-[#66736F] mt-0.5">
                  Percentage change across key Indian sectors
                </p>
              </div>

              {/* Period Selector */}
              <div className="inline-flex rounded-md border border-[#E2E9E6] p-0.5 bg-[#F5F7F7]">
                {[
                  { label: "7d", val: 7 },
                  { label: "30d", val: 30 },
                  { label: "90d", val: 90 },
                ].map((p) => (
                  <button
                    key={p.val}
                    onClick={() => setSectorPeriod(p.val)}
                    className={`px-2.5 py-1 text-xs font-medium rounded transition-colors ${
                      sectorPeriod === p.val
                        ? "bg-[#167568] text-white shadow-sm"
                        : "text-[#66736F] hover:text-[#202C2A]"
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Error Banner */}
            {errorSectors && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-[#dc2626]">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{errorSectors}</span>
              </div>
            )}

            {/* Chart Container */}
            <div className="h-72 w-full pt-2">
              {loadingSectors ? (
                <div className="h-full flex flex-col items-center justify-center gap-3">
                  <div className="w-48 h-3 bg-slate-200 rounded animate-pulse"></div>
                  <div className="w-64 h-3 bg-slate-200 rounded animate-pulse"></div>
                  <div className="w-36 h-3 bg-slate-200 rounded animate-pulse"></div>
                </div>
              ) : sectorData.length === 0 ? (
                <div className="h-full flex items-center justify-center text-sm text-[#66736F]">
                  No sector performance data available.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={sectorData}
                    margin={{ top: 10, right: 10, left: -10, bottom: 25 }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                      stroke="#E2E9E6"
                    />
                    <XAxis
                      dataKey="name"
                      tick={{ fill: "#66736F", fontSize: 11 }}
                      interval={0}
                      angle={-25}
                      textAnchor="end"
                      height={40}
                    />
                    <YAxis
                      unit="%"
                      tick={{ fill: "#66736F", fontSize: 11 }}
                    />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload as SectorChartItem;
                          const isPos = data.change_pct >= 0;
                          return (
                            <div className="bg-white border border-[#E2E9E6] p-2.5 rounded shadow-md text-xs space-y-1">
                              <p className="font-semibold text-[#202C2A]">
                                {data.name}
                              </p>
                              {data.price !== undefined && (
                                <p className="text-[#66736F]">
                                  Index: ₹{formatNumber(data.price)}
                                </p>
                              )}
                              <p
                                className={`font-medium ${
                                  isPos ? "text-[#16a34a]" : "text-[#dc2626]"
                                }`}
                              >
                                Change: {isPos ? "+" : ""}
                                {data.change_pct}%
                              </p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <ReferenceLine y={0} stroke="#E2E9E6" />
                    <Bar dataKey="change_pct" radius={[4, 4, 0, 0]}>
                      {sectorData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={entry.change_pct >= 0 ? "#16a34a" : "#dc2626"}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </section>

          {/* SECTION C: Time-series Chart with Symbol Selector */}
          <section className="bg-[#FFFFFF] border border-[#E2E9E6] rounded-lg p-5 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <h2 className="text-[14px] uppercase tracking-wider text-[#66736F] font-semibold flex items-center gap-2">
                  <LineChartIcon className="w-4 h-4 text-[#167568]" />
                  Historical Trends
                </h2>
                <p className="text-xs text-[#66736F] mt-0.5">
                  {selectedSymbolName} close price with 20 & 50-day MAs
                </p>
              </div>

              {/* Controls: Symbol Selector + Period Selector */}
              <div className="flex items-center gap-2 flex-wrap">
                <select
                  value={historySymbol}
                  onChange={(e) => setHistorySymbol(e.target.value)}
                  className="px-2.5 py-1 text-xs font-medium rounded border border-[#E2E9E6] bg-white text-[#202C2A] focus:outline-none focus:border-[#167568]"
                >
                  {WHITELISTED_SYMBOLS.map((s) => (
                    <option key={s.symbol} value={s.symbol}>
                      {s.name}
                    </option>
                  ))}
                </select>

                <div className="inline-flex rounded-md border border-[#E2E9E6] p-0.5 bg-[#F5F7F7]">
                  {["1mo", "3mo", "6mo", "1y"].map((per) => (
                    <button
                      key={per}
                      onClick={() => setHistoryPeriod(per)}
                      className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
                        historyPeriod === per
                          ? "bg-[#167568] text-white shadow-sm"
                          : "text-[#66736F] hover:text-[#202C2A]"
                      }`}
                    >
                      {per}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Error Banner */}
            {errorHistory && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-[#dc2626]">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{errorHistory}</span>
              </div>
            )}

            {/* Chart Container */}
            <div className="h-72 w-full pt-2">
              {loadingHistory ? (
                <div className="h-full flex flex-col items-center justify-center gap-3">
                  <div className="w-48 h-3 bg-slate-200 rounded animate-pulse"></div>
                  <div className="w-64 h-3 bg-slate-200 rounded animate-pulse"></div>
                  <div className="w-36 h-3 bg-slate-200 rounded animate-pulse"></div>
                </div>
              ) : historyData.length === 0 ? (
                <div className="h-full flex items-center justify-center text-sm text-[#66736F]">
                  No historical data available.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={historyData}
                    margin={{ top: 10, right: 10, left: -10, bottom: 5 }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                      stroke="#E2E9E6"
                    />
                    <XAxis
                      dataKey="date"
                      tick={{ fill: "#66736F", fontSize: 11 }}
                      minTickGap={30}
                    />
                    <YAxis
                      domain={["auto", "auto"]}
                      tick={{ fill: "#66736F", fontSize: 11 }}
                    />
                    <Tooltip
                      content={({ active, payload, label }) => {
                        if (active && payload && payload.length) {
                          return (
                            <div className="bg-white border border-[#E2E9E6] p-2.5 rounded shadow-md text-xs space-y-1">
                              <p className="font-semibold text-[#202C2A]">
                                {label}
                              </p>
                              {payload.map((p: any) => (
                                <p
                                  key={p.dataKey}
                                  style={{ color: p.color }}
                                  className="font-medium"
                                >
                                  {p.name}: ₹{formatNumber(p.value)}
                                </p>
                              ))}
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Legend
                      verticalAlign="top"
                      height={32}
                      wrapperStyle={{ fontSize: 11 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="close"
                      name="Close"
                      stroke="#167568"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="ma20"
                      name="MA 20"
                      stroke="#0d9488"
                      strokeWidth={1.5}
                      strokeDasharray="4 4"
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="ma50"
                      name="MA 50"
                      stroke="#f59e0b"
                      strokeWidth={1.5}
                      strokeDasharray="4 4"
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </section>
        </div>

        {/* ────────────────────────────────────────────────────────────────────
            SECTION D: Regulatory Insights Panel
        ──────────────────────────────────────────────────────────────────── */}
        <section className="bg-[#FFFFFF] border border-[#E2E9E6] rounded-lg p-5 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h2 className="text-[14px] uppercase tracking-wider text-[#66736F] font-semibold flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#167568]" />
                Regulatory Insights Cross-Reference
              </h2>
              <p className="text-xs text-[#66736F] mt-0.5">
                Key circulars, notifications & regulatory guidelines by sector
              </p>
            </div>

            {/* Sector Selector */}
            <div className="flex items-center gap-2">
              <label className="text-xs font-medium text-[#66736F]">
                Sector:
              </label>
              <select
                value={insightSector}
                onChange={(e) => setInsightSector(e.target.value)}
                className="px-3 py-1.5 text-xs font-medium rounded border border-[#E2E9E6] bg-white text-[#202C2A] focus:outline-none focus:border-[#167568]"
              >
                {VALID_SECTORS.map((sec) => (
                  <option key={sec} value={sec}>
                    {sec}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Error Banner */}
          {errorInsights && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-[#dc2626]">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorInsights}</span>
            </div>
          )}

          {/* Documents Table / List */}
          <div className="border border-[#E2E9E6] rounded-lg overflow-hidden">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[#F5F7F7] border-b border-[#E2E9E6] text-[#66736F] font-semibold">
                  <th className="py-2.5 px-4">Document Title</th>
                  <th className="py-2.5 px-4 w-28">Regulator</th>
                  <th className="py-2.5 px-4 w-36">Document Type</th>
                  <th className="py-2.5 px-4 w-32">Issue Date</th>
                  <th className="py-2.5 px-4 w-20 text-right">Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2E9E6]">
                {loadingInsights ? (
                  Array.from({ length: 4 }).map((_, idx) => (
                    <tr key={idx} className="animate-pulse">
                      <td className="py-3 px-4">
                        <div className="h-3.5 bg-slate-200 rounded w-3/4"></div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="h-4 bg-slate-200 rounded w-12"></div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="h-3.5 bg-slate-200 rounded w-20"></div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="h-3.5 bg-slate-200 rounded w-16"></div>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="h-4 bg-slate-200 rounded w-4 ml-auto"></div>
                      </td>
                    </tr>
                  ))
                ) : regulatoryDocs.length === 0 ? (
                  <tr>
                    <td
                      colSpan={5}
                      className="py-8 text-center text-sm text-[#66736F]"
                    >
                      No regulatory documents found for this sector.
                    </td>
                  </tr>
                ) : (
                  regulatoryDocs.map((doc, idx) => {
                    const isRBI = doc.regulator?.toUpperCase() === "RBI";
                    const isSEBI = doc.regulator?.toUpperCase() === "SEBI";
                    const hasLink = Boolean(doc.source_url);

                    return (
                      <tr
                        key={idx}
                        onClick={() => {
                          if (hasLink) {
                            window.open(doc.source_url, "_blank", "noopener,noreferrer");
                          }
                        }}
                        className={`transition-colors ${
                          hasLink
                            ? "hover:bg-slate-50 cursor-pointer"
                            : "hover:bg-slate-50/50"
                        }`}
                      >
                        <td className="py-3 px-4 font-medium text-[#202C2A]">
                          <div className="flex items-center gap-2">
                            <span>{doc.document_title}</span>
                          </div>
                          {doc.relevance_note && (
                            <p className="text-[11px] text-[#66736F] mt-0.5 font-normal">
                              {doc.relevance_note}
                            </p>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`inline-block px-2 py-0.5 rounded text-[11px] font-semibold ${
                              isRBI
                                ? "bg-[#167568]/10 text-[#167568] border border-[#167568]/20"
                                : isSEBI
                                ? "bg-amber-50 text-amber-800 border border-amber-300"
                                : "bg-slate-100 text-[#202C2A] border border-[#E2E9E6]"
                            }`}
                          >
                            {doc.regulator}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-[#66736F]">
                          {doc.document_type}
                        </td>
                        <td className="py-3 px-4 text-[#66736F] whitespace-nowrap">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-3 h-3 text-[#66736F]" />
                            <span>{doc.issue_date}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-right">
                          {hasLink ? (
                            <span
                              className="inline-flex text-[#167568] hover:text-[#125E55]"
                              title="Open source document"
                            >
                              <ExternalLink className="w-3.5 h-3.5" />
                            </span>
                          ) : (
                            <span className="text-slate-300">--</span>
                          )}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
