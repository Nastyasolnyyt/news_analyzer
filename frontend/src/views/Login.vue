<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';

const router = useRouter();
const login = ref('');
const password = ref('');
const error = ref('');
const isLoading = ref(false);

const handleLogin = async () => {
  if (!login.value || !password.value) {
    error.value = 'Заполните все поля';
    return;
  }
  isLoading.value = true;
  error.value = '';
  try {
    const data = await api.login(login.value, password.value);
    localStorage.setItem('token', data.access_token);
    router.push('/');
  } catch (e: any) {
    error.value = 'Неверный логин или пароль';
    console.error(e);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-area">
        <span class="dot" />
        <h1>PulseSight</h1>
      </div>
      <p class="subtitle">Система мониторинга и анализа рисков</p>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label>Логин</label>
          <input v-model="login" type="text" placeholder="Введите логин" required />
        </div>
        <div class="input-group">
          <label>Пароль</label>
          <input v-model="password" type="password" placeholder="••••••••" required />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="primary-btn" :disabled="isLoading">
          {{ isLoading ? 'Вход...' : 'Войти в систему' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: grid;
  place-items: center;
  min-height: 80vh;
}
.login-card {
  background: var(--surface-1);
  padding: 40px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  width: 100%;
  max-width: 400px;
  text-align: center;
}
.logo-area {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}
.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--accent);
}
h1 { margin: 0; font-size: 1.8rem; color: #fff; }
.subtitle { color: var(--text-dim); margin-bottom: 32px; font-size: 0.9rem; }
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  text-align: left;
}
.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
label { font-size: 0.85rem; color: var(--text-dim); margin-left: 4px; }
input {
  background: var(--surface-2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px 16px;
  border-radius: 12px;
  color: #fff;
  outline: none;
}
input:focus { border-color: var(--accent); }
.error-msg { color: var(--negative); font-size: 0.85rem; text-align: center; margin: 0; }
.primary-btn {
  background: var(--accent);
  color: white;
  padding: 14px;
  border-radius: 14px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  margin-top: 10px;
  transition: opacity 0.2s;
}
.primary-btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>