import axios from 'axios';

const instance = axios.create({
  baseURL: '/api/v1', // Прокси настроен в vite.config.ts
});

// Перехватчик: перед каждым запросом добавляем токен из памяти браузера
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default {
  // Авторизация
  async login(login: string, password: string) {
    const response = await instance.post('/auth/login', { login, password });
    return response.data; // Вернет { access_token, refresh_token, ... }
  },

  // Посты для Dashboard
  async getPosts() {
    const response = await instance.get('/core/posts');
    return response.data;
  },

  // Конкретный пост для NewsDetail
  async getPostById(id: number) {
    const response = await instance.get(`/core/posts/${id}`);
    return response.data;
  }
};