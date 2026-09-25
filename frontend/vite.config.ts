import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, res) => {
            console.warn('[Vite Proxy Warning]', err.message);
            if (!res.headersSent && (res as any).writeHead) {
              (res as any).writeHead(502, { 'Content-Type': 'application/json' });
              (res as any).end(JSON.stringify({ 
                detail: 'Backend service temporarily unavailable or starting up. Please try again.' 
              }));
            }
          });
        }
      },
      '/uploads': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
