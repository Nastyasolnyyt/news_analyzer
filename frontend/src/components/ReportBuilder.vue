<script setup lang="ts">
import { computed, ref } from 'vue';

interface Criteria {
  period: string;
  entities: string[];
  topics: string[];
}

interface ReportNews {
  id: number;
  title: string;
  date: string;
  source: string;
  risk: 'low' | 'medium' | 'high';
}

const criteria: Criteria = {
  period: '10.10.2025 — 19.10.2025',
  entities: ['Газпром', 'Иванов А.Л.'],
  topics: ['Санкции', 'Назначения'],
};

const availableNews: ReportNews[] = [
  { id: 1, title: 'Санкции против Х', date: '18.10.2025', source: 'РБК', risk: 'high' },
  { id: 2, title: 'Санкции против Y', date: '18.10.2025', source: 'РБК', risk: 'medium' },
  { id: 3, title: 'Назначение в Газпром', date: '17.10.2025', source: 'Ведомости', risk: 'low' },
  { id: 4, title: 'Отчёт о проверке', date: '16.10.2025', source: 'Коммерсантъ', risk: 'medium' },
  { id: 5, title: 'Риски поставок газа', date: '15.10.2025', source: 'Bloomberg', risk: 'high' },
];

const reportItems = ref<ReportNews[]>(availableNews.slice(0, 4));

const totalFound = availableNews.length;
const removeFromReport = (id: number) => {
  reportItems.value = reportItems.value.filter((item) => item.id !== id);
};

const stats = computed(() => {
  const highRisk = reportItems.value.filter((item) => item.risk === 'high').length;
  return {
    count: reportItems.value.length,
    highRisk,
  };
});
</script>

<template>
  <section class="report-page">
    <header class="page-header">
      <button class="logo">
        <span class="dot" />
        Report Studio
      </button>
      <div class="header-actions">
        <button class="icon-btn" aria-label="search">
          <svg viewBox="0 0 24 24"><path d="M11 4a7 7 0 0 1 5.6 11.2l3.6 3.6-1.4 1.4-3.6-3.6A7 7 0 1 1 11 4Z" /></svg>
        </button>
        <button class="icon-btn" aria-label="notifications">
          <svg viewBox="0 0 24 24">
            <path
              d="M12 2a6 6 0 0 0-6 6v3.4l-.9 2.2a1 1 0 0 0 1 1.4h11.8a1 1 0 0 0 1-.6 1 1 0 0 0 0-.8L18 11.4V8a6 6 0 0 0-6-6Z"
            />
            <path d="M9 18a3 3 0 0 0 6 0" />
          </svg>
        </button>
        <button class="icon-btn profile" aria-label="profile">
          <span>AK</span>
        </button>
      </div>
    </header>

    <section class="hero card">
      <div>
        <p class="overline">Формирование отчёта</p>
        <h1>Подборка по заданным критериям</h1>
        <p>
          Соберите данные, отфильтруйте нужные новости и экспортируйте в формат PDF или Excel для
          отправки заинтересованным сторонам.
        </p>
      </div>
      <button class="primary">Найти новости</button>
    </section>

    <section class="criteria card">
      <div class="criteria-line">
        <span class="label">Период:</span>
        <span>{{ criteria.period }}</span>
      </div>
      <div class="criteria-line">
        <span class="label">Сущности:</span>
        <span>
          <button v-for="entity in criteria.entities" :key="entity" class="pill">
            {{ entity }}
          </button>
        </span>
      </div>
      <div class="criteria-line">
        <span class="label">Темы:</span>
        <span>
          <button v-for="topic in criteria.topics" :key="topic" class="pill neutral">
            {{ topic }}
          </button>
        </span>
      </div>
    </section>

    <section class="news card">
      <header>
        <div>
          <p class="overline">Новости в отчёте</p>
          <h2>{{ stats.count }} элементов</h2>
        </div>
        <span class="count">Всего найдено {{ totalFound }}</span>
      </header>
      <div class="news-list">
        <article v-for="item in reportItems" :key="item.id" class="news-card">
          <div>
            <p class="title">[{{ item.title }}]</p>
            <p class="meta">{{ item.date }} — Источник: {{ item.source }}</p>
          </div>
          <button class="remove" aria-label="Удалить" @click="removeFromReport(item.id)">×</button>
        </article>
        <p v-if="!reportItems.length" class="placeholder">
          Нет выбранных новостей — добавьте их из подборки.
        </p>
      </div>
    </section>

    <section class="stats card">
      <h3>Статистика</h3>
      <ul>
        <li>Всего найдено: {{ totalFound }}</li>
        <li>В отчёте: {{ stats.count }}</li>
        <li>Высокий риск: {{ stats.highRisk }}</li>
      </ul>
    </section>

    <section class="actions card">
      <div>
        <h3>Экспортировать</h3>
        <p>Проверьте состав и выгрузите отчёт в нужном формате.</p>
      </div>
      <div class="cta-buttons">
        <button class="secondary">Экспорт в PDF</button>
        <button class="secondary">Экспорт в Excel</button>
      </div>
    </section>
  </section>
</template>

<style scoped>
.report-page {
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

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(120deg, var(--accent), var(--positive));
}

.header-actions {
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
  padding: 0 14px;
}

.card {
  background: var(--surface-2);
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 20px;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}

.overline {
  margin: 0;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  text-transform: uppercase;
}

.hero p {
  margin: 8px 0 0;
  color: #d0d6e2;
  max-width: 520px;
}

.primary {
  border: none;
  border-radius: 14px;
  padding: 12px 22px;
  background: var(--accent);
  color: white;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 12px 30px rgba(79, 138, 255, 0.35);
}

.criteria {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.criteria-line {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.label {
  font-size: 0.85rem;
  color: var(--text-dim);
}

.pill {
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(79, 138, 255, 0.15);
  color: #fff;
  padding: 6px 12px;
  margin-right: 6px;
}

.pill.neutral {
  background: rgba(255, 255, 255, 0.08);
}

.news header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.count {
  font-size: 0.85rem;
  color: var(--text-dim);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  padding: 6px 12px;
}

.news-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 320px;
  overflow: auto;
  padding-right: 6px;
}

.news-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.title {
  margin: 0;
  font-weight: 600;
}

.meta {
  margin: 6px 0 0;
  color: var(--text-dim);
  font-size: 0.9rem;
}

.remove {
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: inherit;
  width: 32px;
  height: 32px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 1.2rem;
}

.placeholder {
  margin: 0;
  color: var(--text-dim);
  text-align: center;
}

.stats ul {
  margin: 12px 0 0;
  padding-left: 18px;
  color: #d0d6e2;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.cta-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.secondary {
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: transparent;
  color: inherit;
  padding: 12px 18px;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 900px) {
  .actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .cta-buttons {
    width: 100%;
  }

  .cta-buttons button {
    flex: 1;
  }
}
</style>

