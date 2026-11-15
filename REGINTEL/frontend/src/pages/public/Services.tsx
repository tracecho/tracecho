import React from "react";
import { Link } from "react-router-dom";
import PublicLayout from "@/components/layout/PublicLayout";
import { Button } from "@/components/ui/Button";
import {
  Building2,
  Briefcase,
  Cpu,
  Shield,
  Scale,
  BookOpen,
  Search,
  MessageSquare,
  Database,
  FileText,
  Bot,
  Settings,
  ArrowRight,
} from "lucide-react";

const industries = [
  {
    icon: Building2,
    label: "Banks & Financial Institutions",
  },
  {
    icon: Briefcase,
    label: "NBFCs",
  },
  {
    icon: Cpu,
    label: "Fintech Companies",
  },
  {
    icon: Shield,
    label: "Insurance Organizations",
  },
  {
    icon: Scale,
    label: "Legal & Compliance Teams",
  },
  {
    icon: BookOpen,
    label: "Financial Research",
  },
];

const serviceCards = [
  {
    icon: Search,
    title: "Regulatory Intelligence",
    description:
      "Search and understand regulatory circulars, notifications and guidelines from RBI and SEBI.",
  },
  {
    icon: MessageSquare,
    title: "AI-Powered Research",
    description:
      "Source-backed question answering over regulatory documents using retrieval-augmented generation.",
  },
  {
    icon: Database,
    title: "Enterprise RAG Solutions",
    description:
      "Design and implementation of retrieval-augmented generation systems for enterprise knowledge bases.",
  },
  {
    icon: FileText,
    title: "Document Intelligence",
    description:
      "Structured discovery, retrieval and analysis of complex regulatory and compliance documents.",
  },
  {
    icon: Bot,
    title: "Compliance Knowledge Assistants",
    description:
      "Custom AI assistants for internal regulatory and compliance knowledge workflows.",
  },
  {
    icon: Settings,
    title: "Custom AI Integration",
    description:
      "Tailored AI and knowledge-management solutions for your organization's specific requirements.",
  },
];

export default function Services() {
  return (
    <PublicLayout>
      {/* A. Page Header */}
      <section className="bg-white border-b border-[#E2E9E6] py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-xs font-semibold tracking-wider text-[#167568] uppercase mb-2">
            SERVICES
          </p>
          <h1 className="text-3xl sm:text-4xl font-bold text-[#202C2A] tracking-tight">
            What TRACECHO offers
          </h1>
          <p className="mt-3 text-base sm:text-lg text-[#66736F] max-w-3xl leading-relaxed">
            Helping financial institutions, compliance teams and regulatory professionals navigate regulatory complexity.
          </p>
        </div>
      </section>

      {/* B. Who We Serve (Industry Tiles) */}
      <section className="bg-[#F5F7F7] border-b border-[#E2E9E6] py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-10">
            <p className="text-xs font-semibold tracking-wider text-[#167568] uppercase mb-2">
              SECTORS
            </p>
            <h2 className="text-2xl font-bold text-[#202C2A] tracking-tight">
              Industries we serve
            </h2>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {industries.map((ind, idx) => {
              const Icon = ind.icon;
              return (
                <div
                  key={idx}
                  className="bg-white border border-[#E2E9E6] rounded-lg p-5 flex flex-col items-center justify-center text-center shadow-xs transition-shadow hover:shadow-sm"
                >
                  <div className="w-10 h-10 rounded-md bg-[#167568]/10 text-[#167568] flex items-center justify-center mb-3">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-xs sm:text-sm font-medium text-[#202C2A]">
                    {ind.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* C. Service Offerings */}
      <section className="bg-white border-b border-[#E2E9E6] py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-12">
            <p className="text-xs font-semibold tracking-wider text-[#167568] uppercase mb-2">
              SOLUTIONS
            </p>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#202C2A] tracking-tight">
              Comprehensive regulatory capabilities
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {serviceCards.map((service, idx) => {
              const Icon = service.icon;
              return (
                <div
                  key={idx}
                  className="bg-white border border-[#E2E9E6] border-l-4 border-l-[#167568] rounded-r-lg p-6 flex flex-col justify-between shadow-xs transition-all hover:shadow-sm"
                >
                  <div>
                    <div className="flex items-center gap-3 mb-3">
                      <div className="text-[#167568]">
                        <Icon className="h-5 w-5" />
                      </div>
                      <h3 className="font-semibold text-base text-[#202C2A]">
                        {service.title}
                      </h3>
                    </div>
                    <p className="text-sm text-[#66736F] leading-relaxed">
                      {service.description}
                    </p>
                  </div>

                  <div className="mt-5 pt-4 border-t border-[#E2E9E6]/60">
                    <Link
                      to="/contact"
                      className="inline-flex items-center text-sm font-medium text-[#167568] hover:text-[#125E55] transition-colors"
                    >
                      Learn more <ArrowRight className="ml-1 w-4 h-4" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* D. CTA */}
      <section className="bg-[#F5F7F7] py-16">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-2xl sm:text-3xl font-bold text-[#202C2A] tracking-tight">
            Interested in TRACECHO for your organization?
          </h3>
          <p className="mt-3 text-base text-[#66736F]">
            Discover how tailored regulatory intelligence and enterprise RAG workflows can support your compliance mandate.
          </p>
          <div className="mt-8">
            <Button
              size="lg"
              className="bg-[#167568] hover:bg-[#125E55] text-white"
              asChild
            >
              <Link to="/contact">Get in touch</Link>
            </Button>
          </div>
        </div>
      </section>
    </PublicLayout>
  );
}