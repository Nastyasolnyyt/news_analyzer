<script setup lang="ts">
type RiskLevel = 'high' | 'medium' | 'low';

interface EventItem {
  id: number;
  title: string;
  date: string;
  source: string;
  summary: string;
  risk: RiskLevel;
}

defineProps<{
  events: EventItem[];
}>();

const emit = defineEmits<{
  (e: 'news-click', id: number): void;
}>();

const riskLabel: Record<RiskLevel, string> = {
  high: 'Высокий риск',
  medium: 'Средний риск',
  low: 'Низкий риск',
};

const handleClick = (newsId: number) => {
  emit('news-click', newsId);
};

</script>

<template>
  <section class="feed">
    <header>
      <div>
        <p class="overline">Последние события</p>
        <h2>Контекст и риск</h2>
      </div>
      <button>Экспорт ленты</button>
    </header>
    <div class="cards">
      <article v-for="item in events" :key="item.id" class="card" @click="handleClick(item.id)">
        <div class="card-header">
          <div>
            <p class="source">{{ item.source }}</p>
            <h3>{{ item.title }}</h3>
          </div>
          <span class="date">{{ item.date }}</span>
        </div>
        <p class="summary">
          {{ item.summary }}
        </p>
        <div class="footer">
          <span class="risk" :data-risk="item.risk">{{ riskLabel[item.risk] }}</span>
          <button class="inline-link" @click.stop="handleClick(item.id)">Открыть источник</button>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.feed {
  background: var(--surface-1);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

header button {
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: transparent;
  color: inherit;
  padding: 8px 14px;
  font-size: 0.85rem;
  cursor: pointer;
}

.cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  background: var(--surface-2);
  border-radius: 18px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  display: flex;
  flex-direction: column;
  gap: 12px;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.card:hover {
  border-color: var(--accent);
}

.card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.source {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

h3 {
  margin: 4px 0 0;
  font-size: 1.05rem;
}

.date {
  font-size: 0.85rem;
  color: var(--text-dim);
}

.summary {
  margin: 0;
  color: #cfd3dc;
  font-size: 0.95rem;
}

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.risk {
  font-size: 0.85rem;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 999px;
}

.risk[data-risk='high'] {
  color: var(--negative);
  background: rgba(248, 113, 113, 0.12);
}

.risk[data-risk='medium'] {
  color: #facc15;
  background: rgba(250, 204, 21, 0.12);
}

.risk[data-risk='low'] {
  color: var(--positive);
  background: rgba(34, 197, 94, 0.12);
}

.inline-link {
  border: none;
  background: none;
  color: var(--accent);
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 640px) {
  header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .card-header {
    flex-direction: column;
  }
}
</style>

