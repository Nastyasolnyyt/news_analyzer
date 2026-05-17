<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { api, type News } from '../api/client';
 
const news = ref<News[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

// Фильтры
const riskFilter = ref<string>('all');
const sentimentFilter = ref<string>('all');
const riskTypeFilter = ref<string>('all');
const selectedNewsIds = ref<Set<number>>(new Set());
const selectMode = ref<'all' | 'manual'>('all');
 
const riskLevels: Record<string, { label: string; color: string }> = {
  high: { label: 'Высокий риск', color: '#ff6464' },
  medium: { label: 'Средний риск', color: '#ffa500' },
  low: { label: 'Низкий риск', color: '#4ade80' },
};

// Отфильтрованные новости
const filteredNews = computed(() => {
  return news.value.filter(item => {
    const riskMatch = riskFilter.value === 'all' || item.risk_level === riskFilter.value;
    const sentimentMatch = sentimentFilter.value === 'all' || item.sentiment_label === sentimentFilter.value;
    const riskTypeMatch = riskTypeFilter.value === 'all' || item.risk_type === riskTypeFilter.value;
    return riskMatch && sentimentMatch && riskTypeMatch;
  });
});

// Новости для отчета (все или выбранные вручную)
const reportNews = computed<News[]>(() => {
  if (selectMode.value === 'all') {
    return filteredNews.value;
  } else {
    return filteredNews.value.filter((item: News) => selectedNewsIds.value.has(item.id));
  }
});
 
// Статистика по рискам
const riskStats = computed(() => {
  const stats = { high: 0, medium: 0, low: 0 };
  reportNews.value.forEach(item => {
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
  reportNews.value.forEach(item => {
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
  reportNews.value.forEach(item => {
    const sentiment = (item.sentiment_label || 'neutral') as keyof typeof stats;
    if (sentiment in stats) {
      stats[sentiment]++;
    }
  });
  return stats;
});
 
// Статистика по типам риска
const riskTypeStats = computed(() => {
  const typeMap = new Map<string, number>();
  reportNews.value.forEach(item => {
    if (item.risk_type) {
      typeMap.set(item.risk_type, (typeMap.get(item.risk_type) || 0) + 1);
    }
  });
  return Array.from(typeMap.entries())
    .map(([type, count]) => ({ type, count }))
    .sort((a, b) => b.count - a.count);
});
 
// Средние значения
const averageMetrics = computed(() => ({
  tonality: reportNews.value.length > 0 
    ? (reportNews.value.reduce((sum, n) => sum + (n.tonality || 0), 0) / reportNews.value.length).toFixed(2)
    : 0,
  emotion: reportNews.value.length > 0
    ? (reportNews.value.reduce((sum, n) => sum + (n.emotion || 0), 0) / reportNews.value.length).toFixed(2)
    : 0,
  relevance: reportNews.value.length > 0
    ? (reportNews.value.reduce((sum, n) => sum + (n.relevance || 0), 0) / reportNews.value.length).toFixed(2)
    : 0,
}));
 
onMounted(async () => {
  try {
    loading.value = true;
    console.log('Loading reports data...');
    
    const data = await api.getNews({
      page: 1,
      page_size: 500,  // Увеличили лимит до 500 новостей
    });
    
    news.value = data.items;
    console.log('Reports loaded:', data.items.length, 'items');
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
      error.value = 'Ошибка загрузки отчёта';
    }
    console.error('Reports error:', e);
  } finally {
    loading.value = false;
  }
});
 
const handleExport = (format: 'json' | 'csv') => {
  const reportData = {
    exportDate: new Date().toISOString(),
    totalItems: reportNews.value.length,
    filters: {
      risk: riskFilter.value,
      sentiment: sentimentFilter.value,
    },
    statistics: {
      risks: riskStats.value,
      sentiments: sentimentStats.value,
      riskTypes: riskTypeStats.value,
      sources: sourceStats.value,
      averageMetrics: averageMetrics.value,
    },
    items: reportNews.value,
  };
  
  if (format === 'json') {
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `report-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  } else if (format === 'csv') {
    // CSV export
    let csv = 'Дата,Заголовок,Источник,Уровень риска,Тональность\n';
    reportNews.value.forEach(item => {
      const date = new Date(item.pub_date || item.date || '').toLocaleDateString('ru-RU');
      const title = `"${item.title.replace(/"/g, '""')}"`;
      const source = item.source || '';
      const risk = item.risk_level || 'unknown';
      const sentiment = item.sentiment_label || 'unknown';
      csv += `${date},${title},${source},${risk},${sentiment}\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `report-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }
};

const resetFilters = () => {
  riskFilter.value = 'all';
  sentimentFilter.value = 'all';
  riskTypeFilter.value = 'all';
  selectMode.value = 'all';
  selectedNewsIds.value.clear();
};

const toggleNewsSelection = (id: number) => {
  if (selectedNewsIds.value.has(id)) {
    selectedNewsIds.value.delete(id);
  } else {
    selectedNewsIds.value.add(id);
  }
};

const selectAllFiltered = () => {
  reportNews.value.forEach(item => selectedNewsIds.value.add(item.id));
};

const clearSelection = () => {
  selectedNewsIds.value.clear();
};

const reloadPage = () => {
  location.reload();
};
</script>
 
<template>
  <div class="reports-page">
    <!-- Header -->
    <header class="page-header">
      <div>
        <h1>Аналитика и отчёты</h1>
        <p class="subtitle">Детальная аналитика по обработанным новостям</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="handleExport('json')" :disabled="loading">
          Экспорт JSON
        </button>
        <button class="btn-secondary" @click="handleExport('csv')" :disabled="loading">
          Экспорт CSV
        </button>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загружаем аналитику...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button class="btn-secondary" @click="reloadPage">Попробовать снова</button>
    </div>

    <!-- Main Content -->
    <div v-else class="report-content">
      <!-- Filters -->
      <section class="filters-section">
        <div class="filter-group">
          <label>Фильтр по риску:</label>
          <select v-model="riskFilter" class="filter-select">
            <option value="all">Все уровни</option>
            <option value="high">Высокий</option>
            <option value="medium">Средний</option>
            <option value="low">Низкий</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Фильтр по тональности:</label>
          <select v-model="sentimentFilter" class="filter-select">
            <option value="all">Все</option>
            <option value="positive">Позитив</option>
            <option value="neutral">Нейтраль</option>
            <option value="negative">Негатив</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Тип риска:</label>
          <select v-model="riskTypeFilter" class="filter-select">
            <option value="all">Все типы</option>
            <option value="политический">Политический</option>
            <option value="экономический">Экономический</option>
            <option value="социальный">Социальный</option>
          </select>
        </div>

        <button class="btn-reset" @click="resetFilters">↻ Сбросить</button>

        <span class="filter-info">
          Показано <strong>{{ reportNews.length }}</strong> из <strong>{{ news.length }}</strong> новостей
        </span>
      </section>

      <!-- Selection Mode -->
      <section class="selection-section">
        <div class="selection-controls">
          <label class="radio-label">
            <input type="radio" v-model="selectMode" value="all" />
            Все новости из фильтра
          </label>
          <label class="radio-label">
            <input type="radio" v-model="selectMode" value="manual" />
            Выбрать вручную
          </label>
        </div>
        
        <div v-if="selectMode === 'manual'" class="manual-controls">
          <button class="btn-secondary" @click="selectAllFiltered">Выбрать все</button>
          <button class="btn-secondary" @click="clearSelection">Снять все</button>
          <span class="selection-info">
            Выбрано: <strong>{{ selectedNewsIds.size }}</strong>
          </span>
        </div>
      </section>

      <!-- Stats Grid -->
      <div class="stats-grid">
        <!-- Total news -->
        <section class="stat-card">
          <p class="stat-label">Всего новостей</p>
          <p class="stat-value">{{ reportNews.length }}</p>
          <p class="stat-hint">в выборке</p>
        </section>

        <!-- Risk distribution -->
        <section class="stat-card">
          <p class="stat-label">По уровню риска</p>
          <div class="risk-bars">
            <div class="risk-bar">
              <span class="risk-badge high"></span>
              <div class="risk-bar-fill-container">
                <span 
                  class="risk-bar-fill" 
                  :style="{ width: riskStats.high + riskStats.medium + riskStats.low > 0 ? (riskStats.high / (riskStats.high + riskStats.medium + riskStats.low) * 100) + '%' : '0%' }"
                ></span>
              </div>
              <span class="risk-count">{{ riskStats.high }}</span>
            </div>
            <div class="risk-bar">
              <span class="risk-badge medium"></span>
              <div class="risk-bar-fill-container">
                <span 
                  class="risk-bar-fill medium" 
                  :style="{ width: riskStats.high + riskStats.medium + riskStats.low > 0 ? (riskStats.medium / (riskStats.high + riskStats.medium + riskStats.low) * 100) + '%' : '0%' }"
                ></span>
              </div>
              <span class="risk-count">{{ riskStats.medium }}</span>
            </div>
            <div class="risk-bar">
              <span class="risk-badge low"></span>
              <div class="risk-bar-fill-container">
                <span 
                  class="risk-bar-fill low" 
                  :style="{ width: riskStats.high + riskStats.medium + riskStats.low > 0 ? (riskStats.low / (riskStats.high + riskStats.medium + riskStats.low) * 100) + '%' : '0%' }"
                ></span>
              </div>
              <span class="risk-count">{{ riskStats.low }}</span>
            </div>
          </div>
        </section>

        <!-- Sentiment distribution -->
        <section class="stat-card">
          <p class="stat-label">По тональности</p>
          <div class="sentiment-bars">
            <div class="sentiment-bar">
              <span class="sentiment-badge positive"></span>
              <div class="sentiment-bar-fill-container">
                <span 
                  class="sentiment-bar-fill" 
                  :style="{ width: sentimentStats.positive + sentimentStats.neutral + sentimentStats.negative > 0 ? (sentimentStats.positive / (sentimentStats.positive + sentimentStats.neutral + sentimentStats.negative) * 100) + '%' : '0%' }"
                ></span>
              </div>
              <span class="sentiment-count">{{ sentimentStats.positive }}</span>
            </div>
            <div class="sentiment-bar">
              <span class="sentiment-badge neutral"></span>
              <div class="sentiment-bar-fill-container">
                <span 
                  class="sentiment-bar-fill neutral" 
                  :style="{ width: sentimentStats.positive + sentimentStats.neutral + sentimentStats.negative > 0 ? (sentimentStats.neutral / (sentimentStats.positive + sentimentStats.neutral + sentimentStats.negative) * 100) + '%' : '0%' }"
                ></span>
              </div>
              <span class="sentiment-count">{{ sentimentStats.neutral }}</span>
            </div>
            <div class="sentiment-bar">
              <span class="sentiment-badge negative"></span>
              <div class="sentiment-bar-fill-container">
                <span 
                  class="sentiment-bar-fill negative" 
                  :style="{ width: sentimentStats.positive + sentimentStats.neutral + sentimentStats.negative > 0 ? (sentimentStats.negative / (sentimentStats.positive + sentimentStats.neutral + sentimentStats.negative) * 100) + '%' : '0%' }"
                ></span>
              </div>
              <span class="sentiment-count">{{ sentimentStats.negative }}</span>
            </div>
          </div>
        </section>

        <!-- Average metrics -->
        <section class="stat-card">
          <p class="stat-label">Средние метрики</p>
          <div class="metrics-list">
            <div class="metric">
              <span>Тональность:</span>
              <strong>{{ averageMetrics.tonality }}</strong>
            </div>
            <div class="metric">
              <span>Эмоция:</span>
              <strong>{{ averageMetrics.emotion }}</strong>
            </div>
            <div class="metric">
              <span>Релевантность:</span>
              <strong>{{ averageMetrics.relevance }}</strong>
            </div>
          </div>
        </section>
      </div>

      <!-- Risk Types -->
      <section v-if="riskTypeStats.length > 0" class="detail-card">
        <h2>Типы рисков</h2>
        <div class="risk-types-list">
          <div v-for="(type, idx) in riskTypeStats" :key="idx" class="risk-type-item">
            <span class="type-name">{{ type.type }}</span>
            <span class="type-count">{{ type.count }}</span>
          </div>
        </div>
      </section>

      <!-- Top Sources -->
      <section v-if="sourceStats.length > 0" class="detail-card">
        <h2>Топ источники</h2>
        <div class="sources-list">
          <div v-for="(source, idx) in sourceStats" :key="idx" class="source-item">
            <span class="source-name">{{ source.name }}</span>
            <span class="source-bar">
              <span 
                class="bar-fill" 
                :style="{ width: sourceStats.length > 0 ? (source.count / sourceStats[0].count * 100) + '%' : '0%' }"
              ></span>
            </span>
            <span class="source-count">{{ source.count }}</span>
          </div>
        </div>
      </section>

      <!-- Sample News -->
      <section v-if="reportNews.length > 0" class="detail-card">
        <h2>Примеры новостей (первые 5)</h2>
        <div class="news-samples">
          <article v-for="(item, idx) in reportNews.slice(0, 5)" :key="idx" class="sample-news">
            <div class="sample-header">
              <h4>{{ item.title }}</h4>
              <span :class="['risk-label', `risk-${item.risk_level}`]">
                {{ riskLevels[item.risk_level || 'low']?.label || 'Неизвестно' }}
              </span>
            </div>
            <div class="sample-meta">
              <span>{{ item.source }}</span>
              <span>{{ new Date(item.pub_date || item.date || '').toLocaleDateString('ru-RU') }}</span>
            </div>
          </article>
        </div>
      </section>

      <!-- All News List for Manual Selection -->
      <section v-if="selectMode === 'manual'" class="detail-card">
        <h2>Все новости для выбора</h2>
        <div class="news-list-selection">
          <article 
            v-for="item in filteredNews" 
            :key="item.id" 
            :class="['news-item', { selected: selectedNewsIds.has(item.id) }]"
            @click="toggleNewsSelection(item.id)"
          >
            <div class="news-checkbox">
              <input type="checkbox" :checked="selectedNewsIds.has(item.id)" />
            </div>
            <div class="news-content">
              <h4>{{ item.title }}</h4>
              <div class="news-meta">
                <span class="source">{{ item.source }}</span>
                <span class="date">{{ new Date(item.pub_date || item.date || '').toLocaleDateString('ru-RU') }}</span>
                <span :class="['risk-badge', `risk-${item.risk_level}`]">
                  {{ item.risk_level || 'unknown' }}
                </span>
                <span :class="['sentiment-badge', `sentiment-${item.sentiment_label}`]">
                  {{ item.sentiment_label || 'neutral' }}
                </span>
                <span v-if="item.risk_type" class="type-badge">
                  {{ item.risk_type }}
                </span>
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.reports-page {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding-bottom: 40px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
}

.subtitle {
  margin: 8px 0 0;
  color: var(--text-dim);
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  padding: 10px 18px;
  background: rgba(79, 138, 255, 0.1);
  border: 1px solid var(--accent);
  color: var(--accent);
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(79, 138, 255, 0.2);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Loading state */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(79, 138, 255, 0.2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  font-size: 1.1rem;
  color: var(--text-dim);
  margin: 0;
}

/* Error state */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 16px;
  background: rgba(248, 113, 113, 0.05);
  border: 1px solid rgba(248, 113, 113, 0.2);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
}

.error-state p {
  color: var(--negative);
  font-size: 1rem;
  margin: 0;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* Filters */
.filters-section {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--surface-1);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 18px 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 0.9rem;
  color: var(--text-dim);
  white-space: nowrap;
}

.filter-select {
  padding: 8px 12px;
  background: var(--surface-2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: var(--text-base);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-select:hover {
  border-color: var(--accent);
}

.btn-reset {
  padding: 8px 14px;
  background: transparent;
  border: 1px solid rgba(79, 138, 255, 0.5);
  color: var(--accent);
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-reset:hover {
  background: rgba(79, 138, 255, 0.1);
  border-color: var(--accent);
}

.filter-info {
  color: var(--text-dim);
  font-size: 0.85rem;
  white-space: nowrap;
  margin-left: auto;
}

.filter-info strong {
  color: var(--accent);
  font-weight: 600;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.stat-card {
  background: var(--surface-1);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-label {
  margin: 0;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-dim);
  font-weight: 600;
}

.stat-value {
  margin: 0;
  font-size: 2.2rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent), #22c55e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-hint {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-dim);
}

.risk-bars,
.sentiment-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.risk-bar,
.sentiment-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.risk-count,
.sentiment-count {
  font-weight: 600;
  min-width: 30px;
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: var(--text-dim);
}

.metric strong {
  color: var(--accent);
  font-weight: 600;
}

/* Detail cards */
.detail-card {
  background: var(--surface-1);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 24px;
}

.detail-card h2 {
  margin: 0 0 20px;
  font-size: 1.2rem;
  font-weight: 700;
}

.risk-types-list,
.sources-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-type-item,
.source-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
  font-size: 0.95rem;
}

.type-name,
.source-name {
  font-weight: 500;
}

.type-count {
  font-weight: 600;
  min-width: 40px;
  text-align: right;
}

.source-bar {
  flex: 1;
  height: 24px;
  background: rgba(79, 138, 255, 0.1);
  border-radius: 999px;
  margin: 0 12px;
  overflow: hidden;
}

.bar-fill {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--accent), #22c55e);
  border-radius: 999px;
  transition: width 0.3s ease;
}

.source-count {
  font-weight: 600;
  min-width: 40px;
  text-align: right;
  color: var(--accent);
}

/* Selection Section */
.selection-section {
  background: var(--surface-1);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 18px 20px;
}

.selection-controls {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  color: var(--text-base);
}

.radio-label input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.manual-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.selection-info {
  margin-left: auto;
  font-size: 0.9rem;
  color: var(--text-dim);
}

.selection-info strong {
  color: var(--accent);
}

/* News List Selection */
.news-list-selection {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 500px;
  overflow-y: auto;
  padding-right: 6px;
}

.news-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  cursor: pointer;
  transition: all 0.2s ease;
}

.news-item:hover {
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.04);
}

.news-item.selected {
  border-color: var(--accent);
  background: rgba(79, 138, 255, 0.1);
}

.news-checkbox {
  padding-top: 2px;
}

.news-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.news-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.news-content h4 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
}

.news-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.news-meta .source,
.news-meta .date {
  font-size: 0.8rem;
  color: var(--text-dim);
}

.risk-badge,
.sentiment-badge,
.type-badge {
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.risk-badge.risk-high {
  background: rgba(248, 113, 113, 0.15);
  color: var(--negative);
}

.risk-badge.risk-medium {
  background: rgba(247, 201, 72, 0.15);
  color: var(--warning);
}

.risk-badge.risk-low {
  background: rgba(34, 197, 94, 0.15);
  color: var(--positive);
}

.sentiment-badge.sentiment-positive {
  background: rgba(34, 197, 94, 0.15);
  color: var(--positive);
}

.sentiment-badge.sentiment-neutral {
  background: rgba(156, 163, 175, 0.15);
  color: #9ca3af;
}

.sentiment-badge.sentiment-negative {
  background: rgba(248, 113, 113, 0.15);
  color: var(--negative);
}

.type-badge {
  background: rgba(79, 138, 255, 0.15);
  color: var(--accent);
}

.news-samples {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sample-news {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  transition: all 0.2s ease;
}

.sample-news:hover {
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.04);
}

.sample-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.sample-header h4 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  flex: 1;
}

.risk-label {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.risk-label.risk-high {
  background: rgba(248, 113, 113, 0.1);
  color: var(--negative);
}

.risk-label.risk-medium {
  background: rgba(247, 201, 72, 0.1);
  color: var(--warning);
}

.risk-label.risk-low {
  background: rgba(34, 197, 94, 0.1);
  color: var(--positive);
}

.sample-meta {
  display: flex;
  gap: 12px;
  font-size: 0.8rem;
  color: var(--text-dim);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions button {
    flex: 1;
  }

  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    width: 100%;
  }

  .filter-select {
    flex: 1;
  }

  .filter-info {
    margin-left: 0;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
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

