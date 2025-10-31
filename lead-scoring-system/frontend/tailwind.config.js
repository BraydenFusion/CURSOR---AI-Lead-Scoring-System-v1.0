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
      },
    },
  },
  plugins: [],
};
