<script setup lang="ts">
import { ref } from 'vue';

interface EntityLink {
  id: number;
  name: string;
  type: string;
  relation: string;
}

const article = {
  title: 'Регуляторы ЕС расширяют проверку инфраструктуры Northwind Energy',
  source: 'Reuters',
  date: '24 ноября 2025, 08:30',
  tags: ['санкции', 'финансы', 'высокий риск'],
  summary:
    'Европейские регуляторы инициировали углублённую проверку цепочки поставок Northwind Energy на фоне сообщений о растущих рисках и потенциальных нарушениях.',
  body: [
    'По данным источников, Европейское агентство по устойчивой энергетике направило запросы к подрядчикам Northwind Energy после обнаружения расхождений в отчётности о выбросах. Проверка затрагивает поставщиков редкоземельных материалов и логистические компании, обслуживающие ветропарки в Северном море.',
    'Аналитики отмечают, что ужесточение требований может повлиять на финансовую модель холдинга и увеличить стоимость страхования проектов. Руководство Northwind Energy заявило о готовности полностью сотрудничать с регуляторами.',
    'Дополнительное внимание уделяется взаимодействию с Aurora Capital и операторам портовой инфраструктуры. Согласно экспертам, компания может пересмотреть стратегию диверсификации поставок и усилить мониторинг подрядчиков.',
  ],
};

const relatedEntities: EntityLink[] = [
  { id: 1, name: 'Northwind Energy', type: 'Компания', relation: 'Фигурант' },
  { id: 2, name: 'Aurora Capital', type: 'Инвестфонд', relation: 'Акционер' },
  { id: 3, name: 'Европейское агентство по устойчивой энергетике', type: 'Регулятор', relation: 'Инициатор проверки' },
  { id: 4, name: 'Vertex Robotics', type: 'Компания', relation: 'Поставщик' },
];

const showSummary = ref(true);

const toggleMode = () => {
  showSummary.value = !showSummary.value;
};
</script>

<template>
  <section class="news-page">
    <header class="page-header">
      <button class="logo">
        <span class="dot" />
        PulseSight
      </button>
      <div class="actions">
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

    <section class="hero">
      <div class="meta">
        <span class="source">{{ article.source }}</span>
        <span class="date">{{ article.date }}</span>
      </div>
      <h1>{{ article.title }}</h1>
      <div class="tags">
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
      <p class="summary" v-if="showSummary">
        {{ article.summary }}
      </p>
      <div v-else class="full-text">
        <p v-for="paragraph in article.body" :key="paragraph">
          {{ paragraph }}
        </p>
      </div>
    </section>

    <section class="entities card">
      <header>
        <div>
          <p class="overline">Упомянутые сущности</p>
          <h2>Связанные участники</h2>
        </div>
        <button class="outline">Все связи</button>
      </header>
      <div class="entity-list">
        <article v-for="entity in relatedEntities" :key="entity.id" class="entity-card">
          <div>
            <p class="entity-type">{{ entity.type }}</p>
            <h3>{{ entity.name }}</h3>
            <p class="relation">{{ entity.relation }}</p>
          </div>
          <button class="inline-link">Профиль</button>
        </article>
      </div>
    </section>

    <section class="cta card">
      <div>
        <h3>Действия</h3>
        <p>Добавьте новость в отчёт, пометьте как важную или поделитесь с командой.</p>
      </div>
      <div class="cta-buttons">
        <button class="primary">Добавить в отчёт</button>
        <button class="secondary">Отметить как важное</button>
        <button class="ghost">Поделиться</button>
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

