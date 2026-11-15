import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Loader2, ShieldCheck } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { postSignup, getMe } from "@/lib/api";

export default function SignUp() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  // Field validation errors
  const [errors, setErrors] = useState<{
    fullName?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  const validateForm = () => {
    const newErrors: typeof errors = {};

    if (!fullName.trim()) {
      newErrors.fullName = "Full name is required";
    }

    if (!email.trim()) {
      newErrors.email = "Email address is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!password) {
      newErrors.password = "Password is required";
    } else if (password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = "Confirm password is required";
    } else if (confirmPassword !== password) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setServerError(null);

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // 1. Call POST /api/auth/signup
      const tokenRes = await postSignup({
        email: email.trim(),
        password,
        full_name: fullName.trim(),
      });

      const accessToken = tokenRes.access_token;

      // 2. Fetch user profile
      const user = await getMe(accessToken);
      const authUser = {
        ...user,
        name: user.full_name || fullName.trim(),
      };

      // 3. Auto sign-in and redirect to /
      login(accessToken, authUser);
      navigate("/app");
    } catch (err: any) {
      console.error("Sign-up error:", err);
      if (err?.response?.status === 400) {
        setServerError(
          err?.response?.data?.detail || "Email already registered. Please sign in instead."
        );
      } else if (err?.response?.data?.detail) {
        setServerError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Sign up failed. Please check your information."
        );
      } else {
        setServerError("Network or server error. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{ backgroundColor: "#F5F7F7" }}
    >
      <div
        className="w-full max-w-md rounded-lg shadow-sm"
        style={{
          backgroundColor: "#FFFFFF",
          border: "1px solid #E2E9E6",
          padding: "32px",
        }}
      >
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-8">
          <div
            className="w-12 h-12 rounded-lg flex items-center justify-center text-white mb-3 shadow-sm"
            style={{ backgroundColor: "#167568" }}
          >
            <ShieldCheck className="w-7 h-7 stroke-[2.2]" />
          </div>
          <h1
            className="text-2xl font-bold tracking-tight"
            style={{ color: "#202C2A" }}
          >
            TRACECHO
          </h1>
          <p
            className="text-sm mt-1 font-medium"
            style={{ color: "#66736F" }}
          >
            Regulatory Intelligence Platform
          </p>
        </div>

        {/* Server Error Banner */}
        {serverError && (
          <div
            role="alert"
            className="mb-5 text-sm font-medium rounded-md p-3"
            style={{
              backgroundColor: "#FEF2F2",
              color: "#DC2626",
              border: "1px solid #FCA5A5",
            }}
          >
            {serverError}
          </div>
        )}

        {/* Sign Up Form */}
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          {/* Full Name Field */}
          <div>
            <label
              htmlFor="fullName"
              className="block text-sm font-medium mb-1.5"
              style={{ color: "#202C2A" }}
            >
              Full Name
            </label>
            <input
              id="fullName"
              type="text"
              required
              disabled={loading}
              value={fullName}
              onChange={(e) => {
                setFullName(e.target.value);
                if (errors.fullName) {
                  setErrors((prev) => ({ ...prev, fullName: undefined }));
                }
              }}
              placeholder="Dr. Sarah Jenkins"
              className="w-full rounded-md px-3.5 py-2.5 text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                backgroundColor: "#FFFFFF",
                border: errors.fullName ? "1px solid #DC2626" : "1px solid #E2E9E6",
                color: "#202C2A",
                outline: "none",
              }}
              onFocus={(e) => {
                e.currentTarget.style.border = "2px solid #167568";
                e.currentTarget.style.padding = "9px 13px";
              }}
              onBlur={(e) => {
                e.currentTarget.style.border = errors.fullName
                  ? "1px solid #DC2626"
                  : "1px solid #E2E9E6";
                e.currentTarget.style.padding = "10px 14px";
              }}
            />
            {errors.fullName && (
              <p className="mt-1 text-xs font-medium" style={{ color: "#DC2626" }}>
                {errors.fullName}
              </p>
            )}
          </div>

          {/* Email Address Field */}
          <div>
            <label
              htmlFor="signupEmail"
              className="block text-sm font-medium mb-1.5"
              style={{ color: "#202C2A" }}
            >
              Email Address
            </label>
            <input
              id="signupEmail"
              type="email"
              required
              autoComplete="email"
              disabled={loading}
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (errors.email) {
                  setErrors((prev) => ({ ...prev, email: undefined }));
                }
              }}
              placeholder="name@company.com"
              className="w-full rounded-md px-3.5 py-2.5 text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                backgroundColor: "#FFFFFF",
                border: errors.email ? "1px solid #DC2626" : "1px solid #E2E9E6",
                color: "#202C2A",
                outline: "none",
              }}
              onFocus={(e) => {
                e.currentTarget.style.border = "2px solid #167568";
                e.currentTarget.style.padding = "9px 13px";
              }}
              onBlur={(e) => {
                e.currentTarget.style.border = errors.email
                  ? "1px solid #DC2626"
                  : "1px solid #E2E9E6";
                e.currentTarget.style.padding = "10px 14px";
              }}
            />
            {errors.email && (
              <p className="mt-1 text-xs font-medium" style={{ color: "#DC2626" }}>
                {errors.email}
              </p>
            )}
          </div>

          {/* Password Field */}
          <div>
            <label
              htmlFor="signupPassword"
              className="block text-sm font-medium mb-1.5"
              style={{ color: "#202C2A" }}
            >
              Password
            </label>
            <div className="relative">
              <input
                id="signupPassword"
                type={showPassword ? "text" : "password"}
                required
                autoComplete="new-password"
                disabled={loading}
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errors.password) {
                    setErrors((prev) => ({ ...prev, password: undefined }));
                  }
                }}
                placeholder="At least 8 characters"
                className="w-full rounded-md pl-3.5 pr-11 py-2.5 text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  backgroundColor: "#FFFFFF",
                  border: errors.password ? "1px solid #DC2626" : "1px solid #E2E9E6",
                  color: "#202C2A",
                  outline: "none",
                }}
                onFocus={(e) => {
                  e.currentTarget.style.border = "2px solid #167568";
                  e.currentTarget.style.padding = "9px 43px 9px 13px";
                }}
                onBlur={(e) => {
                  e.currentTarget.style.border = errors.password
                    ? "1px solid #DC2626"
                    : "1px solid #E2E9E6";
                  e.currentTarget.style.padding = "10px 44px 10px 14px";
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                aria-label={showPassword ? "Hide password" : "Show password"}
                className="absolute inset-y-0 right-0 flex items-center pr-3.5 hover:opacity-80 transition-opacity"
                style={{ color: "#66736F" }}
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
            {errors.password && (
              <p className="mt-1 text-xs font-medium" style={{ color: "#DC2626" }}>
                {errors.password}
              </p>
            )}
          </div>

          {/* Confirm Password Field */}
          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium mb-1.5"
              style={{ color: "#202C2A" }}
            >
              Confirm Password
            </label>
            <div className="relative">
              <input
                id="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                required
                autoComplete="new-password"
                disabled={loading}
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  if (errors.confirmPassword) {
                    setErrors((prev) => ({ ...prev, confirmPassword: undefined }));
                  }
                }}
                placeholder="Re-enter password"
                className="w-full rounded-md pl-3.5 pr-11 py-2.5 text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  backgroundColor: "#FFFFFF",
                  border: errors.confirmPassword
                    ? "1px solid #DC2626"
                    : "1px solid #E2E9E6",
                  color: "#202C2A",
                  outline: "none",
                }}
                onFocus={(e) => {
                  e.currentTarget.style.border = "2px solid #167568";
                  e.currentTarget.style.padding = "9px 43px 9px 13px";
                }}
                onBlur={(e) => {
                  e.currentTarget.style.border = errors.confirmPassword
                    ? "1px solid #DC2626"
                    : "1px solid #E2E9E6";
                  e.currentTarget.style.padding = "10px 44px 10px 14px";
                }}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                tabIndex={-1}
                aria-label={
                  showConfirmPassword ? "Hide confirm password" : "Show confirm password"
                }
                className="absolute inset-y-0 right-0 flex items-center pr-3.5 hover:opacity-80 transition-opacity"
                style={{ color: "#66736F" }}
              >
                {showConfirmPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
            {errors.confirmPassword && (
              <p className="mt-1 text-xs font-medium" style={{ color: "#DC2626" }}>
                {errors.confirmPassword}
              </p>
            )}
          </div>

          {/* Submit Button */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center font-medium rounded-md py-2.5 px-4 text-sm text-white transition-colors duration-150 shadow-sm disabled:opacity-60 disabled:cursor-not-allowed"
              style={{
                backgroundColor: "#167568",
              }}
              onMouseEnter={(e) => {
                if (!loading) e.currentTarget.style.backgroundColor = "#125E55";
              }}
              onMouseLeave={(e) => {
                if (!loading) e.currentTarget.style.backgroundColor = "#167568";
              }}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  <span>Creating account...</span>
                </>
              ) : (
                "Create Account"
              )}
            </button>
          </div>
        </form>

        {/* Footer Link */}
        <div
          className="mt-6 pt-6 text-center text-sm"
          style={{
            borderTop: "1px solid #E2E9E6",
            color: "#66736F",
          }}
        >
          <span>Already have an account? </span>
          <Link
            to="/login"
            className="font-semibold hover:underline"
            style={{ color: "#167568" }}
          >
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
