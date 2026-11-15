import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Loader2, ShieldCheck } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { postSignin, getMe } from "@/lib/api";

export default function SignIn() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email.trim() || !password) {
      setErrorMessage("Please enter both email and password.");
      return;
    }

    setLoading(true);

    try {
      const tokenRes = await postSignin({
        email: email.trim(),
        password,
      });

      const accessToken = tokenRes.access_token;

      // Fetch user profile
      const user = await getMe(accessToken);
      const authUser = {
        ...user,
        name: user.full_name || user.name || user.email.split("@")[0],
      };

      login(accessToken, authUser);
      navigate("/app");
    } catch (err: any) {
      console.error("Sign-in error:", err);
      if (err?.response?.status === 401) {
        setErrorMessage(
          err?.response?.data?.detail || "Invalid email or password. Please try again."
        );
      } else if (err?.response?.data?.detail) {
        setErrorMessage(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Sign in failed. Please check your credentials."
        );
      } else {
        setErrorMessage("Network or server error. Please try again.");
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

        {/* Sign In Form */}
        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium mb-1.5"
              style={{ color: "#202C2A" }}
            >
              Email Address
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              disabled={loading}
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (errorMessage) setErrorMessage(null);
              }}
              placeholder="name@company.com"
              className="w-full rounded-md px-3.5 py-2.5 text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                backgroundColor: "#FFFFFF",
                border: "1px solid #E2E9E6",
                color: "#202C2A",
                outline: "none",
              }}
              onFocus={(e) => {
                e.currentTarget.style.border = "2px solid #167568";
                e.currentTarget.style.padding = "9px 13px";
              }}
              onBlur={(e) => {
                e.currentTarget.style.border = "1px solid #E2E9E6";
                e.currentTarget.style.padding = "10px 14px";
              }}
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label
                htmlFor="password"
                className="block text-sm font-medium"
                style={{ color: "#202C2A" }}
              >
                Password
              </label>
            </div>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                required
                autoComplete="current-password"
                disabled={loading}
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errorMessage) setErrorMessage(null);
                }}
                placeholder="••••••••"
                className="w-full rounded-md pl-3.5 pr-11 py-2.5 text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  backgroundColor: "#FFFFFF",
                  border: "1px solid #E2E9E6",
                  color: "#202C2A",
                  outline: "none",
                }}
                onFocus={(e) => {
                  e.currentTarget.style.border = "2px solid #167568";
                  e.currentTarget.style.padding = "9px 43px 9px 13px";
                }}
                onBlur={(e) => {
                  e.currentTarget.style.border = "1px solid #E2E9E6";
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
          </div>

          {/* Error Message */}
          {errorMessage && (
            <div
              role="alert"
              className="text-sm font-medium rounded-md p-3"
              style={{
                backgroundColor: "#FEF2F2",
                color: "#DC2626",
                border: "1px solid #FCA5A5",
              }}
            >
              {errorMessage}
            </div>
          )}

          {/* Submit Button */}
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
                <span>Signing in...</span>
              </>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        {/* Footer Link */}
        <div
          className="mt-6 pt-6 text-center text-sm"
          style={{
            borderTop: "1px solid #E2E9E6",
            color: "#66736F",
          }}
        >
          <span>Don't have an account? </span>
          <Link
            to="/signup"
            className="font-semibold hover:underline"
            style={{ color: "#167568" }}
          >
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}
