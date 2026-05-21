<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { api, type Entity } from '../api/client';

const router = useRouter();
const entities = ref<Entity[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
const searchQuery = ref('');

// Пагинация
const currentPage = ref(1);
const pageSize = 50;
const totalEntities = ref(0);
const isLoadingMore = ref(false);

// Кэш для всех загруженных сущностей
const allLoadedEntities = ref<Map<number, Entity>>(new Map());

// Фильтрованные сущности для текущей страницы
const filteredEntities = computed(() => {
  const query = searchQuery.value.toLowerCase();
  const allEntities = Array.from(allLoadedEntities.value.values());
  
  const filtered = query
    ? allEntities.filter(entity => entity.name.toLowerCase().includes(query))
    : allEntities;
  
  return filtered.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize);
});

const totalPages = computed(() => {
  const allEntities = Array.from(allLoadedEntities.value.values());
  const query = searchQuery.value.toLowerCase();
  const filtered = query
    ? allEntities.filter(entity => entity.name.toLowerCase().includes(query))
    : allEntities;
  return Math.ceil(filtered.length / pageSize);
});

onMounted(async () => {
  await loadEntities();
});

const loadEntities = async () => {
  try {
    loading.value = true;
    error.value = null;
    console.log('🚀 Loading first page of entities...');
    
    // ФАЗА 1: Загружаем первую страницу и показываем её немедленно
    try {
      const firstPageResult = await api.getEntities({
        limit: pageSize,
        page: 1,
      });
      
      console.log(`📄 Loaded page 1: ${firstPageResult.items.length} entities (total: ${firstPageResult.total})`);
      
      // Добавляем первую страницу в кэш
      firstPageResult.items.forEach(entity => {
        if (entity && entity.id) {
          allLoadedEntities.value.set(entity.id, entity);
        }
      });
      
      totalEntities.value = firstPageResult.total;
      entities.value = Array.from(allLoadedEntities.value.values());
      
      // Показываем первую страницу немедленно
      loading.value = false;
      
      // ФАЗА 2: Загружаем остальные страницы в фоне (не блокируя UI)
      if (firstPageResult.total > pageSize) {
        console.log('📊 Starting background loading of remaining pages...');
        
        const totalPages = Math.ceil(firstPageResult.total / pageSize);
        
        // Загружаем оставшиеся страницы асинхронно
        (async () => {
          for (let page = 2; page <= totalPages; page++) {
            try {
              const result = await api.getEntities({
                limit: pageSize,
                page: page,
              });
              
              // Добавляем в кэш
              result.items.forEach(entity => {
                if (entity && entity.id) {
                  allLoadedEntities.value.set(entity.id, entity);
                }
              });
              
              console.log(`📄 Loaded page ${page}/${totalPages}: ${result.items.length} entities`);
            } catch (pageError) {
              console.error(`⚠️ Error loading page ${page}:`, pageError);
              // Продолжаем со следующей страницы
            }
          }
          
          // После загрузки всех страниц обновляем список
          const allLoaded = Array.from(allLoadedEntities.value.values());
          entities.value = allLoaded;
          console.log(`✅ Background loading complete: ${allLoaded.length} total entities`);
        })();
      }
    } catch (firstPageError) {
      console.error('❌ Error loading first page:', firstPageError);
      error.value = firstPageError instanceof Error ? firstPageError.message : 'Ошибка загрузки сущностей';
      loading.value = false;
      throw firstPageError;
    }
  } catch (e: any) {
    if (!error.value) {
      error.value = e.message || 'Ошибка загрузки сущностей';
    }
    console.error('❌ Error:', e);
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1; // Сбрасываем на первую страницу при поиске
};

const handleEntityClick = (entityId: number) => {
  router.push(`/entity/${entityId}`);
};

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const reloadPage = async () => {
  allLoadedEntities.value.clear();
  currentPage.value = 1;
  await loadEntities();
};
</script>

<template>
  <div class="all-entities-page">
    <header class="page-header">
      <div class="back-nav">
        <button @click="router.back()" class="back-button">← Назад</button>
      </div>
      <div>
        <h1>Все сущности</h1>
        <p class="description">Полный список упоминаемых сущностей в новостях</p>
      </div>
    </header>

    <!-- LOADING STATE -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>⏳ Загружаем сущности...</p>
      <p class="loading-hint">Это займет несколько секунд</p>
    </div>

    <!-- ERROR STATE -->
    <div v-else-if="error" class="error-state">
      <p class="error-title">Ошибка загрузки</p>
      <p class="error-message">{{ error }}</p>
      <button class="btn-secondary" @click="loadEntities()">Попробовать снова</button>
    </div>

    <!-- LOADED STATE -->
    <div v-else class="content">
      <!-- Search -->
      <div class="search-section">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск по названию..."
          class="search-input"
          @input="handleSearch"
        />
        <span class="search-count">{{ filteredEntities.length }} найдено из {{ entities.length }}</span>
      </div>

      <!-- Entities list -->
      <section class="entities-section">
        <!-- No results -->
        <div v-if="filteredEntities.length === 0" class="no-results">
          <p>😔 Сущности не найдены</p>
        </div>

        <!-- Grid with entities -->
        <div v-else class="entities-grid">
          <article 
            v-for="entity in filteredEntities" 
            :key="entity.id" 
            class="entity-card"
            @click="handleEntityClick(entity.id)"
            role="button"
            tabindex="0"
            @keydown.enter="handleEntityClick(entity.id)"
          >
            <div class="entity-header">
              <h3>{{ entity.name }}</h3>
              <span v-if="entity.entity_type" class="entity-type">{{ entity.entity_type }}</span>
            </div>

            <div v-if="entity.description" class="entity-description">
              {{ entity.description }}
            </div>

            <div v-if="(entity as any).recentMentions || (entity as any).topicCount" class="entity-stats">
              <div v-if="(entity as any).recentMentions" class="stat">
                <span class="stat-label">Упоминаний:</span>
                <span class="stat-value">{{ (entity as any).recentMentions }}</span>
              </div>
              <div v-if="(entity as any).topicCount" class="stat">
                <span class="stat-label">Темы:</span>
                <span class="stat-value">{{ (entity as any).topicCount }}</span>
              </div>
            </div>

            <button class="btn-view">Перейти к профилю →</button>
          </article>
        </div>
      </section>

      <!-- Pagination -->
      <div v-if="filteredEntities.length > 0" class="pagination">
        <button 
          class="pagination-btn"
          @click="prevPage"
          :disabled="currentPage === 1"
        >
          ← Предыдущая
        </button>
        
        <div class="pagination-info">
          Страница {{ currentPage }} из {{ totalPages }}
        </div>
        
        <button 
          class="pagination-btn"
          @click="nextPage"
          :disabled="currentPage === totalPages"
        >
          Следующая →
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.all-entities-page {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding-bottom: 40px;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.back-nav {
  display: flex;
}

.back-button {
  background: transparent;
  border: none;
  color: var(--accent);
  font-size: 1rem;
  cursor: pointer;
  padding: 8px;
  margin-left: -8px;
  transition: all 0.2s ease;
}

.back-button:hover {
  transform: translateX(-4px);
}

.page-header h1 {
  font-size: 2rem;
  margin: 0;
  font-weight: 700;
}

.description {
  color: var(--text-dim);
  margin: 0;
  font-size: 1rem;
  line-height: 1.6;
}

/* ✅ LOADING STATE */
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

.loading-state p:first-of-type {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-base);
}

.loading-hint {
  color: var(--text-dim);
  font-size: 0.9rem;
  margin: 0;
}

/* ✅ ERROR STATE */
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
  padding: 40px 20px;
}

.error-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
  color: var(--negative);
}

.error-message {
  color: var(--text-dim);
  font-size: 1rem;
  margin: 0;
  text-align: center;
  max-width: 500px;
}

.btn-secondary {
  padding: 10px 20px;
  background: rgba(79, 138, 255, 0.1);
  border: 1px solid var(--accent);
  color: var(--accent);
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: rgba(79, 138, 255, 0.2);
}

.content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.search-section {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--surface-1);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 16px 20px;
  transition: all 0.2s ease;
}

.search-section:focus-within {
  border-color: var(--accent);
  background: var(--surface-2);
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-base);
  font-size: 1rem;
  outline: none;
}

.search-input::placeholder {
  color: var(--text-dim);
}

.search-count {
  color: var(--text-dim);
  font-size: 0.9rem;
  white-space: nowrap;
  background: rgba(79, 138, 255, 0.1);
  padding: 4px 12px;
  border-radius: 999px;
  font-weight: 500;
}

.entities-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.no-results {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: var(--text-dim);
  font-size: 1.1rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed rgba(255, 255, 255, 0.1);
  border-radius: 20px;
}

.no-results p {
  margin: 0;
}

.entities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.entity-card {
  background: var(--surface-1);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  outline: none;
}

.entity-card:hover {
  border-color: var(--accent);
  background: var(--surface-2);
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(79, 138, 255, 0.15);
}

.entity-card:focus-visible {
  border-color: var(--accent);
  outline: 2px solid var(--accent);
  outline-offset: 0;
}

.entity-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.entity-header h3 {
  margin: 0;
  font-size: 1.1rem;
  flex: 1;
  color: white;
  word-break: break-word;
}

.entity-type {
  background: rgba(79, 138, 255, 0.1);
  color: var(--accent);
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 0.7rem;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.entity-description {
  color: var(--text-dim);
  font-size: 0.9rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.entity-stats {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  color: var(--text-dim);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--accent);
}

.btn-view {
  padding: 10px 16px;
  background: rgba(79, 138, 255, 0.1);
  border: 1px solid var(--accent);
  color: var(--accent);
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  align-self: flex-start;
}

.btn-view:hover {
  background: rgba(79, 138, 255, 0.2);
  transform: translateX(2px);
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 24px;
  background: var(--surface-1);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  margin-top: 24px;
}

.pagination-btn {
  padding: 10px 16px;
  background: rgba(79, 138, 255, 0.1);
  border: 1px solid var(--accent);
  color: var(--accent);
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: rgba(79, 138, 255, 0.2);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: var(--text-dim);
  font-size: 0.9rem;
  font-weight: 600;
  min-width: 150px;
  text-align: center;
}

@media (max-width: 768px) {
  .entities-grid {
    grid-template-columns: 1fr;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .entity-card {
    padding: 16px;
  }

  .pagination {
    flex-direction: column;
    gap: 12px;
  }

  .pagination-btn {
    width: 100%;
  }
}
</style>
