<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api, type UserDTO } from '../api/client';

const router = useRouter();
const notifications = ref(4);
const user = ref<UserDTO | null>(null);
const showMenu = ref(false);

const getUserInitials = (name: string) => {
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
  } catch (e) {
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
</script>

<template>
  <header class="header">
    <label class="search" @click="handleSearchClick">
      <input type="text" placeholder="Поиск по компаниям, персонам, событиям" readonly />
      <span class="kbd">⌘K</span>
    </label>
    <div class="actions">
      <button class="icon-button" aria-label="notifications" @click="router.push('/notifications')">
        <span class="dot" :data-count="notifications">{{ notifications }}</span>
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M12 2a6 6 0 0 0-6 6v3.382l-.894 2.235A1 1 0 0 0 6.056 15h11.888a1 1 0 0 0 .95-1.383L18 11.382V8a6 6 0 0 0-6-6Z"
          />
          <path d="M9 18a3 3 0 0 0 6 0" />
        </svg>
      </button>

      <div class="profile-menu">
        <button class="profile" @click="toggleMenu">
          <span class="user-initials">{{ user ? getUserInitials(user.name) : 'AK' }}</span>
          <div>
            <strong>{{ user ? user.name : 'Analyst' }}</strong>
          </div>
        </button>

        <div v-if="showMenu" class="menu-popup">
          <div class="menu-item user-info">
            <p class="user-name">{{ user?.name }}</p>
            <p class="user-login">{{ user?.login }}</p>
          </div>
          <div class="menu-divider"></div>
          <button class="menu-item" @click="router.push('/notifications')">
            ⚙️ Настройки
          </button>
          <button class="menu-item logout" @click="handleLogout">
            🚪 Выход
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--surface-1);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 16px 20px;
}

.search {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 0 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.search input {
  flex: 1;
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 0.9rem;
  outline: none;
}

.search input::placeholder {
  color: #6b7280;
}

.kbd {
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  font-size: 0.75rem;
  color: #9ca3af;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-button {
  position: relative;
  width: 44px;
  height: 44px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  color: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.icon-button:hover {
  border-color: rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.08);
}

.icon-button svg {
  width: 20px;
  height: 20px;
  stroke: currentColor;
  fill: none;
  stroke-width: 1.5;
}

.dot {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  background: linear-gradient(120deg, #ef4444, #f87171);
  border: 2px solid var(--surface-1);
  border-radius: 50%;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
}

.profile-menu {
  position: relative;
}

.profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  color: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
}

.profile:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.user-initials {
  width: 32px;
  height: 32px;
  background: linear-gradient(120deg, #4f8aff, #3b82f6);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.profile div {
  display: flex;
  flex-direction: column;
  text-align: left;
  font-size: 0.85rem;
}

.profile strong {
  color: #fff;
  font-weight: 600;
}

.menu-popup {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: var(--surface-2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  min-width: 200px;
  box-shadow: 0 20px 25px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  overflow: hidden;
}

.user-info {
  padding: 12px 16px;
  pointer-events: none;
}

.user-name {
  margin: 0;
  font-weight: 600;
  color: #fff;
  font-size: 0.9rem;
}

.user-login {
  margin: 4px 0 0;
  color: #9ca3af;
  font-size: 0.8rem;
}

.menu-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
}

.menu-item {
  width: 100%;
  text-align: left;
  padding: 12px 16px;
  background: none;
  border: none;
  color: #d1d5db;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.menu-item.logout:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #fca5a5;
}
</style>
