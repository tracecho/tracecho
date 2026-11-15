import React from "react";
import ReactDOM from "react-dom/client";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "@/contexts/AuthContext";
import App from "@/App";
import "@/index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: "#FFFFFF",
            color: "#202C2A",
            border: "1px solid #E2E9E6",
            fontSize: "14px",
            fontFamily: "Inter, sans-serif",
          },
          success: {
            iconTheme: {
              primary: "#167568",
              secondary: "#FFFFFF",
            },
          },
          error: {
            iconTheme: {
              primary: "#DC2626",
              secondary: "#FFFFFF",
            },
          },
        }}
      />
    </AuthProvider>
  </React.StrictMode>
);
