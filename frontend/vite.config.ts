import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://159.194.200.32:8003',  // URL output_module на облаке
        changeOrigin: true,
        secure: false
      }
    }
  }
});

