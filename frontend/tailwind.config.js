/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          border: "hsl(220 13% 91%)",
          background: "hsl(0 0% 100%)",
          foreground: "hsl(224 71% 4%)",
          card: "hsl(0 0% 100%)",
          "card-foreground": "hsl(224 71% 4%)",
          muted: "hsl(220 14% 96%)",
          "muted-foreground": "hsl(220 9% 46%)",
          accent: "hsl(220 14% 96%)",
          "accent-foreground": "hsl(224 71% 4%)",
          primary: "hsl(238 84% 67%)",
          "primary-foreground": "hsl(0 0% 100%)",
        },
        fontFamily: {
          sans: ['Inter', 'system-ui', 'sans-serif'],
        },
      },
    },
    plugins: [],
  }