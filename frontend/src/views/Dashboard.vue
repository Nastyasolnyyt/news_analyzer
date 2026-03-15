<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import HeaderBar from '../components/HeaderBar.vue';
import StatsWidget from '../components/StatsWidget.vue';
import TopEntities from '../components/TopEntities.vue';
import EventFeed from '../components/EventFeed.vue';
import RiskLegend from '../components/RiskLegend.vue';
import ActionPanel from '../components/ActionPanel.vue';
import api from '../api'; 
// Оставляем сущности из моков, если бэкенд их пока не отдает
import { entities as mockEntities } from '../mockData';

const router = useRouter();

const articles = ref<any[]>([]);
const isLoading = ref(true);

onMounted(async () => {
  try {
    // ВАЖНО: Если бэкенд требует авторизацию, проверь, что в api.ts 
    // добавляется заголовок Authorization: Bearer <твой_токен>
    const data = await api.getPosts();
    
    // Проверяем структуру: на FastAPI обычно возвращается объект, 
    // в котором список лежит в ключе 'items'
    articles.value = data.items || data; 
  } catch (error) {
    console.error("Ошибка загрузки реальных данных:", error);
    // Если бэкенд пустой, можно временно оставить articles.value = []
  } finally {
    isLoading.value = false;
  }
});

const stats = computed(() => ({
  relevantNews: articles.value.length,
}));

// Сущности (пока моки, как ты просила)
const topEntities = computed(() => {
  return mockEntities
    .filter((e) => e.changePercent !== undefined)
    .map((e) => ({
      id: e.id,
      name: e.name,
      changePercent: e.changePercent!,
      direction: e.direction!,
      category: e.category || e.type,
    }));
});

// ПРАВИЛЬНЫЙ МАППИНГ: Берем данные из твоей БД (PostWithExternalModelsDTO)
const events = computed(() => {
  return articles.value.map((item: any) => {
    // В зависимости от того, как бэкенд отдает пост: 
    // либо item.post.title, либо просто item.title
    const post = item.post || item;
    const analysis = item.analysis || { tonality: 0 };

    return {
      id: post.id,
      title: post.title,
      date: post.created_at ? new Date(post.created_at).toLocaleDateString('ru-RU') : 'Сегодня',
      source: post.source || 'Источник',
      summary: post.content ? post.content.slice(0, 150) + '...' : 'Нет описания',
      // Тональность из БД переводим в уровень риска для EventFeed
      risk: analysis.tonality < -0.3 ? 'high' : (analysis.tonality < 0 ? 'medium' : 'low'),
    };
  });
});

const riskLegend = [
  { level: 'high', label: 'Высокий риск', description: 'Отрицательная тональность' },
  { level: 'medium', label: 'Средний риск', description: 'Нейтрально-негативно' },
  { level: 'low', label: 'Низкий риск', description: 'Положительно' },
];

const handleEntityClick = (entityId: number) => router.push(`/entity/${entityId}`);
const handleNewsClick = (newsId: number) => router.push(`/news/${newsId}`);
</script>

<template>
  <section class="dashboard">
    <HeaderBar />
    <main class="layout">
      <section class="primary">
        <StatsWidget :count="stats.relevantNews" />
        <TopEntities :entities="topEntities" @entity-click="handleEntityClick" />
        <div v-if="isLoading" style="color: var(--text-dim); padding: 20px;">Загрузка новостей...</div>
        <EventFeed v-else :events="events" @news-click="handleNewsClick" />
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