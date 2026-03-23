<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api'; // Подключаем твой API

const router = useRouter();

// Критерии пока оставим статичными или можно будет потом передавать их через query-параметры
const criteria = ref({
  period: 'Последние 7 дней',
  entities: ['Тестовая Организация'],
  topics: ['Общий анализ'],
});

const allArticles = ref<any[]>([]);
const reportItems = ref<any[]>([]);
const isLoading = ref(true);

onMounted(async () => {
  try {
    // Загружаем новости из базы для формирования отчета
    const data = await api.getPosts();
    const items = data.items || data;
    
    allArticles.value = items;
    // По умолчанию добавим в отчет первые 5 новостей из базы
    reportItems.value = items.slice(0, 5);
  } catch (error) {
    console.error("Ошибка при получении данных для отчета:", error);
  } finally {
    isLoading.value = false;
  }
});

const totalFound = computed(() => allArticles.value.length);

const removeFromReport = (id: number) => {
  reportItems.value = reportItems.value.filter((item) => {
    const postId = item.post?.id || item.id;
    return postId !== id;
  });
};

const stats = computed(() => {
  const highRisk = reportItems.value.filter((item) => {
    const tonality = item.analysis?.tonality || 0;
    return tonality < -0.3;
  }).length;

  return {
    count: reportItems.value.length,
    highRisk,
  };
});

const handleNewsClick = (newsId: number) => {
  router.push(`/news/${newsId}`);
};

// Функция для имитации экспорта
const exportReport = (format: string) => {
  alert(`Отчет из ${reportItems.value.length} элементов экспортирован в ${format}`);
};
</script>

<template>
  <section class="report-page">
    <header class="page-header">
      <button class="logo" @click="router.push('/')">
        <span class="dot" />
        Atlas Report
      </button>
      <div class="header-actions">
        <button class="icon-btn" @click="router.push('/search')">Поиск</button>
        <button class="icon-btn profile">AK</button>
      </div>
    </header>

    <section class="hero card">
      <div>
        <p class="overline">Формирование отчёта</p>
        <h1>Результаты анализа базы</h1>
        <p>
          Данные сформированы на основе последних записей в вашей базе данных. 
          Вы можете удалить лишние элементы перед экспортом.
        </p>
      </div>
      <button class="primary" @click="router.push('/')">Добавить данные</button>
    </section>

    <div v-if="isLoading" class="loading-container">Загрузка данных из БД...</div>

    <template v-else>
      <section class="criteria card">
        <div class="criteria-line">
          <span class="label">Период:</span>
          <span>{{ criteria.period }}</span>
        </div>
        <div class="criteria-line">
          <span class="label">Сущности в поиске:</span>
          <span>
            <button v-for="entity in criteria.entities" :key="entity" class="pill">
              {{ entity }}
            </button>
          </span>
        </div>
      </section>

      <section class="news card">
        <header>
          <div>
            <p class="overline">Выбранные новости</p>
            <h2>{{ stats.count }} элементов в списке</h2>
          </div>
          <span class="count">Всего в базе: {{ totalFound }}</span>
        </header>
        
        <div class="news-list">
          <article
            v-for="item in reportItems"
            :key="item.post?.id || item.id"
            class="news-card"
            @click="handleNewsClick(item.post?.id || item.id)"
          >
            <div>
              <p class="title">[{{ item.post?.title || item.title }}]</p>
              <p class="meta">
                {{ item.post?.source || item.source }} — 
                {{ item.post?.created_at ? new Date(item.post.created_at).toLocaleDateString('ru-RU') : 'Дата не указана' }}
              </p>
            </div>
            <button class="remove" @click.stop="removeFromReport(item.post?.id || item.id)">×</button>
          </article>

          <p v-if="!reportItems.length" class="placeholder">
            Отчет пуст. Вернитесь на главную, чтобы выбрать новости.
          </p>
        </div>
      </section>

      <section class="stats card">
        <h3>Итоговая статистика</h3>
        <ul>
          <li>Объектов анализа: {{ stats.count }}</li>
          <li>Из них критических (высокий риск): {{ stats.highRisk }}</li>
          <li>Средняя тональность выборки: 
             {{ (reportItems.reduce((acc, curr) => acc + (curr.analysis?.tonality || 0), 0) / (reportItems.length || 1)).toFixed(2) }}
          </li>
        </ul>
      </section>

      <section class="actions card">
        <div>
          <h3>Экспортировать документ</h3>
          <p>Сформируйте готовый файл для отправки.</p>
        </div>
        <div class="cta-buttons">
          <button class="secondary" @click="exportReport('PDF')">Скачать PDF</button>
          <button class="secondary" @click="exportReport('Excel')">Скачать Excel</button>
        </div>
      </section>
    </template>
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
  border: none;
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
  cursor: pointer;
}

.icon-btn:hover {
  background: var(--surface-3);
}

.icon-btn svg {
  width: 20px;
  height: 20px;
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
  cursor: pointer;
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
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.news-card:hover {
  border-color: var(--accent);
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

.remove:hover {
  background: rgba(255, 255, 255, 0.15);
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