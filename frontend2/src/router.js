import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from './views/Dashboard.vue';
import Search from './views/Search.vue';
import AllEntities from './views/AllEntities.vue';
import EntityProfile from './views/EntityProfile.vue';
import NewsDetail from './views/NewsDetail.vue';
import Notifications from './views/Notifications.vue';
import Reports from './views/Reports.vue';
const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'dashboard',
            component: Dashboard,
        },
        {
            path: '/entities',
            name: 'all-entities',
            component: AllEntities,
        },
        {
            path: '/entity/:id',
            name: 'entity',
            component: EntityProfile,
            props: true,
        },
        {
            path: '/search',
            name: 'search',
            component: Search,
        },
        {
            path: '/news/:id',
            name: 'news',
            component: NewsDetail,
            props: true,
        },
        {
            path: '/notifications',
            name: 'notifications',
            component: Notifications,
        },
        {
            path: '/reports',
            name: 'reports',
            component: Reports,
        },
    ],
});
export default router;
