/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        turmeric: "#C98A2C",   // urine-color inspired accent
        neem: "#3F6E52",       // deep herbal green
        neemLight: "#EAF2ED",
        clay: "#F6F1E7",       // warm parchment background
        ink: "#2B2620",
        amberRisk: "#C98A2C",
        lowRisk: "#3F6E52",
        modRisk: "#C98A2C",
        highRisk: "#B3432B",
      },
      fontFamily: {
        display: ["'Fraunces'", "serif"],
        body: ["'Inter'", "sans-serif"],
      },
    },
  },
  plugins: [],
};
