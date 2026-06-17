/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae2fd',
          300: '#7cc8fc',
          400: '#38aaf8',
          500: '#0e90e9',
          600: '#0271c7',
          700: '#035ba3',
          800: '#074e87',
          900: '#0c4270',
          950: '#082a4a',
        },
        darkBg: '#0f172a',
        darkCard: '#1e293b',
        darkBorder: '#334155'
      }
    },
  },
  plugins: [],
}
