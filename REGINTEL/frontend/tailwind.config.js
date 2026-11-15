/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#167568",
          hover: "#125E55",
        },
        "bg-page": "#F5F7F7",
        surface: "#FFFFFF",
        "text-main": "#202C2A",
        "text-muted": "#66736F",
        border: "#E2E9E6",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
