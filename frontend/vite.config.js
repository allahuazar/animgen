import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/health': 'http://localhost:8000',
      '/route': 'http://localhost:8000',
      '/search-docs': 'http://localhost:8000',
      '/generate-manim': 'http://localhost:8000',
      '/render-manim': 'http://localhost:8000',
      '/generate-and-render': 'http://localhost:8000',
      '/files': 'http://localhost:8000',
      '/output': 'http://localhost:8000',
      '/media': 'http://localhost:8000',
    },
  },
})
