<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();
</script>

<template>
  <section class="action-panel">
    <h3>Быстрые действия</h3>
    <p>Сформируйте отчёт или уточните фильтры мониторинга за пару кликов.</p>
    <div class="cta">
      <button class="primary" @click="router.push('/reports')">Создать отчёт</button>
      <button class="secondary" @click="router.push('/search')">Настроить фильтры</button>
    </div>
  </section>
</template>

<style scoped>
.action-panel {
  background: linear-gradient(135deg, rgba(79, 138, 255, 0.15), rgba(15, 18, 26, 0.9));
  border-radius: 20px;
  border: 1px solid rgba(79, 138, 255, 0.25);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

h3 {
  margin: 0;
}

p {
  margin: 0;
  color: var(--text-dim);
}

.cta {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}

button {
  height: 44px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.primary {
  background: var(--accent);
  color: white;
  box-shadow: 0 12px 24px rgba(79, 138, 255, 0.3);
}

.secondary {
  background: rgba(255, 255, 255, 0.08);
  color: inherit;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

@media (min-width: 768px) {
  .cta {
    flex-direction: row;
  }

  button {
    flex: 1;
  }
}
</style>

