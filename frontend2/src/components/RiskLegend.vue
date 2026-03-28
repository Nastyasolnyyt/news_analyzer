<script setup lang="ts">
type RiskLevel = 'high' | 'medium' | 'low';

interface LegendItem {
  level: RiskLevel;
  label: string;
  description: string;
}

defineProps<{
  levels: LegendItem[];
}>();
</script>

<template>
  <section class="legend">
    <header>
      <p class="overline">Легенда</p>
      <h3>Уровни риска</h3>
    </header>
    <ul>
      <li v-for="item in levels" :key="item.level">
        <span class="marker" :data-risk="item.level"></span>
        <div>
          <strong>{{ item.label }}</strong>
          <p>{{ item.description }}</p>
        </div>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.legend {
  background: var(--surface-1);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 20px;
}

.overline {
  margin: 0;
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  color: var(--text-dim);
  text-transform: uppercase;
}

h3 {
  margin: 4px 0 16px;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

li {
  display: flex;
  align-items: center;
  gap: 12px;
}

.marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.marker[data-risk='high'] {
  background: var(--negative);
  box-shadow: 0 0 12px rgba(248, 113, 113, 0.5);
}

.marker[data-risk='medium'] {
  background: #facc15;
  box-shadow: 0 0 12px rgba(250, 204, 21, 0.4);
}

.marker[data-risk='low'] {
  background: var(--positive);
  box-shadow: 0 0 12px rgba(34, 197, 94, 0.4);
}

p {
  margin: 4px 0 0;
  color: var(--text-dim);
  font-size: 0.85rem;
}
</style>

