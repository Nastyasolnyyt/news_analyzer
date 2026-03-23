<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'; // Добавили computed
import { useRoute, useRouter } from 'vue-router';
import api from '../api';

const route = useRoute();
const router = useRouter();
const articleData = ref<any>(null);
const isLoading = ref(true);
const showSummary = ref(true);

// Создаем удобную переменную, которая сама поймет структуру данных
const post = computed(() => {
  if (!articleData.value) return null;
  // Если бэкенд прислал { post: {...} }, берем post. Иначе берем весь объект.
  return articleData.value.post || articleData.value;
});

const entities = computed(() => {
  return articleData.value?.entities || [];
});

onMounted(async () => {
  console.log("ЗАПРОС ПО ID:", route.params.id);
  try {
    const id = Number(route.params.id);
    if (isNaN(id)) throw new Error("Неверный ID");
    
    const data = await api.getPostById(id);
    console.log("Данные из БД:", data); // Посмотри в консоль F12, что пришло
    articleData.value = data;
  } catch (e) {
    console.error("Новость не найдена или ошибка сервера");
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div v-if="isLoading" class="loading">Загрузка...</div>
  
  <section v-else-if="post" class="news-page">
    <header class="page-header">
      <button class="logo" @click="router.push('/')">Atlas Insight</button>
    </header>

    <section class="hero">
      <div class="meta">
        <span>{{ post.source }}</span>
        <span v-if="post.created_at">
          {{ new Date(post.created_at).toLocaleString('ru-RU') }}
        </span>
      </div>
      <h1>{{ post.title }}</h1>
    </section>

    <section class="body card">
      <div class="switch">
        <button :class="{active: showSummary}" @click="showSummary = true">AI-Саммари</button>
        <button :class="{active: !showSummary}" @click="showSummary = false">Полный текст</button>
      </div>
      
      <p v-if="showSummary" class="content summary-text">
        {{ post.content?.substring(0, 400) || "Нет описания" }}...
      </p>
      <div v-else class="content full-text">
        {{ post.content || post.text || "Текст отсутствует" }}
      </div>
    </section>

    <section v-if="entities.length" class="entities card">
      <h3>Выделенные сущности</h3>
      <div class="entity-grid">
        <div v-for="(e, index) in entities" :key="index" class="e-badge">
          <small>{{ e.label || e.type }}</small>
          <span>{{ e.name || e.text }}</span>
        </div>
      </div>
    </section>
  </section>

  <div v-else class="error-page">
    <h2>Ошибка 404</h2>
    <p>Новость с ID {{ route.params.id }} не найдена в базе данных.</p>
    <button @click="router.push('/search')">Вернуться к поиску</button>
  </div>
</template>


<style scoped>

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