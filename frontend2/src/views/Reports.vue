<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { api, type News } from '../api/client';
 
const news = ref<News[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
 
const riskLevels = {
  high: { label: 'Высокий риск', color: '#ff6464' },
  medium: { label: 'Средний риск', color: '#ffa500' },
  low: { label: 'Низкий риск', color: '#4ade80' },
};
 
// Статистика по рискам
const riskStats = computed(() => {
  const stats = { high: 0, medium: 0, low: 0 };
  news.value.forEach(item => {
    const risk = (item.risk_level || 'low') as keyof typeof stats;
    if (risk in stats) {
      stats[risk]++;
    }
  });
  return stats;
});
 
// Статистика по источникам
const sourceStats = computed(() => {
  const sources = new Map<string, number>();
  news.value.forEach(item => {
    if (item.source) {
      sources.set(item.source, (sources.get(item.source) || 0) + 1);
    }
  });
  return Array.from(sources.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);
});
 
// Статистика по тональности
const sentimentStats = computed(() => {
  const stats = { positive: 0, neutral: 0, negative: 0 };
  news.value.forEach(item => {
    const sentiment = (item.sentiment_label || 'neutral') as keyof typeof stats;
    if (sentiment in stats) {
      stats[sentiment]++;
    }
  });
  return stats;
});
 
// Средние значения
const averageMetrics = computed(() => ({
  tonality: news.value.length > 0 
    ? (news.value.reduce((sum, n) => sum + (n.tonality || 0), 0) / news.value.length).toFixed(2)
    : 0,
  emotion: news.value.length > 0
    ? (news.value.reduce((sum, n) => sum + (n.emotion || 0), 0) / news.value.length).toFixed(2)
    : 0,
  relevance: news.value.length > 0
    ? (news.value.reduce((sum, n) => sum + (n.relevance || 0), 0) / news.value.length).toFixed(2)
    : 0,
}));
 
onMounted(async () => {
  try {
    loading.value = true;
    console.log('📊 Loading reports data...');
    
    const data = await api.getNews({
      page: 1,
      page_size: 100, // Берём больше для аналитики
    });
    
    news.value = data.items;
    console.log('✅ Reports loaded:', data.items.length, 'items');
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки отчёта';
    console.error('❌ Reports error:', error.value);
  } finally {
    loading.value = false;
  }
});
 
const handleExport = (format: 'json' | 'csv') => {
  if (format === 'json') {
    const data = {
      exportDate: new Date().toISOString(),
      totalItems: news.value.length,
      riskStats: riskStats.value,
      sourceStats: sourceStats.value,
      sentimentStats: sentimentStats.value,
      averageMetrics: averageMetrics.value,
      items: news.value,
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `report-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }
};
</script>
 
<template>
  <div class="reports-page">
    <header class="page-header">
      <h1>📊 Аналитика и отчёты</h1>
      <div class="header-actions">
        <button class="action-btn" @click="handleExport('json')" :disabled="loading">
          📥 Экспортировать JSON
        </button>
      </div>
    </header>
 
    <div v-if="loading" class="loading-state">
      <p>⏳ Загружаем аналитику...</p>
    </div>
 
    <div v-else-if="error" class="error-state">
      <p>❌ {{ error }}</p>
      <p style="font-size: 0.9rem; color: var(--text-dim); margin-top: 8px;">
        Проверьте подключение к API
      </p>
    </div>
 
    <div v-else class="reports-grid">
      <!-- Общая статистика -->
      <section class="stat-card card">
        <h3>Всего новостей</h3>
        <p class="stat-value">{{ news.length }}</p>
      </section>
 
      <!-- Риски -->
      <section class="stat-card card">
        <h3>По уровню риска</h3>
        <div class="risk-distribution">
          <div class="risk-item">
            <span class="risk-label">🔴 Высокий:</span>
            <span class="risk-count">{{ riskStats.high }}</span>
          </div>
          <div class="risk-item">
            <span class="risk-label">🟠 Средний:</span>
            <span class="risk-count">{{ riskStats.medium }}</span>
          </div>
          <div class="risk-item">
            <span class="risk-label">🟢 Низкий:</span>
            <span class="risk-count">{{ riskStats.low }}</span>
          </div>
        </div>
      </section>
 
      <!-- Тональность -->
      <section class="stat-card card">
        <h3>По тональности</h3>
        <div class="sentiment-distribution">
          <div class="sentiment-item">
            <span class="sentiment-label">😊 Позитив:</span>
            <span class="sentiment-count">{{ sentimentStats.positive }}</span>
          </div>
          <div class="sentiment-item">
            <span class="sentiment-label">😐 Нейтраль:</span>
            <span class="sentiment-count">{{ sentimentStats.neutral }}</span>
          </div>
          <div class="sentiment-item">
            <span class="sentiment-label">😞 Негатив:</span>
            <span class="sentiment-count">{{ sentimentStats.negative }}</span>
          </div>
        </div>
      </section>
 
      <!-- Средние метрики -->
      <section class="stat-card card">
        <h3>Средние метрики</h3>
        <div class="metrics">
          <div class="metric-item">
            <span class="metric-label">Тональность:</span>
            <span class="metric-value">{{ averageMetrics.tonality }}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Эмоция:</span>
            <span class="metric-value">{{ averageMetrics.emotion }}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Релевантность:</span>
            <span class="metric-value">{{ averageMetrics.relevance }}</span>
          </div>
        </div>
      </section>
 
      <!-- Топ источники -->
      <section class="sources-card card" v-if="sourceStats.length > 0">
        <h3>Топ источники</h3>
        <div class="sources-list">
          <div v-for="source in sourceStats" :key="source.name" class="source-item">
            <span class="source-name">{{ source.name }}</span>
            <span class="source-count">{{ source.count }}</span>
          </div>
        </div>
      </section>
 
      <!-- Список новостей -->
      <section class="news-list-card card">
        <h3>Обработанные новости</h3>
        <div class="news-list">
          <article v-for="item in news.slice(0, 10)" :key="item.id" class="news-item">
            <div class="news-meta">
              <span class="news-title">{{ item.title }}</span>
              <span 
                :class="['risk-badge', `risk-${item.risk_level || 'low'}`]"
              >
                {{ riskLevels[item.risk_level as keyof typeof riskLevels]?.label || 'Неизвестно' }}
              </span>
            </div>
            <div class="news-details">
              <span class="source">{{ item.source }}</span>
              <span class="date">{{ new Date(item.pub_date || item.date || '').toLocaleDateString('ru-RU') }}</span>
              <span v-if="item.sentiment_label" class="sentiment">{{ item.sentiment_label }}</span>
            </div>
          </article>
        </div>
        <p v-if="news.length > 10" class="more-items">
          ... и ещё {{ news.length - 10 }} новостей
        </p>
      </section>
    </div>
  </div>
</template>
<style scoped>
.report-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: var(--surface-1);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: var(--surface-2);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.logo:hover {
  background: var(--surface-3);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(120deg, var(--accent), var(--positive));
}

.header-actions {
  display: flex;
  gap: 12px;
}

.icon-btn {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: var(--surface-2);
  display: grid;
  place-items: center;
  color: inherit;
  cursor: pointer;
}

.icon-btn:hover {
  background: var(--surface-3);
}

.icon-btn svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.4;
}

.icon-btn.profile {
  width: auto;
  padding: 0 14px;
}

.card {
  background: var(--surface-2);
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 20px;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}

.overline {
  margin: 0;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  text-transform: uppercase;
}

.hero p {
  margin: 8px 0 0;
  color: #d0d6e2;
  max-width: 520px;
}

.primary {
  border: none;
  border-radius: 14px;
  padding: 12px 22px;
  background: var(--accent);
  color: white;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 12px 30px rgba(79, 138, 255, 0.35);
}

.criteria {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.criteria-line {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.label {
  font-size: 0.85rem;
  color: var(--text-dim);
}

.pill {
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(79, 138, 255, 0.15);
  color: #fff;
  padding: 6px 12px;
  margin-right: 6px;
}

.pill.neutral {
  background: rgba(255, 255, 255, 0.08);
}

.news header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.count {
  font-size: 0.85rem;
  color: var(--text-dim);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  padding: 6px 12px;
}

.news-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 320px;
  overflow: auto;
  padding-right: 6px;
}

.news-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.news-card:hover {
  border-color: var(--accent);
}

.title {
  margin: 0;
  font-weight: 600;
}

.meta {
  margin: 6px 0 0;
  color: var(--text-dim);
  font-size: 0.9rem;
}

.remove {
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: inherit;
  width: 32px;
  height: 32px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 1.2rem;
}

.remove:hover {
  background: rgba(255, 255, 255, 0.15);
}

.placeholder {
  margin: 0;
  color: var(--text-dim);
  text-align: center;
}

.stats ul {
  margin: 12px 0 0;
  padding-left: 18px;
  color: #d0d6e2;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.cta-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.secondary {
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: transparent;
  color: inherit;
  padding: 12px 18px;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 900px) {
  .actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .cta-buttons {
    width: 100%;
  }

  .cta-buttons button {
    flex: 1;
  }
}
</style>

