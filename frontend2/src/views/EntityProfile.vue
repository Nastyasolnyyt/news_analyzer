<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { api, type Entity, type News } from '../api/client';
 
const router = useRouter();
const route = useRoute();
const entityId = Number(route.params.id);
 
const entity = ref<Entity | null>(null);
const mentions = ref<News[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
 
onMounted(async () => {
  try {
    loading.value = true;
    console.log('📋 Loading entity:', entityId);
    
    // Получаем упоминания сущности (они содержат информацию о сущности)
    const mentionData = await api.getEntityMentions(entityId);
    
    if (mentionData.length === 0) {
      throw new Error('Сущность не найдена');
    }
    
    // Извлекаем информацию о сущности из первого упоминания
    const entityInfo = mentionData[0]?.entity;
    if (entityInfo) {
      entity.value = {
        id: entityInfo.id,
        name: entityInfo.name,
        type: 'Company', // можно определить по entity_type
        entity_type: entityInfo.entity_type,
        linkedEntityIds: [],
      };
    }
    
    // Преобразуем упоминания в новости
    mentions.value = mentionData.map((m: any) => ({
      id: m.post_id,
      title: `Упоминание #${m.post_id}`,
      text: `Упомянута сущность: ${entityInfo?.name}`,
      source: 'система',
      date: m.mentioned_at,
      pub_date: m.mentioned_at,
    }));
    
    console.log('✅ Entity loaded:', entity.value?.name, 'with', mentions.value.length, 'mentions');
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки сущности';
    console.error('❌ Error:', error.value);
  } finally {
    loading.value = false;
  }
});
 
const handleNewsClick = (newsId: number) => {
  router.push(`/news/${newsId}`);
};
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
      <section v-if="entity.description" class="info-card card">
        <h2>Описание</h2>
        <p>{{ entity.description }}</p>
      </section>
 
      <!-- Упоминания -->
      <section v-if="mentions.length > 0" class="mentions-card card">
        <header>
          <div>
            <p class="overline">Упоминания в системе</p>
            <h2>Новости с упоминанием</h2>
          </div>
          <span class="count">{{ mentions.length }} упоминаний</span>
        </header>
        
        <div class="mentions-list">
          <article v-for="mention in mentions" :key="mention.id" class="mention-card" tabindex="0">
            <div class="card-top">
              <h4>{{ mention.title }}</h4>
              <span class="date">{{ new Date(mention.pub_date || mention.date || '').toLocaleDateString('ru-RU') }}</span>
            </div>
            <p class="summary">{{ mention.text }}</p>
            <button class="inline-link" @click="handleNewsClick(mention.id)">
              Перейти к новости →
            </button>
          </article>
        </div>
      </section>
 
      <!-- Пустое состояние -->
      <section v-else class="empty-state">
        <p>Нет упоминаний в системе</p>
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

