/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        hot: "#ef4444",
        warm: "#f59e0b",
        cold: "#3b82f6",
        navy: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#1e3a8a", // Main navy accent
          700: "#1e40af",
          800: "#1e3a8a",
          900: "#1e3a8a",
        },
      },
    },
  },
  plugins: [],
};
