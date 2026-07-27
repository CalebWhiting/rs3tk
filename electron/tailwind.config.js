/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'rs-gold': 'var(--rs-gold)',
        'rs-gold-light': 'var(--rs-gold-light)',
        'rs-gold-dark': 'var(--rs-gold-dark)',
        'rs-bg': 'var(--rs-bg)',
        'rs-bg-light': 'var(--rs-bg-light)',
        'rs-border': 'var(--rs-border)',
        'rs-muted': 'var(--rs-muted)',
        'rs-header': 'var(--rs-header)',
        'rs-green': 'var(--rs-green)',
        'rs-blue': 'var(--rs-blue)',
        'rs-yellow': 'var(--rs-yellow)',
        'rs-red': 'var(--rs-red)',
        'rs-card': 'var(--rs-card)',
        'rs-card-hover': 'var(--rs-card-hover)',
        'rs-divider': 'var(--rs-divider)',
        'rs-text': 'var(--rs-text)',
        'rs-btn-text': 'var(--rs-btn-text)',
      },
    },
  },
  plugins: [],
}
