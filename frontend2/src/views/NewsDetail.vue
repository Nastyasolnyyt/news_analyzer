<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { api, type News, type Entity } from '../api/client';

const router = useRouter();
const route = useRoute();
const newsId = Number(route.params.id);

const article = ref<News | null>(null);
const relatedEntities = ref<Entity[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
const showSummary = ref(true);

onMounted(async () => {
  try {
    article.value = await api.getNewsById(newsId);
    if (article.value?.relatedEntityIds) {
      relatedEntities.value = await api.getEntitiesByIds(article.value.relatedEntityIds);
    }
  } catch (e: any) {
    error.value = e.message;
    if (e.message.includes('Not found')) {
      router.push('/');
    }
  } finally {
    loading.value = false;
  }
});

const handleEntityClick = (entityId: number) => {
  router.push(`/entity/${entityId}`);
};

const toggleMode = () => {
  showSummary.value = !showSummary.value;
};
</script>

<template>
  <div class="news-page">
    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else-if="error" class="error">Ошибка: {{ error }}</div>
    <div v-else-if="article">
      <section class="hero">
        <div class="meta">
          <span class="source">{{ article.source }}</span>
          <span class="date">{{ article.pub_date || article.date }}</span>
        </div>
        <h1>{{ article.title }}</h1>
        <div v-if="article.tags" class="tags">
          <span v-for="tag in article.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
      </section>

      <section class="body card">
        <header class="body-header">
          <p class="mode-label">Режим чтения</p>
          <div class="switch">
            <button :class="{ active: showSummary }" @click="showSummary = true">Кратко</button>
            <button :class="{ active: !showSummary }" @click="showSummary = false">Полный текст</button>
          </div>
        </header>
        <p v-if="showSummary" class="summary">{{ article.summary || article.text?.slice(0, 500) }}...</p>
        <div v-else class="full-text">
          <p v-for="(paragraph, idx) in (article.fullText || [article.text])" :key="idx">{{ paragraph }}</p>
        </div>
      </section>

      <section v-if="relatedEntities.length > 0" class="entities card">
        <header>
          <div>
            <p class="overline">Упомянутые сущности</p>
            <h2>Связанные участники</h2>
          </div>
        </header>
        <div class="entity-list">
          <article v-for="entity in relatedEntities" :key="entity.id" class="entity-card">
            <div>
              <p class="entity-type">
                {{ entity.type === 'Company' ? 'Компания' : entity.type === 'Person' ? 'Персона' : 'Событие' }}
              </p>
              <h3>{{ entity.name }}</h3>
            </div>
            <button class="inline-link" @click="handleEntityClick(entity.id)">Профиль</button>
          </article>
        </div>
      </section>
    </div>
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
  padding: 0 12px;
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

.mode-label {
  margin: 0;
  color: var(--text-dim);
  font-size: 0.9rem;
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

.summary {
  margin: 16px 0 0;
  color: #eef1f6;
  font-size: 1rem;
  line-height: 1.6;
}

.full-text {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 16px;
  color: #dadfe9;
  font-size: 1rem;
  line-height: 1.7;
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
  letter-spacing: 0.08em;
  color: var(--text-dim);
}

.relation {
  margin: 0;
  color: var(--text-dim);
  font-size: 0.85rem;
}

.inline-link {
  border: none;
  background: none;
  color: var(--accent);
  font-weight: 600;
  padding: 0;
  align-self: flex-start;
  cursor: pointer;
}

.inline-link:hover {
  text-decoration: underline;
}

.outline {
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  padding: 6px 12px;
  background: transparent;
  color: inherit;
  cursor: pointer;
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
  flex-wrap: wrap;
  justify-content: flex-end;
}

.primary,
.secondary,
.ghost {
  border-radius: 14px;
  padding: 12px 20px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.primary {
  background: var(--accent);
  color: white;
  box-shadow: 0 10px 20px rgba(79, 138, 255, 0.3);
}

.secondary {
  background: rgba(255, 255, 255, 0.08);
  color: inherit;
}

.ghost {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: inherit;
}

@media (max-width: 900px) {
  .cta {
    flex-direction: column;
    align-items: flex-start;
  }

  .cta-buttons {
    width: 100%;
    justify-content: flex-start;
  }

  .cta-buttons button {
    flex: 1 1 160px;
  }
}
</style>

