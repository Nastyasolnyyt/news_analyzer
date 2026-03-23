<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();
const notifications = 4;

const handleSearchClick = () => {
  router.push('/search');
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
      <button class="profile">
        <span class="user-initials">AK</span>
        <div>
          <strong>Analyst</strong>
        </div>
      </button>
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

.logo {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  color: #f8fafc;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  padding: 8px 0;
  cursor: pointer;
}

.logo-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--positive));
  display: inline-block;
}

.search {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.search input {
  width: 100%;
  padding: 10px 44px 10px 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: var(--surface-2);
  color: inherit;
  font-size: 0.95rem;
}

.search .kbd {
  position: absolute;
  right: 12px;
  font-size: 0.75rem;
  color: var(--text-dim);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  padding: 2px 6px;
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
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: var(--surface-2);
  display: grid;
  place-items: center;
  cursor: pointer;
  color: inherit;
}

.icon-button svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.6;
}

.dot {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--negative);
  color: #fff;
  border-radius: 999px;
  font-size: 0.7rem;
  line-height: 1;
  padding: 4px 6px;
}

.profile {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.user-initials {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 600;
}

small {
  color: var(--text-dim);
}

@media (max-width: 768px) {
  .header {
    flex-wrap: wrap;
  }

  .search {
    order: 3;
    width: 100%;
  }
}
</style>

