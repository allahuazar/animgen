import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/health': 'http://localhost:8000',
      '/upload-pdf': 'http://localhost:8000',
      '/markdown': 'http://localhost:8000',
      '/lesson-json': 'http://localhost:8000',
      '/render': 'http://localhost:8000',
      '/files': 'http://localhost:8000',
      '/output': 'http://localhost:8000',
      '/media': 'http://localhost:8000',
      '/parsed': 'http://localhost:8000',
    },
  },
})
