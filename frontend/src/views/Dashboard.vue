<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import HeaderBar from '../components/HeaderBar.vue';
import StatsWidget from '../components/StatsWidget.vue';
import TopEntities from '../components/TopEntities.vue';
import EventFeed from '../components/EventFeed.vue';
import RiskLegend from '../components/RiskLegend.vue';
import ActionPanel from '../components/ActionPanel.vue';
import { entities, news, type RiskLevel } from '../mockData';

const router = useRouter();

const stats = {
  relevantNews: news.length,
};

const topEntities = computed(() => {
  return entities
    .filter((e) => e.changePercent !== undefined)
    .map((e) => ({
      id: e.id,
      name: e.name,
      changePercent: e.changePercent!,
      direction: e.direction!,
      category: e.category || e.type,
    }));
});

const events = computed(() => {
  return news.slice(0, 4).map((n) => ({
    id: n.id,
    title: n.title,
    date: n.date,
    source: n.source,
    summary: n.summary,
    risk: n.riskLevel,
  }));
});

const riskLegend: Array<{ level: RiskLevel; label: string; description: string }> = [
  { level: 'high', label: 'Высокий риск', description: 'Требует немедленной реакции' },
  { level: 'medium', label: 'Средний риск', description: 'Нужен мониторинг' },
  { level: 'low', label: 'Низкий риск', description: 'Информация к сведению' },
];

const handleEntityClick = (entityId: number) => {
  router.push(`/entity/${entityId}`);
};

const handleNewsClick = (newsId: number) => {
  router.push(`/news/${newsId}`);
};
</script>

<template>
  <section class="dashboard">
    <HeaderBar />
    <main class="layout">
      <section class="primary">
        <StatsWidget :count="stats.relevantNews" />
        <TopEntities :entities="topEntities" @entity-click="handleEntityClick" />
        <EventFeed :events="events" @news-click="handleNewsClick" />
      </section>
      <aside class="secondary">
        <RiskLegend :levels="riskLegend" />
        <ActionPanel />
      </aside>
    </main>
  </section>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(280px, 360px);
  gap: 24px;
}

.primary {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.secondary {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

@media (max-width: 1024px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .secondary {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .secondary > * {
    flex: 1 1 240px;
  }
}
</style>

