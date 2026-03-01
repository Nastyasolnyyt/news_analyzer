<script setup lang="ts">
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { getEntityById, getEntitiesByIds, news } from '../mockData';

const router = useRouter();
const route = useRoute();
const entityId = Number(route.params.id);

const entity = computed(() => getEntityById(entityId));
const linkedEntities = computed(() => {
  if (!entity.value) return [];
  return getEntitiesByIds(entity.value.linkedEntityIds);
});
const relatedNews = computed(() => {
  if (!entity.value) return [];
  return news.filter((n) => n.relatedEntityIds.includes(entityId));
});

const handleLinkedEntityClick = (linkedId: number) => {
  router.push(`/entity/${linkedId}`);
};

const handleNewsClick = (newsId: number) => {
  router.push(`/news/${newsId}`);
};

if (!entity.value) {
  router.push('/');
}
</script>

<template>
  <section v-if="entity" class="profile">
    <header class="profile-header">
      <button class="logo" @click="router.push('/')">
        <span class="dot" />
        Atlas Risk
      </button>
      <div class="header-icons">
        <button aria-label="search" class="icon-btn" @click="router.push('/search')">
          <svg viewBox="0 0 24 24"><path d="M11 4a7 7 0 0 1 5.6 11.2l3.6 3.6-1.4 1.4-3.6-3.6A7 7 0 1 1 11 4Z" /></svg>
        </button>
        <button aria-label="notifications" class="icon-btn" @click="router.push('/notifications')">
          <svg viewBox="0 0 24 24">
            <path
              d="M12 2a6 6 0 0 0-6 6v3.4l-.9 2.2a1 1 0 0 0 1 1.4h11.8a1 1 0 0 0 1-.6 1 1 0 0 0 0-.8L18 11.4V8a6 6 0 0 0-6-6Z"
            />
            <path d="M9 18a3 3 0 0 0 6 0" />
          </svg>
        </button>
        <button aria-label="profile" class="icon-btn profile">
          <span>AK</span>
        </button>
      </div>
    </header>

    <section class="hero">
      <div>
        <p class="entity-type">{{ entity.type === 'Company' ? 'Организация' : entity.type === 'Person' ? 'Персона' : 'Событие' }}</p>
        <h1>{{ entity.name }}</h1>
        <p v-if="entity.jurisdiction" class="jurisdiction">{{ entity.jurisdiction }}</p>
      </div>
      <p class="description">
        {{ entity.description }}
      </p>
    </section>

    <section class="grid">
      <article v-if="entity.identifiers || entity.registryInfo" class="card identifiers">
        <h2>Основные данные</h2>
        <dl v-if="entity.identifiers">
          <div v-for="item in entity.identifiers" :key="item.label">
            <dt>{{ item.label }}</dt>
            <dd>{{ item.value }}</dd>
          </div>
        </dl>
        <div v-if="entity.registryInfo" class="registry">
          <p><strong>Юр. адрес:</strong> {{ entity.registryInfo.address }}</p>
          <p><strong>Реестр:</strong> {{ entity.registryInfo.registry }}</p>
          <p><strong>Основана:</strong> {{ entity.registryInfo.founded }}</p>
        </div>
        <p v-if="linkedEntities.length > 0" class="links">
          Связан с:
          <a
            v-for="linked in linkedEntities.slice(0, 3)"
            :key="linked.id"
            href="#"
            @click.prevent="handleLinkedEntityClick(linked.id)"
            >{{ linked.name }}</a
          >
        </p>
      </article>

      <article v-if="linkedEntities.length > 0" class="card related">
        <header>
          <div>
            <p class="overline">Связанные сущности</p>
            <h2>Ключевые связи</h2>
          </div>
          <button class="outline">Все связи</button>
        </header>
        <ul>
          <li v-for="item in linkedEntities" :key="item.id">
            <div>
              <strong>{{ item.name }}</strong>
              <span>{{ item.type === 'Company' ? 'Компания' : item.type === 'Person' ? 'Персона' : 'Событие' }}</span>
            </div>
            <button @click="handleLinkedEntityClick(item.id)">Перейти</button>
          </li>
        </ul>
      </article>
    </section>

    <section v-if="entity.mentions" class="mentions card">
      <header>
        <div>
          <p class="overline">Упоминания</p>
          <h2>Динамика за 8 недель</h2>
        </div>
        <button class="outline">Подробнее</button>
      </header>
      <div class="chart">
        <div v-for="point in entity.mentions" :key="point.week" class="bar">
          <div class="bar-fill" :style="{ height: `${point.count * 5}px` }">
            <span v-if="point.note" class="note">{{ point.note }}</span>
          </div>
          <span class="count">{{ point.count }}</span>
          <span class="week">{{ point.week }}</span>
        </div>
      </div>
      <p class="chart-summary">Среднее 6 упоминаний / неделя, резкий рост 18.11 из-за инцидента.</p>
    </section>

    <section v-if="relatedNews.length > 0" class="news card">
      <header>
        <div>
          <p class="overline">Новости</p>
          <h2>Связанные события</h2>
        </div>
        <button class="outline">Все новости</button>
      </header>
      <div class="news-list">
        <article
          v-for="newsItem in relatedNews.slice(0, 3)"
          :key="newsItem.id"
          class="news-card"
          @click="handleNewsClick(newsItem.id)"
        >
          <div class="news-meta">
            <span class="date">{{ newsItem.date }}</span>
            <span class="source">{{ newsItem.source }}</span>
          </div>
          <h3>{{ newsItem.title }}</h3>
          <p>{{ newsItem.summary }}</p>
          <button class="inline-link" @click.stop="handleNewsClick(newsItem.id)">Перейти к новости</button>
        </article>
      </div>
    </section>

    <section class="actions card">
      <div>
        <h3>Что дальше?</h3>
        <p>Просматривайте график в деталях, анализируйте связи и создавайте отчет по рискам.</p>
      </div>
      <div class="cta">
        <button class="primary">Открыть график</button>
        <button class="secondary" @click="router.push('/reports')">Создать отчёт</button>
      </div>
    </section>
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

