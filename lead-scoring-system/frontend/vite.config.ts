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
    // For Railway: Allow the specific Railway domain pattern
    // Railway domains follow: *.up.railway.app
    // Setting to empty array should disable host checking in Vite 5+
    allowedHosts: [".up.railway.app"],
  },
  build: {
    sourcemap: true,
  },
});
