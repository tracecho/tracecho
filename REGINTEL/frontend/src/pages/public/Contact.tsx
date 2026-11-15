import React, { useState } from "react";
import PublicLayout from "@/components/layout/PublicLayout";
import { Button } from "@/components/ui/Button";
import { postContactSubmission, ContactSubmissionResponse } from "@/lib/api";
import {
  Mail,
  MapPin,
  MessageCircle,
  CheckCircle,
  Send,
  Building2,
  Loader2,
  AlertCircle,
  ShieldCheck,
} from "lucide-react";

const enquiryOptions = [
  "General Enquiry",
  "Platform Access",
  "Enterprise Solutions",
  "Technical Question",
  "Partnership",
];

export default function Contact() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [organization, setOrganization] = useState("");
  const [enquiryType, setEnquiryType] = useState("");
  const [message, setMessage] = useState("");
  const [honeypot, setHoneypot] = useState("");

  const [hasAttemptedSubmit, setHasAttemptedSubmit] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [submissionResult, setSubmissionResult] = useState<ContactSubmissionResponse | null>(null);

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!name.trim()) {
      newErrors.name = "Full Name is required.";
    } else if (name.trim().length < 2) {
      newErrors.name = "Name must be at least 2 characters.";
    }

    if (!email.trim()) {
      newErrors.email = "Work Email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      newErrors.email = "Please enter a valid work email address.";
    }

    if (!organization.trim()) {
      newErrors.organization = "Organization / Firm name is required.";
    } else if (organization.trim().length < 2) {
      newErrors.organization = "Organization must be at least 2 characters.";
    }

    if (!enquiryType) {
      newErrors.enquiryType = "Please select an enquiry type.";
    }

    if (!message.trim()) {
      newErrors.message = "Message is required.";
    } else if (message.trim().length < 20) {
      newErrors.message = "Message must be at least 20 characters in length.";
    }

    return newErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting || submissionResult) return;

    setHasAttemptedSubmit(true);
    setApiError(null);

    const validationErrors = validate();
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await postContactSubmission({
        name: name.trim(),
        email: email.trim().toLowerCase(),
        organization: organization.trim(),
        enquiry_type: enquiryType,
        message: message.trim(),
        honeypot: honeypot.trim() || undefined,
      });

      setSubmissionResult(response);
    } catch (err: any) {
      const detail =
        err.response?.data?.detail ||
        (typeof err.response?.data?.detail === "string"
          ? err.response.data.detail
          : "Failed to submit your enquiry. Please check your network connection and try again.");
      setApiError(detail);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setName("");
    setEmail("");
    setOrganization("");
    setEnquiryType("");
    setMessage("");
    setHoneypot("");
    setHasAttemptedSubmit(false);
    setErrors({});
    setApiError(null);
    setSubmissionResult(null);
  };

  return (
    <PublicLayout>
      {/* A. Page Header */}
      <section className="bg-white border-b border-[#E2E9E6] py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-xs font-semibold tracking-wider text-[#167568] uppercase mb-2">
            CONTACT TRACECHO
          </p>
          <h1 className="text-3xl sm:text-4xl font-bold text-[#202C2A] tracking-tight">
            Get in touch
          </h1>
          <p className="mt-3 text-base sm:text-lg text-[#66736F] max-w-3xl leading-relaxed">
            Have a question about TRACECHO or interested in deploying regulatory intelligence for your organization? We would like to hear from you.
          </p>
        </div>
      </section>

      {/* B. Two-Column Layout */}
      <section className="py-16 bg-[#F5F7F7]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
            {/* Left Column (40%) — Contact Context */}
            <div className="lg:col-span-5 space-y-6">
              <div>
                <p className="text-xs font-semibold tracking-wider text-[#167568] uppercase mb-2">
                  COMMUNICATION CHANNELS
                </p>
                <h2 className="text-2xl font-bold text-[#202C2A] tracking-tight">
                  Business enquiries
                </h2>
                <p className="mt-2 text-sm text-[#66736F] leading-relaxed">
                  We collaborate with financial institutions, regulatory compliance practitioners, and technology partners.
                </p>
              </div>

              <div className="space-y-4">
                <div className="flex items-start gap-4 p-5 rounded-lg border border-[#E2E9E6] bg-white shadow-xs">
                  <div className="p-2.5 rounded-md bg-[#167568]/10 text-[#167568] shrink-0">
                    <MapPin className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#202C2A] text-sm sm:text-base">
                      Platform Operations
                    </h3>
                    <p className="mt-1 text-xs sm:text-sm text-[#66736F] leading-relaxed">
                      TRACECHO is a regulatory intelligence platform engineered for Indian financial compliance environments (RBI and SEBI).
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-5 rounded-lg border border-[#E2E9E6] bg-white shadow-xs">
                  <div className="p-2.5 rounded-md bg-[#167568]/10 text-[#167568] shrink-0">
                    <Mail className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#202C2A] text-sm sm:text-base">
                      Direct Inquiries
                    </h3>
                    <p className="mt-1 text-xs sm:text-sm text-[#66736F] leading-relaxed">
                      Submit an enquiry via this form to directly reach our research and compliance engineering specialists.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-5 rounded-lg border border-[#E2E9E6] bg-white shadow-xs">
                  <div className="p-2.5 rounded-md bg-[#167568]/10 text-[#167568] shrink-0">
                    <MessageCircle className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#202C2A] text-sm sm:text-base">
                      Advisory &amp; Feedback
                    </h3>
                    <p className="mt-1 text-xs sm:text-sm text-[#66736F] leading-relaxed">
                      We actively engage with compliance officers, internal audit leads, and risk managers to tailor our regulatory corpus.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-5 rounded-lg border border-[#E2E9E6] bg-white shadow-xs">
                  <div className="p-2.5 rounded-md bg-[#167568]/10 text-[#167568] shrink-0">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#202C2A] text-sm sm:text-base">
                      Institutional Deployment
                    </h3>
                    <p className="mt-1 text-xs sm:text-sm text-[#66736F] leading-relaxed">
                      Tailored enterprise RAG and internal regulatory intelligence solutions for banks, NBFCs, and financial market intermediaries.
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-white border border-[#E2E9E6] flex items-center gap-3">
                <ShieldCheck className="w-5 h-5 text-[#167568] shrink-0" />
                <p className="text-xs sm:text-sm text-[#66736F] leading-relaxed">
                  Every submission is logged securely with an auditable reference code.
                </p>
              </div>
            </div>

            {/* Right Column (60%) — Contact Form */}
            <div className="lg:col-span-7">
              <div className="bg-white border border-[#E2E9E6] rounded-[8px] p-8 shadow-xs">
                {submissionResult ? (
                  <div className="py-8 text-center space-y-4 animate-in fade-in-50 duration-200">
                    <div className="w-14 h-14 rounded-full bg-emerald-50 text-emerald-600 mx-auto flex items-center justify-center border border-emerald-200">
                      <CheckCircle className="w-8 h-8" />
                    </div>
                    <h3 className="text-2xl font-bold text-[#202C2A]">
                      Enquiry Received
                    </h3>
                    <p className="text-sm text-[#66736F] max-w-md mx-auto leading-relaxed">
                      {submissionResult.message}
                    </p>

                    {submissionResult.submission_id && submissionResult.submission_id !== "bot-filtered" && (
                      <div className="inline-block bg-[#F5F7F7] border border-[#E2E9E6] px-4 py-2 rounded-md text-xs font-mono text-[#202C2A] my-2">
                        Reference ID: <span className="text-[#167568] font-bold">{submissionResult.submission_id}</span>
                      </div>
                    )}

                    <div className="pt-2 text-xs text-[#66736F] max-w-md mx-auto">
                      {submissionResult.email_delivered ? (
                        <p className="text-emerald-700">
                          A confirmation receipt has been dispatched to your email address.
                        </p>
                      ) : (
                        <p>
                          Your enquiry is recorded in our system. Our team will contact you directly via your work email.
                        </p>
                      )}
                    </div>

                    <div className="pt-4">
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={handleReset}
                        className="text-sm border-[#E2E9E6] hover:bg-[#F5F7F7]"
                      >
                        Submit another enquiry
                      </Button>
                    </div>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} noValidate className="space-y-5">
                    <div>
                      <h3 className="text-xl font-bold text-[#202C2A]">
                        Send an Enquiry
                      </h3>
                      <p className="text-xs text-[#66736F] mt-1">
                        All fields are required. Your request will be directly dispatched to our regulatory intelligence team.
                      </p>
                    </div>

                    {/* API Error Notification */}
                    {apiError && (
                      <div className="p-3.5 bg-red-50 border border-red-200 rounded-md text-xs text-red-700 flex items-start gap-2.5">
                        <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                        <div>
                          <strong className="font-semibold">Submission Error:</strong> {apiError}
                        </div>
                      </div>
                    )}

                    {/* Spam Honeypot Field (invisible to genuine users) */}
                    <div className="hidden" aria-hidden="true" style={{ display: "none" }}>
                      <label htmlFor="b_hp_field">Do not fill this</label>
                      <input
                        id="b_hp_field"
                        type="text"
                        name="b_hp_field"
                        tabIndex={-1}
                        autoComplete="off"
                        value={honeypot}
                        onChange={(e) => setHoneypot(e.target.value)}
                      />
                    </div>

                    {/* Name */}
                    <div>
                      <label
                        htmlFor="name"
                        className="block text-xs font-semibold text-[#202C2A] uppercase tracking-wider mb-1.5"
                      >
                        Full Name
                      </label>
                      <input
                        id="name"
                        type="text"
                        disabled={isSubmitting}
                        value={name}
                        onChange={(e) => {
                          setName(e.target.value);
                          if (hasAttemptedSubmit && errors.name) {
                            setErrors((prev) => ({ ...prev, name: "" }));
                          }
                        }}
                        placeholder="e.g. Aditi Sharma"
                        className="w-full rounded-md border border-[#E2E9E6] px-3.5 py-2.5 text-sm text-[#202C2A] placeholder:text-[#66736F]/50 focus:outline-none focus:ring-2 focus:ring-[#167568] focus:border-transparent bg-white disabled:bg-[#F5F7F7] disabled:text-[#66736F]"
                      />
                      {hasAttemptedSubmit && errors.name && (
                        <p className="mt-1.5 text-xs text-red-600">
                          {errors.name}
                        </p>
                      )}
                    </div>

                    {/* Email */}
                    <div>
                      <label
                        htmlFor="email"
                        className="block text-xs font-semibold text-[#202C2A] uppercase tracking-wider mb-1.5"
                      >
                        Work Email
                      </label>
                      <input
                        id="email"
                        type="email"
                        disabled={isSubmitting}
                        value={email}
                        onChange={(e) => {
                          setEmail(e.target.value);
                          if (hasAttemptedSubmit && errors.email) {
                            setErrors((prev) => ({ ...prev, email: "" }));
                          }
                        }}
                        placeholder="aditi.sharma@institution.com"
                        className="w-full rounded-md border border-[#E2E9E6] px-3.5 py-2.5 text-sm text-[#202C2A] placeholder:text-[#66736F]/50 focus:outline-none focus:ring-2 focus:ring-[#167568] focus:border-transparent bg-white disabled:bg-[#F5F7F7] disabled:text-[#66736F]"
                      />
                      {hasAttemptedSubmit && errors.email && (
                        <p className="mt-1.5 text-xs text-red-600">
                          {errors.email}
                        </p>
                      )}
                    </div>

                    {/* Organization */}
                    <div>
                      <label
                        htmlFor="organization"
                        className="block text-xs font-semibold text-[#202C2A] uppercase tracking-wider mb-1.5"
                      >
                        Organization / Firm
                      </label>
                      <input
                        id="organization"
                        type="text"
                        disabled={isSubmitting}
                        value={organization}
                        onChange={(e) => {
                          setOrganization(e.target.value);
                          if (hasAttemptedSubmit && errors.organization) {
                            setErrors((prev) => ({ ...prev, organization: "" }));
                          }
                        }}
                        placeholder="e.g. National Capital Bank"
                        className="w-full rounded-md border border-[#E2E9E6] px-3.5 py-2.5 text-sm text-[#202C2A] placeholder:text-[#66736F]/50 focus:outline-none focus:ring-2 focus:ring-[#167568] focus:border-transparent bg-white disabled:bg-[#F5F7F7] disabled:text-[#66736F]"
                      />
                      {hasAttemptedSubmit && errors.organization && (
                        <p className="mt-1.5 text-xs text-red-600">
                          {errors.organization}
                        </p>
                      )}
                    </div>

                    {/* Enquiry Type */}
                    <div>
                      <label
                        htmlFor="enquiryType"
                        className="block text-xs font-semibold text-[#202C2A] uppercase tracking-wider mb-1.5"
                      >
                        Enquiry Type
                      </label>
                      <select
                        id="enquiryType"
                        disabled={isSubmitting}
                        value={enquiryType}
                        onChange={(e) => {
                          setEnquiryType(e.target.value);
                          if (hasAttemptedSubmit && errors.enquiryType) {
                            setErrors((prev) => ({ ...prev, enquiryType: "" }));
                          }
                        }}
                        className="w-full rounded-md border border-[#E2E9E6] px-3.5 py-2.5 text-sm text-[#202C2A] focus:outline-none focus:ring-2 focus:ring-[#167568] focus:border-transparent bg-white disabled:bg-[#F5F7F7] disabled:text-[#66736F]"
                      >
                        <option value="">Select an enquiry type</option>
                        {enquiryOptions.map((opt) => (
                          <option key={opt} value={opt}>
                            {opt}
                          </option>
                        ))}
                      </select>
                      {hasAttemptedSubmit && errors.enquiryType && (
                        <p className="mt-1.5 text-xs text-red-600">
                          {errors.enquiryType}
                        </p>
                      )}
                    </div>

                    {/* Message */}
                    <div>
                      <label
                        htmlFor="message"
                        className="block text-xs font-semibold text-[#202C2A] uppercase tracking-wider mb-1.5"
                      >
                        Message (minimum 20 characters)
                      </label>
                      <textarea
                        id="message"
                        rows={5}
                        disabled={isSubmitting}
                        value={message}
                        onChange={(e) => {
                          setMessage(e.target.value);
                          if (hasAttemptedSubmit && errors.message) {
                            setErrors((prev) => ({ ...prev, message: "" }));
                          }
                        }}
                        placeholder="Please describe your requirements, regulatory questions, or organization scope..."
                        className="w-full rounded-md border border-[#E2E9E6] px-3.5 py-2.5 text-sm text-[#202C2A] placeholder:text-[#66736F]/50 focus:outline-none focus:ring-2 focus:ring-[#167568] focus:border-transparent bg-white resize-y disabled:bg-[#F5F7F7] disabled:text-[#66736F]"
                      />
                      <div className="flex justify-between items-center mt-1">
                        {hasAttemptedSubmit && errors.message ? (
                          <p className="text-xs text-red-600">{errors.message}</p>
                        ) : (
                          <span className="text-[11px] text-[#66736F]">
                            Minimum 20 characters required.
                          </span>
                        )}
                        <span className="text-[11px] text-[#66736F] font-mono">
                          {message.length} chars
                        </span>
                      </div>
                    </div>

                    {/* Submit Button */}
                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full bg-[#167568] hover:bg-[#125E55] text-white py-2.5 h-auto text-sm font-semibold rounded-md shadow-xs flex items-center justify-center gap-2 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                      {isSubmitting ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Submitting Enquiry...
                        </>
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          Submit Enquiry
                        </>
                      )}
                    </Button>
                  </form>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>
    </PublicLayout>
  );
}
