<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../api'; 

const router = useRouter();
const route = useRoute();

const entity = ref<any>(null);
const relatedNews = ref<any[]>([]);
const isLoading = ref(true);

const entityId = computed(() => Number(route.params.id));

const fetchData = async (id: number) => {
  isLoading.value = true;
  try {
    // Получаем сущность (в базе это колонки id, text, type, details)
    const data = await api.getEntityById(id);
    entity.value = data;

    // Загружаем новости, связанные с этой сущностью (через article_id или поиск)
    const newsData = await api.getPosts({ entity_id: id });
    relatedNews.value = newsData.items || [];
  } catch (error) {
    console.error("Ошибка загрузки профиля:", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => fetchData(entityId.value));
watch(entityId, (newId) => fetchData(newId));

// Безопасное получение данных из JSON-поля details
const details = computed(() => entity.value?.details || {});
</script>
<template>
  <div v-if="isLoading" class="loading">
    Загрузка профиля...
  </div>

  <section v-else-if="entity" class="profile">
    <header class="profile-header">
      <button class="logo" @click="router.push('/')">
        <span class="dot" /> Atlas Risk
      </button>
      </header>

    <section class="hero">
      <div>
        <p class="entity-type">
          {{ entity.type === 'Company' ? 'Организация' : 'Персона' }}
        </p>
        <h1>{{ entity.text }}</h1>
        <p v-if="details.jurisdiction" class="jurisdiction">
          {{ details.jurisdiction }}
        </p>
      </div>
      <p class="description">
        {{ details.description || 'Описание отсутствует' }}
      </p>
    </section>

    <section class="grid">
      <article class="card identifiers">
        <h2>Основные данные</h2>
        <div class="registry">
          <p v-if="details.address"><strong>Адрес:</strong> {{ details.address }}</p>
          <p v-if="details.founded"><strong>Основана:</strong> {{ details.founded }}</p>
          <p><strong>Тип в системе:</strong> {{ entity.type }}</p>
        </div>
      </article>

      <article v-if="relatedNews.length > 0" class="card news">
        <h2>Последние события</h2>
        <div class="news-list">
          <div v-for="item in relatedNews.slice(0, 3)" :key="item.id" class="news-card">
            <strong>{{ item.title || 'Новость без заголовка' }}</strong>
            <p>{{ item.content?.slice(0, 80) }}...</p>
          </div>
        </div>
      </article>
    </section>

    <div class="actions">
      <button class="primary" @click="router.push('/')">Вернуться к списку</button>
    </div>
  </section>

  <section v-else class="error">
    <h2>Сущность с ID {{ entityId }} не найдена</h2>
    <p>Проверьте правильность ссылки или наличие записи в базе данных.</p>
    <button @click="router.push('/')">На главную</button>
  </section>
</template>


<style scoped>
.profile {
  display: flex;
  flex-direction: column;
  gap: 24px;
  background: var(--surface-1);
  border-radius: 24px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.profile-header {
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
  color: white;
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

.header-icons {
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
  border-radius: 24px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.entity-type {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.78rem;
  color: var(--text-dim);
  margin: 0;
}

h1 {
  margin: 4px 0;
  font-size: 2rem;
}

.jurisdiction {
  margin: 0;
  color: var(--text-dim);
}

.description {
  margin: 12px 0 0;
  color: #d2d6e0;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.card {
  background: var(--surface-2);
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 20px;
}

.identifiers dl {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin: 0;
}

dt {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
}

dd {
  margin: 4px 0 0;
  font-weight: 600;
}

.registry {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #d2d6e0;
}

.links {
  margin-top: 16px;
  color: var(--text-dim);
}

.links a {
  color: var(--accent);
  margin-left: 6px;
  cursor: pointer;
  text-decoration: none;
}

.links a:hover {
  text-decoration: underline;
}

.related ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.related li:last-child {
  border-bottom: none;
}

.related span {
  color: var(--text-dim);
}

.related button {
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  padding: 6px 14px;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.related button:hover {
  background: rgba(255, 255, 255, 0.05);
}

.overline {
  margin: 0;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-dim);
}

.outline {
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  padding: 6px 12px;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.mentions .chart {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex: 1;
}

.bar-fill {
  width: 100%;
  max-width: 40px;
  border-radius: 12px 12px 4px 4px;
  background: linear-gradient(180deg, rgba(79, 138, 255, 0.5), rgba(79, 138, 255, 0.1));
  position: relative;
}

.note {
  position: absolute;
  top: -28px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.7rem;
  background: rgba(15, 18, 26, 0.9);
  padding: 4px 6px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.count {
  font-weight: 600;
}

.week {
  font-size: 0.8rem;
  color: var(--text-dim);
}

.chart-summary {
  margin-top: 16px;
  color: var(--text-dim);
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.news-card {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 18px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
}

.news-card:hover {
  border-color: var(--accent);
}

.news-meta {
  display: flex;
  gap: 12px;
  font-size: 0.85rem;
  color: var(--text-dim);
}

.news-card h3 {
  margin: 0;
}

.news-card p {
  margin: 0;
  color: #d2d6e0;
}

.inline-link {
  border: none;
  background: none;
  color: var(--accent);
  font-weight: 600;
  padding: 0;
  cursor: pointer;
  align-self: flex-start;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.cta {
  display: flex;
  gap: 10px;
}

.primary,
.secondary {
  border-radius: 14px;
  padding: 12px 22px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.primary {
  background: var(--accent);
  color: white;
}

.secondary {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: inherit;
}

@media (max-width: 900px) {
  .actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .cta {
    width: 100%;
    flex-direction: column;
  }

  .cta button {
    width: 100%;
  }
}
</style>

