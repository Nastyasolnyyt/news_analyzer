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
</script>

<template>
  <section class="panel">
    <header>
      <div>
        <p class="overline">ТОП сущностей за 24 часа</p>
        <h2>Рост интереса</h2>
      </div>
      <button class="manage">См. все сущности</button>
    </header>
    <ul>
      <li v-for="entity in props.entities" :key="entity.id" class="entity" @click="handleClick(entity.id)">
        <div class="meta">
          <strong>{{ entity.name }}</strong>
          <span>{{ entity.category }}</span>
        </div>
        <div class="trend" :class="directionClass[entity.direction]">
          <span>{{ directionIcon[entity.direction] }}</span>
          {{ entity.changePercent }}%
        </div>
        <button class="profile-link" @click.stop="handleClick(entity.id)">Профиль</button>
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

.manage {
  border: none;
  background: transparent;
  color: var(--accent);
  font-weight: 600;
  cursor: pointer;
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

.profile-link {
  border: none;
  background: none;
  color: inherit;
  font-size: 0.9rem;
  opacity: 0.8;
  cursor: pointer;
  padding: 0;
}

@media (max-width: 700px) {
  .entity {
    grid-template-columns: 1fr;
  }

  .profile-link {
    justify-self: flex-start;
  }
}
</style>

