<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api, type UserDTO } from '../api/client';

const router = useRouter();
const user = ref<UserDTO | null>(null);
const reports = ref<any[]>([]);
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
    
    // Получаем отчеты пользователя (если есть API метод)
    try {
      reports.value = await api.getUserReports?.() || [];
    } catch (e) {
      // Если метода нет, просто оставляем пустой массив
      reports.value = [];
    }
  } catch (e) {
    error.value = 'Ошибка загрузки профиля';
    console.error('Error loading profile:', e);
  } finally {
    loading.value = false;
  }
});

const handleDeleteReport = async (reportId: number) => {
  if (!confirm('Вы уверены, что хотите удалить этот отчет?')) return;
  
  try {
    if (api.deleteReport) {
      await api.deleteReport(reportId);
      reports.value = reports.value.filter(r => r.id !== reportId);
    }
  } catch (e) {
    error.value = 'Ошибка при удалении отчета';
    console.error('Error deleting report:', e);
  }
};

const handleViewReport = (reportId: number) => {
  router.push(`/reports/${reportId}`);
};
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

        <!-- Секция отчетов -->
        <div class="reports-section card">
          <div class="section-header">
            <h3>Мои отчеты</h3>
            <button class="btn-secondary" @click="router.push('/reports')">
              + Создать отчет
            </button>
          </div>

          <!-- Список отчетов -->
          <div v-if="reports.length === 0" class="empty-state">
            <div class="empty-icon">📄</div>
            <p class="empty-title">Нет отчетов</p>
            <p class="empty-text">Создавайте отчеты, и они будут сохраняться здесь</p>
            <button class="btn-primary" @click="router.push('/reports')">
              Создать первый отчет
            </button>
          </div>

          <div v-else class="reports-list">
            <div
              v-for="report in reports"
              :key="report.id"
              class="report-item"
            >
              <div class="report-header">
                <h4 class="report-title">{{ report.title || `Отчет #${report.id}` }}</h4>
                <span class="report-date">{{ formatDate(report.created_at) }}</span>
              </div>

              <p v-if="report.description" class="report-description">
                {{ report.description }}
              </p>

              <div class="report-stats">
                <span v-if="report.entities_count" class="stat-badge">
                  📊 {{ report.entities_count }} сущностей
                </span>
                <span v-if="report.articles_count" class="stat-badge">
                  📰 {{ report.articles_count }} статей
                </span>
              </div>

              <div class="report-actions">
                <button class="action-btn view" @click="handleViewReport(report.id)">
                  👁️ Просмотр
                </button>
                <button class="action-btn delete" @click="handleDeleteReport(report.id)">
                  🗑️ Удалить
                </button>
              </div>
            </div>
          </div>
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

/* ===== ОТЧЕТЫ ===== */
.reports-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.btn-secondary {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: inherit;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  color: #9ca3af;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.empty-title {
  margin: 0 0 8px;
  font-size: 1.1rem;
  font-weight: 600;
  color: #d1d5db;
}

.empty-text {
  margin: 0 0 24px;
  font-size: 0.95rem;
  color: #6b7280;
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-item {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.report-item:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.15);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 12px;
}

.report-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  flex: 1;
}

.report-date {
  font-size: 0.85rem;
  color: #6b7280;
  white-space: nowrap;
}

.report-description {
  margin: 0 0 12px;
  font-size: 0.9rem;
  color: #d1d5db;
  line-height: 1.5;
}

.report-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.stat-badge {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  font-size: 0.85rem;
  color: #9ca3af;
}

.report-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}

.action-btn {
  flex: 1;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  color: #d1d5db;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.action-btn.delete:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #fca5a5;
}

@media (max-width: 768px) {
  .profile-header {
    flex-wrap: wrap;
  }

  .profile-stats {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .btn-secondary {
    width: 100%;
  }

  .report-header {
    flex-direction: column;
    gap: 8px;
  }

  .action-btn {
    padding: 10px 8px;
  }
}
</style>
