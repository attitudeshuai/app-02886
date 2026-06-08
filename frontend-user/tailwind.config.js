/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary - 基于参考图 #515d6d
        primary: {
          DEFAULT: '#515d6d',
          light: '#6b7a8a',
          dark: '#3d4654',
        },
        // Background
        background: '#f7f7f7',
        surface: {
          DEFAULT: '#ffffff',
          alt: '#eeeeee',
        },
        // Text
        'text-primary': '#515d6d',
        'text-secondary': '#8a939e',
        'text-muted': '#b8bfc7',
        // Border
        border: '#e8e8e8',
        divider: '#eeeeee',
        // Accent
        accent: {
          DEFAULT: '#4ca6cf',
          light: '#e8f4f9',
        },
        // Status
        success: '#5cb85c',
        warning: '#f0ad4e',
        error: '#d9534f',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'card': '0 2px 8px rgba(81, 93, 109, 0.08)',
        'card-hover': '0 4px 16px rgba(81, 93, 109, 0.12)',
      },
    },
  },
  plugins: [],
}
