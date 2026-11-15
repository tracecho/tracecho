import axios from "axios";

// ─── Query / Assistant Types ──────────────────────────────────────────────────

export interface Citation {
  chunk_id: string;
  regulator: string;
  document_title: string;
  section: string;
  issue_date: string;
  source_url: string;
}

export interface QueryAnalysis {
  regulator: string;
  intent: string;
  temporal_context: string;
  optimized_search_query: string;
}

export interface RetrievedChunk {
  chunk_id: string;
  regulator: string;
  document_title: string;
  document_type: string;
  section: string;
  issue_date: string;
  validity_status: string;
  source_url: string;
  text: string;
  dense_score?: number | null;
  bm25_score?: number | null;
  hybrid_score?: number | null;
  raw_dense_score?: number | null;
  raw_bm25_score?: number | null;
  metadata_adj?: number | null;
  reranker_score?: number | null;
  norm_reranker_score?: number | null;
}

export interface SystemStatusType {
  status: string;
  reason: string;
}

export interface GuardrailsSummary {
  passed: boolean;
  blocked: boolean;
  modified: boolean;
  failures: string[];
  checks: Record<string, boolean>;
}

export interface QueryResponse {
  query_analysis?: QueryAnalysis | null;
  answer: string;
  regulatory_requirement: string;
  applicability: string;
  conditions: string[];
  exceptions: string[];
  evidence: string[];
  citations: Citation[];
  retrieved_chunks: RetrievedChunk[];
  evidence_insufficient: boolean;
  verification_status: string;
  guardrails?: GuardrailsSummary | null;
  regulator: string;
  system_status?: SystemStatusType | null;
  retrieval_status: string;
  evidence_status: string;
  error?: string | null;
}

// ─── Dashboard Types ─────────────────────────────────────────────────────────

export interface MarketIndex {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_pct: number;
  high?: number;
  low?: number;
  open?: number;
  prev_close?: number;
  timestamp?: string;
}

export interface MarketOverviewResponse {
  indices: MarketIndex[];
}

export interface SectorData {
  sector: string;
  symbol: string;
  return_pct: number;
  current_price?: number;
  start_price?: number;
}

export interface SectorPerformanceResponse {
  period_days: number;
  sectors: SectorData[];
}

export interface HistoricalCandle {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  ma20?: number | null;
  ma50?: number | null;
  volatility20?: number | null;
}

export interface HistoricalData {
  symbol: string;
  period: string;
  candles: HistoricalCandle[];
}

export interface RegulatoryInsightDoc {
  chunk_id: string;
  regulator: string;
  document_title: string;
  document_type: string;
  section: string;
  issue_date: string;
  source_url: string;
  summary?: string;
}

export interface RegulatoryInsightsResponse {
  sector: string;
  documents: RegulatoryInsightDoc[];
}

// ─── Explorer Types ───────────────────────────────────────────────────────────

export interface ExplorerChunk {
  chunk_id: string;
  section: string;
  text: string;
  chunk_index: number;
}

export interface ExplorerDocument {
  document_id: string;
  title: string;
  regulator: "RBI" | "SEBI";
  doc_type: string;
  issue_date: string;
  validity: string;
  source_url?: string;
  chunk_count?: number;
}

export interface ExplorerDocumentDetail extends ExplorerDocument {
  chunks: ExplorerChunk[];
}

export interface ExplorerFilters {
  regulators: string[];
  document_types: Record<string, string[]>;
  validity_statuses: Record<string, string[]>;
}

export interface ExplorerCatalogParams {
  regulator?: "RBI" | "SEBI" | "Both";
  doc_type?: string;
  validity?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface ExplorerCatalog {
  items: ExplorerDocument[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ─── Evaluation Types ─────────────────────────────────────────────────────────

export interface EvalMetric {
  k: number;
  method: string;
  recall: number;
  mrr: number;
  hit_rate: number;
}

export interface EvalQuestionResult {
  question_id: string;
  question: string;
  category: string;
  difficulty: string;
  ground_truth_chunks: string[];
  retrieved_chunks: string[];
  hit_at_k: Record<number, boolean>;
  reciprocal_rank: number;
}

export interface EvalResults {
  timestamp: string;
  ks: number[];
  overall_metrics: Record<string, Record<string, number>>;
  questions: EvalQuestionResult[];
}

export interface BenchmarkMeta {
  total_questions: number;
  answerable_count: number;
  out_of_domain_count: number;
  categories: Record<string, number>;
  difficulties: Record<string, number>;
}

export interface RunStatus {
  status: "idle" | "running" | "done" | "error";
  message: string;
}

// ─── Auth Types ───────────────────────────────────────────────────────────────

export interface AuthUser {
  id: string;
  email: string;
  name?: string | null;
  full_name?: string | null;
  role: string;
  is_active: boolean;
  created_at?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// ─── Axios Instance ───────────────────────────────────────────────────────────

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("regintel_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── Assistant API ────────────────────────────────────────────────────────────

export const postAsk = (query: string) =>
  api.post<QueryResponse>("/api/ask", { query }).then((r) => r.data);

// ─── Dashboard API ────────────────────────────────────────────────────────────

export const getMarketOverview = () =>
  api.get<MarketOverviewResponse>("/api/dashboard/market").then((r) => r.data);

export const getSectorPerformance = (period = 30) =>
  api
    .get<SectorPerformanceResponse>("/api/dashboard/sectors", {
      params: { period },
    })
    .then((r) => r.data);

export const getHistoricalData = (symbol: string, period = "6mo") =>
  api
    .get<HistoricalData>(`/api/dashboard/history/${encodeURIComponent(symbol)}`, {
      params: { period },
    })
    .then((r) => r.data);

export const getRegulatoryInsights = (sector: string, top_k = 5) =>
  api
    .get<RegulatoryInsightsResponse>("/api/dashboard/regulatory-insights", {
      params: { sector, top_k },
    })
    .then((r) => r.data);

// ─── Explorer API ─────────────────────────────────────────────────────────────

export const getExplorerFilters = () =>
  api.get<ExplorerFilters>("/api/explorer/filters").then((r) => r.data);

export const getExplorerCatalog = (params?: ExplorerCatalogParams) =>
  api
    .get<ExplorerCatalog>("/api/explorer/catalog", { params })
    .then((r) => r.data);

export const getExplorerDocument = (id: string) =>
  api
    .get<ExplorerDocumentDetail>(`/api/explorer/document/${encodeURIComponent(id)}`)
    .then((r) => r.data);

// ─── Evaluation API ───────────────────────────────────────────────────────────

export const getEvalResults = (k: number[] = [3, 5, 10]) => {
  const params = new URLSearchParams();
  k.forEach((val) => params.append("k", val.toString()));
  return api
    .get<EvalResults>("/api/eval/results", { params })
    .then((r) => r.data);
};

export const getEvalResultsByTimestamp = (
  timestamp: string,
  k: number[] = [3, 5, 10]
) => {
  const params = new URLSearchParams();
  k.forEach((val) => params.append("k", val.toString()));
  return api
    .get<EvalResults>(`/api/eval/results/${timestamp}`, { params })
    .then((r) => r.data);
};

export const getEvalBenchmark = () =>
  api.get<BenchmarkMeta>("/api/eval/benchmark").then((r) => r.data);

export const getEvalRunStatus = () =>
  api.get<RunStatus>("/api/eval/run/status").then((r) => r.data);

export const postEvalRun = () =>
  api.post<RunStatus>("/api/eval/run").then((r) => r.data);

// ─── Auth API ─────────────────────────────────────────────────────────────────

export const postSignup = (payload: {
  email: string;
  password: string;
  full_name?: string;
}) => api.post<TokenResponse>("/api/auth/signup", payload).then((r) => r.data);

export const postSignin = (payload: { email: string; password: string }) =>
  api.post<TokenResponse>("/api/auth/signin", payload).then((r) => r.data);

export const postSignout = () =>
  api.post<{ detail: string }>("/api/auth/signout").then((r) => r.data);

export const getMe = (token?: string) => {
  const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
  return api.get<AuthUser>("/api/auth/me", { headers }).then((r) => r.data);
};

// ─── Contact API ──────────────────────────────────────────────────────────────

export interface ContactSubmissionPayload {
  name: string;
  email: string;
  organization: string;
  enquiry_type: string;
  message: string;
  honeypot?: string;
}

export interface ContactSubmissionResponse {
  success: boolean;
  message: string;
  submission_id?: string;
  email_delivered: boolean;
}

export const postContactSubmission = (payload: ContactSubmissionPayload) =>
  api.post<ContactSubmissionResponse>("/api/contact", payload).then((r) => r.data);

export default api;
