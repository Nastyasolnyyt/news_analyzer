<template>
  <div class="search-page">
    <!-- ПАНЕЛЬ ПОИСКА И ФИЛЬТРОВ -->
    <section class="search-panel">
      <label class="search-input" aria-label="Поисковый запрос">
        <input
          v-model="query"
          type="text"
          placeholder="Например: санкции, дизельный рынок, Газпром"
          @input="handleSearchInput"
        />
        <button type="button" @click="fetchResults">Искать</button>
      </label>

      <button class="filter-toggle" type="button" @click="toggleFilters">
        {{ showFilters ? 'Скрыть фильтры' : 'Показать фильтры' }}
      </button>

      <div v-if="showFilters" class="filters">
        <!-- Фильтр по источникам -->
        <div class="filter-group">
          <p>Источники</p>
          <label v-for="option in sourceOptions" :key="option.id">
            <input type="checkbox" v-model="selectedSources" :value="option.id" />
            <span>{{ option.label }}</span>
          </label>
        </div>

        <!-- Фильтр по уровню риска -->
        <div class="filter-group">
          <p>Уровень риска</p>
          <label v-for="option in riskLevelOptions" :key="option.id">
            <input
              type="checkbox"
              v-model="selectedRiskLevels"
              :value="option.id"
            />
            <span>{{ option.label }}</span>
          </label>
        </div>

        <!-- Фильтр по типу риска -->
        <div class="filter-group">
          <p>Тип риска</p>
          <label v-for="option in riskTypeOptions" :key="option.id">
            <input
              type="checkbox"
              v-model="selectedRiskTypes"
              :value="option.id"
            />
            <span>{{ option.label }}</span>
          </label>
        </div>
      </div>
    </section>

    <!-- ИНФОРМАЦИОННЫЙ БЛОК -->
    <section class="info-block">
      <h2>Что можно делать</h2>
      <ul>
        <li v-for="item in infoChecklist" :key="item">
          <span class="bullet" />
          <span>{{ item }}</span>
        </li>
      </ul>
    </section>

    <!-- РЕЗУЛЬТАТЫ ПОИСКА -->
    <section class="results">
      <header>
        <div>
          <p class="overline">Найденные события</p>
          <h3>Актуальные новости по запросу</h3>
        </div>
        <span class="count">{{ filteredResults.length }} результатов</span>
      </header>

      <div class="card-list">
        <!-- Загрузка -->
        <p v-if="loading" class="placeholder">Загрузка...</p>

        <!-- Нет результатов -->
        <p v-if="!loading && query.trim() && filteredResults.length === 0" class="placeholder">
          Нет результатов по вашему запросу
        </p>

        <!-- Пустой поиск — показываем все новости -->
        <p v-if="!loading && !query.trim() && filteredResults.length === 0" class="placeholder">
          Новости загружаются...
        </p>

        <!-- Список карточек -->
        <article
          v-for="item in displayedResults"
          :key="item.id"
          class="result-card"
          tabindex="0"
          @click="selectArticle(item)"
        >
          <div class="card-top">
            <h4>{{ item.title || 'Без заголовка' }}</h4>
            <span class="date">{{ formatDate(item.pub_date) }}</span>
          </div>
          <p class="source">{{ item.source || 'Unknown' }}</p>
          <p class="summary">{{ (item.text || '').slice(0, 200) }}...</p>

          <!-- Бейджи риска -->
          <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px">
            <span
              v-if="item.risk_level"
              class="risk-badge"
              :class="`risk-${item.risk_level}`"
            >
              <span class="dot" />
              {{ riskLevelLabel(item.risk_level) }}
            </span>
            <span v-if="item.risk_type" class="type-badge">
              {{ riskTypeLabel(item.risk_type) }}
            </span>
          </div>

          <button class="inline-link" @click.stop="selectArticle(item)">
            Перейти к карточке
          </button>
        </article>

        <!-- Кнопка "Загрузить ещё" -->
        <div v-if="canLoadMore" style="text-align: center; margin-top: 12px">
          <button class="inline-link" @click="loadMore">
            Загрузить ещё ({{ displayedCount }} из {{ filteredResults.length }})
          </button>
        </div>
      </div>
    </section>

    <!-- ФУТЕР С ДЕЙСТВИЕМ -->
    <section class="action-footer">
      <div>
        <h4>Готовы зафиксировать выводы?</h4>
        <p>Соберите подборку новостей в единый отчёт и отправьте заинтересованным сторонам.</p>
      </div>
      <button class="primary" @click="router.push('/reports')">Создать отчёт</button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api, type News } from '../api/client'

const router = useRouter()

// ==================== ТИПЫ ====================
interface NewsArticle extends News {
  source_type?: 'media' | 'telegram' | 'registry'
}

// ==================== ОПЦИИ ФИЛЬТРОВ ====================
const sourceOptions = [
  { id: 'media', label: 'СМИ' },
  { id: 'telegram', label: 'Telegram' },
  { id: 'registry', label: 'Реестры' },
]

const riskLevelOptions = [
  { id: 'high', label: 'Высокий' },
  { id: 'medium', label: 'Средний' },
  { id: 'low', label: 'Низкий' },
]

const riskTypeOptions = [
  { id: 'политический', label: 'Политический' },
  { id: 'экономический', label: 'Экономический' },
  { id: 'социальный', label: 'Социальный' },
]

const infoChecklist = [
  'Вводите ключевые слова, названия компаний или персон',
  'Комбинируйте фильтры по источникам, темам и рискам',
  'Просматривайте карточки найденных событий',
  'Переходите в полную карточку для деталей и отчётов',
]

// ==================== СОСТОЯНИЕ ====================
const query = ref('')
const loading = ref(false)
const showFilters = ref(true)
const allResults = ref<NewsArticle[]>([])
const selectedArticleId = ref<number | null>(null)
const displayedCount = ref(20)
const PAGE_SIZE = 20

const selectedSources = ref<string[]>([])
const selectedRiskLevels = ref<string[]>(['high', 'medium', 'low'])
const selectedRiskTypes = ref<string[]>([])

let searchTimeout: NodeJS.Timeout | null = null

// ==================== ВЫЧИСЛЯЕМЫЕ СВОЙСТВА ====================
const filteredResults = computed(() => {
  let filtered = allResults.value

  // Фильтр по тексту поиска
  if (query.value.trim()) {
    const searchLower = query.value.toLowerCase()
    filtered = filtered.filter(
      (item) =>
        (item.title?.toLowerCase() || '').includes(searchLower) ||
        (item.text?.toLowerCase() || '').includes(searchLower) ||
        (item.source?.toLowerCase() || '').includes(searchLower)
    )
  }

  // Фильтр по источнику
  if (selectedSources.value.length > 0) {
    filtered = filtered.filter((item) => {
      const sourceType = getSourceType(item.source || '')
      return selectedSources.value.includes(sourceType)
    })
  }

  // Фильтр по уровню риска
  if (selectedRiskLevels.value.length > 0) {
    filtered = filtered.filter((item) =>
      selectedRiskLevels.value.includes(item.risk_level || 'low')
    )
  }

  // Фильтр по типу риска
  if (selectedRiskTypes.value.length > 0) {
    filtered = filtered.filter((item) =>
      selectedRiskTypes.value.includes(item.risk_type || '')
    )
  }

  return filtered
})

const displayedResults = computed(() => {
  return filteredResults.value.slice(0, displayedCount.value)
})

const canLoadMore = computed(() => {
  return displayedCount.value < filteredResults.value.length
})

// ==================== ФУНКЦИИ ====================
const getSourceType = (source: string): 'media' | 'telegram' | 'registry' => {
  if (source.toLowerCase().includes('telegram')) return 'telegram'
  if (source.toLowerCase().includes('реестр') || source.toLowerCase().includes('registry')) return 'registry'
  return 'media'
}

const handleSearchInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  query.value = target.value

  if (searchTimeout) clearTimeout(searchTimeout)

  loading.value = true
  searchTimeout = setTimeout(() => {
    if (query.value.trim()) {
      fetchResults()
    } else {
      fetchAllNews()
    }
  }, 500)
}

const fetchAllNews = async () => {
  try {
    const data = await api.getNews({ page: 1, page_size: 500 })
    allResults.value = data.items as NewsArticle[]
    displayedCount.value = 20
    selectedArticleId.value = null
  } catch (error) {
    console.error('Ошибка при загрузке новостей:', error)
    allResults.value = []
  } finally {
    loading.value = false
  }
}

const fetchResults = async () => {
  try {
    const data = await api.getNews({
      search: query.value || undefined,
      page: 1,
      page_size: 500,
    })
    allResults.value = data.items as NewsArticle[]
    displayedCount.value = 20
    selectedArticleId.value = null
  } catch (error) {
    console.error('Ошибка при поиске:', error)
    allResults.value = []
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  displayedCount.value += PAGE_SIZE
}

const selectArticle = (item: NewsArticle) => {
  selectedArticleId.value = item.id
  router.push(`/news/${item.id}`)
}

const toggleFilters = () => {
  showFilters.value = !showFilters.value
}

const formatDate = (dateStr?: string): string => {
  if (!dateStr) return 'Unknown'
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

const riskLevelLabel = (level?: string): string => {
  const map: Record<string, string> = {
    high: 'Высокий риск',
    medium: 'Средний риск',
    low: 'Низкий риск',
  }
  return map[level || 'low'] || 'Неизвестно'
}

const riskTypeLabel = (type?: string): string => {
  const map: Record<string, string> = {
    политический: 'Политический',
    экономический: 'Экономический',
    социальный: 'Социальный',
  }
  return map[type || ''] || type || 'Неизвестно'
}

// ==================== ИНИЦИАЛИЗАЦИЯ ====================
onMounted(() => {
  fetchAllNews()
})
</script>

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

.search-input input::placeholder {
  color: rgba(255, 255, 255, 0.5);
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

.filter-group label input[type="checkbox"] {
  accent-color: var(--accent);
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

.risk-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.risk-badge .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.risk-badge.risk-high {
  background: rgba(255, 59, 48, 0.15);
  color: #ff3b30;
}
.risk-badge.risk-high .dot {
  background: #ff3b30;
}

.risk-badge.risk-medium {
  background: rgba(255, 152, 0, 0.15);
  color: #ff9800;
}
.risk-badge.risk-medium .dot {
  background: #ff9800;
}

.risk-badge.risk-low {
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
}
.risk-badge.risk-low .dot {
  background: #4caf50;
}

.type-badge {
  padding: 4px 10px;
  background: rgba(158, 158, 158, 0.15);
  border-radius: 4px;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
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

.placeholder {
  margin: 0;
  color: var(--text-dim);
  text-align: center;
  padding: 20px;
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

  .filters {
    grid-template-columns: 1fr;
  }
}
</style>