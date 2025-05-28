module.exports = {
  content: [
    "./templates/**/*.html", // Scan all HTML templates
    "./**/forms.py", // Scan form definitions if you use Tailwind classes there
    "./**/views.py", // Scan views if you use Tailwind classes there
    "./**/models.py", // Scan models if you use Tailwind classes there
  ],
  theme: {
    extend: {
      fontFamily: {
        // Use Geist as default sans and mono fonts (with fallbacks)
        sans: [
          '"Geist"',
          ...require("tailwindcss/defaultTheme").fontFamily.sans,
        ],
        mono: [
          '"Geist Mono"',
          ...require("tailwindcss/defaultTheme").fontFamily.mono,
        ],
      },
    },
  },
  plugins: [],
};
