<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../api/client';

const router = useRouter();
const isLogin = ref(true);
const loading = ref(false);
const error = ref<string | null>(null);

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

    console.log('✅ Успешный вход');
    router.push('/');
    } catch (e: any) {
    if (e.response?.data?.detail) {
      error.value = e.response.data.detail;
    } else if (e.response?.data?.message) {
      error.value = e.response.data.message;
    } else if (e.message && e.message !== '[object Object]') {
      error.value = e.message;
    } else {
      error.value = 'Неверный логин или пароль';
    }
    console.error('❌ Login error:', e);
  } finally {
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

    console.log('✅ Успешная регистрация');
    // Переходим на вход
    isLogin.value = true;
    registerForm.value = { login: '', password: '', name: '', passwordConfirm: '' };
    } catch (e: any) {
    if (e.response?.data?.detail) {
      error.value = e.response.data.detail;
    } else if (e.response?.data?.message) {
      error.value = e.response.data.message;
    } else if (e.message && e.message !== '[object Object]') {
      error.value = e.message;
    } else {
      error.value = 'Ошибка при регистрации';
    }
    console.error('❌ Register error:', e);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-header">
        <h1>Signal Desk</h1>
        <p>Платформа мониторинга новостей и рисков</p>
      </div>

      <div v-if="error" class="error-banner">
        {{ error }}
      </div>

      <!-- Login Form -->
      <form v-if="isLogin" @submit.prevent="handleLogin" class="auth-form">
        <h2>Вход</h2>

        <div class="form-group">
          <label>Логин</label>
          <input
            v-model="loginForm.login"
            type="text"
            placeholder="Введите логин"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label>Пароль</label>
          <input
            v-model="loginForm.password"
            type="password"
            placeholder="Введите пароль"
            required
            :disabled="loading"
          />
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Загрузка...' : 'Вход' }}
        </button>

        <p class="switch-form">
          Нет аккаунта?
          <button type="button" @click="isLogin = false" class="link-btn">
            Зарегистрироваться
          </button>
        </p>
      </form>

      <!-- Register Form -->
      <form v-else @submit.prevent="handleRegister" class="auth-form">
        <h2>Регистрация</h2>

        <div class="form-group">
          <label>ФИО</label>
          <input
            v-model="registerForm.name"
            type="text"
            placeholder="Ваше имя"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label>Логин</label>
          <input
            v-model="registerForm.login"
            type="text"
            placeholder="Выберите логин"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label>Пароль</label>
          <input
            v-model="registerForm.password"
            type="password"
            placeholder="Пароль (минимум 6 символов)"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label>Подтвердите пароль</label>
          <input
            v-model="registerForm.passwordConfirm"
            type="password"
            placeholder="Повторите пароль"
            required
            :disabled="loading"
          />
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Загрузка...' : 'Регистрация' }}
        </button>

        <p class="switch-form">
          Уже есть аккаунт?
          <button type="button" @click="isLogin = true" class="link-btn">
            Войти
          </button>
        </p>
      </form>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
  padding: 20px;
}

.auth-container {
  width: 100%;
  max-width: 420px;
}

.auth-header {
  text-align: center;
  margin-bottom: 40px;
}

.auth-header h1 {
  font-size: 2.5rem;
  margin: 0 0 8px;
  background: linear-gradient(120deg, #4f8aff, #22c55e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.auth-header p {
  color: #9ca3af;
  margin: 0;
  font-size: 0.9rem;
}

.error-banner {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.auth-form {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 32px;
  backdrop-filter: blur(10px);
}

.auth-form h2 {
  margin: 0 0 24px;
  font-size: 1.5rem;
  color: #fff;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  color: #d1d5db;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: #fff;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.form-group input:hover {
  border-color: rgba(255, 255, 255, 0.25);
}

.form-group input:focus {
  outline: none;
  border-color: #4f8aff;
  box-shadow: 0 0 0 3px rgba(79, 138, 255, 0.1);
}

.form-group input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  width: 100%;
  padding: 12px 24px;
  background: linear-gradient(120deg, #4f8aff, #3b82f6);
  border: none;
  color: #fff;
  font-weight: 600;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(79, 138, 255, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.switch-form {
  text-align: center;
  margin-top: 20px;
  color: #9ca3af;
  font-size: 0.9rem;
}

.link-btn {
  background: none;
  border: none;
  color: #4f8aff;
  cursor: pointer;
  text-decoration: underline;
  font-weight: 600;
  padding: 0;
  font: inherit;
}

.link-btn:hover {
  color: #3b82f6;
}

@media (max-width: 480px) {
  .auth-form {
    padding: 24px;
  }

  .auth-header h1 {
    font-size: 2rem;
  }
}
</style>
