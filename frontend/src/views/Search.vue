<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api'; 

const router = useRouter();
const query = ref(''); 
const showFilters = ref(false);
const isLoading = ref(false);
const results = ref<any[]>([]);

// Возвращаем переменные, которые требует шаблон
const sourceOptions = [
  { id: 'media', label: 'СМИ' },
  { id: 'telegram', label: 'Telegram' },
  { id: 'registry', label: 'Реестры' },
];

const riskOptions = [
  { id: 'high', label: 'Высокий' },
  { id: 'medium', label: 'Средний' },
  { id: 'low', label: 'Низкий' },
];

const infoChecklist = [
  'Вводите ключевые слова или названия компаний',
  'Система ищет по заголовкам и содержанию статей',
  'Результаты подтягиваются напрямую из вашей БД',
];

const handleSearch = async () => {
  if (!query.value.trim()) return;
  
  isLoading.value = true;
  try {
    // Вызываем API. Передаем query третьим аргументом (для поиска)
    const data = await api.getPosts(1, 50, query.value);
    
    const items = data.items || data || [];
    
    results.value = items.map((item: any) => {
      // Поддерживаем структуру { post, analysis } как в Dashboard
      const post = item.post || item;
      const analysis = item.analysis || {};
      
      return {
        id: post.id,
        title: post.title,
        date: post.created_at 
          ? new Date(post.created_at).toLocaleDateString('ru-RU') 
          : 'Неизвестно',
        source: post.source,
        summary: post.content || post.text || 'Нет описания',
        risk: analysis.risk_level || 'low'
      };
    });
  } catch (error) {
    console.error("Ошибка при поиске:", error);
    results.value = [];
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  if (query.value) handleSearch();
});

const toggleFilters = () => {
  showFilters.value = !showFilters.value;
};

const handleNewsClick = (newsId: number) => {
  router.push(`/news/${newsId}`);
};
</script>

<template>
  <section class="search-page">
    <header class="search-header">
      <button class="home-btn" @click="router.push('/')">
        <span class="dot" />
        Atlas Insight
      </button>
      <div class="header-actions">
        <button class="icon-btn profile">AK</button>
      </div>
    </header>

    <section class="search-panel">
      <form class="search-input" @submit.prevent="handleSearch">
        <input 
          v-model="query" 
          type="text" 
          placeholder="Введите запрос (например: Газпром, санкции)..." 
        />
        <button type="submit" :disabled="isLoading">
          {{ isLoading ? '...' : 'Искать' }}
        </button>
      </form>
      
      <button class="filter-toggle" type="button" @click="toggleFilters">
        {{ showFilters ? 'Скрыть фильтры' : 'Показать фильтры' }}
      </button>

      <div v-if="showFilters" class="filters">
        <div class="filter-group">
          <p>Источники</p>
          <label v-for="option in sourceOptions" :key="option.id">
            <input type="checkbox" checked />
            <span>{{ option.label }}</span>
          </label>
        </div>
        <div class="filter-group">
          <p>Уровень риска (AI)</p>
          <label v-for="option in riskOptions" :key="option.id">
            <input type="checkbox" checked />
            <span>{{ option.label }}</span>
          </label>
        </div>
      </div>
    </section>

    <div v-if="isLoading" class="loading-status">
      Поиск в базе данных...
    </div>

    <template v-else>
      <section v-if="results.length > 0" class="results">
        <header>
          <div>
            <p class="overline">Результаты</p>
            <h3>Найдено в вашей системе</h3>
          </div>
          <span class="count">{{ results.length }} новостей</span>
        </header>
        <div class="card-list">
          <article 
            v-for="item in results" 
            :key="item.id" 
            class="result-card"
            @click="handleNewsClick(item.id)"
          >
            <div class="card-top">
              <h4>{{ item.title }}</h4>
              <span class="date">{{ item.date }}</span>
            </div>
            <p class="source">
              {{ item.source }} • 
              <span :class="['risk-tag', item.risk]">{{ item.risk }}</span>
            </p>
            <p class="summary">{{ item.summary.slice(0, 160) }}...</p>
            <button class="inline-link">Подробнее →</button>
          </article>
        </div>
      </section>

      <section v-else-if="query" class="info-block">
        <h2>Ничего не найдено</h2>
        <p>Попробуйте изменить запрос или проверить наличие данных в PostgreSQL.</p>
      </section>

      <section v-else class="info-block">
        <h2>Начните поиск</h2>
        <ul>
          <li v-for="item in infoChecklist" :key="item">
            <span class="bullet" />
            <span>{{ item }}</span>
          </li>
        </ul>
      </section>
    </template>

    <section class="action-footer">
      <div>
        <h4>Нужен официальный отчёт?</h4>
        <p>Вы можете отобрать найденные новости и сформировать PDF-документ.</p>
      </div>
      <button class="primary" @click="router.push('/reports')">В студию отчётов</button>
    </section>
  </section>
</template>

<style scoped>
.search-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: var(--surface-1);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.home-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: var(--surface-2);
  color: #fff;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--positive));
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
}

.icon-btn svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.4;
}

.profile {
  width: auto;
  min-width: 44px;
  padding: 0 14px;
}

.initials {
  font-weight: 600;
}

.search-panel {
  background: var(--surface-2);
  border-radius: 20px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.search-input {
  display: flex;
  gap: 12px;
}

.search-input input {
  flex: 1;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.2);
  color: #fff;
  padding: 14px 18px;
  font-size: 1rem;
}

.search-input button {
  border: none;
  border-radius: 14px;
  padding: 0 20px;
  background: var(--accent);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.filter-toggle {
  align-self: flex-start;
  border: none;
  background: transparent;
  color: var(--accent);
  font-weight: 600;
  cursor: pointer;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-top: 8px;
}

.filter-group {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.filter-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  cursor: pointer;
}

.info-block {
  background: var(--surface-2);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 20px;
}

.info-block h2 {
  margin: 0 0 12px;
}

.info-block ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-block li {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  color: var(--text-dim);
}

.bullet {
  width: 6px;
  height: 6px;
  margin-top: 8px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 10px rgba(79, 138, 255, 0.6);
}

.results {
  background: var(--surface-2);
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.results header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.overline {
  margin: 0;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-dim);
}

.count {
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  font-size: 0.85rem;
  color: var(--text-dim);
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.result-card {
  background: rgba(15, 18, 26, 0.6);
  border-radius: 18px;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.result-card:hover,
.result-card:focus-visible {
  border-color: var(--accent);
  transform: translateY(-2px);
}

.card-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.result-card h4 {
  margin: 0;
  font-size: 1rem;
  color: #f8fafc;
}

.date {
  font-size: 0.85rem;
  color: var(--text-dim);
}

.source {
  margin: 0;
  color: var(--text-dim);
  font-size: 0.85rem;
}

.summary {
  margin: 0;
  color: #d2d6e0;
  font-size: 0.95rem;
}

.inline-link {
  align-self: flex-start;
  border: none;
  background: none;
  color: var(--accent);
  font-weight: 600;
  padding: 0;
  cursor: pointer;
}

.action-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  background: linear-gradient(120deg, rgba(79, 138, 255, 0.2), rgba(26, 31, 45, 0.9));
  border-radius: 22px;
  border: 1px solid rgba(79, 138, 255, 0.25);
  padding: 24px;
}

.action-footer h4 {
  margin: 0 0 6px;
}

.action-footer p {
  margin: 0;
  color: var(--text-dim);
  max-width: 520px;
}

.primary {
  border: none;
  border-radius: 16px;
  padding: 14px 28px;
  background: var(--accent);
  color: white;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 12px 30px rgba(79, 138, 255, 0.35);
}

@media (max-width: 800px) {
  .search-page {
    padding: 18px;
  }

  .results header {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-input {
    flex-direction: column;
  }

  .search-input button {
    height: 48px;
  }

  .action-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .primary {
    width: 100%;
  }
}
</style>

