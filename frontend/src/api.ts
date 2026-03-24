import axios from 'axios';

const instance = axios.create({
  baseURL: '/api/v1',
});

export default {
  // Авторизация
  async login(login: string, password: string) {
    const response = await instance.post('/auth/login', { login, password });
    return response.data;
  },

  // Получение списка постов (используем /posts, так как бэкенд настроен на этот роут)
  async getPosts(page = 1, pageSize = 20, search = '') {
    const response = await instance.get('/posts', {
      params: {
        page: page,
        page_size: pageSize,
        search: search,
        order: 'desc',
        sort: 'created_at'
      }
    });
    return response.data;
  },

  // Получение конкретного поста по ID
  async getPostById(id: number | string) {
    const response = await instance.get(`/posts/${id}`);
    return response.data;
  },

  // Поиск постов (просто вызывает getPosts с нужными параметрами)
  async searchPosts(query: string) {
    return this.getPosts(1, 50, query);
  }
};