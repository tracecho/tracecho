import React from "react";
import { Link } from "react-router-dom";
import { AlertCircle, ArrowLeft, LayoutDashboard, ShieldCheck } from "lucide-react";

export default function NotFound() {
  return (
    <div
      className="min-h-screen flex items-center justify-center p-4 bg-[#F5F7F7]"
    >
      <div
        className="w-full max-w-md text-center rounded-lg shadow-sm bg-white border border-[#E2E9E6] p-8"
      >
        {/* Brand header */}
        <div className="flex items-center justify-center space-x-2.5 mb-6">
          <div
            className="w-8 h-8 rounded-md flex items-center justify-center text-white bg-[#167568]"
          >
            <ShieldCheck className="w-5 h-5" />
          </div>
          <span
            className="font-bold text-lg tracking-tight text-[#202C2A]"
          >
            TRACECHO
          </span>
        </div>

        {/* 404 Badge & Icon */}
        <div className="my-4 flex flex-col items-center">
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center mb-3 bg-[#F5F7F7] border border-[#E2E9E6]"
          >
            <AlertCircle className="w-8 h-8 text-[#167568]" />
          </div>
          <span
            className="text-4xl font-extrabold tracking-tight text-[#202C2A]"
          >
            404
          </span>
        </div>

        <h2
          className="text-xl font-bold tracking-tight mb-2 text-[#202C2A]"
        >
          Page not found
        </h2>

        <p
          className="text-sm font-medium mb-8 max-w-xs mx-auto text-[#66736F]"
        >
          The page you are looking for doesn't exist or has been moved to another URL.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            to="/"
            className="w-full sm:w-auto inline-flex items-center justify-center font-medium rounded-md py-2.5 px-4 text-sm text-white bg-[#167568] hover:bg-[#125E55] transition-colors shadow-xs"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Public Home
          </Link>
          <Link
            to="/app"
            className="w-full sm:w-auto inline-flex items-center justify-center font-medium rounded-md py-2.5 px-4 text-sm text-[#202C2A] bg-white border border-[#E2E9E6] hover:bg-[#F5F7F7] transition-colors shadow-xs"
          >
            <LayoutDashboard className="w-4 h-4 mr-2 text-[#167568]" />
            Go to App
          </Link>
        </div>
      </div>
    </div>
  );
}
