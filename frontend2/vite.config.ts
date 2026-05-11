// frontend/vite.config.ts
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://185.130.212.50:8003',
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path,
        onError: (err, req, res) => {
          console.error('Proxy error:', err);
          res.writeHead(502, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Backend unavailable', details: err.message }));
        },
      },
    },
  },
});