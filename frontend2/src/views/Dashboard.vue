<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import HeaderBar from '../components/HeaderBar.vue';
import StatsWidget from '../components/StatsWidget.vue';
import TopEntities from '../components/TopEntities.vue';
import EventFeed from '../components/EventFeed.vue';
import RiskLegend from '../components/RiskLegend.vue';
import ActionPanel from '../components/ActionPanel.vue';
import { api, type News, type RiskLevel } from '../api/client';
 
const router = useRouter();
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8003';
// Реальные данные из API
const newsData = ref<News[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
 
// Статистика
const stats = computed(() => ({
  relevantNews: newsData.value.length,
}));
 
// Сущности для отображения (генерируем из новостей для демо)
const topEntities = computed(() => {
  const entities: any[] = [];
  const seen = new Set<string>();
  
  // Парсим названия компаний из источников
  const sources = new Map<string, number>();
  newsData.value.forEach(news => {
    if (news.source) {
      sources.set(news.source, (sources.get(news.source) || 0) + 1);
    }
  });
  
  // Берём топ источники как сущности
  Array.from(sources.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .forEach((entry, idx) => {
      const [source, count] = entry;
      if (!seen.has(source)) {
        entities.push({
          id: idx + 1,
          name: source,
          changePercent: Math.floor(Math.random() * 20 - 10),
          direction: Math.random() > 0.5 ? 'up' : 'down',
          category: 'Источник',
        });
        seen.add(source);
      }
    });
  
  return entities;
});
 
// События для ленты (последние новости)
const events = computed(() => {
  return newsData.value.slice(0, 4).map((n) => ({
    id: n.id,
    title: n.title,
    date: n.pub_date || n.date || new Date().toISOString(),
    source: n.source,
    summary: n.summary || n.text?.slice(0, 200),
    risk: n.risk_level || 'low',
    riskType: n.risk_type || null,  // ✅ Добавляем тип риска
  }));
});

const riskLegend: Array<{ level: RiskLevel; label: string; description: string }> = [
  { level: 'high', label: 'Высокий риск', description: 'Требует немедленной реакции' },
  { level: 'medium', label: 'Средний риск', description: 'Нужен мониторинг' },
  { level: 'low', label: 'Низкий риск', description: 'Информация к сведению' },
];
 
// Загрузка данных при монтировании
onMounted(async () => {
  try {
    loading.value = true;
    console.log('📊 Loading dashboard data...');
    
    const data = await api.getNews({
      page: 1,
      page_size: 20,
    });
    
    newsData.value = data.items;
    console.log('✅ Dashboard loaded:', data.items.length, 'items');
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки данных';
    console.error('❌ Dashboard error:', error.value);
  } finally {
    loading.value = false;
  }
});
 
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
    
    <div v-if="loading" class="loading-state">
      <p>⏳ Загружаем данные...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>❌ {{ error }}</p>
      <p style="font-size: 0.9rem; color: var(--text-dim); margin-top: 8px;">
        Проверьте, что backend запущен на {{ API_URL }}
      </p>
    </div>
    
    <main v-else class="layout">
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

