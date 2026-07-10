/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}", "./tests/**/*.ts"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        focus: "0 0 0 3px rgb(20 184 166 / 0.2)",
      },
    },
  },
  plugins: [],
};
