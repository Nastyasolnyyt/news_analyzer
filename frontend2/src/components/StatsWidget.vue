<script setup lang="ts">
defineProps<{
  count: number;
}>();
</script>

<template>
  <section class="widget">
    <div class="badge">Новые релевантные новости</div>
    <div class="value">
      {{ count }}
      <span class="unit">/ Всего новостей</span>
    </div>
    <p>Система отобрала новости с наивысшей релевантностью для ваших подписок.</p>
  </section>
</template>

<style scoped>
.widget {
  background: linear-gradient(135deg, var(--surface-2), var(--surface-3));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.badge {
  width: fit-content;
  font-size: 0.85rem;
  padding: 4px 10px;
  background: var(--accent-soft);
  color: var(--accent);
  border-radius: 999px;
  font-weight: 600;
}

.value {
  font-size: 2.5rem;
  font-weight: 600;
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.unit {
  font-size: 1rem;
  color: var(--text-dim);
}

p {
  margin: 0;
  color: var(--text-dim);
}
</style>

