<script setup lang="ts">
type TrendDirection = 'up' | 'down' | 'flat';

interface EntityTrend {
  id: number;
  name: string;
  changePercent: number;
  direction: TrendDirection;
  category: string;
}

const props = defineProps<{
  entities: EntityTrend[];
}>();

const emit = defineEmits<{
  (e: 'entity-click', id: number): void;
  (e: 'view-all', ): void;
}>();

const directionIcon: Record<TrendDirection, string> = {
  up: '▲',
  down: '▼',
  flat: '➜',
};

const directionClass: Record<TrendDirection, string> = {
  up: 'positive',
  down: 'negative',
  flat: 'neutral',
};

const handleClick = (entityId: number) => {
  emit('entity-click', entityId);
};

const handleViewAll = () => {
  emit('view-all');
};
</script>

<template>
  <section class="panel">
    <header>
      <div>
        <p class="overline">ТОП сущностей за 24 часа</p>
        <h2>Рост интереса</h2>
      </div>
      <button class="btn-secondary" @click="handleViewAll">См. все сущности</button>
    </header>
    <ul>
      <li v-for="entity in props.entities" :key="entity.id" class="entity" @click="handleClick(entity.id)">
        <div class="meta">
          <strong>{{ entity.name }}</strong>
          <span>{{ entity.category }}</span>
        </div>
        <div class="trend" :class="directionClass[entity.direction]">
          <span>{{ directionIcon[entity.direction] }}</span>
          {{ entity.changePercent }} упом.
        </div>
        <button class="btn-tertiary" @click.stop="handleClick(entity.id)">Профиль</button>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.panel {
  background: var(--surface-1);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overline {
  margin: 0;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  text-transform: uppercase;
}

h2 {
  margin: 4px 0 0;
  font-size: 1.3rem;
}

/* ✅ УНИФИЦИРОВАННЫЕ СТИЛИ КНОПОК */
.btn-secondary {
  padding: 8px 16px;
  background: rgba(var(--accent-rgb), 0.1);
  border: 1px solid var(--accent);
  color: var(--accent);
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: rgba(var(--accent-rgb), 0.2);
}

.btn-tertiary {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid rgba(var(--accent-rgb), 0.5);
  color: var(--accent);
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-tertiary:hover {
  background: rgba(var(--accent-rgb), 0.1);
  border-color: var(--accent);
}

ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.entity {
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-items: center;
  gap: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 16px 20px;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.entity:hover {
  border-color: var(--accent);
}

.meta strong {
  font-size: 1rem;
}

.meta span {
  display: block;
  font-size: 0.85rem;
  color: var(--text-dim);
}

.trend {
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
}

.trend.positive {
  color: var(--positive);
  background: rgba(34, 197, 94, 0.1);
}

.trend.negative {
  color: var(--negative);
  background: rgba(248, 113, 113, 0.1);
}

.trend.neutral {
  color: var(--text-dim);
  background: rgba(148, 163, 184, 0.12);
}

@media (max-width: 700px) {
  .entity {
    grid-template-columns: 1fr;
  }

  .btn-tertiary {
    justify-self: flex-start;
  }
}
</style>

