/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18212f",
        field: "#f6f8fb",
        line: "#d9e1ea",
        brand: "#0f766e",
        alert: "#b42318",
        amber: "#b7791f",
      },
      boxShadow: {
        soft: "0 18px 45px rgba(24, 33, 47, 0.08)",
      },
    },
  },
  plugins: [],
};
