<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import HeaderBar from '../components/HeaderBar.vue';
import StatsWidget from '../components/StatsWidget.vue';
import TopEntities from '../components/TopEntities.vue';
import EventFeed from '../components/EventFeed.vue';
import RiskLegend from '../components/RiskLegend.vue';
import ActionPanel from '../components/ActionPanel.vue';
import { api, type News, type RiskLevel, type Entity } from '../api/client';
 
const router = useRouter();
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8003';
// Реальные данные из API
const newsData = ref<News[]>([]);
const allEntities = ref<Entity[]>([]);
const topEntitiesData = ref<Array<{
  id: number;
  name: string;
  changePercent: number;
  direction: 'up' | 'down' | 'flat';
  category: string;
}>>([]);
const loading = ref(true);
const error = ref<string | null>(null);
 
// Статистика
const totalNewsCount = ref(0);
const stats = computed(() => ({
  relevantNews: totalNewsCount.value,
}));
 
// Сущности для отображения (топ за 24 часа из API)
const topEntities = computed(() => {
  return topEntitiesData.value.map((entity) => ({
    id: entity.id,
    name: entity.name,
    changePercent: entity.changePercent,
    direction: entity.direction,
    category: entity.category,
  }));
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
    riskType: n.risk_type || null,  //  Добавляем тип риска
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
    console.log('Loading dashboard data...');
    
    // Загружаем новости
    const newsResponse = await api.getNews({
      page: 1,
      page_size: 20,
    });
    newsData.value = newsResponse.items;
    totalNewsCount.value = newsResponse.total || newsResponse.items.length;

    
    // Загружаем топ сущностей за 24 часа (реальные данные из API)
    const topEntitiesRaw = await api.getTopEntities24h({ limit: 5 });
    topEntitiesData.value = topEntitiesRaw.map((e: any) => ({
      id: e.id,
      name: e.name,
      changePercent: e.changePercent,
      direction: e.direction,
      category: mapEntityTypeToCategory(e.entity_type),
    }));
    
    // Загружаем все сущности (для других целей)
    const entitiesResult = await api.getEntities({ limit: 10 });
    allEntities.value = entitiesResult.items;
    
    console.log('Dashboard loaded:', {
      newsItems: newsData.value.length,
      topEntities: topEntitiesData.value.length,
      entities: allEntities.value.length
    });
  } catch (e: any) {
    if (e.response?.data?.detail) {
      error.value = typeof e.response.data.detail === 'string'
        ? e.response.data.detail
        : JSON.stringify(e.response.data.detail);
    } else if (e.response?.data?.message) {
      error.value = typeof e.response.data.message === 'string'
        ? e.response.data.message
        : JSON.stringify(e.response.data.message);
    } else if (e.message) {
      error.value = e.message;
    } else if (typeof e === 'string') {
      error.value = e;
    } else {
      error.value = 'Ошибка загрузки данных';
    }
    console.error('❌ Dashboard error:', e);
  } finally {
    loading.value = false;
  }
});

// Функция для маппинга типа сущности на категорию для отображения
function mapEntityTypeToCategory(entityType?: string): string {
  if (!entityType) return 'Сущность';
  const type = entityType.toLowerCase();
  if (type.includes('per') || type.includes('person') || type.includes('персона')) return 'Персона';
  if (type.includes('company') || type.includes('org') || type.includes('организация')) return 'Компания';
  if (type.includes('event') || type.includes('событие')) return 'Событие';
  if (type.includes('loc') || type.includes('location') || type.includes('локация')) return 'Локация';
  return 'Сущность';
}
 
const handleEntityClick = (entityId: number) => {
  router.push(`/entity/${entityId}`);
};

const handleViewAllEntities = () => {
  router.push('/entities');
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
        <TopEntities :entities="topEntities" @entity-click="handleEntityClick" @view-all="handleViewAllEntities" />
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

