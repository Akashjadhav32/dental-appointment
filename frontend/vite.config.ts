import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    allowedHosts: [
      'a2f9acbb-f983-4352-9cd5-9948de5e84ce.preview.emergentagent.com',
      '.emergentagent.com',
      '.choreoapps.dev',
      'localhost'
    ]
  },
  build: {
    outDir: 'build'
  }
})