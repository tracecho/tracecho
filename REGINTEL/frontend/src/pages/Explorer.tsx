import React, { useState, useEffect, useMemo, useRef, useCallback } from "react";
import AppShell from "@/components/layout/AppShell";
import api from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  Search,
  Filter,
  X,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  FileText,
  RotateCcw,
  Loader2,
  SlidersHorizontal,
  ArrowUpDown,
  BookOpen,
} from "lucide-react";

// Types
interface DocumentItem {
  document_id: string;
  document_title?: string;
  display_title?: string;
  subject?: string;
  regulator: string;
  document_type: string;
  issue_date?: string;
  validity_status?: string;
  source_url?: string;
  chunk_count?: number;
  circular_number?: string;
}

interface ChunkItem {
  chunk_id: string;
  section?: string;
  text: string;
}

interface DocumentDetail {
  document_id: string;
  document_title?: string;
  display_title?: string;
  subject?: string;
  regulator: string;
  document_type: string;
  issue_date?: string;
  validity_status?: string;
  source_url?: string;
  chunk_count?: number;
  chunks?: ChunkItem[];
  circular_number?: string;
  metadata?: Record<string, unknown>;
}

export const Explorer: React.FC = () => {
  // Filter States
  const [searchInput, setSearchInput] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [selectedRegulators, setSelectedRegulators] = useState<string[]>([]);
  const [selectedDocTypes, setSelectedDocTypes] = useState<string[]>([]);
  const [minYear, setMinYear] = useState<string>("");
  const [maxYear, setMaxYear] = useState<string>("");
  const [sortBy, setSortBy] = useState<"issue_date" | "document_title">("issue_date");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  // Pagination & Loading States
  const [page, setPage] = useState<number>(1);
  const pageSize = 20;
  const [loading, setLoading] = useState<boolean>(true);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(1);

  // Filter options from API
  const [availableRegulators, setAvailableRegulators] = useState<string[]>(["RBI", "SEBI"]);
  const [availableDocTypes, setAvailableDocTypes] = useState<string[]>([]);

  // Document Detail Slide-in Panel
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);
  const [detailDoc, setDetailDoc] = useState<DocumentDetail | null>(null);
  const [expandedChunks, setExpandedChunks] = useState<Record<string, boolean>>({});

  // Debounce search input by 300ms
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  useEffect(() => {
    setIsSearching(true);
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    searchTimeoutRef.current = setTimeout(() => {
      setDebouncedSearch(searchInput);
      setIsSearching(false);
      setPage(1);
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchInput]);

  // Fetch Filters on mount
  useEffect(() => {
    let mounted = true;
    const fetchFilters = async () => {
      try {
        const res = await api.get("/api/explorer/filters");
        if (!mounted) return;
        const data = res.data;

        const regs = new Set<string>();
        const types = new Set<string>();

        if (Array.isArray(data.regulators)) {
          data.regulators.forEach((r: string) => regs.add(r));
        }
        if (Array.isArray(data.document_types)) {
          data.document_types.forEach((t: string) => types.add(t));
        }

        // Handle { rbi: { document_types: [] }, sebi: { document_types: [] } } format
        if (data.rbi) {
          regs.add("RBI");
          if (Array.isArray(data.rbi.document_types)) {
            data.rbi.document_types.forEach((t: string) => types.add(t));
          }
        }
        if (data.sebi) {
          regs.add("SEBI");
          if (Array.isArray(data.sebi.document_types)) {
            data.sebi.document_types.forEach((t: string) => types.add(t));
          }
        }

        if (regs.size > 0) {
          setAvailableRegulators(Array.from(regs));
        }
        if (types.size > 0) {
          setAvailableDocTypes(Array.from(types).filter(Boolean));
        }
      } catch (err) {
        console.error("Failed to fetch explorer filters:", err);
      }
    };

    fetchFilters();
    return () => {
      mounted = false;
    };
  }, []);

  // Fetch Catalog Documents
  const fetchCatalog = useCallback(async () => {
    setLoading(true);
    try {
      let regParam = "Both";
      if (selectedRegulators.length === 1) {
        regParam = selectedRegulators[0];
      }

      const params: Record<string, unknown> = {
        page,
        page_size: pageSize,
        regulator: regParam,
        search: debouncedSearch,
        q: debouncedSearch,
        sort_by: sortBy,
        sort_order: sortOrder,
      };

      if (selectedDocTypes.length > 0) {
        params.doc_type = selectedDocTypes.join(",");
      }

      const res = await api.get("/api/explorer/catalog", { params });
      const data = res.data;

      let docs: DocumentItem[] = [];
      if (Array.isArray(data.documents)) {
        docs = data.documents;
      } else if (Array.isArray(data.items)) {
        docs = data.items;
      }

      // Filter by min/max year on client if specified
      if (minYear || maxYear) {
        docs = docs.filter((doc) => {
          if (!doc.issue_date) return true;
          const year = parseInt(doc.issue_date.substring(0, 4), 10);
          if (isNaN(year)) return true;
          if (minYear && year < parseInt(minYear, 10)) return false;
          if (maxYear && year > parseInt(maxYear, 10)) return false;
          return true;
        });
      }

      // Client-side sort fallback
      docs.sort((a, b) => {
        let valA = "";
        let valB = "";
        if (sortBy === "issue_date") {
          valA = a.issue_date || "";
          valB = b.issue_date || "";
        } else {
          valA = a.display_title || a.document_title || a.subject || "";
          valB = b.display_title || b.document_title || b.subject || "";
        }
        if (sortOrder === "asc") {
          return valA.localeCompare(valB);
        }
        return valB.localeCompare(valA);
      });

      setDocuments(docs);
      setTotal(data.total || docs.length);
      setTotalPages(data.total_pages || Math.max(1, Math.ceil((data.total || docs.length) / pageSize)));
    } catch (err) {
      console.error("Failed to fetch catalog:", err);
      setDocuments([]);
      setTotal(0);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, selectedRegulators, selectedDocTypes, debouncedSearch, sortBy, sortOrder, minYear, maxYear]);

  useEffect(() => {
    fetchCatalog();
  }, [fetchCatalog]);

  // Fetch document detail
  const handleSelectDoc = async (docId: string) => {
    setSelectedDocId(docId);
    setDetailLoading(true);
    setExpandedChunks({});
    try {
      const res = await api.get(`/api/explorer/document/${encodeURIComponent(docId)}`);
      setDetailDoc(res.data);
    } catch (err) {
      console.error("Failed to fetch document detail:", err);
      // Fallback: use catalog info
      const fallback = documents.find((d) => d.document_id === docId);
      if (fallback) {
        setDetailDoc({
          ...fallback,
          chunks: [],
        });
      }
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetail = () => {
    setSelectedDocId(null);
    setDetailDoc(null);
    setExpandedChunks({});
  };

  const toggleChunkExpand = (chunkId: string) => {
    setExpandedChunks((prev) => ({
      ...prev,
      [chunkId]: !prev[chunkId],
    }));
  };

  // Filter calculations
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (selectedRegulators.length > 0) count += selectedRegulators.length;
    if (selectedDocTypes.length > 0) count += selectedDocTypes.length;
    if (minYear) count += 1;
    if (maxYear) count += 1;
    if (searchInput.trim()) count += 1;
    return count;
  }, [selectedRegulators, selectedDocTypes, minYear, maxYear, searchInput]);

  const handleClearFilters = () => {
    setSearchInput("");
    setDebouncedSearch("");
    setSelectedRegulators([]);
    setSelectedDocTypes([]);
    setMinYear("");
    setMaxYear("");
    setPage(1);
  };

  const toggleRegulator = (reg: string) => {
    setPage(1);
    setSelectedRegulators((prev) =>
      prev.includes(reg) ? prev.filter((r) => r !== reg) : [...prev, reg]
    );
  };

  const toggleDocType = (type: string) => {
    setPage(1);
    setSelectedDocTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  // Helper for regulator badge styling
  const renderRegulatorBadge = (regulator?: string) => {
    const reg = (regulator || "").toUpperCase();
    if (reg === "RBI") {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-[#167568]/10 text-[#167568] border border-[#167568]/20">
          RBI
        </span>
      );
    }
    if (reg === "SEBI") {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
          SEBI
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
        {reg || "Unknown"}
      </span>
    );
  };

  // Helper for status badge styling
  const renderStatusBadge = (status?: string) => {
    const s = (status || "").toLowerCase();
    if (s.includes("valid") || s.includes("active")) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
          Valid
        </span>
      );
    }
    if (s.includes("superseded") || s.includes("inactive") || s.includes("repealed")) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200">
          Superseded
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
        {status || "Unknown"}
      </span>
    );
  };

  return (
    <AppShell>
      <div className="flex flex-col h-full space-y-4">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 border-b border-[#E2E9E6] gap-2">
          <div>
            <h1 className="text-2xl font-bold text-[#202C2A] tracking-tight">
              Regulatory Explorer
            </h1>
            <p className="text-sm text-[#66736F]">
              Browse, filter, and inspect RBI and SEBI circulars, master directions, and regulatory documents.
            </p>
          </div>
          <div className="flex items-center space-x-2 text-xs text-[#66736F]">
            <BookOpen className="w-4 h-4 text-[#167568]" />
            <span>Total Catalog: <strong className="text-[#202C2A]">{total}</strong> docs</span>
          </div>
        </div>

        {/* Content Layout: Left Filter Panel + Main Catalog Table */}
        <div className="flex flex-col md:flex-row gap-6 items-start flex-1 min-h-0">
          {/* Left Panel: Filter Sidebar (240px width) */}
          <aside
            className="w-full md:w-[240px] flex-shrink-0 bg-white border border-[#E2E9E6] rounded-lg p-4 space-y-5 shadow-xs"
            aria-label="Explorer Filters"
          >
            {/* Sidebar Title & Filter Count Badge */}
            <div className="flex items-center justify-between border-b border-[#E2E9E6] pb-3">
              <div className="flex items-center space-x-2 text-sm font-semibold text-[#202C2A]">
                <Filter className="w-4 h-4 text-[#167568]" />
                <span>Filters</span>
                {activeFilterCount > 0 && (
                  <Badge variant="default" className="text-xs px-2 py-0.5">
                    {activeFilterCount}
                  </Badge>
                )}
              </div>
              {activeFilterCount > 0 && (
                <button
                  onClick={handleClearFilters}
                  className="text-xs text-[#167568] hover:text-[#125E55] font-medium flex items-center space-x-1 cursor-pointer"
                  title="Clear all active filters"
                >
                  <RotateCcw className="w-3 h-3" />
                  <span>Reset</span>
                </button>
              )}
            </div>

            {/* Search Input with Spinner */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#202C2A] uppercase tracking-wider block">
                Search
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Subject, circular #..."
                  className="w-full text-xs py-2 pl-8 pr-7 border border-[#E2E9E6] rounded-md focus:outline-none focus:ring-1 focus:ring-[#167568] focus:border-[#167568] bg-white text-[#202C2A]"
                />
                <Search className="w-3.5 h-3.5 text-[#66736F] absolute left-2.5 top-2.5 pointer-events-none" />
                {isSearching ? (
                  <Loader2 className="w-3.5 h-3.5 text-[#167568] animate-spin absolute right-2.5 top-2.5" />
                ) : searchInput ? (
                  <button
                    onClick={() => setSearchInput("")}
                    className="absolute right-2.5 top-2.5 text-[#66736F] hover:text-[#202C2A]"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                ) : null}
              </div>
            </div>

            {/* Regulator Multi-select */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-[#202C2A] uppercase tracking-wider block">
                Regulator
              </label>
              <div className="space-y-1.5">
                {availableRegulators.map((reg) => (
                  <label
                    key={reg}
                    className="flex items-center space-x-2 text-xs text-[#202C2A] cursor-pointer hover:text-[#167568] select-none"
                  >
                    <input
                      type="checkbox"
                      checked={selectedRegulators.includes(reg)}
                      onChange={() => toggleRegulator(reg)}
                      className="rounded border-[#E2E9E6] text-[#167568] focus:ring-[#167568] w-3.5 h-3.5"
                    />
                    <span>{reg}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Document Type Multi-select */}
            {availableDocTypes.length > 0 && (
              <div className="space-y-2">
                <label className="text-xs font-semibold text-[#202C2A] uppercase tracking-wider block">
                  Document Type
                </label>
                <div className="max-h-40 overflow-y-auto space-y-1.5 pr-1">
                  {availableDocTypes.map((type) => (
                    <label
                      key={type}
                      className="flex items-center space-x-2 text-xs text-[#202C2A] cursor-pointer hover:text-[#167568] select-none"
                    >
                      <input
                        type="checkbox"
                        checked={selectedDocTypes.includes(type)}
                        onChange={() => toggleDocType(type)}
                        className="rounded border-[#E2E9E6] text-[#167568] focus:ring-[#167568] w-3.5 h-3.5"
                      />
                      <span className="truncate" title={type}>
                        {type}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Date Range: Min/Max Year Inputs */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-[#202C2A] uppercase tracking-wider block">
                Year Range
              </label>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <input
                    type="number"
                    min="1990"
                    max="2030"
                    value={minYear}
                    onChange={(e) => {
                      setMinYear(e.target.value);
                      setPage(1);
                    }}
                    placeholder="Min (e.g. 2018)"
                    className="w-full text-xs px-2 py-1.5 border border-[#E2E9E6] rounded-md focus:outline-none focus:ring-1 focus:ring-[#167568] text-[#202C2A]"
                  />
                </div>
                <div>
                  <input
                    type="number"
                    min="1990"
                    max="2030"
                    value={maxYear}
                    onChange={(e) => {
                      setMaxYear(e.target.value);
                      setPage(1);
                    }}
                    placeholder="Max (e.g. 2024)"
                    className="w-full text-xs px-2 py-1.5 border border-[#E2E9E6] rounded-md focus:outline-none focus:ring-1 focus:ring-[#167568] text-[#202C2A]"
                  />
                </div>
              </div>
            </div>

            {/* Sort Controls */}
            <div className="space-y-2 pt-2 border-t border-[#E2E9E6]">
              <label className="text-xs font-semibold text-[#202C2A] uppercase tracking-wider block">
                Sort By
              </label>
              <div className="space-y-2">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as "issue_date" | "document_title")}
                  className="w-full text-xs px-2 py-1.5 border border-[#E2E9E6] rounded-md focus:outline-none focus:ring-1 focus:ring-[#167568] text-[#202C2A] bg-white"
                >
                  <option value="issue_date">Issue Date</option>
                  <option value="document_title">Document Title</option>
                </select>

                <button
                  type="button"
                  onClick={() => setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"))}
                  className="w-full flex items-center justify-between text-xs px-2.5 py-1.5 border border-[#E2E9E6] rounded-md text-[#202C2A] hover:bg-[#F5F7F7] transition-colors"
                >
                  <span className="flex items-center space-x-1">
                    <ArrowUpDown className="w-3.5 h-3.5 text-[#66736F]" />
                    <span>Order: {sortOrder === "desc" ? "Descending" : "Ascending"}</span>
                  </span>
                  <span className="text-[10px] uppercase font-bold text-[#167568]">
                    {sortOrder.toUpperCase()}
                  </span>
                </button>
              </div>
            </div>

            {/* Clear Filters Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={handleClearFilters}
              disabled={activeFilterCount === 0}
              className="w-full text-xs mt-2"
            >
              Clear Filters
            </Button>
          </aside>

          {/* Main Area: Catalog Table */}
          <section className="flex-1 min-w-0 bg-white border border-[#E2E9E6] rounded-lg shadow-xs overflow-hidden flex flex-col">
            {/* Table Header Bar */}
            <div className="p-4 border-b border-[#E2E9E6] flex flex-wrap items-center justify-between gap-2 bg-[#F5F7F7]/50">
              <div className="flex items-center space-x-2">
                <SlidersHorizontal className="w-4 h-4 text-[#167568]" />
                <span className="text-sm font-semibold text-[#202C2A]">Catalog Documents</span>
                <span className="text-xs text-[#66736F]">
                  (Showing {(page - 1) * pageSize + (documents.length > 0 ? 1 : 0)}-{Math.min(page * pageSize, total)} of {total})
                </span>
              </div>
            </div>

            {/* Table / Loading / Empty State */}
            <div className="overflow-x-auto flex-1">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-[#E2E9E6] bg-[#F5F7F7] text-[#202C2A] font-semibold">
                    <th className="py-3 px-4">Title</th>
                    <th className="py-3 px-3 w-20">Regulator</th>
                    <th className="py-3 px-3 w-32">Type</th>
                    <th className="py-3 px-3 w-28">Issue Date</th>
                    <th className="py-3 px-3 w-24">Status</th>
                    <th className="py-3 px-3 w-20 text-center">Chunks</th>
                    <th className="py-3 px-3 w-20 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2E9E6]">
                  {loading ? (
                    // 5 Skeleton rows while loading
                    Array.from({ length: 5 }).map((_, idx) => (
                      <tr key={`skeleton-${idx}`} className="animate-pulse">
                        <td className="py-3 px-4">
                          <Skeleton className="h-4 w-3/4 mb-1" />
                          <Skeleton className="h-3 w-1/3" />
                        </td>
                        <td className="py-3 px-3">
                          <Skeleton className="h-5 w-12 rounded" />
                        </td>
                        <td className="py-3 px-3">
                          <Skeleton className="h-4 w-20" />
                        </td>
                        <td className="py-3 px-3">
                          <Skeleton className="h-4 w-16" />
                        </td>
                        <td className="py-3 px-3">
                          <Skeleton className="h-5 w-14 rounded-full" />
                        </td>
                        <td className="py-3 px-3 text-center">
                          <Skeleton className="h-4 w-8 mx-auto" />
                        </td>
                        <td className="py-3 px-3 text-right">
                          <Skeleton className="h-6 w-12 ml-auto rounded" />
                        </td>
                      </tr>
                    ))
                  ) : documents.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-12 text-center text-[#66736F]">
                        <div className="flex flex-col items-center justify-center space-y-2">
                          <FileText className="w-8 h-8 text-[#66736F]/50" />
                          <p className="text-sm font-medium text-[#202C2A]">No documents found</p>
                          <p className="text-xs text-[#66736F]">
                            Try broadening your search term or clearing some filters.
                          </p>
                          {activeFilterCount > 0 && (
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={handleClearFilters}
                              className="mt-2 text-xs"
                            >
                              Reset All Filters
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ) : (
                    documents.map((doc, idx) => {
                      const title =
                        doc.display_title ||
                        doc.subject ||
                        doc.document_title ||
                        doc.document_id;
                      return (
                        <tr
                          key={doc.document_id || idx}
                          onClick={() => handleSelectDoc(doc.document_id)}
                          className="hover:bg-[#F5F7F7] cursor-pointer transition-colors duration-150 odd:bg-white even:bg-[#FAFCFB]"
                        >
                          <td className="py-3 px-4">
                            <div className="font-medium text-[#202C2A] line-clamp-1" title={title}>
                              {title}
                            </div>
                            <div className="text-[11px] text-[#66736F] font-mono mt-0.5">
                              {doc.circular_number || doc.document_id}
                            </div>
                          </td>
                          <td className="py-3 px-3">{renderRegulatorBadge(doc.regulator)}</td>
                          <td className="py-3 px-3 text-[#202C2A] truncate" title={doc.document_type}>
                            {doc.document_type || "—"}
                          </td>
                          <td className="py-3 px-3 text-[#66736F] font-mono">
                            {doc.issue_date || "—"}
                          </td>
                          <td className="py-3 px-3">{renderStatusBadge(doc.validity_status)}</td>
                          <td className="py-3 px-3 text-center text-[#66736F]">
                            {doc.chunk_count !== undefined ? doc.chunk_count : "—"}
                          </td>
                          <td className="py-3 px-3 text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleSelectDoc(doc.document_id);
                              }}
                              className="text-xs text-[#167568] hover:text-[#125E55] px-2 h-7"
                            >
                              View
                            </Button>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="p-3 border-t border-[#E2E9E6] flex items-center justify-between bg-white text-xs text-[#66736F]">
              <div className="flex items-center space-x-1">
                <span>Page</span>
                <strong className="text-[#202C2A]">{page}</strong>
                <span>of</span>
                <strong className="text-[#202C2A]">{totalPages}</strong>
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                  disabled={page <= 1 || loading}
                  className="h-8 px-2.5 text-xs"
                >
                  <ChevronLeft className="w-3.5 h-3.5 mr-1" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
                  disabled={page >= totalPages || loading}
                  className="h-8 px-2.5 text-xs"
                >
                  Next
                  <ChevronRight className="w-3.5 h-3.5 ml-1" />
                </Button>
              </div>
            </div>
          </section>
        </div>

        {/* Document Detail Right Slide-in Panel */}
        {selectedDocId && (
          <div className="fixed inset-0 z-50 overflow-hidden bg-black/40 flex justify-end">
            <div
              className="bg-white w-full max-w-xl h-full shadow-2xl flex flex-col border-l border-[#E2E9E6] animate-in slide-in-from-right duration-200"
              role="dialog"
              aria-modal="true"
            >
              {/* Drawer Header */}
              <div className="p-4 border-b border-[#E2E9E6] flex items-center justify-between bg-[#F5F7F7]">
                <div className="flex items-center space-x-2 truncate pr-2">
                  <FileText className="w-5 h-5 text-[#167568] flex-shrink-0" />
                  <span className="font-semibold text-sm text-[#202C2A] truncate">
                    Document Details
                  </span>
                </div>
                <button
                  onClick={closeDetail}
                  className="p-1.5 rounded-md text-[#66736F] hover:text-[#202C2A] hover:bg-[#E2E9E6]/60 transition-colors"
                  aria-label="Close detail panel"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Drawer Content */}
              <div className="flex-1 overflow-y-auto p-5 space-y-5">
                {detailLoading ? (
                  <div className="space-y-4">
                    <Skeleton className="h-6 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                    <div className="grid grid-cols-2 gap-3 mt-4">
                      <Skeleton className="h-10 w-full" />
                      <Skeleton className="h-10 w-full" />
                    </div>
                    <Skeleton className="h-32 w-full mt-6" />
                  </div>
                ) : detailDoc ? (
                  <>
                    {/* Header info */}
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        {renderRegulatorBadge(detailDoc.regulator)}
                        {renderStatusBadge(detailDoc.validity_status)}
                        {detailDoc.source_url && (
                          <a
                            href={detailDoc.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center space-x-1 text-xs text-[#167568] hover:underline ml-auto"
                          >
                            <span>Open Source</span>
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                        )}
                      </div>
                      <h2 className="text-base font-bold text-[#202C2A] leading-snug">
                        {detailDoc.display_title ||
                          detailDoc.subject ||
                          detailDoc.document_title ||
                          detailDoc.document_id}
                      </h2>
                      <div className="text-xs text-[#66736F] font-mono">
                        {detailDoc.circular_number || detailDoc.document_id}
                      </div>
                    </div>

                    {/* Metadata Grid */}
                    <div className="grid grid-cols-2 gap-3 bg-[#F5F7F7] p-3 rounded-md border border-[#E2E9E6] text-xs">
                      <div>
                        <span className="text-[#66736F] block">Document Type</span>
                        <span className="font-semibold text-[#202C2A]">
                          {detailDoc.document_type || "—"}
                        </span>
                      </div>
                      <div>
                        <span className="text-[#66736F] block">Issue Date</span>
                        <span className="font-semibold text-[#202C2A]">
                          {detailDoc.issue_date || "—"}
                        </span>
                      </div>
                      <div>
                        <span className="text-[#66736F] block">Total Chunks</span>
                        <span className="font-semibold text-[#202C2A]">
                          {detailDoc.chunks ? detailDoc.chunks.length : detailDoc.chunk_count || 0}
                        </span>
                      </div>
                      <div>
                        <span className="text-[#66736F] block">Regulator</span>
                        <span className="font-semibold text-[#202C2A]">
                          {detailDoc.regulator || "—"}
                        </span>
                      </div>
                    </div>

                    {/* Expandable Chunks List */}
                    <div className="space-y-3 pt-2">
                      <div className="flex items-center justify-between">
                        <h3 className="text-xs font-bold text-[#202C2A] uppercase tracking-wider">
                          Document Chunks ({detailDoc.chunks ? detailDoc.chunks.length : 0})
                        </h3>
                      </div>

                      {detailDoc.chunks && detailDoc.chunks.length > 0 ? (
                        <div className="space-y-2.5">
                          {detailDoc.chunks.map((chunk, idx) => {
                            const isExpanded = !!expandedChunks[chunk.chunk_id || String(idx)];
                            const preview =
                              chunk.text.length > 200 && !isExpanded
                                ? chunk.text.slice(0, 200) + "…"
                                : chunk.text;

                            return (
                              <div
                                key={chunk.chunk_id || idx}
                                className="border border-[#E2E9E6] rounded-md p-3 bg-white text-xs space-y-2"
                              >
                                <div className="flex items-center justify-between border-b border-[#E2E9E6]/60 pb-1.5">
                                  <span className="font-semibold text-[#167568]">
                                    {chunk.section || `Chunk ${idx + 1}`}
                                  </span>
                                  <span className="text-[10px] text-[#66736F] font-mono">
                                    {chunk.chunk_id}
                                  </span>
                                </div>
                                <p className="text-[#202C2A] whitespace-pre-wrap leading-relaxed">
                                  {preview}
                                </p>
                                {chunk.text.length > 200 && (
                                  <button
                                    type="button"
                                    onClick={() => toggleChunkExpand(chunk.chunk_id || String(idx))}
                                    className="text-[11px] font-semibold text-[#167568] hover:text-[#125E55] flex items-center space-x-1 cursor-pointer pt-1"
                                  >
                                    <span>{isExpanded ? "Show less" : "Show more"}</span>
                                    {isExpanded ? (
                                      <ChevronUp className="w-3 h-3" />
                                    ) : (
                                      <ChevronDown className="w-3 h-3" />
                                    )}
                                  </button>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <p className="text-xs text-[#66736F] italic">
                          No text chunks available for this document.
                        </p>
                      )}
                    </div>
                  </>
                ) : (
                  <p className="text-xs text-rose-600">Failed to load document details.</p>
                )}
              </div>

              {/* Drawer Footer */}
              <div className="p-3 border-t border-[#E2E9E6] bg-white flex justify-end">
                <Button variant="secondary" size="sm" onClick={closeDetail} className="text-xs">
                  Close
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
};

export default Explorer;
