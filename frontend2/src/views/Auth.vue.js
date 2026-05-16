import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../api/client';
const router = useRouter();
const isLogin = ref(true);
const loading = ref(false);
const error = ref(null);
// Login form
const loginForm = ref({
    login: '',
    password: '',
});
// Register form
const registerForm = ref({
    login: '',
    password: '',
    name: '',
    passwordConfirm: '',
});
const handleLogin = async () => {
    try {
        error.value = null;
        loading.value = true;
        const response = await api.login({
            login: loginForm.value.login,
            password: loginForm.value.password,
        });
        // Сохраняем токены
        localStorage.setItem('accessToken', response.access_token);
        localStorage.setItem('refreshToken', response.refresh_token);
        console.log('Успешный вход');
        router.push('/');
    }
    catch (e) {
        error.value = e.message || 'Ошибка входа';
        console.error('Login error:', e);
    }
    finally {
        loading.value = false;
    }
};
const handleRegister = async () => {
    try {
        error.value = null;
        if (registerForm.value.password !== registerForm.value.passwordConfirm) {
            error.value = 'Пароли не совпадают';
            return;
        }
        if (registerForm.value.password.length < 6) {
            error.value = 'Пароль должен быть минимум 6 символов';
            return;
        }
        loading.value = true;
        await api.register({
            login: registerForm.value.login,
            password: registerForm.value.password,
            name: registerForm.value.name,
        });
        console.log('Успешная регистрация');
        // Переходим на вход
        isLogin.value = true;
        registerForm.value = { login: '', password: '', name: '', passwordConfirm: '' };
    }
    catch (e) {
        error.value = e.message || 'Ошибка регистрации';
        console.error('Register error:', e);
    }
    finally {
        loading.value = false;
    }
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['auth-header']} */ ;
/** @type {__VLS_StyleScopedClasses['auth-header']} */ ;
/** @type {__VLS_StyleScopedClasses['auth-form']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['link-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['auth-form']} */ ;
/** @type {__VLS_StyleScopedClasses['auth-header']} */ ;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "auth-page" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "auth-container" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "auth-header" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "error-banner" },
    });
    (__VLS_ctx.error);
}
if (__VLS_ctx.isLogin) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.form, __VLS_intrinsicElements.form)({
        ...{ onSubmit: (__VLS_ctx.handleLogin) },
        ...{ class: "auth-form" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "form-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        value: (__VLS_ctx.loginForm.login),
        type: "text",
        placeholder: "Введите логин",
        required: true,
        disabled: (__VLS_ctx.loading),
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "form-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        type: "password",
        placeholder: "Введите пароль",
        required: true,
        disabled: (__VLS_ctx.loading),
    });
    (__VLS_ctx.loginForm.password);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        type: "submit",
        ...{ class: "btn-primary" },
        disabled: (__VLS_ctx.loading),
    });
    (__VLS_ctx.loading ? 'Загрузка...' : 'Вход');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "switch-form" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.isLogin))
                    return;
                __VLS_ctx.isLogin = false;
            } },
        type: "button",
        ...{ class: "link-btn" },
    });
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.form, __VLS_intrinsicElements.form)({
        ...{ onSubmit: (__VLS_ctx.handleRegister) },
        ...{ class: "auth-form" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "form-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        value: (__VLS_ctx.registerForm.name),
        type: "text",
        placeholder: "Ваше имя",
        required: true,
        disabled: (__VLS_ctx.loading),
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "form-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        value: (__VLS_ctx.registerForm.login),
        type: "text",
        placeholder: "Выберите логин",
        required: true,
        disabled: (__VLS_ctx.loading),
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "form-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        type: "password",
        placeholder: "Пароль (минимум 6 символов)",
        required: true,
        disabled: (__VLS_ctx.loading),
    });
    (__VLS_ctx.registerForm.password);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "form-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        type: "password",
        placeholder: "Повторите пароль",
        required: true,
        disabled: (__VLS_ctx.loading),
    });
    (__VLS_ctx.registerForm.passwordConfirm);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        type: "submit",
        ...{ class: "btn-primary" },
        disabled: (__VLS_ctx.loading),
    });
    (__VLS_ctx.loading ? 'Загрузка...' : 'Регистрация');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "switch-form" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                if (!!(__VLS_ctx.isLogin))
                    return;
                __VLS_ctx.isLogin = true;
            } },
        type: "button",
        ...{ class: "link-btn" },
    });
}
/** @type {__VLS_StyleScopedClasses['auth-page']} */ ;
/** @type {__VLS_StyleScopedClasses['auth-container']} */ ;
/** @type {__VLS_StyleScopedClasses['auth-header']} */ ;
/** @type {__VLS_StyleScopedClasses['error-banner']} */ ;
/** @type {__VLS_StyleScopedClasses['auth-form']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['switch-form']} */ ;
/** @type {__VLS_StyleScopedClasses['link-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['auth-form']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['switch-form']} */ ;
/** @type {__VLS_StyleScopedClasses['link-btn']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            isLogin: isLogin,
            loading: loading,
            error: error,
            loginForm: loginForm,
            registerForm: registerForm,
            handleLogin: handleLogin,
            handleRegister: handleRegister,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
