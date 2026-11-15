import React, { useState, useRef, useCallback } from 'react';
import AppShell from '../components/layout/AppShell';
import {
  Send,
  RotateCcw,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Clock,
  AlertTriangle,
  ShieldAlert,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  FileText,
  Trash2,
  Sparkles,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { postAsk, QueryResponse, Citation, RetrievedChunk } from '../lib/api';

// ─── Constants ────────────────────────────────────────────────────────────────

const SUGGESTED_PROMPTS = [
  "What are RBI's current repo rate guidelines?",
  "What are SEBI's disclosure requirements for listed companies?",
  "What is RBI's KYC policy for bank accounts?",
  "What are SEBI's insider trading regulations?",
  "What capital adequacy requirements does RBI mandate for banks?",
  "What are SEBI's mutual fund advertisement guidelines?",
  "What are RBI's foreign exchange management regulations?",
  "What are SEBI's regulations on algorithmic trading?",
];

const MAX_HISTORY = 5;
const MAX_CHARS = 500;

// ─── Badge Components ─────────────────────────────────────────────────────────

function RegulatorBadge({ regulator }: { regulator?: string | null }) {
  if (!regulator) return null;
  const upper = regulator.toUpperCase();

  if (upper === 'RBI') {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-[#E6F4F1] text-[#167568] border border-[#C5E5DF]">
        RBI
      </span>
    );
  }
  if (upper === 'SEBI') {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A]">
        SEBI
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-gray-100 text-[#202C2A] border border-[#E2E9E6]">
      {regulator}
    </span>
  );
}

function VerificationBadge({ status }: { status: string }) {
  const norm = status?.toLowerCase() || 'unknown';

  if (norm === 'verified') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
        <CheckCircle2 size={13} className="text-emerald-600" />
        Verified
      </span>
    );
  }
  if (norm === 'insufficient_evidence') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
        <AlertTriangle size={13} className="text-amber-600" />
        Insufficient Evidence
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-gray-100 text-[#66736F] border border-[#E2E9E6]">
      <HelpCircle size={13} className="text-[#66736F]" />
      Unknown
    </span>
  );
}

// ─── Citation Card ─────────────────────────────────────────────────────────────

interface CitationCardProps {
  citation: Citation;
  chunk?: RetrievedChunk;
}

function CitationCard({ citation, chunk }: CitationCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-[#E2E9E6] rounded-lg bg-white overflow-hidden transition-all hover:border-[#167568]/40 shadow-sm">
      <div
        onClick={() => setExpanded((prev) => !prev)}
        className="w-full text-left px-4 py-3 flex items-start gap-3 cursor-pointer hover:bg-[#F5F7F7]/60 transition-colors"
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setExpanded((prev) => !prev);
          }
        }}
      >
        <FileText size={16} className="mt-0.5 text-[#167568] flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <RegulatorBadge regulator={citation.regulator} />
            {citation.issue_date && (
              <span className="text-xs text-[#66736F] font-medium">
                {citation.issue_date}
              </span>
            )}
            {citation.section && (
              <span className="text-xs text-[#66736F] bg-gray-50 px-1.5 py-0.5 rounded border border-[#E2E9E6]">
                Section {citation.section}
              </span>
            )}
          </div>
          <p className="text-sm font-semibold text-[#202C2A] leading-snug">
            {citation.document_title || 'Untitled Document'}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
          {citation.source_url && (
            <a
              href={citation.source_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="inline-flex items-center gap-1 text-xs font-medium text-[#167568] hover:text-[#125E55] hover:underline px-2 py-1 rounded bg-[#E6F4F1]/60"
            >
              <span>Open Source</span>
              <ExternalLink size={12} />
            </a>
          )}
          <span className="p-1 text-[#66736F] hover:text-[#202C2A]">
            {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </span>
        </div>
      </div>

      {expanded && (
        <div className="px-4 py-3 border-t border-[#E2E9E6] bg-[#F5F7F7]/70 text-xs text-[#202C2A] space-y-2">
          {chunk ? (
            <>
              <div className="flex items-center justify-between text-[#66736F] text-[11px] font-mono">
                <span>Chunk ID: {chunk.chunk_id}</span>
                {chunk.validity_status && (
                  <span className="capitalize">Status: {chunk.validity_status}</span>
                )}
              </div>
              <p className="leading-relaxed whitespace-pre-wrap font-sans text-sm text-[#202C2A] bg-white p-3 rounded border border-[#E2E9E6]">
                {chunk.text}
              </p>
            </>
          ) : (
            <p className="text-[#66736F] italic">
              Full text excerpt unavailable for this citation.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Citations Accordion ────────────────────────────────────────────────────────

function CitationsAccordion({
  citations,
  retrievedChunks,
}: {
  citations: Citation[];
  retrievedChunks: RetrievedChunk[];
}) {
  const [isOpen, setIsOpen] = useState(citations.length <= 3);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-5 border border-[#E2E9E6] rounded-xl bg-white overflow-hidden shadow-sm">
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="w-full px-5 py-3.5 flex items-center justify-between text-left font-semibold text-[#202C2A] hover:bg-[#F5F7F7]/50 transition-colors"
      >
        <span className="flex items-center gap-2 text-sm">
          <FileText size={16} className="text-[#167568]" />
          Sources &amp; Citations ({citations.length})
        </span>
        {isOpen ? (
          <ChevronDown size={18} className="text-[#66736F]" />
        ) : (
          <ChevronRight size={18} className="text-[#66736F]" />
        )}
      </button>

      {isOpen && (
        <div className="p-4 pt-1 space-y-2.5 border-t border-[#E2E9E6] bg-[#F5F7F7]/30">
          {citations.map((c, idx) => {
            const chunk = retrievedChunks?.find((rc) => rc.chunk_id === c.chunk_id);
            return (
              <CitationCard
                key={c.chunk_id || `citation-${idx}`}
                citation={c}
                chunk={chunk}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}

// ─── Collapsible Evidence Box ──────────────────────────────────────────────────

function EvidenceCollapsible({ evidence }: { evidence: string[] }) {
  const [open, setOpen] = useState(false);
  if (!evidence || evidence.length === 0) return null;

  return (
    <div className="border border-[#E2E9E6] rounded-lg overflow-hidden bg-[#F5F7F7]/50">
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="w-full px-4 py-2.5 flex items-center justify-between text-left text-xs font-semibold uppercase tracking-wider text-[#66736F] hover:bg-[#F5F7F7] transition-colors"
      >
        <span>Supporting Evidence ({evidence.length})</span>
        {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
      </button>
      {open && (
        <div className="p-4 pt-2 border-t border-[#E2E9E6] bg-white">
          <ul className="space-y-2">
            {evidence.map((item, idx) => (
              <li
                key={idx}
                className="text-xs text-[#202C2A] leading-relaxed flex items-start gap-2"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-[#167568] mt-1.5 flex-shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// ─── Skeleton Loading State ────────────────────────────────────────────────────

function SkeletonLoader() {
  return (
    <div className="bg-white border border-[#E2E9E6] rounded-xl p-6 shadow-sm space-y-4">
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 rounded-full border-2 border-[#167568] border-t-transparent animate-spin" />
        <span className="text-sm font-medium text-[#167568]">
          Processing regulatory query...
        </span>
      </div>
      <div className="space-y-2.5 pt-2">
        <div className="h-4 bg-[#E2E9E6] rounded animate-pulse w-5/6" />
        <div className="h-4 bg-[#E2E9E6] rounded animate-pulse w-full" />
        <div className="h-4 bg-[#E2E9E6] rounded animate-pulse w-4/6" />
      </div>
    </div>
  );
}

// ─── Main Assistant Page Component ─────────────────────────────────────────────

export default function Assistant() {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [history, setHistory] = useState<string[]>([]);
  const [copied, setCopied] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Submit Handler
  const handleSubmit = useCallback(async () => {
    const trimmed = query.trim();
    if (!trimmed || loading) return;

    setLoading(true);
    setSubmittedQuery(trimmed);
    setResponse(null);
    setQuery(''); // Clear input for next query

    try {
      const data = await postAsk(trimmed);
      setResponse(data);
      setHistory((prev) => {
        const filtered = prev.filter((item) => item !== trimmed);
        return [trimmed, ...filtered].slice(0, MAX_HISTORY);
      });
    } catch (err: unknown) {
      const errorMsg =
        err instanceof Error ? err.message : 'An unexpected error occurred while querying.';
      toast.error('Query execution failed');
      setResponse({
        query_analysis: null,
        answer: '',
        regulatory_requirement: '',
        applicability: '',
        conditions: [],
        exceptions: [],
        evidence: [],
        citations: [],
        retrieved_chunks: [],
        evidence_insufficient: false,
        verification_status: 'error',
        guardrails: null,
        regulator: '',
        system_status: null,
        retrieval_status: 'error',
        evidence_status: 'error',
        error: errorMsg,
      });
    } finally {
      setLoading(false);
    }
  }, [query, loading]);

  // Keyboard shortcut Ctrl+Enter / Cmd+Enter
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Reset/Clear Query
  const handleClear = () => {
    setQuery('');
    setSubmittedQuery('');
    setResponse(null);
    setCopied(false);
    textareaRef.current?.focus();
  };

  // Select a prompt or history item
  const handleSelectPrompt = (text: string) => {
    setQuery(text);
    textareaRef.current?.focus();
  };

  // Copy Answer
  const handleCopy = () => {
    if (!response?.answer) return;
    navigator.clipboard.writeText(response.answer);
    setCopied(true);
    toast.success('Copied!');
    setTimeout(() => setCopied(false), 2000);
  };

  // Status checks
  const isInsufficient =
    response?.evidence_insufficient === true ||
    response?.verification_status === 'insufficient_evidence';
  const isBlocked = response?.verification_status === 'blocked';
  const isError = response?.verification_status === 'error';

  return (
    <AppShell>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-[#202C2A] tracking-tight">
            Regulatory Assistant
          </h1>
          <p className="text-sm text-[#66736F] mt-1">
            Ask targeted questions against RBI and SEBI circulars, master directions, and regulatory notifications.
          </p>
        </div>

        {/* Two-Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* ── Left Column (~65% / 8 cols) ── */}
          <div className="lg:col-span-8 space-y-6">
            {/* Query Input Card */}
            <div className="bg-white border border-[#E2E9E6] rounded-xl p-5 shadow-sm">
              <label
                htmlFor="regulatory-query"
                className="block text-sm font-semibold text-[#202C2A] mb-2"
              >
                Regulatory Query
              </label>

              <div className="relative">
                <textarea
                  id="regulatory-query"
                  ref={textareaRef}
                  value={query}
                  onChange={(e) => setQuery(e.target.value.slice(0, MAX_CHARS))}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask a regulatory question about RBI or SEBI guidelines..."
                  rows={4}
                  maxLength={MAX_CHARS}
                  className="w-full resize-none border border-[#E2E9E6] rounded-lg p-3 text-sm text-[#202C2A] placeholder-[#66736F] bg-[#F5F7F7]/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#167568]/20 focus:border-[#167568] transition-colors leading-relaxed"
                />
              </div>

              {/* Action row */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mt-3">
                <div className="text-xs text-[#66736F]">
                  <span>{query.length} / {MAX_CHARS} characters</span>
                  <span className="hidden sm:inline ml-2 text-gray-400">· Press Ctrl+Enter to submit</span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleClear}
                    className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-4 py-2 border border-[#E2E9E6] text-xs font-semibold text-[#66736F] rounded-lg hover:bg-[#F5F7F7] hover:text-[#202C2A] transition-colors"
                  >
                    <RotateCcw size={14} />
                    <span>New Query</span>
                  </button>

                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={!query.trim() || loading}
                    className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-5 py-2 bg-[#167568] text-white text-xs font-semibold rounded-lg hover:bg-[#125E55] disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                  >
                    <Send size={14} />
                    <span>Submit Query</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Active / Submitted Question Display */}
            {submittedQuery && (
              <div className="bg-[#FAFBFB] border border-[#E2E9E6] rounded-xl p-4 flex items-start gap-3 shadow-2xs">
                <div className="w-7 h-7 rounded-lg bg-[#167568]/10 text-[#167568] flex items-center justify-center shrink-0 mt-0.5">
                  <HelpCircle size={15} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#66736F]">
                      Submitted Query
                    </span>
                    {loading && (
                      <span className="text-[11px] font-medium text-[#167568] flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-[#167568] animate-ping" />
                        Searching regulations...
                      </span>
                    )}
                  </div>
                  <p className="text-sm font-semibold text-[#202C2A] mt-0.5 leading-relaxed">
                    {submittedQuery}
                  </p>
                </div>
              </div>
            )}

            {/* Response Section */}
            {loading && <SkeletonLoader />}

            {response && !loading && (
              <div className="space-y-4">
                {/* 1. Insufficient Evidence Banner */}
                {isInsufficient && (
                  <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
                    <AlertTriangle size={18} className="text-amber-600 flex-shrink-0 mt-0.5" />
                    <div className="text-xs sm:text-sm text-amber-800">
                      <p className="font-semibold">Insufficient Evidence</p>
                      <p className="mt-0.5 text-amber-700">
                        The available regulatory documents do not contain sufficient information to answer this query.
                      </p>
                    </div>
                  </div>
                )}

                {/* 2. Guardrails Blocked Banner */}
                {isBlocked && (
                  <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-start gap-3">
                    <ShieldAlert size={18} className="text-rose-600 flex-shrink-0 mt-0.5" />
                    <div className="text-xs sm:text-sm text-rose-800">
                      <p className="font-semibold">Query Blocked</p>
                      <p className="mt-0.5 text-rose-700">Query Blocked by guardrails.</p>
                      {response.guardrails?.failures && response.guardrails.failures.length > 0 && (
                        <ul className="list-disc list-inside mt-1 text-xs text-rose-600">
                          {response.guardrails.failures.map((f, idx) => (
                            <li key={idx}>{f}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                )}

                {/* 3. Error Banner */}
                {isError && (
                  <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-start gap-3">
                    <AlertCircle size={18} className="text-rose-600 flex-shrink-0 mt-0.5" />
                    <div className="text-xs sm:text-sm text-rose-800">
                      <p className="font-semibold">System Error</p>
                      <p className="mt-0.5 text-rose-700">
                        {response.error || 'Failed to process query.'}
                      </p>
                    </div>
                  </div>
                )}

                {/* 4. Normal Answer Card */}
                {response.answer && (
                  <div className="bg-white border border-[#E2E9E6] rounded-xl p-6 shadow-sm space-y-5">
                    {/* Top Row: Verification & Regulator Badges + Copy Button */}
                    <div className="flex items-center justify-between flex-wrap gap-2 pb-3 border-b border-[#E2E9E6]">
                      <div className="flex items-center gap-2">
                        <VerificationBadge status={response.verification_status} />
                        {response.regulator && (
                          <RegulatorBadge regulator={response.regulator} />
                        )}
                        {response.query_analysis?.intent && (
                          <span className="hidden sm:inline-block text-xs text-[#66736F] bg-gray-100 px-2 py-0.5 rounded font-medium">
                            Intent: {response.query_analysis.intent}
                          </span>
                        )}
                      </div>

                      <button
                        type="button"
                        onClick={handleCopy}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#E2E9E6] text-xs font-medium text-[#66736F] hover:text-[#167568] hover:border-[#167568]/40 hover:bg-[#F5F7F7] transition-colors"
                      >
                        {copied ? (
                          <>
                            <Check size={13} className="text-emerald-600" />
                            <span className="text-emerald-600 font-semibold">Copied!</span>
                          </>
                        ) : (
                          <>
                            <Copy size={13} />
                            <span>Copy Answer</span>
                          </>
                        )}
                      </button>
                    </div>

                    {/* Answer text */}
                    <div className="text-sm text-[#202C2A] leading-relaxed whitespace-pre-wrap">
                      {response.answer}
                    </div>

                    {/* Regulatory Requirement Box */}
                    {response.regulatory_requirement && (
                      <div className="p-3.5 bg-[#F5F7F7] border border-[#E2E9E6] rounded-lg">
                        <p className="text-xs font-semibold uppercase tracking-wider text-[#167568] mb-1">
                          Regulatory Requirement
                        </p>
                        <p className="text-xs sm:text-sm text-[#202C2A] leading-relaxed">
                          {response.regulatory_requirement}
                        </p>
                      </div>
                    )}

                    {/* Conditions */}
                    {response.conditions && response.conditions.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold uppercase tracking-wider text-[#202C2A] mb-2">
                          Conditions
                        </h4>
                        <ul className="space-y-1.5">
                          {response.conditions.map((item, idx) => (
                            <li
                              key={idx}
                              className="text-xs sm:text-sm text-[#202C2A] flex items-start gap-2"
                            >
                              <span className="w-1.5 h-1.5 rounded-full bg-[#167568] mt-2 flex-shrink-0" />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Exceptions */}
                    {response.exceptions && response.exceptions.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold uppercase tracking-wider text-[#202C2A] mb-2">
                          Exceptions
                        </h4>
                        <ul className="space-y-1.5">
                          {response.exceptions.map((item, idx) => (
                            <li
                              key={idx}
                              className="text-xs sm:text-sm text-[#202C2A] flex items-start gap-2"
                            >
                              <span className="w-1.5 h-1.5 rounded-full bg-amber-600 mt-2 flex-shrink-0" />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Evidence Section (collapsed by default) */}
                    {response.evidence && response.evidence.length > 0 && (
                      <EvidenceCollapsible evidence={response.evidence} />
                    )}
                  </div>
                )}

                {/* Citations / Sources Accordion */}
                {response.citations && response.citations.length > 0 && (
                  <CitationsAccordion
                    citations={response.citations}
                    retrievedChunks={response.retrieved_chunks || []}
                  />
                )}
              </div>
            )}
          </div>

          {/* ── Right Column (~35% / 4 cols) ── */}
          <div className="lg:col-span-4 space-y-6 lg:sticky lg:top-6">
            {/* Suggested Queries Card */}
            <div className="bg-white border border-[#E2E9E6] rounded-xl p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles size={16} className="text-[#167568]" />
                <h3 className="text-sm font-semibold text-[#202C2A]">Suggested Queries</h3>
              </div>
              <p className="text-xs text-[#66736F] mb-3">
                Click any prompt to populate the query box.
              </p>

              <div className="space-y-2">
                {SUGGESTED_PROMPTS.map((prompt, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectPrompt(prompt)}
                    className="w-full text-left p-2.5 rounded-lg border border-[#E2E9E6] text-xs text-[#202C2A] hover:bg-[#F5F7F7] hover:border-[#167568] hover:text-[#167568] transition-all leading-snug group flex items-start justify-between gap-2"
                  >
                    <span>{prompt}</span>
                    <ChevronRight
                      size={14}
                      className="text-[#66736F] opacity-0 group-hover:opacity-100 group-hover:text-[#167568] transition-opacity flex-shrink-0 mt-0.5"
                    />
                  </button>
                ))}
              </div>
            </div>

            {/* Query History Card */}
            <div className="bg-white border border-[#E2E9E6] rounded-xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Clock size={16} className="text-[#167568]" />
                  <h3 className="text-sm font-semibold text-[#202C2A]">Recent Queries</h3>
                </div>
                {history.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setHistory([])}
                    className="inline-flex items-center gap-1 text-[11px] font-medium text-[#66736F] hover:text-rose-600 transition-colors"
                  >
                    <Trash2 size={12} />
                    <span>Clear history</span>
                  </button>
                )}
              </div>

              {history.length === 0 ? (
                <p className="text-xs text-[#66736F] py-2">
                  No queries run in this session yet.
                </p>
              ) : (
                <div className="space-y-1.5">
                  {history.map((item, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSelectPrompt(item)}
                      className="w-full text-left p-2 rounded-lg text-xs text-[#202C2A] hover:bg-[#F5F7F7] hover:text-[#167568] transition-colors flex items-start gap-2 group"
                    >
                      <Clock
                        size={13}
                        className="text-[#66736F] mt-0.5 flex-shrink-0 group-hover:text-[#167568]"
                      />
                      <span className="truncate leading-tight">{item}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
