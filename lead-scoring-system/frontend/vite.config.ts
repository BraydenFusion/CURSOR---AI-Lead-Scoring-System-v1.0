import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  preview: {
    port: parseInt(process.env.PORT || "5173"),
    host: "0.0.0.0",
    // For Railway: Allow any host by not setting allowedHosts
    // This should allow all hosts when combined with --host 0.0.0.0 in CLI
    // If needed, add specific Railway domain: allowedHosts: ["your-domain.up.railway.app"]
    strictPort: false,
  },
  build: {
    sourcemap: true,
  },
});
