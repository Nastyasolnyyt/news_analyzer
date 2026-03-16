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

  // Исправленный метод для получения списка постов
  async getPosts(page = 1, pageSize = 20) {
    // Путь теперь совпадает с тем, что мы видели в логах бэкенда
    const response = await instance.get('/posts', {
      params: {
        page: page,
        page_size: pageSize,
        order: 'desc',
        sort: 'created_at'
      }
    });
    // Важно: возвращаем всё response.data, так как там лежат { items, total, page, page_size }
    return response.data;
  },

  // Конкретный пост
  async getPostById(id: number) {
    // Убираем /core/, так как роутинг в FastAPI, судя по логам, плоский
    const response = await instance.get(`/posts/${id}`);
    return response.data;
  }
  
};
