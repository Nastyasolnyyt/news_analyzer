<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { api, type Entity, type News } from '../api/client';
 
const router = useRouter();
const route = useRoute();
const entityId = Number(route.params.id);
 
const entity = ref<Entity | null>(null);
const chartData = ref<Array<{ week: string; count: number; note?: string }>>([]);
const relatedEntities = ref<Array<{ id: number; name: string; type: string; relation: string }>>([]);
const newsList = ref<News[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
 
onMounted(async () => {
  try {
    loading.value = true;
    console.log('📋 Loading entity profile:', entityId);
    
    // Получаем полный профиль сущности
    const profile = await api.getEntityProfile(entityId);
    
    entity.value = profile.entity;
    chartData.value = profile.chartData;
    relatedEntities.value = profile.relatedEntities;
    newsList.value = profile.news;
    
    console.log('✅ Entity profile loaded:', entity.value?.name, {
      chartPoints: chartData.value.length,
      relatedEntities: relatedEntities.value.length,
      newsCount: newsList.value.length,
    });
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки профиля сущности';
    console.error('❌ Error:', error.value);
  } finally {
    loading.value = false;
  }
});
 
const handleNewsClick = (newsId: number) => {
  router.push(`/news/${newsId}`);
};

const handleRelatedEntityClick = (entityId: number) => {
  router.push(`/entity/${entityId}`);
};

// Вычисляем максимальное значение для графика после загрузки данных
const maxChartValue = ref(1);
watch(chartData, (newData) => {
  if (newData.length > 0) {
    maxChartValue.value = Math.max(...newData.map(d => d.count), 1);
  }
}, { immediate: true });
</script>
 
<template>
  <div class="entity-page">
    <div v-if="loading" class="loading">⏳ Загружаем профиль...</div>
    <div v-else-if="error" class="error">❌ {{ error }}</div>
    <div v-else-if="entity">
      <!-- Заголовок -->
      <section class="hero">
        <div class="back-nav">
          <button @click="router.back()" class="back-button">← Назад</button>
        </div>
        <h1>{{ entity.name }}</h1>
        <p class="entity-type">
          {{ entity.type === 'Company' ? '🏢 Компания' : entity.type === 'Person' ? '👤 Персона' : '📅 Событие' }}
        </p>
        <p v-if="entity.entity_type" class="meta">{{ entity.entity_type }}</p>
      </section>
 
      <!-- Основная информация -->
      <section class="info-grid">
        <!-- Описание -->
        <section v-if="entity.description" class="info-card card">
          <h2>Описание</h2>
          <p>{{ entity.description }}</p>
        </section>

        <!-- Регистрационная информация -->
        <section v-if="entity.registryInfo" class="info-card card">
          <h2>Регистрационные данные</h2>
          <dl class="registry-dl">
            <dt v-if="entity.registryInfo.address">Адрес</dt>
            <dd v-if="entity.registryInfo.address">{{ entity.registryInfo.address }}</dd>
            
            <dt v-if="entity.registryInfo.registry">Реестр</dt>
            <dd v-if="entity.registryInfo.registry">{{ entity.registryInfo.registry }}</dd>
            
            <dt v-if="entity.registryInfo.founded">Дата основания</dt>
            <dd v-if="entity.registryInfo.founded">{{ entity.registryInfo.founded }}</dd>
          </dl>
        </section>

        <!-- Идентификаторы -->
        <section v-if="entity.identifiers && entity.identifiers.length > 0" class="info-card card">
          <h2>Идентификаторы</h2>
          <dl class="identifiers-dl">
            <div v-for="(id, idx) in entity.identifiers" :key="idx">
              <dt>{{ id.label }}</dt>
              <dd>{{ id.value }}</dd>
            </div>
          </dl>
        </section>
      </section>

      <!-- График динамики упоминаний -->
      <section v-if="chartData.length > 0" class="mentions-card card">
        <header>
          <div>
            <p class="overline">Динамика упоминаний</p>
            <h2>Упоминания по дням (за неделю)</h2>
          </div>
          <span class="count">{{ chartData.reduce((sum, d) => sum + d.count, 0) }} всего</span>
        </header>
        
        <div class="chart-container">
          <div class="chart">
            <div 
              v-for="(item, idx) in chartData" 
              :key="idx" 
              class="bar"
              :title="item.note || `${item.week}: ${item.count} упоминаний`"
            >
              <div 
                class="bar-fill" 
                :style="{ height: `${maxChartValue > 0 ? (item.count / maxChartValue) * 100 : 0}%` }"
                :class="{ 'has-note': item.note }"
              >
                <span v-if="item.note" class="note">{{ item.note }}</span>
              </div>
              <span class="week">{{ item.week }}</span>
              <span class="bar-value">{{ item.count }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Связанные сущности -->
      <section v-if="relatedEntities.length > 0" class="related-card card">
        <header>
          <div>
            <p class="overline">Связи</p>
            <h2>Связанные сущности</h2>
          </div>
        </header>
        
        <div class="related-list">
          <div 
            v-for="(rel, idx) in relatedEntities" 
            :key="idx" 
            class="related-item"
            @click="handleRelatedEntityClick(rel.id)"
          >
            <div class="related-info">
              <span class="related-name">{{ rel.name }}</span>
              <span class="related-type">{{ rel.type === 'PER' ? 'Персона' : rel.type === 'ORG' ? 'Организация' : rel.type }}</span>
            </div>
            <span class="related-relation">{{ rel.relation }}</span>
          </div>
        </div>
      </section>

      <!-- Новости с упоминанием -->
      <section v-if="newsList.length > 0" class="mentions-card card">
        <header>
          <div>
            <p class="overline">Новости с упоминанием</p>
            <h2>Последние публикации</h2>
          </div>
          <span class="count">{{ newsList.length }} упоминаний</span>
        </header>
        
        <div class="mentions-list">
          <article v-for="news in newsList" :key="news.id" class="mention-card" tabindex="0">
            <div class="card-top">
              <h4>{{ news.title }}</h4>
              <span class="date">{{ new Date(news.pub_date || news.date || '').toLocaleDateString('ru-RU') }}</span>
            </div>
            <p class="summary">{{ news.text }}</p>
            <button class="inline-link" @click="handleNewsClick(news.id)">
              Перейти к новости →
            </button>
          </article>
        </div>
      </section>

      <!-- Пустое состояние -->
      <section v-if="newsList.length === 0 && chartData.length === 0" class="empty-state">
        <p>Нет данных об упоминаниях в системе</p>
      </section>
 
      <!-- Действия -->
      <section class="action-section">
        <button class="primary" @click="router.push('/search')">
          ← Вернуться к поиску
        </button>
      </section>
    </div>
  </div>
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

/* Info grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.info-card h2 {
  font-size: 1.1rem;
  margin: 0 0 12px;
  color: white;
}

.registry-dl,
.identifiers-dl {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 8px 16px;
  margin: 0;
}

.registry-dl dt,
.identifiers-dl dt {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  font-weight: 500;
}

.registry-dl dd,
.identifiers-dl dd {
  margin: 0;
  color: #d2d6e0;
  font-weight: 500;
}

/* Chart styles */
.chart-container {
  margin-top: 16px;
  overflow-x: auto;
}

.chart {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  padding: 20px 10px;
  min-height: 200px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 50px;
  position: relative;
}

.bar-fill {
  width: 100%;
  max-width: 60px;
  border-radius: 8px 8px 4px 4px;
  background: linear-gradient(180deg, var(--accent), rgba(79, 138, 255, 0.2));
  position: relative;
  transition: height 0.3s ease;
  min-height: 4px;
}

.bar-value {
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
}

.note {
  position: absolute;
  top: -32px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.7rem;
  background: rgba(15, 18, 26, 0.95);
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  white-space: nowrap;
  z-index: 10;
  pointer-events: none;
}

.week {
  font-size: 0.75rem;
  color: var(--text-dim);
  text-align: center;
}

/* Related entities */
.related-card header {
  margin-bottom: 16px;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.2s ease;
}

.related-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: var(--accent);
}

.related-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.related-name {
  font-weight: 600;
  color: white;
  font-size: 0.95rem;
}

.related-type {
  font-size: 0.75rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.related-relation {
  font-size: 0.8rem;
  color: var(--accent);
  padding: 4px 10px;
  background: rgba(79, 138, 255, 0.1);
  border-radius: 6px;
  font-weight: 500;
}

/* Mentions list */
.mentions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.mention-card {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: all 0.2s ease;
}

.mention-card:hover {
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.04);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.card-top h4 {
  margin: 0;
  font-size: 1rem;
  color: white;
}

.date {
  font-size: 0.8rem;
  color: var(--text-dim);
  white-space: nowrap;
}

.summary {
  margin: 0;
  color: #cfd3dc;
  font-size: 0.9rem;
  line-height: 1.5;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-dim);
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  border: 1px dashed rgba(255, 255, 255, 0.1);
}

.action-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
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

