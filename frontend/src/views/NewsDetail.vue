<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api';

const route = useRoute();
const router = useRouter();
const newsId = Number(route.params.id);

const articleData = ref<any>(null);
const isLoading = ref(true);
const showSummary = ref(true);

const toggleMode = () => {
  showSummary.value = !showSummary.value;
};

onMounted(async () => {
  try {
    // Получаем данные: пост + анализ + сущности
    const data = await api.getPostById(newsId);
    articleData.value = data;
  } catch (e) {
    console.error("Ошибка загрузки новости:", e);
    // Если новости нет, лучше вернуться на главную через 2 секунды или сразу
    // router.push('/');
  } finally {
    isLoading.value = false;
  }
});

// Безопасное форматирование даты
const formattedDate = computed(() => {
  const dateStr = articleData.value?.post?.created_at;
  return dateStr ? new Date(dateStr).toLocaleDateString('ru-RU') : '';
});

const goBack = () => router.push('/');
</script>

<template>
  <div v-if="isLoading" class="loading-container">
    <div class="loader">Загрузка контента...</div>
  </div>
  
  <section v-else-if="articleData && articleData.post" class="news-page">
    <header class="page-header">
      <button class="logo" @click="goBack">
        <span class="dot" />
        Atlas Risk
      </button>
      <div class="actions">
        <button class="icon-btn" @click="router.push('/search')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
        <button class="icon-btn profile">AK</button>
      </div>
    </header>

    <div class="hero">
      <div class="meta">
        <span>{{ formattedDate }}</span>
        <span>•</span>
        <span>{{ articleData.post.source }}</span>
        <span>•</span>
        <span class="tonality-tag">
          Тональность: {{ articleData.analysis?.tonality?.toFixed(2) || '0.00' }}
        </span>
      </div>
      <h1>{{ articleData.post.title }}</h1>
      <div class="tags">
        <span v-for="entity in articleData.entities" :key="entity.id" class="tag">
          #{{ entity.text }}
        </span>
      </div>
    </div>

    <div class="card content-card">
      <div class="body-header">
        <p class="mode-label">Режим просмотра:</p>
        <div class="switch">
          <button :class="{ active: showSummary }" @click="showSummary = true">Кратко</button>
          <button :class="{ active: !showSummary }" @click="showSummary = false">Текст</button>
        </div>
      </div>

      <div class="text-content">
        <p v-if="showSummary" class="summary">
          {{ articleData.post.content?.slice(0, 400) }}...
        </p>
        <div v-else class="full-text">
          {{ articleData.post.content }}
        </div>
      </div>
    </div>

    <section v-if="articleData.entities?.length" class="entities-section card">
      <header>
        <h3>Выявленные объекты</h3>
        <button class="outline" @click="router.push('/analysis')">Граф связей</button>
      </header>
      <div class="entity-list">
        <div v-for="entity in articleData.entities" :key="entity.id" class="entity-card">
          <p class="entity-type">{{ entity.type }}</p>
          <h4>{{ entity.text }}</h4>
          <p class="relation">Упомянут в тексте</p>
          <button class="inline-link" @click="router.push(`/entity/${entity.id}`)">
            Открыть профиль →
          </button>
        </div>
      </div>
    </section>

    <footer class="cta-footer">
      <p>Хотите получить подробный отчет по этому событию?</p>
      <div class="cta-buttons">
        <button class="ghost">В закладки</button>
        <button class="secondary">Поделиться</button>
        <button class="primary">Сформировать отчёт</button>
      </div>
    </footer>
  </section>

  <div v-else class="error-container">
    <h2>Новость не найдена</h2>
    <button class="primary" @click="goBack">Вернуться назад</button>
  </div>
</template>


<style scoped>
/* Я сохранил все твои оригинальные стили, которые ты прислала выше */
.news-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: var(--surface-1);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.loading-container {
  padding: 100px;
  text-align: center;
  color: var(--text-dim);
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

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(120deg, var(--accent), var(--positive));
}

.actions {
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

.hero {
  background: linear-gradient(120deg, rgba(79, 138, 255, 0.15), rgba(21, 25, 37, 0.9));
  border-radius: 22px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.meta {
  display: flex;
  gap: 12px;
  font-size: 0.9rem;
  color: var(--text-dim);
  align-items: center;
}

h1 {
  margin: 0;
  font-size: 2rem;
  color: #fff;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  font-size: 0.85rem;
  text-transform: lowercase;
}

.card {
  background: var(--surface-2);
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 20px;
}

.body-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.switch {
  display: inline-flex;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 999px;
  padding: 4px;
  gap: 4px;
}

.switch button {
  border: none;
  border-radius: 999px;
  padding: 6px 14px;
  color: var(--text-dim);
  background: transparent;
  cursor: pointer;
  font-weight: 600;
}

.switch button.active {
  background: var(--accent);
  color: white;
}

.summary, .full-text {
  margin: 16px 0 0;
  color: #eef1f6;
  font-size: 1rem;
  line-height: 1.6;
}

.entities header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.entity-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
  margin-top: 16px;
}

.entity-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 18px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.entity-type {
  margin: 0;
  text-transform: uppercase;
  font-size: 0.75rem;
  color: var(--text-dim);
}

.inline-link {
  border: none;
  background: none;
  color: var(--accent);
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

.cta {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.cta-buttons {
  display: flex;
  gap: 12px;
}

.primary {
  background: var(--accent);
  color: white;
  border-radius: 14px;
  padding: 12px 20px;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.secondary, .ghost {
  border-radius: 14px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.08);
  color: inherit;
  border: none;
  cursor: pointer;
}

@media (max-width: 900px) {
  .cta { flex-direction: column; align-items: flex-start; }
}
</style>