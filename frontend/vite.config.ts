import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://185.130.212.50:8003',  // URL output_module на облаке
        changeOrigin: true,
        secure: false
      }
    }
  }
});

