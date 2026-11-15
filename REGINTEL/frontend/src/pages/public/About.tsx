import React from "react";
import { Link } from "react-router-dom";
import PublicLayout from "@/components/layout/PublicLayout";
import { Button } from "@/components/ui/Button";
import {
  AlertCircle,
  Clock,
  Database,
  Search,
  FileCheck,
  ShieldCheck,
  Check,
  ArrowRight,
  ExternalLink,
} from "lucide-react";

export default function About() {
  return (
    <PublicLayout>
      {/* A. Page Header */}
      <section className="bg-white border-b border-[#E2E9E6] py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-xs font-semibold tracking-wider text-[#167568] uppercase mb-2">
            ABOUT TRACECHO
          </p>
          <h1 className="text-3xl sm:text-4xl font-bold text-[#202C2A] tracking-tight">
            AI-powered regulatory intelligence
          </h1>
          <p className="mt-3 text-base sm:text-lg text-[#66736F] max-w-3xl leading-relaxed">
            Our mission is to make regulatory compliance and research accessible, transparent, and verifiable for financial institutions, compliance teams, and legal professionals navigating complex regulatory frameworks.
          </p>
        </div>
      </section>

      {/* B. The Problem */}
      <section className="bg-white border-b border-[#E2E9E6] py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
            {/* Left Column */}
            <div>
              <p className="text-xs font-semibold tracking-wider text-[#167568] uppercase mb-2">
                THE CHALLENGE
              </p>
              <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A] tracking-tight">
                The regulatory complexity challenge
              </h2>
              <p className="mt-4 text-[#66736F] leading-relaxed">
                Financial institutions and regulated entities face an ever-expanding volume of regulatory directives across banking and capital markets. New circulars, notifications, and amendments are published continuously, creating significant compliance risk when teams must locate, cross-reference, and interpret interdependent guidelines across disparate publications.
              </p>
              <p className="mt-3 text-[#66736F] leading-relaxed">
                Traditional keyword searches struggle with legacy document structures, while standard language models risk hallucinations when queried on critical legal boundaries. Compliance professionals need precise, attributable information with unassailable source provenance.
              </p>
            </div>

            {/* Right Column */}
            <div className="space-y-4">
              <div className="flex items-start gap-4 p-5 rounded-lg border border-[#E2E9E6] bg-white">
                <div className="p-2 rounded-md bg-[#167568]/10 text-[#167568] shrink-0">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-[#202C2A] text-base">
                    Expanding Document Volumes
                  </h3>
                  <p className="mt-1 text-sm text-[#66736F] leading-relaxed">
                    Thousands of pages of master directions, circulars, and notifications make comprehensive tracking across multiple regulatory bodies arduous and resource-intensive.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-5 rounded-lg border border-[#E2E9E6] bg-white">
                <div className="p-2 rounded-md bg-[#167568]/10 text-[#167568] shrink-0">
                  <Clock className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-[#202C2A] text-base">
                    Frequent Amendments & Updates
                  </h3>
                  <p className="mt-1 text-sm text-[#66736F] leading-relaxed">
                    Regulatory notices frequently supersede, amend, or clarify previous directives, making it difficult to determine current applicable mandates in historical records.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-5 rounded-lg border border-[#E2E9E6] bg-white">
                <div className="p-2 rounded-md bg-[#167568]/10 text-[#167568] shrink-0">
                  <AlertCircle className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-[#202C2A] text-base">
                    Search Difficulty & Compliance Risk
                  </h3>
                  <p className="mt-1 text-sm text-[#66736F] leading-relaxed">
                    Complex legal clauses and unstandardized PDF formatting cause conventional search tools to miss critical obligations, amplifying institutional compliance risk.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* C. Our Approach */}
      <section className="bg-[#F5F7F7] border-b border-[#E2E9E6] py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <p className="text-xs font-semibold tracking-wider text-[#167568] uppercase mb-2">
              METHODOLOGY
            </p>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A] tracking-tight">
              Our approach
            </h2>
            <p className="mt-3 text-[#66736F] text-sm sm:text-base">
              Engineered specifically for regulatory precision, combining verified retrieval with strict factual grounding.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white border border-[#E2E9E6] rounded-lg p-6">
              <div className="w-9 h-9 rounded-md bg-[#167568]/10 text-[#167568] flex items-center justify-center mb-4">
                <Search className="w-4 h-4" />
              </div>
              <h3 className="text-base font-semibold text-[#202C2A]">
                Retrieval-Augmented Generation
              </h3>
              <p className="mt-2 text-sm text-[#66736F] leading-relaxed">
                Connects modern language models directly to authoritative regulatory archives so answers are generated strictly from indexed texts. This prevents models from guessing and guarantees that every statement reflects official documentation.
              </p>
            </div>

            <div className="bg-white border border-[#E2E9E6] rounded-lg p-6">
              <div className="w-9 h-9 rounded-md bg-[#167568]/10 text-[#167568] flex items-center justify-center mb-4">
                <Database className="w-4 h-4" />
              </div>
              <h3 className="text-base font-semibold text-[#202C2A]">
                Hybrid document search
              </h3>
              <p className="mt-2 text-sm text-[#66736F] leading-relaxed">
                Combines BM25 exact keyword matching with vector semantic search to capture both specific circular numbers and conceptual queries. This dual approach ensures precise statutory clauses and broader thematic policies are retrieved equally well.
              </p>
            </div>

            <div className="bg-white border border-[#E2E9E6] rounded-lg p-6">
              <div className="w-9 h-9 rounded-md bg-[#167568]/10 text-[#167568] flex items-center justify-center mb-4">
                <FileCheck className="w-4 h-4" />
              </div>
              <h3 className="text-base font-semibold text-[#202C2A]">
                Evidence-first answers
              </h3>
              <p className="mt-2 text-sm text-[#66736F] leading-relaxed">
                Every generated response includes direct citations, paragraph quotes, and document references. If the retrieved evidence is insufficient to address a query, the system explicitly declines rather than extrapolating unsupported claims.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* D. What TRACECHO Covers */}
      <section className="bg-white border-b border-[#E2E9E6] py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <p className="text-xs font-semibold tracking-wider text-[#167568] uppercase mb-2">
              REGULATORY SCOPE
            </p>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A] tracking-tight">
              What TRACECHO covers
            </h2>
            <p className="mt-3 text-[#66736F] text-sm sm:text-base">
              Systematic indexing of primary publications issued by India's apex financial and market authorities.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* RBI Card */}
            <div className="bg-white border border-[#E2E9E6] rounded-lg p-6">
              <div className="flex items-center justify-between pb-4 border-b border-[#E2E9E6] mb-4">
                <div>
                  <h3 className="text-lg font-bold text-[#202C2A]">RBI Corpus</h3>
                  <p className="text-xs text-[#66736F]">Reserve Bank of India</p>
                </div>
                <span className="text-xs font-medium px-2.5 py-1 rounded bg-[#167568]/10 text-[#167568]">
                  Banking & NBFCs
                </span>
              </div>
              <ul className="space-y-3">
                {[
                  "Master Directions across all banking sectors",
                  "Regulatory circulars and operational notifications",
                  "Guidelines on digital lending, KYC, and AML",
                  "Statutory clarifications and press releases",
                  "Departmental notifications and instructions",
                ].map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-sm text-[#66736F]">
                    <Check className="w-4 h-4 text-[#167568] shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* SEBI Card */}
            <div className="bg-white border border-[#E2E9E6] rounded-lg p-6">
              <div className="flex items-center justify-between pb-4 border-b border-[#E2E9E6] mb-4">
                <div>
                  <h3 className="text-lg font-bold text-[#202C2A]">SEBI Corpus</h3>
                  <p className="text-xs text-[#66736F]">Securities and Exchange Board of India</p>
                </div>
                <span className="text-xs font-medium px-2.5 py-1 rounded bg-[#167568]/10 text-[#167568]">
                  Capital Markets
                </span>
              </div>
              <ul className="space-y-3">
                {[
                  "Master Circulars for intermediaries and stock exchanges",
                  "Operational circulars and procedural directions",
                  "Securities market regulations and amendments",
                  "Guidance notes, FAQs, and interpretive letters",
                  "Selected regulatory and compliance directives",
                ].map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-sm text-[#66736F]">
                    <Check className="w-4 h-4 text-[#167568] shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* E. Our Commitment */}
      <section className="bg-[#F5F7F7] border-b border-[#E2E9E6] py-16">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-xs font-semibold tracking-wider text-[#167568] uppercase mb-2">
            INTEGRITY & STANDARDS
          </p>
          <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A] tracking-tight mb-8">
            Our commitment
          </h2>

          <div className="space-y-6 text-[#66736F] leading-relaxed text-left sm:text-center">
            <div className="bg-white border border-[#E2E9E6] rounded-lg p-6 text-left">
              <h3 className="font-semibold text-[#202C2A] text-base mb-1">
                Transparency
              </h3>
              <p className="text-sm">
                Every answer generated by TRACECHO links directly to official source documents with identifiable circular numbers, publication dates, and specific paragraph citations. We believe regulatory technology must never be a black box.
              </p>
            </div>

            <div className="bg-white border border-[#E2E9E6] rounded-lg p-6 text-left">
              <h3 className="font-semibold text-[#202C2A] text-base mb-1">
                Accuracy
              </h3>
              <p className="text-sm">
                Compliance decisions require uncompromised fidelity to published texts. When available evidence is insufficient, ambiguous, or out of scope, the system explicitly declines to answer rather than providing speculative guidance.
              </p>
            </div>

            <div className="bg-white border border-[#E2E9E6] rounded-lg p-6 text-left">
              <h3 className="font-semibold text-[#202C2A] text-base mb-1">
                Trust
              </h3>
              <p className="text-sm">
                We enforce strict guardrails against fabricated regulatory content. Answers reflect only authentic publications from recognized authorities, giving compliance officers and legal professionals confidence in every review.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* F. CTA */}
      <section className="bg-white py-16">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A] tracking-tight">
            Ready to explore regulatory intelligence?
          </h2>
          <p className="mt-3 text-[#66736F] text-base">
            Search, analyze, and verify regulatory requirements with source-backed precision.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button
              size="lg"
              className="bg-[#167568] hover:bg-[#125E55] text-white w-full sm:w-auto"
              asChild
            >
              <Link to="/app">
                Explore the platform <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-[#E2E9E6] text-[#202C2A] hover:bg-[#F5F7F7] w-full sm:w-auto"
              asChild
            >
              <Link to="/contact">Contact us</Link>
            </Button>
          </div>
        </div>
      </section>
    </PublicLayout>
  );
}