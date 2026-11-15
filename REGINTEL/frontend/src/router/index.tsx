import React from "react";
import { Navigate, createBrowserRouter, RouterProvider } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

// Lazy load pages for better chunking
import Home from "@/pages/public/Home";
import About from "@/pages/public/About";
import Services from "@/pages/public/Services";
import Contact from "@/pages/public/Contact";
import SignIn from "@/pages/SignIn";
import SignUp from "@/pages/SignUp";
import Dashboard from "@/pages/Dashboard";
import Assistant from "@/pages/Assistant";
import Explorer from "@/pages/Explorer";
import Evaluation from "@/pages/Evaluation";
import NotFound from "@/pages/NotFound";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export function PublicOnlyGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  if (isAuthenticated) return <Navigate to="/app" replace />;
  return <>{children}</>;
}

export const router = createBrowserRouter([
  // Public website
  { path: "/", element: <Home /> },
  { path: "/about", element: <About /> },
  { path: "/services", element: <Services /> },
  { path: "/contact", element: <Contact /> },
  { path: "/login", element: <PublicOnlyGuard><SignIn /></PublicOnlyGuard> },
  { path: "/signin", element: <PublicOnlyGuard><SignIn /></PublicOnlyGuard> },
  { path: "/signup", element: <PublicOnlyGuard><SignUp /></PublicOnlyGuard> },
  // Protected app routes
  { path: "/app", element: <AuthGuard><Dashboard /></AuthGuard> },
  { path: "/app/assistant", element: <AuthGuard><Assistant /></AuthGuard> },
  { path: "/app/explorer", element: <AuthGuard><Explorer /></AuthGuard> },
  { path: "/app/evaluation", element: <AuthGuard><Evaluation /></AuthGuard> },
  // Legacy redirects
  { path: "/dashboard", element: <AuthGuard><Dashboard /></AuthGuard> },
  { path: "/assistant", element: <AuthGuard><Assistant /></AuthGuard> },
  { path: "/explorer", element: <AuthGuard><Explorer /></AuthGuard> },
  { path: "/evaluation", element: <AuthGuard><Evaluation /></AuthGuard> },
  { path: "*", element: <NotFound /> },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}

export default AppRouter;
