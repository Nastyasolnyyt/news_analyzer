import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../api/client';
const router = useRouter();
const notifications = ref(4);
const user = ref(null);
const showMenu = ref(false);
const getUserInitials = (name) => {
    return name
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
};
onMounted(async () => {
    try {
        user.value = await api.getCurrentUser();
    }
    catch (e) {
        console.error('Error loading user:', e);
    }
});
const handleSearchClick = () => {
    router.push('/search');
};
const handleLogout = () => {
    api.logout();
    router.push('/auth');
};
const toggleMenu = () => {
    showMenu.value = !showMenu.value;
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['search']} */ ;
/** @type {__VLS_StyleScopedClasses['search']} */ ;
/** @type {__VLS_StyleScopedClasses['search']} */ ;
/** @type {__VLS_StyleScopedClasses['icon-button']} */ ;
/** @type {__VLS_StyleScopedClasses['icon-button']} */ ;
/** @type {__VLS_StyleScopedClasses['profile']} */ ;
/** @type {__VLS_StyleScopedClasses['profile']} */ ;
/** @type {__VLS_StyleScopedClasses['profile']} */ ;
/** @type {__VLS_StyleScopedClasses['menu-item']} */ ;
/** @type {__VLS_StyleScopedClasses['menu-item']} */ ;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)({
    ...{ class: "header" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
    ...{ onClick: (__VLS_ctx.handleSearchClick) },
    ...{ class: "search" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    type: "text",
    placeholder: "Поиск по компаниям, персонам, событиям",
    readonly: true,
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "kbd" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "actions" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.router.push('/notifications');
        } },
    ...{ class: "icon-button" },
    'aria-label': "notifications",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "dot" },
    'data-count': (__VLS_ctx.notifications),
});
(__VLS_ctx.notifications);
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
    viewBox: "0 0 24 24",
    'aria-hidden': "true",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
    d: "M12 2a6 6 0 0 0-6 6v3.382l-.894 2.235A1 1 0 0 0 6.056 15h11.888a1 1 0 0 0 .95-1.383L18 11.382V8a6 6 0 0 0-6-6Z",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
    d: "M9 18a3 3 0 0 0 6 0",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "profile-menu" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (__VLS_ctx.toggleMenu) },
    ...{ class: "profile" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "user-initials" },
});
(__VLS_ctx.user ? __VLS_ctx.getUserInitials(__VLS_ctx.user.name) : 'AK');
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
(__VLS_ctx.user ? __VLS_ctx.user.name : 'Analyst');
if (__VLS_ctx.showMenu) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "menu-popup" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "menu-item user-info" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "user-name" },
    });
    (__VLS_ctx.user?.name);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "user-login" },
    });
    (__VLS_ctx.user?.login);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "menu-divider" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.showMenu))
                    return;
                __VLS_ctx.router.push('/profile');
            } },
        ...{ class: "menu-item" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.showMenu))
                    return;
                __VLS_ctx.router.push('/notifications');
            } },
        ...{ class: "menu-item" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.handleLogout) },
        ...{ class: "menu-item logout" },
    });
}
/** @type {__VLS_StyleScopedClasses['header']} */ ;
/** @type {__VLS_StyleScopedClasses['search']} */ ;
/** @type {__VLS_StyleScopedClasses['kbd']} */ ;
/** @type {__VLS_StyleScopedClasses['actions']} */ ;
/** @type {__VLS_StyleScopedClasses['icon-button']} */ ;
/** @type {__VLS_StyleScopedClasses['dot']} */ ;
/** @type {__VLS_StyleScopedClasses['profile-menu']} */ ;
/** @type {__VLS_StyleScopedClasses['profile']} */ ;
/** @type {__VLS_StyleScopedClasses['user-initials']} */ ;
/** @type {__VLS_StyleScopedClasses['menu-popup']} */ ;
/** @type {__VLS_StyleScopedClasses['menu-item']} */ ;
/** @type {__VLS_StyleScopedClasses['user-info']} */ ;
/** @type {__VLS_StyleScopedClasses['user-name']} */ ;
/** @type {__VLS_StyleScopedClasses['user-login']} */ ;
/** @type {__VLS_StyleScopedClasses['menu-divider']} */ ;
/** @type {__VLS_StyleScopedClasses['menu-item']} */ ;
/** @type {__VLS_StyleScopedClasses['menu-item']} */ ;
/** @type {__VLS_StyleScopedClasses['menu-item']} */ ;
/** @type {__VLS_StyleScopedClasses['logout']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            router: router,
            notifications: notifications,
            user: user,
            showMenu: showMenu,
            getUserInitials: getUserInitials,
            handleSearchClick: handleSearchClick,
            handleLogout: handleLogout,
            toggleMenu: toggleMenu,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
