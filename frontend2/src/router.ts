import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from './views/Dashboard.vue';
import Search from './views/Search.vue';
import AllEntities from './views/AllEntities.vue';
import EntityProfile from './views/EntityProfile.vue';
import NewsDetail from './views/NewsDetail.vue';
import Notifications from './views/Notifications.vue';
import Reports from './views/Reports.vue';
import Auth from './views/Auth.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/auth',
      name: 'auth',
      component: Auth,
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard,
      meta: { requiresAuth: true },
    },
    {
      path: '/entities',
      name: 'all-entities',
      component: AllEntities,
      meta: { requiresAuth: true },
    },
    { 
      path: '/entity/:id',
      name: 'entity',
      component: EntityProfile,
      props: true,
      meta: { requiresAuth: true },
    },
    {
      path: '/search',
      name: 'search',
      component: Search,
      meta: { requiresAuth: true },
    },
    {
      path: '/news/:id',
      name: 'news',
      component: NewsDetail,
      props: true,
      meta: { requiresAuth: true },
    },
    {
      path: '/notifications',
      name: 'notifications',
      component: Notifications,
      meta: { requiresAuth: true },
    },
    {
      path: '/reports',
      name: 'reports',
      component: Reports,
      meta: { requiresAuth: true },
    },
  ],
});

// Guard для проверки аутентификации
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('accessToken');
  const requiresAuth = to.meta.requiresAuth !== false;

  if (requiresAuth && !isAuthenticated) {
    // Если требуется авторизация, но токена нет - перенаправляем на /auth
    next('/auth');
  } else if (to.path === '/auth' && isAuthenticated) {
    // Если уже авторизован и пытается перейти на /auth - перенаправляем на /
    next('/');
  } else {
    next();
  }
});

export default router;

