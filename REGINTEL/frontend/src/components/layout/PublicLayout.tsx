import React, { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { ShieldCheck, Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";

interface PublicLayoutProps {
  children?: React.ReactNode;
}

const navLinks = [
  { name: "Home", to: "/" },
  { name: "About", to: "/about" },
  { name: "Services", to: "/services" },
  { name: "Contact", to: "/contact" },
];

export const PublicLayout: React.FC<PublicLayoutProps> = ({ children }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-bg-page font-sans text-text-main selection:bg-primary/20 selection:text-primary">
      {/* Top Navbar */}
      <header className="sticky top-0 z-50 bg-white border-b border-[#E2E9E6] h-16">
        <div className="max-w-7xl mx-auto h-full px-4 sm:px-6 lg:px-8 flex items-center justify-between">
          {/* Left: Brand Logo */}
          <Link to="/" className="flex items-center space-x-2.5 group">
            <div className="flex items-center justify-center h-8 w-8 rounded-md bg-[#167568] text-white shadow-xs transition-transform group-hover:scale-105">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <span className="font-bold text-base tracking-wider text-[#202C2A]">
              TRACECHO
            </span>
          </Link>

          {/* Center (desktop): Nav Links */}
          <nav className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === "/"}
                className={({ isActive }) =>
                  cn(
                    "text-sm transition-colors",
                    isActive
                      ? "text-[#167568] font-medium"
                      : "text-[#66736F] hover:text-[#202C2A]"
                  )
                }
              >
                {link.name}
              </NavLink>
            ))}
          </nav>

          {/* Right (desktop): Auth Buttons */}
          <div className="hidden md:flex items-center space-x-3">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/login" className="text-[#202C2A] hover:text-[#167568]">
                Sign In
              </Link>
            </Button>
            <Button
              size="sm"
              asChild
              className="bg-[#167568] hover:bg-[#125E55] text-white shadow-xs"
            >
              <Link to="/signup">Get Started</Link>
            </Button>
          </div>

          {/* Mobile hamburger button */}
          <div className="flex md:hidden">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-[#66736F] hover:text-[#202C2A] hover:bg-bg-page focus:outline-none focus:ring-2 focus:ring-[#167568]"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile drawer / overlay */}
        {mobileMenuOpen && (
          <div className="md:hidden fixed inset-x-0 top-16 bg-white border-b border-[#E2E9E6] shadow-lg animate-in slide-in-from-top-2 duration-150 z-40">
            <div className="px-4 pt-3 pb-6 space-y-3">
              <nav className="flex flex-col space-y-2">
                {navLinks.map((link) => (
                  <NavLink
                    key={link.to}
                    to={link.to}
                    end={link.to === "/"}
                    onClick={() => setMobileMenuOpen(false)}
                    className={({ isActive }) =>
                      cn(
                        "px-3 py-2 rounded-md text-base transition-colors",
                        isActive
                          ? "bg-primary/10 text-[#167568] font-medium"
                          : "text-[#66736F] hover:bg-bg-page hover:text-[#202C2A]"
                      )
                    }
                  >
                    {link.name}
                  </NavLink>
                ))}
              </nav>
              <div className="pt-3 border-t border-[#E2E9E6] flex flex-col space-y-2">
                <Button
                  variant="ghost"
                  className="w-full justify-center"
                  asChild
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Link to="/login">Sign In</Link>
                </Button>
                <Button
                  className="w-full justify-center bg-[#167568] hover:bg-[#125E55] text-white"
                  asChild
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Link to="/signup">Get Started</Link>
                </Button>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main content */}
      <main className="flex-1 bg-[#F5F7F7] min-h-[calc(100vh-64px-48px)]">
        {children ?? <Outlet />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-[#E2E9E6] h-12 flex items-center justify-center px-4">
        <p className="text-sm text-[#66736F] text-center">
          © 2024 TRACECHO. AI-powered regulatory intelligence.
        </p>
      </footer>
    </div>
  );
};

export default PublicLayout;
