<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import HeaderBar from '../components/HeaderBar.vue';
import StatsWidget from '../components/StatsWidget.vue';
import TopEntities from '../components/TopEntities.vue';
import EventFeed from '../components/EventFeed.vue';
import RiskLegend from '../components/RiskLegend.vue';
import api from '../api'; 

const router = useRouter();
const articles = ref<any[]>([]);
const totalNews = ref(0);
const isLoading = ref(true);

onMounted(async () => {
  try {
    const data = await api.getPosts();
    // Сохраняем сырые данные как они есть (с вложенными post и analysis)
    articles.value = data.items || [];
    totalNews.value = data.total || articles.value.length;
  } catch (error) {
    console.error("Ошибка загрузки:", error);
  } finally {
    isLoading.value = false;
  }
});

// ГЛАВНОЕ: Формируем список для ленты
const events = computed(() => {
  return articles.value.map((item: any) => {
    // Безопасно достаем данные. Если структуры разные, проверяем оба варианта.
    const post = item.post || item; 
    const analysis = item.analysis || {};
    
    const dbRisk = analysis.risk_level || 
                   item.risk_level|| 
                   (item.risks && item.risks[0]?.risk_level) || 
                   'low';

    return {
      id: post.id,
      title: post.title,
      date: new Date(post.created_at).toLocaleString('ru-RU'),
      source: post.source,
      // Берем content или text (смотря что заполнено в БД)
      summary: (post.content || post.text || '').substring(0, 160) + '...',
      risk: dbRisk as 'high' | 'medium' | 'low'
    };
  });
});

// Вытягиваем сущности динамически
const topEntities = computed(() => {
  // Ищем сущности либо в корне, либо внутри post
  const allEntities = articles.value.flatMap(item => (item.post?.entities || item.entities || []));
  const unique = Array.from(new Map(allEntities.map(e => [e.text, e])).values());
  
  return unique.slice(0, 5).map((e: any) => ({
    id: e.id,
    name: e.text,
    changePercent: 0, 
    direction: 'flat' as const,
    category: e.type,
  }));
});

type RiskLevel = 'high' | 'medium' | 'low';
const riskLegend: { level: RiskLevel; label: string; description: string }[] = [
  { level: 'high', label: 'Высокий', description: 'Критическая угроза' },
  { level: 'medium', label: 'Средний', description: 'Требует внимания' },
  { level: 'low', label: 'Низкий', description: 'Информационный фон' }
];
    
const handleNewsClick = (id: number) => router.push(`/news/${id}`);
const handleEntityClick = (id: number) => router.push(`/entity/${id}`);
</script>

<template>
  <section class="dashboard">
    <HeaderBar />
    <main class="layout">
      <section class="primary">
        <StatsWidget :count="totalNews" />
        
        <TopEntities 
          v-if="topEntities.length > 0" 
          :entities="topEntities" 
          @entity-click="handleEntityClick" 
        />
        
        <div v-if="isLoading" class="loading">Загрузка данных из API...</div>
        
        <template v-else>
          <EventFeed 
            v-if="events.length > 0" 
            :events="events" 
            @news-click="handleNewsClick" 
          />
          <div v-else class="empty-state">
            <p>База данных пуста. Записи появятся здесь после работы парсера.</p>
          </div>
        </template>
      </section>
      
      <aside class="secondary">
        <RiskLegend :levels="riskLegend" />
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