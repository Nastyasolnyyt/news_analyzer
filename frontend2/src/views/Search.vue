<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { api, type News } from '../api/client';

const router = useRouter();
const query = ref('');
const showFilters = ref(true);
const results = ref<News[]>([]);
const loading = ref(false);
const total = ref(0);

const sourceOptions = [
  { id: 'media', label: 'СМИ' },
  { id: 'telegram', label: 'Telegram' },
  { id: 'registry', label: 'Реестры' },
];

const topicOptions = [
  { id: 'economics', label: 'Экономика' },
  { id: 'politics', label: 'Политика' },
];

const riskOptions = [
  { id: 'high', label: 'Высокий' },
  { id: 'medium', label: 'Средний' },
  { id: 'low', label: 'Низкий' },
];

const infoChecklist = [
  'Вводите ключевые слова, названия компаний или персон',
  'Комбинируйте фильтры по источникам, темам и рискам',
  'Просматривайте карточки найденных событий',
  'Переходите в полную карточку для деталей и отчётов',
];

const fetchResults = async () => {
  loading.value = true;
  try {
    const data = await api.getNews({
      search: query.value || undefined,  // ← правильно: 'search'
      page: 1,
      page_size: 20,  // ← также исправил: page_size вместо per_page
    });
    results.value = data.items;
    total.value = data.total;
  } catch (e) {
    console.error('Ошибка загрузки:', e);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchResults);
watch(query, () => fetchResults());

const handleNewsClick = (newsId: number) => {
  router.push(`/news/${newsId}`);
};

const toggleFilters = () => {
  showFilters.value = !showFilters.value;
};
</script>

<template>
  <div class="search-page">
    <section class="search-panel">
      <label class="search-input" aria-label="Поисковый запрос">
        <input v-model="query" type="text" placeholder="Например: санкции, дизельный рынок" />
        <button type="button" @click="fetchResults">Искать</button>
      </label>
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
          <p>Темы</p>
          <label v-for="option in topicOptions" :key="option.id">
            <input type="checkbox" />
            <span>{{ option.label }}</span>
          </label>
        </div>
        <div class="filter-group">
          <p>Уровень риска</p>
          <label v-for="option in riskOptions" :key="option.id">
            <input type="checkbox" :checked="option.id !== 'low'" />
            <span>{{ option.label }}</span>
          </label>
        </div>
      </div>
    </section>

    <section class="info-block">
      <h2>Что можно делать</h2>
      <ul>
        <li v-for="item in infoChecklist" :key="item">
          <span class="bullet" />
          <span>{{ item }}</span>
        </li>
      </ul>
    </section>

    <section class="results">
      <header>
        <div>
          <p class="overline">Найденные события</p>
          <h3>Актуальные новости по запросу</h3>
        </div>
        <span class="count">{{ results.length }} результатов</span>
      </header>
      <div class="card-list">
        <article v-for="item in results" :key="item.id" class="result-card" tabindex="0">
          <div class="card-top">
            <h4>{{ item.title }}</h4>
            <span class="date">{{ item.pub_date || item.date }}</span>
          </div>
          <p class="source">{{ item.source }}</p>
          <p class="summary">{{ item.summary || item.text?.slice(0, 200) }}...</p>
          <button class="inline-link" @click="handleNewsClick(item.id)">Перейти к карточке</button>
        </article>
        <p v-if="!results.length && !loading" class="placeholder">Нет результатов по вашему запросу</p>
        <p v-if="loading" class="placeholder">Загрузка...</p>
      </div>
    </section>

    <section class="action-footer">
      <div>
        <h4>Готовы зафиксировать выводы?</h4>
        <p>Соберите подборку новостей в единый отчёт и отправьте заинтересованным сторонам.</p>
      </div>
      <button class="primary" @click="router.push('/reports')">Создать отчёт</button>
    </section>
  </div>
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

