<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api, type UserDTO } from '../api/client';

const router = useRouter();
const user = ref<UserDTO | null>(null);
const loading = ref(true);
const error = ref('');

const getUserInitials = (name: string) => {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};

const getRoleLabel = (role: string) => {
  const roles: Record<string, string> = {
    'admin': '👑 Администратор',
    'user': '👤 Пользователь',
    'analyst': '📊 Аналитик',
  };
  return roles[role] || role;
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

onMounted(async () => {
  try {
    loading.value = true;
    // Получаем текущего пользователя
    user.value = await api.getCurrentUser();
  } catch (e) {
    error.value = 'Ошибка загрузки профиля';
    console.error('Error loading profile:', e);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="profile-container">
    <!-- Заголовок -->
    <header class="profile-header">
      <button class="back-btn" @click="router.back()">
        <span>←</span> Назад
      </button>
      <h1>Мой профиль</h1>
      <div class="header-spacer"></div>
    </header>

    <!-- Основной контент -->
    <div class="profile-content">
      <!-- Загрузка -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Загрузка профиля...</p>
      </div>

      <!-- Ошибка -->
      <div v-else-if="error" class="error-banner">
        {{ error }}
      </div>

      <!-- Данные профиля -->
      <div v-else-if="user" class="profile-grid">
        <!-- Карточка профиля -->
        <div class="profile-card card">
          <div class="profile-avatar">
            <span class="avatar">{{ getUserInitials(user.name) }}</span>
          </div>
          
          <div class="profile-info">
            <h2 class="user-name">{{ user.name }}</h2>
            <p class="user-login">@{{ user.login }}</p>
            <p class="user-role">{{ getRoleLabel(user.role) }}</p>
          </div>

          <div class="profile-stats">
            <div class="stat">
              <span class="stat-label">ID</span>
              <span class="stat-value">#{{ user.id }}</span>
            </div>
            <div class="stat">
              <span class="stat-label">Аккаунт создан</span>
              <span class="stat-value">{{ formatDate(user.created_at) }}</span>
            </div>
          </div>

          <button class="btn-primary" @click="router.push('/notifications')">
            ⚙️ Настройки уведомлений
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--surface-0);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: inherit;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.profile-header h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-spacer {
  flex: 1;
}

.profile-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.loading,
.error-banner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 16px;
  color: #9ca3af;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #4f8aff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-banner {
  padding: 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: #fca5a5;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  background: var(--surface-1);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 24px;
}

/* ===== ПРОФИЛЬ КАРТОЧКА ===== */
.profile-card {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-avatar {
  display: flex;
  justify-content: center;
}

.avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(120deg, #4f8aff, #3b82f6);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 600;
}

.profile-info {
  text-align: center;
}

.user-name {
  margin: 0 0 8px;
  font-size: 1.5rem;
  font-weight: 600;
}

.user-login {
  margin: 0 0 4px;
  color: #9ca3af;
  font-size: 0.95rem;
}

.user-role {
  margin: 0;
  font-size: 0.9rem;
  color: #60a5fa;
}

.profile-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 0.8rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
}

.btn-primary {
  padding: 12px 24px;
  background: linear-gradient(120deg, #4f8aff, #3b82f6);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.95rem;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(79, 138, 255, 0.3);
}

@media (max-width: 768px) {
  .profile-header {
    flex-wrap: wrap;
  }

  .profile-stats {
    grid-template-columns: 1fr;
  }
}
</style>
