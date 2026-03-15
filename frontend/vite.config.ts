import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8003',  // URL output_module
        changeOrigin: true,
        secure: false
      }
    }
  }
});

