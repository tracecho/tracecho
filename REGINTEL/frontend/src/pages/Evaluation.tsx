import React, { useState, useEffect, useMemo, useCallback } from "react";
import AppShell from "@/components/layout/AppShell";
import api from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import toast from "react-hot-toast";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import {
  BarChart3,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Layers,
  ChevronDown,
  ChevronUp,
  Play,
  Loader2,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Database,
  Calendar,
} from "lucide-react";

// Method configuration with designated colors
const METHOD_CONFIG: Record<
  string,
  { label: string; color: string; order: number }
> = {
  vector: { label: "Vector", color: "#60a5fa", order: 1 },
  bm25: { label: "BM25", color: "#a78bfa", order: 2 },
  hybrid: { label: "Hybrid", color: "#34d399", order: 3 },
  hybrid_reranking: { label: "Hybrid + Reranking", color: "#2563EB", order: 4 },
  agentic: { label: "Agentic RAG", color: "#f59e0b", order: 5 },
};

interface BenchmarkMeta {
  available?: boolean;
  total?: number;
  answerable?: number;
  out_of_domain?: number;
  categories?: Record<string, number>;
  difficulties?: Record<string, number>;
  regulators?: Record<string, number>;
}

interface MethodMetrics {
  label?: string;
  [key: string]: unknown;
}

interface PerQuestionItem {
  question_id: string;
  question: string;
  answerable?: boolean;
  hit_at_5?: boolean | null;
  first_rank?: number | null;
  reciprocal_rank?: number | null;
}

interface EvalResponse {
  available: boolean;
  timestamp?: string;
  display_ts?: string;
  timestamps?: string[];
  k_values?: number[];
  methods?: Record<string, MethodMetrics>;
  per_question?: PerQuestionItem[];
  message?: string;
}

interface RunStatusResponse {
  status: "idle" | "starting" | "running" | "done" | "error";
  message?: string;
}

export const Evaluation: React.FC = () => {
  // Benchmark Overview
  const [benchmark, setBenchmark] = useState<BenchmarkMeta | null>(null);
  const [benchLoading, setBenchLoading] = useState<boolean>(true);

  // K-value selector: checkboxes (1, 3, 5, 10, 15) - default [3, 5, 10]
  const availableK = [1, 3, 5, 10, 15];
  const [selectedK, setSelectedK] = useState<number[]>([3, 5, 10]);

  // Timestamps / Run Selector
  const [timestamps, setTimestamps] = useState<string[]>([]);
  const [selectedTimestamp, setSelectedTimestamp] = useState<string>("");

  // Results & Metrics
  const [results, setResults] = useState<EvalResponse | null>(null);
  const [resultsLoading, setResultsLoading] = useState<boolean>(true);

  // Per-Question Table
  const [showQuestions, setShowQuestions] = useState<boolean>(false);
  const [questionPage, setQuestionPage] = useState<number>(1);
  const questionsPerPage = 20;

  // Run Pipeline State
  const [runStatus, setRunStatus] = useState<RunStatusResponse>({
    status: "idle",
  });
  const [confirmModalOpen, setConfirmModalOpen] = useState<boolean>(false);
  const [triggeringRun, setTriggeringRun] = useState<boolean>(false);

  // 1. Fetch Benchmark Metadata
  useEffect(() => {
    let mounted = true;
    const fetchBenchmark = async () => {
      setBenchLoading(true);
      try {
        const res = await api.get<BenchmarkMeta>("/api/eval/benchmark");
        if (mounted) setBenchmark(res.data);
      } catch (err) {
        console.error("Failed to fetch benchmark metadata:", err);
      } finally {
        if (mounted) setBenchLoading(false);
      }
    };
    fetchBenchmark();
    return () => {
      mounted = false;
    };
  }, []);

  // 2. Fetch Run Status (Poll every 5s if starting/running)
  const fetchStatus = useCallback(async () => {
    try {
      const res = await api.get<RunStatusResponse>("/api/eval/run/status");
      setRunStatus(res.data);
      return res.data;
    } catch (err) {
      console.error("Failed to fetch eval run status:", err);
      return null;
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  useEffect(() => {
    if (runStatus.status === "running" || runStatus.status === "starting") {
      const timer = setInterval(async () => {
        const current = await fetchStatus();
        if (current && current.status === "done") {
          toast.success("Evaluation pipeline run completed!");
          // Refetch results
          fetchResults();
        } else if (current && current.status === "error") {
          toast.error(`Evaluation failed: ${current.message || "Unknown error"}`);
        }
      }, 5000);
      return () => clearInterval(timer);
    }
  }, [runStatus.status, fetchStatus]);

  // 3. Fetch Evaluation Results
  const fetchResults = useCallback(async () => {
    if (selectedK.length === 0) return;
    setResultsLoading(true);
    try {
      const qs = selectedK.map((k) => `k=${k}`).join("&");
      const url = selectedTimestamp
        ? `/api/eval/results/${encodeURIComponent(selectedTimestamp)}?${qs}`
        : `/api/eval/results?${qs}`;

      const res = await api.get<EvalResponse>(url);
      setResults(res.data);
      if (res.data.timestamps && res.data.timestamps.length > 0) {
        setTimestamps(res.data.timestamps);
        if (!selectedTimestamp && res.data.timestamp) {
          setSelectedTimestamp(res.data.timestamp);
        }
      }
    } catch (err) {
      console.error("Failed to fetch evaluation results:", err);
    } finally {
      setResultsLoading(false);
    }
  }, [selectedK, selectedTimestamp]);

  useEffect(() => {
    fetchResults();
  }, [fetchResults]);

  // Handle K toggle
  const toggleK = (val: number) => {
    setSelectedK((prev) => {
      if (prev.includes(val)) {
        if (prev.length === 1) return prev; // Keep at least one
        return prev.filter((k) => k !== val).sort((a, b) => a - b);
      } else {
        return [...prev, val].sort((a, b) => a - b);
      }
    });
  };

  // Trigger Evaluation Run
  const handleConfirmRun = async () => {
    setTriggeringRun(true);
    try {
      await api.post("/api/eval/run");
      toast.success("Evaluation pipeline triggered successfully.");
      setConfirmModalOpen(false);
      setRunStatus({
        status: "running",
        message: "Evaluation pipeline started…",
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to trigger run";
      toast.error(msg);
    } finally {
      setTriggeringRun(false);
    }
  };

  // Chart 1 & 2 Data Preparation: Grouped by K value
  const recallGroupedData = useMemo(() => {
    if (!results?.methods) return [];
    return selectedK.map((k) => {
      const entry: Record<string, unknown> = { kLabel: `K = ${k}` };
      Object.entries(results.methods || {}).forEach(([methodKey, metrics]) => {
        const val = metrics[`Recall@${k}`];
        if (typeof val === "number") {
          entry[methodKey] = Number((val * 100).toFixed(1));
        } else {
          entry[methodKey] = 0;
        }
      });
      return entry;
    });
  }, [results, selectedK]);

  const mrrGroupedData = useMemo(() => {
    if (!results?.methods) return [];
    return selectedK.map((k) => {
      const entry: Record<string, unknown> = { kLabel: `K = ${k}` };
      Object.entries(results.methods || {}).forEach(([methodKey, metrics]) => {
        const val = metrics[`MRR@${k}`];
        if (typeof val === "number") {
          entry[methodKey] = Number(val.toFixed(3));
        } else {
          entry[methodKey] = 0;
        }
      });
      return entry;
    });
  }, [results, selectedK]);

  // Chart 3: Horizontal BarChart for HitRate@5
  const hitRateData = useMemo(() => {
    if (!results?.methods) return [];
    return Object.entries(results.methods).map(([methodKey, metrics]) => {
      const cfg = METHOD_CONFIG[methodKey] || {
        label: methodKey,
        color: "#167568",
        order: 99,
      };
      const rawHit = metrics["HitRate@5"];
      const hitVal =
        typeof rawHit === "number" ? Number((rawHit * 100).toFixed(1)) : 0;
      return {
        key: methodKey,
        method: cfg.label,
        hitRate: hitVal,
        color: cfg.color,
        order: cfg.order,
      };
    }).sort((a, b) => a.order - b.order);
  }, [results]);

  // Questions Pagination
  const totalQuestions = results?.per_question?.length || 0;
  const paginatedQuestions = useMemo(() => {
    if (!results?.per_question) return [];
    const start = (questionPage - 1) * questionsPerPage;
    return results.per_question.slice(start, start + questionsPerPage);
  }, [results?.per_question, questionPage]);
  const totalQuestionPages = Math.max(1, Math.ceil(totalQuestions / questionsPerPage));

  return (
    <AppShell>
      <div className="space-y-6 max-w-7xl mx-auto pb-12">
        {/* Page Header + Run Pipeline Action */}
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-[#E2E9E6] gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[#202C2A] tracking-tight">
              Evaluation Centre
            </h1>
            <p className="text-sm text-[#66736F]">
              Comprehensive retrieval and generation benchmarks across Vector, BM25, Hybrid, Reranking, and Agentic RAG.
            </p>
          </div>

          {/* Run evaluation section */}
          <div className="flex items-center space-x-3">
            {runStatus.status === "running" || runStatus.status === "starting" ? (
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-amber-50 border border-amber-200 text-amber-800 text-xs font-medium">
                <Loader2 className="w-4 h-4 animate-spin text-amber-600" />
                <span>Running Pipeline…</span>
              </div>
            ) : (
              <Button
                variant="default"
                size="md"
                onClick={() => setConfirmModalOpen(true)}
                className="flex items-center space-x-1.5 text-xs font-semibold shadow-xs"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Run Evaluation</span>
              </Button>
            )}
          </div>
        </div>

        {/* Error Banner if Run Pipeline Failed */}
        {runStatus.status === "error" && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md flex items-center space-x-2 text-xs text-red-800">
            <AlertTriangle className="w-4 h-4 text-red-600 flex-shrink-0" />
            <span>
              Evaluation pipeline encountered an error: {runStatus.message || "Unknown error occurred"}
            </span>
          </div>
        )}

        {/* TOP SECTION — BENCHMARK OVERVIEW */}
        <section className="space-y-4">
          <div className="flex items-center space-x-2 text-sm font-bold text-[#202C2A]">
            <Database className="w-4 h-4 text-[#167568]" />
            <h2>Benchmark Dataset Overview</h2>
          </div>

          {benchLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Skeleton className="h-24 w-full rounded-lg" />
              <Skeleton className="h-24 w-full rounded-lg" />
              <Skeleton className="h-24 w-full rounded-lg" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* KPI 1: Total Questions */}
              <div className="bg-white border border-[#E2E9E6] rounded-lg p-4 shadow-xs">
                <div className="text-xs text-[#66736F] font-medium uppercase tracking-wider">
                  Total Questions
                </div>
                <div className="text-3xl font-extrabold text-[#202C2A] mt-1">
                  {benchmark?.total ?? 0}
                </div>
                <div className="text-xs text-[#66736F] mt-1">
                  Gold-standard regulatory questions
                </div>
              </div>

              {/* KPI 2: Answerable */}
              <div className="bg-white border border-[#E2E9E6] rounded-lg p-4 shadow-xs">
                <div className="text-xs text-[#66736F] font-medium uppercase tracking-wider flex items-center justify-between">
                  <span>Answerable in Corpus</span>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                </div>
                <div className="text-3xl font-extrabold text-emerald-700 mt-1">
                  {benchmark?.answerable ?? 0}
                </div>
                <div className="text-xs text-[#66736F] mt-1">
                  {benchmark?.total
                    ? `${Math.round(((benchmark.answerable || 0) / benchmark.total) * 100)}% coverage`
                    : "0%"}
                </div>
              </div>

              {/* KPI 3: Out of Domain */}
              <div className="bg-white border border-[#E2E9E6] rounded-lg p-4 shadow-xs">
                <div className="text-xs text-[#66736F] font-medium uppercase tracking-wider flex items-center justify-between">
                  <span>Out-of-Domain / Negative</span>
                  <HelpCircle className="w-3.5 h-3.5 text-amber-600" />
                </div>
                <div className="text-3xl font-extrabold text-amber-700 mt-1">
                  {benchmark?.out_of_domain ?? 0}
                </div>
                <div className="text-xs text-[#66736F] mt-1">
                  Evaluates guardrail / refusal precision
                </div>
              </div>
            </div>
          )}

          {/* Two small tables: Category breakdown & Difficulty breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Category breakdown table */}
            <div className="bg-white border border-[#E2E9E6] rounded-lg p-4 shadow-xs space-y-2">
              <h3 className="text-xs font-bold text-[#202C2A] uppercase tracking-wider">
                Category Breakdown
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left border-collapse">
                  <thead>
                    <tr className="border-b border-[#E2E9E6] text-[#66736F] font-semibold">
                      <th className="py-2 px-2">Category</th>
                      <th className="py-2 px-2 text-right">Count</th>
                      <th className="py-2 px-2 text-right">Share</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E2E9E6]/60">
                    {benchmark?.categories && Object.keys(benchmark.categories).length > 0 ? (
                      Object.entries(benchmark.categories).map(([cat, count]) => {
                        const pct = benchmark.total ? Math.round((count / benchmark.total) * 100) : 0;
                        return (
                          <tr key={cat} className="hover:bg-[#F5F7F7]">
                            <td className="py-1.5 px-2 font-medium text-[#202C2A] truncate max-w-[200px]" title={cat}>
                              {cat}
                            </td>
                            <td className="py-1.5 px-2 text-right text-[#66736F] font-mono">{count}</td>
                            <td className="py-1.5 px-2 text-right text-[#167568] font-semibold">{pct}%</td>
                          </tr>
                        );
                      })
                    ) : (
                      <tr>
                        <td colSpan={3} className="py-2 text-center text-[#66736F]">
                          No category data
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Difficulty breakdown table */}
            <div className="bg-white border border-[#E2E9E6] rounded-lg p-4 shadow-xs space-y-2">
              <h3 className="text-xs font-bold text-[#202C2A] uppercase tracking-wider">
                Difficulty Breakdown
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left border-collapse">
                  <thead>
                    <tr className="border-b border-[#E2E9E6] text-[#66736F] font-semibold">
                      <th className="py-2 px-2">Difficulty Level</th>
                      <th className="py-2 px-2 text-right">Count</th>
                      <th className="py-2 px-2 text-right">Share</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E2E9E6]/60">
                    {benchmark?.difficulties && Object.keys(benchmark.difficulties).length > 0 ? (
                      Object.entries(benchmark.difficulties).map(([diff, count]) => {
                        const pct = benchmark.total ? Math.round((count / benchmark.total) * 100) : 0;
                        return (
                          <tr key={diff} className="hover:bg-[#F5F7F7]">
                            <td className="py-1.5 px-2 font-medium text-[#202C2A]">{diff}</td>
                            <td className="py-1.5 px-2 text-right text-[#66736F] font-mono">{count}</td>
                            <td className="py-1.5 px-2 text-right text-[#167568] font-semibold">{pct}%</td>
                          </tr>
                        );
                      })
                    ) : (
                      <tr>
                        <td colSpan={3} className="py-2 text-center text-[#66736F]">
                          No difficulty data
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </section>

        {/* MIDDLE SECTION — CONTROLS & METHOD COMPARISON CARDS */}
        <section className="space-y-4">
          <div className="bg-white border border-[#E2E9E6] rounded-lg p-4 shadow-xs flex flex-wrap items-center justify-between gap-4">
            {/* K-Value Selector: Checkboxes (1, 3, 5, 10, 15) */}
            <div className="flex items-center space-x-3">
              <span className="text-xs font-bold text-[#202C2A] uppercase tracking-wider">
                K Values:
              </span>
              <div className="flex items-center space-x-3">
                {availableK.map((k) => (
                  <label
                    key={k}
                    className="flex items-center space-x-1.5 text-xs text-[#202C2A] cursor-pointer hover:text-[#167568] select-none"
                  >
                    <input
                      type="checkbox"
                      checked={selectedK.includes(k)}
                      onChange={() => toggleK(k)}
                      className="rounded border-[#E2E9E6] text-[#167568] focus:ring-[#167568] w-3.5 h-3.5"
                    />
                    <span className="font-semibold">{k}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Run Selector Dropdown */}
            {timestamps.length > 0 && (
              <div className="flex items-center space-x-2">
                <Calendar className="w-3.5 h-3.5 text-[#66736F]" />
                <span className="text-xs text-[#66736F] font-medium">Run:</span>
                <select
                  value={selectedTimestamp}
                  onChange={(e) => setSelectedTimestamp(e.target.value)}
                  className="text-xs px-2.5 py-1.5 border border-[#E2E9E6] rounded-md focus:outline-none focus:ring-1 focus:ring-[#167568] text-[#202C2A] bg-white font-mono"
                >
                  {timestamps.map((ts) => (
                    <option key={ts} value={ts}>
                      {ts}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Method Comparison Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
            {Object.keys(METHOD_CONFIG).map((methodKey) => {
              const cfg = METHOD_CONFIG[methodKey];
              const metrics = results?.methods?.[methodKey];
              const recall5 = metrics?.["Recall@5"];
              const mrr5 = metrics?.["MRR@5"];

              return (
                <div
                  key={methodKey}
                  className="bg-white border rounded-lg p-3.5 shadow-xs flex flex-col justify-between"
                  style={{ borderLeftColor: cfg.color, borderLeftWidth: "4px" }}
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#202C2A]">{cfg.label}</span>
                      <span
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ backgroundColor: cfg.color }}
                      />
                    </div>

                    {/* Recall@5 prominently */}
                    <div className="mt-2.5">
                      <div className="text-[10px] text-[#66736F] font-medium uppercase tracking-wider">
                        Recall@5
                      </div>
                      <div className="text-2xl font-extrabold text-[#202C2A] mt-0.5">
                        {typeof recall5 === "number"
                          ? `${(recall5 * 100).toFixed(1)}%`
                          : "—"}
                      </div>
                    </div>

                    {/* MRR@5 secondary */}
                    <div className="mt-2">
                      <div className="text-[10px] text-[#66736F] font-medium uppercase tracking-wider">
                        MRR@5
                      </div>
                      <div className="text-sm font-semibold text-[#66736F] mt-0.5 font-mono">
                        {typeof mrr5 === "number" ? mrr5.toFixed(3) : "—"}
                      </div>
                    </div>
                  </div>

                  <div className="mt-3 pt-2 border-t border-[#E2E9E6]/60 flex items-center justify-between text-[11px] text-[#66736F]">
                    <span>HitRate@5:</span>
                    <span className="font-semibold text-[#202C2A]">
                      {typeof metrics?.["HitRate@5"] === "number"
                        ? `${(Number(metrics["HitRate@5"]) * 100).toFixed(0)}%`
                        : "—"}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* CHARTS SECTION (RECHARTS) */}
        <section className="space-y-4">
          <div className="flex items-center space-x-2 text-sm font-bold text-[#202C2A]">
            <BarChart3 className="w-4 h-4 text-[#167568]" />
            <h2>Retrieval Performance Visualizations</h2>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Chart 1: Grouped BarChart: Recall@K per method */}
            <div className="bg-white border border-[#E2E9E6] rounded-lg p-4 shadow-xs">
              <h3 className="text-xs font-bold text-[#202C2A] uppercase tracking-wider mb-1">
                Recall@K by Method (%)
              </h3>
              <p className="text-[11px] text-[#66736F] mb-4">
                Comparison of recall across chosen K thresholds
              </p>
              <div className="h-64 w-full">
                {resultsLoading ? (
                  <Skeleton className="h-full w-full rounded" />
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={recallGroupedData}
                      margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E9E6" />
                      <XAxis dataKey="kLabel" tick={{ fontSize: 11, fill: "#202C2A" }} />
                      <YAxis
                        domain={[0, 100]}
                        tick={{ fontSize: 11, fill: "#66736F" }}
                        tickFormatter={(v) => `${v}%`}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#FFFFFF",
                          border: "1px solid #E2E9E6",
                          borderRadius: "6px",
                          fontSize: "12px",
                        }}
                        formatter={(val: number) => [`${val}%`, "Recall"]}
                      />
                      <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                      {Object.keys(METHOD_CONFIG).map((mKey) => (
                        <Bar
                          key={mKey}
                          dataKey={mKey}
                          name={METHOD_CONFIG[mKey].label}
                          fill={METHOD_CONFIG[mKey].color}
                          radius={[3, 3, 0, 0]}
                        />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* Chart 2: Grouped BarChart: MRR@K per method */}
            <div className="bg-white border border-[#E2E9E6] rounded-lg p-4 shadow-xs">
              <h3 className="text-xs font-bold text-[#202C2A] uppercase tracking-wider mb-1">
                Mean Reciprocal Rank (MRR@K)
              </h3>
              <p className="text-[11px] text-[#66736F] mb-4">
                Position of first relevant document across thresholds
              </p>
              <div className="h-64 w-full">
                {resultsLoading ? (
                  <Skeleton className="h-full w-full rounded" />
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={mrrGroupedData}
                      margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E9E6" />
                      <XAxis dataKey="kLabel" tick={{ fontSize: 11, fill: "#202C2A" }} />
                      <YAxis
                        domain={[0, 1]}
                        tick={{ fontSize: 11, fill: "#66736F" }}
                        tickFormatter={(v) => v.toFixed(2)}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#FFFFFF",
                          border: "1px solid #E2E9E6",
                          borderRadius: "6px",
                          fontSize: "12px",
                        }}
                        formatter={(val: number) => [val.toFixed(3), "MRR"]}
                      />
                      <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                      {Object.keys(METHOD_CONFIG).map((mKey) => (
                        <Bar
                          key={mKey}
                          dataKey={mKey}
                          name={METHOD_CONFIG[mKey].label}
                          fill={METHOD_CONFIG[mKey].color}
                          radius={[3, 3, 0, 0]}
                        />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </div>

          {/* Chart 3: Horizontal BarChart: HitRate@5 per method */}
          <div className="bg-white border border-[#E2E9E6] rounded-lg p-4 shadow-xs">
            <h3 className="text-xs font-bold text-[#202C2A] uppercase tracking-wider mb-1">
              Hit Rate @ 5 per Method (%)
            </h3>
            <p className="text-[11px] text-[#66736F] mb-4">
              Percentage of questions with at least one relevant document retrieved in top 5
            </p>
            <div className="h-56 w-full">
              {resultsLoading ? (
                <Skeleton className="h-full w-full rounded" />
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    layout="vertical"
                    data={hitRateData}
                    margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E9E6" />
                    <XAxis
                      type="number"
                      domain={[0, 100]}
                      tick={{ fontSize: 11, fill: "#66736F" }}
                      tickFormatter={(v) => `${v}%`}
                    />
                    <YAxis
                      type="category"
                      dataKey="method"
                      tick={{ fontSize: 11, fill: "#202C2A" }}
                      width={120}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#FFFFFF",
                        border: "1px solid #E2E9E6",
                        borderRadius: "6px",
                        fontSize: "12px",
                      }}
                      formatter={(val: number) => [`${val}%`, "HitRate@5"]}
                    />
                    <Bar dataKey="hitRate" radius={[0, 4, 4, 0]}>
                      {hitRateData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </section>

        {/* PER-QUESTION DETAIL TABLE (COLLAPSIBLE) */}
        <section className="bg-white border border-[#E2E9E6] rounded-lg shadow-xs overflow-hidden">
          {/* Header toggle */}
          <button
            type="button"
            onClick={() => setShowQuestions((prev) => !prev)}
            className="w-full p-4 flex items-center justify-between bg-[#F5F7F7]/60 hover:bg-[#F5F7F7] text-left transition-colors"
          >
            <div className="flex items-center space-x-2">
              <Layers className="w-4 h-4 text-[#167568]" />
              <span className="text-sm font-bold text-[#202C2A]">
                Per-Question Diagnostic Detail ({totalQuestions} queries)
              </span>
            </div>
            <div className="flex items-center space-x-2 text-xs text-[#167568] font-semibold">
              <span>{showQuestions ? "Hide questions" : `Show ${totalQuestions} questions`}</span>
              {showQuestions ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </div>
          </button>

          {/* Collapsible Content */}
          {showQuestions && (
            <div className="p-4 border-t border-[#E2E9E6] space-y-3">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-[#E2E9E6] bg-[#F5F7F7] text-[#202C2A] font-semibold">
                      <th className="py-2.5 px-3 w-20">ID</th>
                      <th className="py-2.5 px-4">Question</th>
                      <th className="py-2.5 px-3 w-28 text-center">Hit@5</th>
                      <th className="py-2.5 px-3 w-24 text-center">First Rank</th>
                      <th className="py-2.5 px-3 w-32 text-right">Reciprocal Rank</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E2E9E6]">
                    {paginatedQuestions.map((q) => {
                      const hit = q.hit_at_5;
                      return (
                        <tr
                          key={q.question_id}
                          className="hover:bg-[#F5F7F7] odd:bg-white even:bg-[#FAFCFB] transition-colors"
                        >
                          <td className="py-2.5 px-3 font-mono font-medium text-[#66736F]">
                            {q.question_id}
                          </td>
                          <td className="py-2.5 px-4 font-medium text-[#202C2A] max-w-md truncate" title={q.question}>
                            {q.question}
                          </td>
                          <td className="py-2.5 px-3 text-center">
                            {hit === true ? (
                              <span className="inline-flex items-center space-x-1 text-emerald-700 font-semibold">
                                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                                <span>Hit</span>
                              </span>
                            ) : hit === false ? (
                              <span className="inline-flex items-center space-x-1 text-rose-700 font-semibold">
                                <XCircle className="w-4 h-4 text-rose-600" />
                                <span>Miss</span>
                              </span>
                            ) : (
                              <span className="text-[#66736F]">—</span>
                            )}
                          </td>
                          <td className="py-2.5 px-3 text-center font-mono text-[#202C2A]">
                            {q.first_rank !== undefined && q.first_rank !== null ? `#${q.first_rank}` : "—"}
                          </td>
                          <td className="py-2.5 px-3 text-right font-mono font-semibold text-[#167568]">
                            {typeof q.reciprocal_rank === "number" ? q.reciprocal_rank.toFixed(3) : "—"}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Question Table Pagination */}
              {totalQuestions > questionsPerPage && (
                <div className="pt-2 flex items-center justify-between text-xs text-[#66736F]">
                  <div>
                    Page <strong className="text-[#202C2A]">{questionPage}</strong> of{" "}
                    <strong className="text-[#202C2A]">{totalQuestionPages}</strong>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setQuestionPage((p) => Math.max(1, p - 1))}
                      disabled={questionPage <= 1}
                      className="h-7 px-2 text-xs"
                    >
                      <ChevronLeft className="w-3.5 h-3.5 mr-1" />
                      Prev
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setQuestionPage((p) => Math.min(totalQuestionPages, p + 1))}
                      disabled={questionPage >= totalQuestionPages}
                      className="h-7 px-2 text-xs"
                    >
                      Next
                      <ChevronRight className="w-3.5 h-3.5 ml-1" />
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        {/* CONFIRMATION DIALOG FOR RUNNING EVALUATION */}
        {confirmModalOpen && (
          <div className="fixed inset-0 z-50 overflow-hidden bg-black/40 flex items-center justify-center p-4">
            <div
              className="bg-white rounded-lg border border-[#E2E9E6] shadow-xl max-w-md w-full p-5 space-y-4 animate-in fade-in zoom-in-95 duration-150"
              role="dialog"
              aria-modal="true"
            >
              <div className="flex items-center space-x-2 text-[#202C2A]">
                <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
                <h3 className="font-bold text-sm">Run Full Evaluation Pipeline?</h3>
              </div>

              <p className="text-xs text-[#66736F] leading-relaxed">
                This will run the full evaluation pipeline across all benchmark questions and methods, which may take several minutes to execute. Continue?
              </p>

              <div className="flex items-center justify-end space-x-2 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setConfirmModalOpen(false)}
                  disabled={triggeringRun}
                  className="text-xs"
                >
                  Cancel
                </Button>
                <Button
                  variant="default"
                  size="sm"
                  onClick={handleConfirmRun}
                  disabled={triggeringRun}
                  className="text-xs font-semibold"
                >
                  {triggeringRun ? (
                    <span className="flex items-center space-x-1">
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Starting…</span>
                    </span>
                  ) : (
                    "Confirm Run"
                  )}
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
};

export default Evaluation;
