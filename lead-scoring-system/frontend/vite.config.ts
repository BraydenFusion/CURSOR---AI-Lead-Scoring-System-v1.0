import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Get backend URL from environment at build time
// Railway Reference Variables work, but we can also read from env
const backendUrl = process.env.VITE_API_URL || process.env.RAILWAY_BACKEND_URL || process.env.BACKEND_URL;

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  preview: {
    port: parseInt(process.env.PORT || "8080"),
    host: "0.0.0.0",
    // Allow Railway domain - Railway provides this via RAILWAY_PUBLIC_DOMAIN or use pattern
    // This specific domain is from your current deployment
    allowedHosts: [
      "cursor-ai-lead-scoring-system-v10-production-8d7f.up.railway.app",
      "ventrix.tech",
      ".up.railway.app", // Try suffix pattern as fallback
      ".ventrix.tech", // Allow subdomains of ventrix.tech
    ],
    strictPort: false,
  },
  build: {
    sourcemap: true,
    // Inject backend URL at build time if available
    define: backendUrl ? {
      'import.meta.env.VITE_API_URL': JSON.stringify(backendUrl),
    } : {},
  },
});
