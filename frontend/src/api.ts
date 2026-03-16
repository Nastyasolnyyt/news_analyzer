import axios from 'axios';

const instance = axios.create({
  baseURL: '/api/v1', 
});

// Перехватчик для токена
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
    return response.data;
  },

  async getPosts(page = 1, pageSize = 20, search = '') {
    const response = await instance.get('/posts', {
      params: {
        page: page,
        page_size: pageSize,
        search: search, // Передаем строку поиска на бэкенд
        order: 'desc',
        sort: 'created_at'
      }
    });
    // Возвращаем объект { items, total, page, page_size }
    return response.data;
  },

  // Конкретный пост по ID
  async getPostById(id: number | string) {
    const response = await instance.get(`/posts/${id}`);
    return response.data;
  },

  async searchPosts(query: string) {
    const response = await instance.get('/posts', {
      params: {
        search: query,
        page: 1,
        page_size: 50,
        order: 'desc'
      }
    });
    return response.data;
  }
};