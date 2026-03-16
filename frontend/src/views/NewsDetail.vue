<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api';

const route = useRoute();
const router = useRouter();
const articleData = ref<any>(null);
const isLoading = ref(true);
const showSummary = ref(true);

onMounted(async () => {
  try {
    const id = Number(route.params.id);
    articleData.value = await api.getPostById(id);
  } catch (e) {
    console.error("Новость не найдена");
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div v-if="isLoading" class="loading">Загрузка...</div>
  <section v-else-if="articleData" class="news-page">
    <header class="page-header">
      <button class="logo" @click="router.push('/')">PulseSight</button>
    </header>

    <section class="hero">
      <div class="meta">
        <span>{{ articleData.post.source }}</span>
        <span>{{ new Date(articleData.post.created_at).toLocaleString() }}</span>
      </div>
      <h1>{{ articleData.post.title }}</h1>
    </section>

    <section class="body card">
      <div class="switch">
        <button :class="{active: showSummary}" @click="showSummary = true">AI-Саммари</button>
        <button :class="{active: !showSummary}" @click="showSummary = false">Текст</button>
      </div>
      
      <p v-if="showSummary" class="content">
        {{ articleData.post.content.substring(0, 300) }}...
      </p>
      <div v-else class="content">
        {{ articleData.post.content }}
      </div>
    </section>

    <section v-if="articleData.entities?.length" class="entities card">
      <h3>Выделенные сущности</h3>
      <div class="entity-grid">
        <div v-for="e in articleData.entities" :key="e.id" class="e-badge">
          <small>{{ e.type }}</small>
          <span>{{ e.text }}</span>
        </div>
      </div>
    </section>
  </section>
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