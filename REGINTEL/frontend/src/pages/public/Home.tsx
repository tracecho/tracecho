import React, { useState } from "react";
import { Link } from "react-router-dom";
import PublicLayout from "@/components/layout/PublicLayout";
import { Button } from "@/components/ui/Button";
import {
  Search,
  MessageSquare,
  FileText,
  Shield,
  CheckCircle,
  ChevronRight,
  ChevronDown,
  Building2,
  FileSearch,
  Sparkles,
  ExternalLink,
  BookOpen,
  Filter,
  Layers,
  HelpCircle,
  AlertCircle,
  X,
  Database,
  ArrowRight,
  SlidersHorizontal,
} from "lucide-react";

interface DemoScenario {
  id: string;
  question: string;
  tag: string;
  regulator: "RBI" | "SEBI";
  answer: string;
  citations: {
    docId: string;
    circularNo: string;
    regulator: "RBI" | "SEBI";
    department: string;
    title: string;
    date: string;
    section: string;
    excerpt: string;
    confidence: string;
  }[];
}

const DEMO_SCENARIOS: DemoScenario[] = [
  {
    id: "rbi-psl",
    question: "What are the overall Priority Sector Lending (PSL) targets for Small Finance Banks?",
    tag: "RBI • Priority Sector Lending",
    regulator: "RBI",
    answer:
      "Under the Reserve Bank of India Master Directions on Priority Sector Lending, Small Finance Banks (SFBs) are mandated to achieve an overall priority sector lending target of 75% of their Adjusted Net Bank Credit (ANBC) or Credit Equivalent Amount of Off-Balance Sheet Exposure (CEOBE), whichever is higher [RBI/FIDD/2020-21/72 §6.1]. Within this target, sub-targets apply for Agriculture (18%), Micro Enterprises (7.5%), and Advances to Weaker Sections (12%).",
    citations: [
      {
        docId: "rbi-psl-sfb-2021",
        circularNo: "RBI/FIDD/2020-21/72 (Master Direction FIDD.CO.Plan.BC.5/04.09.01/2020-21)",
        regulator: "RBI",
        department: "Financial Inclusion and Development Department (FIDD)",
        title: "Master Direction – Priority Sector Lending (PSL) – Targets and Classification",
        date: "September 04, 2020 (Updated as on April 24, 2023)",
        section: "Section 6.1 – Targets / Sub-targets for Small Finance Banks",
        excerpt:
          "Small Finance Banks shall achieve an overall priority sector lending target of 75 per cent of their Adjusted Net Bank Credit (ANBC) or Credit Equivalent Amount of Off-Balance Sheet Exposure (CEOBE), whichever is higher. Small Finance Banks are also required to extend 40 per cent of their total loans in sizes up to ₹25 lakh.",
        confidence: "98.4% Match",
      },
    ],
  },
  {
    id: "sebi-cybersecurity",
    question: "What are the mandatory reporting timelines for cybersecurity incidents under SEBI guidelines?",
    tag: "SEBI • Cybersecurity (CSCRF)",
    regulator: "SEBI",
    answer:
      "Pursuant to the SEBI Cybersecurity and Cyber Resilience Framework (CSCRF), regulated entities (including Market Infrastructure Institutions and Qualified Intermediaries) must report any cybersecurity incident to SEBI and CERT-In within 6 hours of detection [SEBI/HO/MRD/TPD/P/CIR/2023/144 §3.2]. A comprehensive root-cause analysis (RCA) and mitigation report must be formally submitted to SEBI within 14 calendar days.",
    citations: [
      {
        docId: "sebi-cscrf-2023",
        circularNo: "SEBI/HO/MRD/TPD/P/CIR/2023/144",
        regulator: "SEBI",
        department: "Market Regulation Department (Technology & Cyber Resilience)",
        title: "Cybersecurity and Cyber Resilience Framework (CSCRF) for Regulated Entities",
        date: "August 20, 2023",
        section: "Clause 3.2 – Incident Notification & Escalation Protocols",
        excerpt:
          "All registered entities shall report any incident affecting critical IT infrastructure or unauthorized data exfiltration to SEBI and CERT-In within six (6) hours of noticing or being brought to notice such incidents. A comprehensive Root Cause Analysis (RCA) shall be submitted within 14 calendar days.",
        confidence: "96.7% Match",
      },
    ],
  },
  {
    id: "rbi-kyc",
    question: "What is the prescribed frequency for periodic updation of KYC for high-risk accounts under RBI norms?",
    tag: "RBI • KYC Master Direction",
    regulator: "RBI",
    answer:
      "Under Chapter VI of the RBI Master Direction on Know Your Customer (KYC), Regulated Entities must carry out periodic KYC updation at least once every two years for high-risk customers [RBI/DBR/2015-16/18 §38(b)]. For medium-risk customers, the requirement is at least once every eight years, and for low-risk customers, at least once every ten years, subject to continuous transaction monitoring.",
    citations: [
      {
        docId: "rbi-kyc-md-2016",
        circularNo: "RBI/DBR/2015-16/18 (Master Direction DBR.AML.BC.No.81/14.01.001/2015-16)",
        regulator: "RBI",
        department: "Department of Banking Regulation (KYC/AML Cell)",
        title: "Master Direction – Know Your Customer (KYC) Direction, 2016",
        date: "February 25, 2016 (Amended as on May 04, 2023)",
        section: "Section 38 – Periodic Updation of Customer Identification Data",
        excerpt:
          "Periodic updation shall be carried out at least once in every two years for high risk customers, once in every eight years for medium risk customers and once in every ten years for low risk customers from the date of opening of the account or last KYC verification.",
        confidence: "99.1% Match",
      },
    ],
  },
];

interface FAQItem {
  question: string;
  answer: string;
}

const FAQ_ITEMS: FAQItem[] = [
  {
    question: "How does TRACECHO ensure answers are grounded in official regulatory documents?",
    answer:
      "TRACECHO uses a retrieval-augmented generation (RAG) architecture. When a user asks a question, the system queries a strictly verified corpus of RBI and SEBI circulars, master directions, and notifications using hybrid search (lexical BM25 and dense embeddings). The LLM is constrained to synthesize answers solely from retrieved document chunks, citing paragraph-level source references.",
  },
  {
    question: "Which regulatory bodies and document types are supported?",
    answer:
      "TRACECHO covers the Reserve Bank of India (RBI) and the Securities and Exchange Board of India (SEBI). Document formats include Master Directions, Master Circulars, statutory notifications, circular updates, operational guidelines, and board regulatory orders.",
  },
  {
    question: "What happens when documentary evidence is insufficient to answer a query?",
    answer:
      "Unlike generalized AI models that extrapolate or hallucinate plausible answers, TRACECHO operates on an evidence-first refusal protocol. When the retrieved documents do not contain sufficient evidence to answer with high confidence, the system explicitly reports that evidence is insufficient.",
  },
  {
    question: "Can I inspect the underlying circular or paragraph referenced in an answer?",
    answer:
      "Yes. Every answer features clickable source citations that link to the exact circular number, issuing date, section, and verbatim paragraph excerpt in the Document Explorer, allowing compliance teams to conduct auditable verification.",
  },
  {
    question: "How often is the regulatory document corpus updated?",
    answer:
      "The document repository is synchronized with public RBI and SEBI publication portals, indexing newly published notifications, master circular renewals, and amendments as they are gazetted.",
  },
];

export default function Home() {
  // Demo Workspace State
  const [selectedScenarioIndex, setSelectedScenarioIndex] = useState<number>(0);
  const [inputQuery, setInputQuery] = useState<string>(DEMO_SCENARIOS[0].question);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [activeCitationModal, setActiveCitationModal] = useState<DemoScenario["citations"][0] | null>(null);

  // How It Works State
  const [activeStep, setActiveStep] = useState<number>(1);

  // Regulatory Sources State
  const [activeSourceTab, setActiveSourceTab] = useState<"RBI" | "SEBI">("RBI");

  // FAQ Accordion State
  const [expandedFaq, setExpandedFaq] = useState<number | null>(0);

  const activeScenario = DEMO_SCENARIOS[selectedScenarioIndex];

  const handleSelectScenario = (index: number) => {
    setSelectedScenarioIndex(index);
    setInputQuery(DEMO_SCENARIOS[index].question);
    setIsSimulating(true);
    setTimeout(() => {
      setIsSimulating(false);
    }, 350);
  };

  const handleSimulateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSimulating(true);
    setTimeout(() => {
      setIsSimulating(false);
    }, 400);
  };

  return (
    <PublicLayout>
      <div className="w-full flex flex-col font-sans">
        {/* SECTION A: HERO */}
        <section className="w-full bg-white border-b border-[#E2E9E6] py-20 lg:py-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center flex flex-col items-center">
            {/* Eyebrow label */}
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#167568]/10 text-[#167568] text-xs font-semibold tracking-widest uppercase mb-2">
              <Shield className="w-3.5 h-3.5" />
              <span>AI-POWERED REGULATORY INTELLIGENCE</span>
            </div>

            {/* H1 */}
            <h1 className="text-4xl sm:text-5xl font-bold text-[#202C2A] leading-tight max-w-2xl mt-4 tracking-tight">
              Regulatory intelligence,
              <br />
              grounded in evidence.
            </h1>

            {/* Subheading */}
            <p className="text-base sm:text-lg text-[#66736F] max-w-xl mt-4 leading-relaxed">
              Discover, understand and navigate complex regulatory information with
              AI-powered research and source-backed answers from RBI and SEBI
              documents.
            </p>

            {/* Two CTA buttons */}
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4 w-full sm:w-auto">
              <Button
                asChild
                className="bg-[#167568] hover:bg-[#125E55] text-white font-medium px-6 py-2.5 rounded-md h-auto transition-all shadow-xs hover:shadow hover:-translate-y-0.5 w-full sm:w-auto"
              >
                <Link to="/app" className="flex items-center justify-center gap-2">
                  <span>Explore the Platform</span>
                  <ChevronRight className="w-4 h-4" />
                </Link>
              </Button>

              <Button
                asChild
                variant="outline"
                className="border border-[#E2E9E6] bg-white text-[#202C2A] hover:bg-[#F5F7F7] hover:border-[#167568]/40 font-medium px-6 py-2.5 rounded-md h-auto transition-all w-full sm:w-auto"
              >
                <Link to="/about">Learn More</Link>
              </Button>
            </div>

            {/* Subtle stat / evidence badge row */}
            <div className="mt-12 pt-8 border-t border-[#E2E9E6] w-full max-w-2xl flex flex-wrap items-center justify-center gap-6 sm:gap-8 text-xs font-medium text-[#66736F]">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#167568]" />
                <span>RBI Documents</span>
              </div>
              <div className="hidden sm:block text-[#E2E9E6]">|</div>
              <div className="flex items-center gap-2">
                <FileSearch className="w-4 h-4 text-[#167568]" />
                <span>SEBI Circulars</span>
              </div>
              <div className="hidden sm:block text-[#E2E9E6]">|</div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-[#167568]" />
                <span>Evidence-Backed Answers</span>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION INTERACTIVE WORKSPACE PREVIEW */}
        <section className="w-full bg-[#F5F7F7] py-16 px-4 sm:px-6 lg:px-8 border-b border-[#E2E9E6]">
          <div className="max-w-5xl mx-auto">
            {/* Header with Sample Demonstration Badge */}
            <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
              <div>
                <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-amber-50 border border-amber-200 text-amber-800 text-xs font-medium mb-2">
                  <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                  <span>Interactive Workspace Preview • Sample Demonstration</span>
                </div>
                <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A]">
                  Experience source-grounded answers
                </h2>
                <p className="text-sm text-[#66736F] mt-1">
                  Click a sample inquiry below or test query submission to see citation retrieval in action.
                </p>
              </div>

              {/* Sample Question Chips */}
              <div className="flex flex-wrap gap-2">
                {DEMO_SCENARIOS.map((scenario, idx) => (
                  <button
                    key={scenario.id}
                    type="button"
                    onClick={() => handleSelectScenario(idx)}
                    className={`text-xs px-3 py-1.5 rounded-md font-medium transition-all ${
                      selectedScenarioIndex === idx
                        ? "bg-[#167568] text-white shadow-xs"
                        : "bg-white text-[#202C2A] border border-[#E2E9E6] hover:border-[#167568]/40 hover:bg-white"
                    }`}
                  >
                    {scenario.tag}
                  </button>
                ))}
              </div>
            </div>

            {/* Interactive Preview Container */}
            <div className="bg-white rounded-xl border border-[#E2E9E6] shadow-xs overflow-hidden">
              {/* Workspace Top Toolbar */}
              <div className="bg-[#FAFBFB] px-5 py-3 border-b border-[#E2E9E6] flex items-center justify-between text-xs text-[#66736F]">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="font-semibold text-[#202C2A]">AI Regulatory Research Engine</span>
                  <span className="text-[#E2E9E6]">|</span>
                  <span>Model: Hybrid RAG + Strict Evidence Gate</span>
                </div>
                <span className="hidden sm:inline-block bg-white px-2 py-0.5 rounded border border-[#E2E9E6] text-[11px] font-medium text-[#167568]">
                  Target Corpus: {activeScenario.regulator} Master Repository
                </span>
              </div>

              {/* Workspace Main Grid */}
              <div className="p-6">
                {/* Search / Question Input Bar */}
                <form onSubmit={handleSimulateSubmit} className="relative mb-6">
                  <div className="flex items-center gap-2">
                    <div className="relative flex-1">
                      <Search className="w-4 h-4 text-[#66736F] absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input
                        type="text"
                        value={inputQuery}
                        onChange={(e) => setInputQuery(e.target.value)}
                        placeholder="Ask a regulatory question..."
                        className="w-full pl-10 pr-4 py-2.5 bg-[#F5F7F7] border border-[#E2E9E6] rounded-lg text-sm text-[#202C2A] focus:outline-none focus:ring-2 focus:ring-[#167568] focus:bg-white transition-all"
                      />
                    </div>
                    <Button
                      type="submit"
                      disabled={isSimulating}
                      className="bg-[#167568] hover:bg-[#125E55] text-white px-5 py-2.5 rounded-lg text-sm font-medium h-auto flex items-center gap-2"
                    >
                      {isSimulating ? (
                        <>
                          <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          <span>Retrieving...</span>
                        </>
                      ) : (
                        <>
                          <span>Search Evidence</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </>
                      )}
                    </Button>
                  </div>
                </form>

                {/* Simulation / Results Display */}
                {isSimulating ? (
                  <div className="py-12 flex flex-col items-center justify-center text-center space-y-3">
                    <div className="w-7 h-7 border-2 border-[#167568]/20 border-t-[#167568] rounded-full animate-spin" />
                    <p className="text-xs font-medium text-[#66736F]">
                      Searching BM25 index &amp; dense vector embeddings across {activeScenario.regulator} corpus...
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left 2 Cols: Synthesized Answer */}
                    <div className="lg:col-span-2 space-y-4">
                      <div className="bg-[#FAFBFB] p-5 rounded-lg border border-[#E2E9E6]">
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-xs font-semibold text-[#167568] uppercase tracking-wider flex items-center gap-1.5">
                            <CheckCircle className="w-3.5 h-3.5" />
                            Grounded Answer
                          </span>
                          <span className="text-[11px] text-[#66736F] bg-white px-2 py-0.5 rounded border border-[#E2E9E6]">
                            Lineage Verified
                          </span>
                        </div>
                        <p className="text-sm text-[#202C2A] leading-relaxed">
                          {activeScenario.answer}
                        </p>
                      </div>

                      {/* Evidence Verification Callout */}
                      <div className="flex items-start gap-3 p-3.5 bg-emerald-50/60 border border-emerald-200/80 rounded-lg text-xs text-emerald-900">
                        <Shield className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
                        <div>
                          <span className="font-semibold text-emerald-950">Confidence Guarantee: </span>
                          All claims in this synthesized response are anchored in verified regulatory paragraphs. If documentary evidence were insufficient, the system would refuse to answer.
                        </div>
                      </div>
                    </div>

                    {/* Right 1 Col: Retrieved Source Citation Card */}
                    <div className="lg:col-span-1">
                      <div className="border border-[#E2E9E6] rounded-lg p-4 bg-white flex flex-col h-full justify-between">
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-bold text-[#202C2A] flex items-center gap-1.5">
                              <BookOpen className="w-3.5 h-3.5 text-[#167568]" />
                              Cited Source
                            </span>
                            <span className="text-[10px] font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded">
                              {activeScenario.citations[0].confidence}
                            </span>
                          </div>

                          <div className="text-xs font-semibold text-[#167568] line-clamp-1 mb-1">
                            {activeScenario.citations[0].circularNo}
                          </div>
                          <div className="text-xs font-medium text-[#202C2A] line-clamp-2 mb-2">
                            {activeScenario.citations[0].title}
                          </div>
                          <div className="text-[11px] text-[#66736F] mb-3">
                            {activeScenario.citations[0].section}
                          </div>

                          <div className="p-2.5 bg-[#F5F7F7] rounded border border-[#E2E9E6] text-xs text-[#202C2A] font-serif italic line-clamp-3">
                            &ldquo;{activeScenario.citations[0].excerpt}&rdquo;
                          </div>
                        </div>

                        <div className="mt-4 pt-3 border-t border-[#E2E9E6]">
                          <button
                            type="button"
                            onClick={() => setActiveCitationModal(activeScenario.citations[0])}
                            className="w-full text-xs font-medium text-[#167568] hover:text-[#125E55] flex items-center justify-center gap-1.5 py-1.5 rounded hover:bg-[#167568]/5 transition-colors"
                          >
                            <span>Inspect Citation Details</span>
                            <ExternalLink className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* SECTION B: WHAT IS TRACECHO */}
        <section className="w-full bg-[#F5F7F7] py-20 px-4 sm:px-6 lg:px-8 border-b border-[#E2E9E6]">
          <div className="max-w-5xl mx-auto">
            <div className="text-center md:text-left mb-10">
              <span className="text-[#167568] text-xs font-semibold tracking-widest uppercase">
                WHAT IS TRACECHO
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A] mt-2">
                Built for regulatory clarity
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12">
              {/* Left Column: The Challenge */}
              <div className="bg-white p-8 rounded-lg border border-[#E2E9E6] hover:border-[#167568]/30 transition-colors shadow-xs">
                <h3 className="text-lg font-bold text-[#202C2A] mb-4 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-amber-600" />
                  <span>The challenge</span>
                </h3>
                <div className="space-y-4 text-sm text-[#66736F] leading-relaxed">
                  <p>
                    Financial institutions, banks, and market intermediaries operate
                    in a continuously evolving regulatory landscape governed by
                    thousands of circulars, master directions, and notifications
                    issued by Indian regulatory bodies.
                  </p>
                  <p>
                    Navigating fragmented document archives, tracking circular
                    amendments across multiple years, and cross-referencing statutory
                    mandates manually creates substantial operational overhead and
                    heightens compliance exposure.
                  </p>
                  <p>
                    Conventional keyword-based search lacks context, struggling to
                    differentiate between superseding guidelines, historical
                    frameworks, and specific operational caveats.
                  </p>
                </div>
              </div>

              {/* Right Column: Our Approach */}
              <div className="bg-white p-8 rounded-lg border border-[#E2E9E6] hover:border-[#167568]/30 transition-colors shadow-xs">
                <h3 className="text-lg font-bold text-[#202C2A] mb-4 flex items-center gap-2">
                  <Layers className="w-5 h-5 text-[#167568]" />
                  <span>Our approach</span>
                </h3>
                <div className="space-y-4 text-sm text-[#66736F] leading-relaxed">
                  <p>
                    TRACECHO pairs advanced retrieval-augmented generation (RAG)
                    with an authoritative corpus of regulatory publications from the
                    Reserve Bank of India (RBI) and Securities and Exchange Board of
                    India (SEBI).
                  </p>
                  <p>
                    Our hybrid retrieval pipeline pairs BM25 lexical precision with
                    dense semantic embeddings to identify exact regulatory clauses,
                    definitions, and specific compliance requirements across complex
                    multi-section documents.
                  </p>
                  <p>
                    Every synthesized response is anchored directly in verifiable
                    source documents, maintaining an auditable evidence chain that
                    empowers compliance and legal professionals with confidence.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION C: CAPABILITIES STRIP */}
        <section className="w-full bg-white py-20 px-4 sm:px-6 lg:px-8 border-b border-[#E2E9E6]">
          <div className="max-w-6xl mx-auto">
            <div className="text-center max-w-2xl mx-auto mb-12">
              <span className="text-[#167568] text-xs font-semibold tracking-widest uppercase">
                CORE CAPABILITIES
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A] mt-2">
                Designed for precision compliance workflows
              </h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Card 1 */}
              <div className="bg-white border border-[#E2E9E6] rounded-lg p-6 flex flex-col transition-all duration-200 hover:-translate-y-1 hover:border-[#167568]/40 hover:shadow-sm cursor-default">
                <div className="w-10 h-10 rounded-md bg-[#167568]/10 text-[#167568] flex items-center justify-center mb-4 transition-transform group-hover:scale-105">
                  <Search className="w-5 h-5" />
                </div>
                <h3 className="font-semibold text-[#202C2A] text-base mb-2">
                  Regulatory Search
                </h3>
                <p className="text-sm text-[#66736F] leading-relaxed">
                  Quickly surface relevant circulars, notifications and guidelines
                  from RBI and SEBI.
                </p>
              </div>

              {/* Card 2 */}
              <div className="bg-white border border-[#E2E9E6] rounded-lg p-6 flex flex-col transition-all duration-200 hover:-translate-y-1 hover:border-[#167568]/40 hover:shadow-sm cursor-default">
                <div className="w-10 h-10 rounded-md bg-[#167568]/10 text-[#167568] flex items-center justify-center mb-4">
                  <MessageSquare className="w-5 h-5" />
                </div>
                <h3 className="font-semibold text-[#202C2A] text-base mb-2">
                  AI-Powered Q&amp;A
                </h3>
                <p className="text-sm text-[#66736F] leading-relaxed">
                  Ask questions in plain language. Get structured answers with
                  supporting evidence and source citations.
                </p>
              </div>

              {/* Card 3 */}
              <div className="bg-white border border-[#E2E9E6] rounded-lg p-6 flex flex-col transition-all duration-200 hover:-translate-y-1 hover:border-[#167568]/40 hover:shadow-sm cursor-default">
                <div className="w-10 h-10 rounded-md bg-[#167568]/10 text-[#167568] flex items-center justify-center mb-4">
                  <FileText className="w-5 h-5" />
                </div>
                <h3 className="font-semibold text-[#202C2A] text-base mb-2">
                  Document Intelligence
                </h3>
                <p className="text-sm text-[#66736F] leading-relaxed">
                  Browse and inspect the full regulatory document corpus with
                  metadata, sections and direct links.
                </p>
              </div>

              {/* Card 4 */}
              <div className="bg-white border border-[#E2E9E6] rounded-lg p-6 flex flex-col transition-all duration-200 hover:-translate-y-1 hover:border-[#167568]/40 hover:shadow-sm cursor-default">
                <div className="w-10 h-10 rounded-md bg-[#167568]/10 text-[#167568] flex items-center justify-center mb-4">
                  <Shield className="w-5 h-5" />
                </div>
                <h3 className="font-semibold text-[#202C2A] text-base mb-2">
                  Evidence Accountability
                </h3>
                <p className="text-sm text-[#66736F] leading-relaxed">
                  Every answer is grounded in retrieved documents. The system
                  clearly signals when evidence is insufficient.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION D: INTERACTIVE HOW IT WORKS (3 STEPS) */}
        <section className="w-full bg-[#F5F7F7] py-20 px-4 sm:px-6 lg:px-8 border-b border-[#E2E9E6]">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <span className="text-[#167568] text-xs font-semibold tracking-widest uppercase">
                INTERACTIVE WORKFLOW
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A] mt-2">
                How TRACECHO works
              </h2>
              <p className="text-sm text-[#66736F] mt-2">
                Click any of the 3 steps to inspect the operational stage under the hood.
              </p>
            </div>

            {/* 3 Interactive Step Buttons */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              {/* Step 1 Button */}
              <button
                type="button"
                onClick={() => setActiveStep(1)}
                className={`p-6 rounded-lg text-left transition-all border ${
                  activeStep === 1
                    ? "bg-white border-[#167568] shadow-sm ring-1 ring-[#167568]"
                    : "bg-white/80 border-[#E2E9E6] hover:bg-white hover:border-[#167568]/40"
                }`}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                      activeStep === 1 ? "bg-[#167568] text-white" : "bg-[#F5F7F7] text-[#66736F] border border-[#E2E9E6]"
                    }`}
                  >
                    1
                  </div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-[#167568]">
                    Inquiry Formulation
                  </span>
                </div>
                <h3 className="font-semibold text-[#202C2A] text-base mb-1">
                  Ask a regulatory question
                </h3>
                <p className="text-xs text-[#66736F] leading-relaxed">
                  Type questions in plain language regarding statutory mandates or circular provisions.
                </p>
              </button>

              {/* Step 2 Button */}
              <button
                type="button"
                onClick={() => setActiveStep(2)}
                className={`p-6 rounded-lg text-left transition-all border ${
                  activeStep === 2
                    ? "bg-white border-[#167568] shadow-sm ring-1 ring-[#167568]"
                    : "bg-white/80 border-[#E2E9E6] hover:bg-white hover:border-[#167568]/40"
                }`}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                      activeStep === 2 ? "bg-[#167568] text-white" : "bg-[#F5F7F7] text-[#66736F] border border-[#E2E9E6]"
                    }`}
                  >
                    2
                  </div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-[#167568]">
                    Hybrid Retrieval
                  </span>
                </div>
                <h3 className="font-semibold text-[#202C2A] text-base mb-1">
                  AI retrieves relevant documents
                </h3>
                <p className="text-xs text-[#66736F] leading-relaxed">
                  Hybrid BM25 + vector search scans across the complete RBI &amp; SEBI corpus.
                </p>
              </button>

              {/* Step 3 Button */}
              <button
                type="button"
                onClick={() => setActiveStep(3)}
                className={`p-6 rounded-lg text-left transition-all border ${
                  activeStep === 3
                    ? "bg-white border-[#167568] shadow-sm ring-1 ring-[#167568]"
                    : "bg-white/80 border-[#E2E9E6] hover:bg-white hover:border-[#167568]/40"
                }`}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                      activeStep === 3 ? "bg-[#167568] text-white" : "bg-[#F5F7F7] text-[#66736F] border border-[#E2E9E6]"
                    }`}
                  >
                    3
                  </div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-[#167568]">
                    Evidence Synthesis
                  </span>
                </div>
                <h3 className="font-semibold text-[#202C2A] text-base mb-1">
                  Get a grounded, cited answer
                </h3>
                <p className="text-xs text-[#66736F] leading-relaxed">
                  Structured response with strict source citations and explicit verification.
                </p>
              </button>
            </div>

            {/* Step Detail Explanation Panel */}
            <div className="bg-white rounded-lg border border-[#E2E9E6] p-6 shadow-xs">
              {activeStep === 1 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                  <div className="md:col-span-2 space-y-3">
                    <span className="text-xs font-bold text-[#167568] uppercase">Step 1 Mechanism</span>
                    <h4 className="text-lg font-bold text-[#202C2A]">
                      Semantic Query Disambiguation &amp; Entity Parsing
                    </h4>
                    <p className="text-sm text-[#66736F] leading-relaxed">
                      User questions are parsed to isolate regulatory entities (e.g., Scheduled Commercial Banks, NBFC-ICC, Depositories), statutory acts (Banking Regulation Act 1949, SEBI Act 1992), and temporal constraints before search dispatch.
                    </p>
                    <div className="flex flex-wrap gap-2 pt-1 text-xs">
                      <span className="bg-[#F5F7F7] border border-[#E2E9E6] px-2.5 py-1 rounded text-[#202C2A]">
                        Entity Extraction
                      </span>
                      <span className="bg-[#F5F7F7] border border-[#E2E9E6] px-2.5 py-1 rounded text-[#202C2A]">
                        Synonym Expansion
                      </span>
                      <span className="bg-[#F5F7F7] border border-[#E2E9E6] px-2.5 py-1 rounded text-[#202C2A]">
                        Regulator Targeting
                      </span>
                    </div>
                  </div>
                  <div className="bg-[#FAFBFB] border border-[#E2E9E6] rounded-md p-4 text-xs font-mono text-[#202C2A] space-y-1">
                    <div className="text-[#66736F]">// Query Formulation</div>
                    <div>&gt; Target: <span className="text-[#167568]">RBI/SEBI</span></div>
                    <div>&gt; Intent: <span className="text-[#167568]">Mandatory Rule</span></div>
                    <div>&gt; Scope: <span className="text-[#167568]">Master Directions</span></div>
                  </div>
                </div>
              )}

              {activeStep === 2 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                  <div className="md:col-span-2 space-y-3">
                    <span className="text-xs font-bold text-[#167568] uppercase">Step 2 Mechanism</span>
                    <h4 className="text-lg font-bold text-[#202C2A]">
                      Dual-Path Hybrid Retrieval (BM25 + Dense Embeddings)
                    </h4>
                    <p className="text-sm text-[#66736F] leading-relaxed">
                      Keywords locate exact statutory circular identifiers and circular clause numbers, while semantic embeddings match conceptual synonyms across multi-page PDF documents. Results are fused using Reciprocal Rank Fusion (RRF).
                    </p>
                    <div className="flex flex-wrap gap-2 pt-1 text-xs">
                      <span className="bg-[#F5F7F7] border border-[#E2E9E6] px-2.5 py-1 rounded text-[#202C2A]">
                        BM25 Keyword Indexing
                      </span>
                      <span className="bg-[#F5F7F7] border border-[#E2E9E6] px-2.5 py-1 rounded text-[#202C2A]">
                        Vector Chunk Embeddings
                      </span>
                      <span className="bg-[#F5F7F7] border border-[#E2E9E6] px-2.5 py-1 rounded text-[#202C2A]">
                        Cross-Encoder Reranking
                      </span>
                    </div>
                  </div>
                  <div className="bg-[#FAFBFB] border border-[#E2E9E6] rounded-md p-4 text-xs font-mono text-[#202C2A] space-y-1">
                    <div className="text-[#66736F]">// Retrieval Ranking</div>
                    <div>&gt; BM25 Score: <span className="text-emerald-700">0.942</span></div>
                    <div>&gt; Vector Sim: <span className="text-emerald-700">0.891</span></div>
                    <div>&gt; Top Passages: <span className="text-[#167568]">5 Chunks</span></div>
                  </div>
                </div>
              )}

              {activeStep === 3 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                  <div className="md:col-span-2 space-y-3">
                    <span className="text-xs font-bold text-[#167568] uppercase">Step 3 Mechanism</span>
                    <h4 className="text-lg font-bold text-[#202C2A]">
                      Strict Lineage Verification &amp; Refusal Standard
                    </h4>
                    <p className="text-sm text-[#66736F] leading-relaxed">
                      Every statement in the synthesized response is mapped to an authoritative paragraph identifier. If retrieved context fails to satisfy the query with high confidence, the platform refuses to generate speculative information.
                    </p>
                    <div className="flex flex-wrap gap-2 pt-1 text-xs">
                      <span className="bg-[#F5F7F7] border border-[#E2E9E6] px-2.5 py-1 rounded text-[#202C2A]">
                        Strict Citation Check
                      </span>
                      <span className="bg-[#F5F7F7] border border-[#E2E9E6] px-2.5 py-1 rounded text-[#202C2A]">
                        Zero-Hallucination Gate
                      </span>
                      <span className="bg-[#F5F7F7] border border-[#E2E9E6] px-2.5 py-1 rounded text-[#202C2A]">
                        Direct Source Linkage
                      </span>
                    </div>
                  </div>
                  <div className="bg-[#FAFBFB] border border-[#E2E9E6] rounded-md p-4 text-xs font-mono text-[#202C2A] space-y-1">
                    <div className="text-[#66736F]">// Verification Gate</div>
                    <div>&gt; Source Cited: <span className="text-emerald-700">Yes (100%)</span></div>
                    <div>&gt; Refusal Guard: <span className="text-[#167568]">Active</span></div>
                    <div>&gt; Audit Hash: <span className="text-[#167568]">SHA-256 Verified</span></div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* SECTION E: INTERACTIVE REGULATORY SOURCES */}
        <section className="w-full bg-white py-20 px-4 sm:px-6 lg:px-8 border-b border-[#E2E9E6]">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-10">
              <span className="text-[#167568] text-xs font-semibold tracking-widest uppercase">
                DOCUMENT CORPUS
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A] mt-2">
                Supported regulatory sources
              </h2>
              <p className="text-sm text-[#66736F] mt-2">
                Explore document classifications and indexing depth for both regulatory authorities.
              </p>
            </div>

            {/* Source Tab Switcher */}
            <div className="flex justify-center mb-8">
              <div className="inline-flex p-1 bg-[#F5F7F7] border border-[#E2E9E6] rounded-lg">
                <button
                  type="button"
                  onClick={() => setActiveSourceTab("RBI")}
                  className={`px-5 py-2 text-xs font-semibold rounded-md transition-all ${
                    activeSourceTab === "RBI"
                      ? "bg-white text-[#167568] shadow-xs"
                      : "text-[#66736F] hover:text-[#202C2A]"
                  }`}
                >
                  Reserve Bank of India (RBI)
                </button>
                <button
                  type="button"
                  onClick={() => setActiveSourceTab("SEBI")}
                  className={`px-5 py-2 text-xs font-semibold rounded-md transition-all ${
                    activeSourceTab === "SEBI"
                      ? "bg-white text-[#167568] shadow-xs"
                      : "text-[#66736F] hover:text-[#202C2A]"
                  }`}
                >
                  Securities and Exchange Board of India (SEBI)
                </button>
              </div>
            </div>

            {/* Tab Content Display */}
            {activeSourceTab === "RBI" ? (
              <div className="bg-white border border-[#E2E9E6] border-l-4 border-l-[#167568] rounded-r-lg p-6 sm:p-8 shadow-xs animate-in fade-in-50 duration-200">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-md bg-[#167568]/10 text-[#167568] flex items-center justify-center">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-[#202C2A] text-lg">
                      Reserve Bank of India (RBI)
                    </h3>
                    <span className="text-xs text-[#66736F]">
                      Central Bank &amp; Monetary Authority of India
                    </span>
                  </div>
                </div>

                <p className="text-sm text-[#66736F] leading-relaxed mb-6">
                  Comprehensive coverage of statutory circulars, Master Directions, notifications, and policy directives governing scheduled commercial banks, non-banking financial companies (NBFCs), primary dealers, and payment systems.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-[#E2E9E6]">
                  <div className="space-y-1.5">
                    <h4 className="text-xs font-bold text-[#202C2A] uppercase tracking-wider">
                      Document Categories Covered
                    </h4>
                    <ul className="text-xs text-[#66736F] space-y-1">
                      <li>• Master Directions &amp; Master Circulars</li>
                      <li>• Statutory Circulars &amp; Notifications</li>
                      <li>• Prudential Guidelines &amp; Capital Adequacy</li>
                      <li>• KYC / AML / CFT Frameworks</li>
                    </ul>
                  </div>

                  <div className="space-y-1.5">
                    <h4 className="text-xs font-bold text-[#202C2A] uppercase tracking-wider">
                      Key Regulated Entities
                    </h4>
                    <ul className="text-xs text-[#66736F] space-y-1">
                      <li>• Scheduled Commercial Banks &amp; Small Finance Banks</li>
                      <li>• Non-Banking Financial Companies (NBFC-ICC/ML)</li>
                      <li>• Payment Aggregators &amp; Prepaid Instruments</li>
                      <li>• Urban Co-operative Banks</li>
                    </ul>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white border border-[#E2E9E6] border-l-4 border-l-[#167568] rounded-r-lg p-6 sm:p-8 shadow-xs animate-in fade-in-50 duration-200">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-md bg-[#167568]/10 text-[#167568] flex items-center justify-center">
                    <FileSearch className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-[#202C2A] text-lg">
                      Securities and Exchange Board of India (SEBI)
                    </h3>
                    <span className="text-xs text-[#66736F]">
                      Capital Markets &amp; Securities Regulator
                    </span>
                  </div>
                </div>

                <p className="text-sm text-[#66736F] leading-relaxed mb-6">
                  Complete indexing of statutory regulations, circulars, Master Circulars, operational guidelines, and board regulatory orders for listed companies, registered intermediaries, and collective investment vehicles.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-[#E2E9E6]">
                  <div className="space-y-1.5">
                    <h4 className="text-xs font-bold text-[#202C2A] uppercase tracking-wider">
                      Document Categories Covered
                    </h4>
                    <ul className="text-xs text-[#66736F] space-y-1">
                      <li>• SEBI (LODR) Regulations &amp; Amendments</li>
                      <li>• Operational &amp; Intermediary Circulars</li>
                      <li>• Cybersecurity &amp; Cyber Resilience (CSCRF)</li>
                      <li>• Board Orders &amp; Informal Guidance</li>
                    </ul>
                  </div>

                  <div className="space-y-1.5">
                    <h4 className="text-xs font-bold text-[#202C2A] uppercase tracking-wider">
                      Key Regulated Entities
                    </h4>
                    <ul className="text-xs text-[#66736F] space-y-1">
                      <li>• Listed Companies &amp; Issuers</li>
                      <li>• Stock Exchanges, Depositories &amp; Clearing Corps</li>
                      <li>• Mutual Funds &amp; Alternative Investment Funds (AIF)</li>
                      <li>• Stock Brokers &amp; Registered Investment Advisers</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* SECTION F: TRUST SECTION */}
        <section className="w-full bg-[#F5F7F7] py-20 px-4 sm:px-6 lg:px-8 border-b border-[#E2E9E6]">
          <div className="max-w-4xl mx-auto text-center">
            <span className="text-[#167568] text-xs font-semibold tracking-widest uppercase">
              RELIABILITY &amp; INTEGRITY
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A] mt-2 mb-4">
              Responsible AI, traceable answers
            </h2>
            <p className="text-base text-[#66736F] max-w-2xl mx-auto mb-10 leading-relaxed">
              In regulatory analysis, accuracy is essential. TRACECHO operates on an
              evidence-first standard: when retrieved documents do not contain
              sufficient evidence to verify an answer, the system explicitly refuses
              to answer rather than producing hallucinated or speculative claims.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
              <div className="bg-white border border-[#E2E9E6] rounded-lg p-5 flex items-start gap-3 shadow-xs">
                <CheckCircle className="w-5 h-5 text-[#167568] shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-sm text-[#202C2A]">
                    Source-cited answers
                  </h4>
                  <p className="text-xs text-[#66736F] mt-1 leading-relaxed">
                    Every answer is tied to specific regulatory circulars, master
                    directions, and paragraph numbers.
                  </p>
                </div>
              </div>

              <div className="bg-white border border-[#E2E9E6] rounded-lg p-5 flex items-start gap-3 shadow-xs">
                <CheckCircle className="w-5 h-5 text-[#167568] shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-sm text-[#202C2A]">
                    Transparent evidence chain
                  </h4>
                  <p className="text-xs text-[#66736F] mt-1 leading-relaxed">
                    Inspect original text passages, document metadata, and retrieval
                    lineage behind every insight.
                  </p>
                </div>
              </div>

              <div className="bg-white border border-[#E2E9E6] rounded-lg p-5 flex items-start gap-3 shadow-xs">
                <CheckCircle className="w-5 h-5 text-[#167568] shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-sm text-[#202C2A]">
                    Clear refusal when unsupported
                  </h4>
                  <p className="text-xs text-[#66736F] mt-1 leading-relaxed">
                    The platform refuses unsupported inquiries rather than
                    fabricating regulatory advice.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION FAQ ACCORDION */}
        <section className="w-full bg-white py-20 px-4 sm:px-6 lg:px-8 border-b border-[#E2E9E6]">
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-12">
              <span className="text-[#167568] text-xs font-semibold tracking-widest uppercase">
                FREQUENTLY ASKED QUESTIONS
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A] mt-2">
                Frequently asked questions
              </h2>
              <p className="text-sm text-[#66736F] mt-2">
                Learn how TRACECHO retrieves, verifies, and cites regulatory information.
              </p>
            </div>

            <div className="space-y-3">
              {FAQ_ITEMS.map((item, index) => {
                const isOpen = expandedFaq === index;
                return (
                  <div
                    key={index}
                    className="border border-[#E2E9E6] rounded-lg overflow-hidden transition-all"
                  >
                    <button
                      type="button"
                      onClick={() => setExpandedFaq(isOpen ? null : index)}
                      className="w-full py-4 px-5 text-left flex items-center justify-between gap-4 bg-white hover:bg-[#FAFBFB] transition-colors"
                      aria-expanded={isOpen}
                    >
                      <span className="text-sm font-semibold text-[#202C2A]">
                        {item.question}
                      </span>
                      <ChevronDown
                        className={`w-4 h-4 text-[#66736F] shrink-0 transition-transform duration-200 ${
                          isOpen ? "rotate-180 text-[#167568]" : ""
                        }`}
                      />
                    </button>
                    {isOpen && (
                      <div className="px-5 pb-5 pt-1 text-sm text-[#66736F] bg-white leading-relaxed border-t border-[#E2E9E6]/60 animate-in fade-in-50 duration-150">
                        {item.answer}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* SECTION G: CTA BANNER */}
        <section className="w-full bg-white border-b border-[#E2E9E6] py-16 px-4 sm:px-6 lg:px-8 text-center">
          <div className="max-w-2xl mx-auto flex flex-col items-center">
            <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A]">
              Ready to explore regulatory intelligence?
            </h2>
            <p className="text-[#66736F] text-base mt-2 mb-8">
              Sign up to access the full platform, live document search, and interactive AI assistant.
            </p>
            <Button
              asChild
              className="bg-[#167568] hover:bg-[#125E55] text-white font-medium px-8 py-3 rounded-md h-auto transition-all shadow-xs hover:shadow hover:-translate-y-0.5"
            >
              <Link to="/signup" className="flex items-center gap-2">
                <span>Get Started with TRACECHO</span>
                <ChevronRight className="w-4 h-4" />
              </Link>
            </Button>
          </div>
        </section>
      </div>

      {/* CITATION INSPECTION MODAL */}
      {activeCitationModal && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs animate-in fade-in-50 duration-150"
        >
          <div className="bg-white rounded-lg border border-[#E2E9E6] max-w-xl w-full p-6 shadow-xl relative animate-in zoom-in-95 duration-150">
            <button
              type="button"
              onClick={() => setActiveCitationModal(null)}
              className="absolute right-4 top-4 text-[#66736F] hover:text-[#202C2A] p-1 rounded-md hover:bg-[#F5F7F7] transition-colors"
              aria-label="Close dialog"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-2 mb-3">
              <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-[#167568]/10 text-[#167568]">
                {activeCitationModal.regulator} Official Citation
              </span>
              <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 text-emerald-800 border border-emerald-200">
                Confidence: {activeCitationModal.confidence}
              </span>
            </div>

            <h3 className="text-base font-bold text-[#202C2A] mb-1">
              {activeCitationModal.title}
            </h3>
            <div className="text-xs font-mono text-[#167568] mb-3">
              {activeCitationModal.circularNo}
            </div>

            <div className="grid grid-cols-2 gap-3 py-3 border-y border-[#E2E9E6] text-xs text-[#66736F] mb-4">
              <div>
                <span className="font-medium text-[#202C2A]">Issuing Department:</span>
                <p className="mt-0.5">{activeCitationModal.department}</p>
              </div>
              <div>
                <span className="font-medium text-[#202C2A]">Gazetted Date:</span>
                <p className="mt-0.5">{activeCitationModal.date}</p>
              </div>
            </div>

            <div className="mb-4">
              <span className="text-xs font-bold text-[#202C2A] block mb-1">
                Extracted Clause / Verbatim Excerpt:
              </span>
              <div className="p-3 bg-[#F5F7F7] rounded border border-[#E2E9E6] text-xs text-[#202C2A] font-serif leading-relaxed">
                &ldquo;{activeCitationModal.excerpt}&rdquo;
              </div>
              <p className="text-[11px] text-[#66736F] mt-1 italic">
                Reference: {activeCitationModal.section}
              </p>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setActiveCitationModal(null)}
                className="text-xs border-[#E2E9E6]"
              >
                Close Preview
              </Button>
              <Button
                size="sm"
                asChild
                className="bg-[#167568] hover:bg-[#125E55] text-white text-xs"
              >
                <Link to="/app/explorer">Explore Document in App</Link>
              </Button>
            </div>
          </div>
        </div>
      )}
    </PublicLayout>
  );
}
