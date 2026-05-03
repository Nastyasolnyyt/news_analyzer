<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { api, type Entity } from '../api/client';

const router = useRouter();

const statusEnabled = ref(true);
const loading = ref(true);
const error = ref<string | null>(null);
const saveSuccess = ref(false);

// Данные
const organizations = ref<Entity[]>([]);
const persons = ref<Entity[]>([]);
const selectedOrganizations = ref<Set<number>>(new Set());
const selectedPersons = ref<Set<number>>(new Set());

// Настройки уведомлений
const email = ref('');
const mentionThreshold = ref(1);
const digestFrequency = ref('instant'); // instant, daily, weekly

// Загрузить данные
onMounted(async () => {
  try {
    loading.value = true;
    error.value = null;

    // Загружаем конфиг, организации и персон параллельно
    const [config, orgs, persons_list] = await Promise.all([
      api.getNotificationConfig(),
      api.getOrganizations(100),
      api.getPersons(100),
    ]);

    // Сохраняем организации и персон
    organizations.value = orgs;
    persons.value = persons_list;

    // Восстанавливаем сохраненные триггеры
    config.triggers.forEach(trigger => {
      if (trigger.trigger_type === 'organization') {
        selectedOrganizations.value.add(parseInt(trigger.trigger_value));
      } else if (trigger.trigger_type === 'person') {
        selectedPersons.value.add(parseInt(trigger.trigger_value));
      }
    });

    // Загружаем настройки
    const settings = config.settings;
    statusEnabled.value = settings.enabled;
    digestFrequency.value = settings.digest_frequency || 'instant';

    // Попытаемся получить email из первого канала (если есть)
    if (config.channels.length > 0 && config.channels[0].channel_type === 'email') {
      email.value = config.channels[0].channel_address || '';
    }

    console.log('✅ Loaded settings and entities');
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки';
    console.error('❌ Error:', e);
  } finally {
    loading.value = false;
  }
});

const toggleOrganization = (id: number) => {
  const next = new Set(selectedOrganizations.value);
  if (next.has(id)) {
    next.delete(id);
  } else {
    next.add(id);
  }
  selectedOrganizations.value = next;
};

const togglePerson = (id: number) => {
  const next = new Set(selectedPersons.value);
  if (next.has(id)) {
    next.delete(id);
  } else {
    next.add(id);
  }
  selectedPersons.value = next;
};

const handleSaveSettings = async () => {
  try {
    if (!email.value) {
      error.value = 'Пожалуйста, введите email';
      return;
    }

    loading.value = true;
    error.value = null;

    // Обновляем основные настройки
    await api.updateNotificationSettings({
      enabled: statusEnabled.value,
      digest_frequency: digestFrequency.value,
    });

    // Обновляем триггеры для организаций
    const config = await api.getNotificationConfig();
    const orgTriggers = config.triggers.filter(t => t.trigger_type === 'organization');
    for (const trigger of orgTriggers) {
      const orgId = parseInt(trigger.trigger_value);
      await api.updateNotificationTrigger(trigger.id, {
        enabled: selectedOrganizations.value.has(orgId),
      } as any);
    }

    // Обновляем триггеры для персон
    const personTriggers = config.triggers.filter(t => t.trigger_type === 'person');
    for (const trigger of personTriggers) {
      const personId = parseInt(trigger.trigger_value);
      await api.updateNotificationTrigger(trigger.id, {
        enabled: selectedPersons.value.has(personId),
      } as any);
    }

    // Обновляем email канал
    const emailChannel = config.channels.find(c => c.channel_type === 'email');
    if (emailChannel) {
      await api.updateNotificationChannel(emailChannel.id, {
        channel_address: email.value,
        enabled: true,
      } as any);
    }

    saveSuccess.value = true;
    console.log('✅ Settings saved');

    setTimeout(() => {
      saveSuccess.value = false;
    }, 3000);
  } catch (e: any) {
    error.value = e.message || 'Ошибка сохранения';
    console.error('❌ Error saving:', e);
  } finally {
    loading.value = false;
  }
};

const selectedOrgsCount = computed(() => selectedOrganizations.value.size);
const selectedPersonsCount = computed(() => selectedPersons.value.size);
</script>

<template>
  <section class="notify-page">
    <header class="page-header">
      <button class="logo" @click="router.push('/')">
        <span class="dot" />
        Signal Desk
      </button>
      <div class="header-actions">
        <button class="icon-btn" @click="router.push('/search')">
          <svg viewBox="0 0 24 24"><path d="M11 4a7 7 0 0 1 5.6 11.2l3.6 3.6-1.4 1.4-3.6-3.6A7 7 0 1 1 11 4Z" /></svg>
        </button>
        <button class="icon-btn">
          <svg viewBox="0 0 24 24">
            <path d="M12 2a6 6 0 0 0-6 6v3.4l-.9 2.2a1 1 0 0 0 1 1.4h11.8a1 1 0 0 0 1-.6 1 1 0 0 0 0-.8L18 11.4V8a6 6 0 0 0-6-6Z" />
            <path d="M9 18a3 3 0 0 0 6 0" />
          </svg>
        </button>
        <button class="icon-btn profile">
          <span>AK</span>
        </button>
      </div>
    </header>

    <section class="hero">
      <div>
        <p class="overline">Настройки уведомлений</p>
        <h1>Триггеры и каналы</h1>
        <p class="subtitle">
          Выбирайте организации и персон для мониторинга с получением уведомлений на email.
        </p>
      </div>
      <label class="status-toggle">
        <span>Статус</span>
        <button type="button" :class="{ active: statusEnabled }" @click="statusEnabled = !statusEnabled">
          <span class="pill" :class="{ on: statusEnabled }" />
          {{ statusEnabled ? 'Включено' : 'Выключено' }}
        </button>
      </label>
    </section>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>⏳ Загружаем настройки...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p class="error-title">❌ Ошибка</p>
      <p class="error-message">{{ error }}</p>
    </div>

    <div v-if="saveSuccess" class="success-banner">
      ✅ Настройки успешно сохранены!
    </div>

    <section v-if="!loading && !error" class="settings-grid">
      <!-- Email -->
      <article class="card">
        <header>
          <div>
            <p class="overline">Уведомления</p>
            <h2>Email для получения уведомлений</h2>
          </div>
        </header>
        <div class="form-group">
          <input
            v-model="email"
            type="email"
            placeholder="your.email@example.com"
            class="email-input"
          />
        </div>
        <div class="form-group">
          <label>Частота отправки:</label>
          <select v-model="digestFrequency" class="select-input">
            <option value="instant">Сразу же</option>
            <option value="daily">Ежедневно</option>
            <option value="weekly">Еженедельно</option>
          </select>
        </div>
      </article>

      <!-- Organizations -->
      <article class="card">
        <header>
          <div>
            <p class="overline">Организации</p>
            <h2>Отслеживать упоминания ({{ selectedOrgsCount }})</h2>
          </div>
        </header>
        <div class="entities-list">
          <div v-if="organizations.length === 0" class="empty-state">
            Организации не найдены
          </div>
          <label v-for="org in organizations" :key="org.id" class="entity-checkbox">
            <input
              type="checkbox"
              :checked="selectedOrganizations.has(org.id)"
              @change="toggleOrganization(org.id)"
            />
            <span class="entity-name">{{ org.name }}</span>
          </label>
        </div>
      </article>

      <!-- Persons -->
      <article class="card">
        <header>
          <div>
            <p class="overline">Персоны</p>
            <h2>Отслеживать упоминания ({{ selectedPersonsCount }})</h2>
          </div>
        </header>
        <div class="entities-list">
          <div v-if="persons.length === 0" class="empty-state">
            Персоны не найдены
          </div>
          <label v-for="person in persons" :key="person.id" class="entity-checkbox">
            <input
              type="checkbox"
              :checked="selectedPersons.has(person.id)"
              @change="togglePerson(person.id)"
            />
            <span class="entity-name">{{ person.name }}</span>
          </label>
        </div>
      </article>
    </section>

    <section v-if="!loading && !error" class="summary card">
      <h3>Сводка</h3>
      <ul>
        <li>Отслеживаете {{ selectedOrgsCount }} организаций и {{ selectedPersonsCount }} персон</li>
        <li>Уведомления будут отправлены на: {{ email }}</li>
        <li>Частота: {{ digestFrequency === 'instant' ? 'Сразу же' : digestFrequency === 'daily' ? 'Ежедневно' : 'Еженедельно' }}</li>
      </ul>
      <button class="primary" :disabled="loading" @click="handleSaveSettings">
        {{ loading ? 'Сохраняем...' : 'Сохранить настройки' }}
      </button>
    </section>
  </section>
</template>

<style scoped>
.notify-page {
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
  padding: 0 14px;
}

.hero {
  background: linear-gradient(120deg, rgba(79, 138, 255, 0.15), rgba(19, 23, 33, 0.9));
  border-radius: 22px;
  padding: 24px;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}

.overline {
  margin: 0;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  text-transform: uppercase;
}

.subtitle {
  margin: 8px 0 0;
  color: #d5dae5;
  max-width: 520px;
}

.status-toggle {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.9rem;
  color: var(--text-dim);
}

.status-toggle button {
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  padding: 8px 14px;
  background: rgba(0, 0, 0, 0.2);
  color: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-toggle button.active {
  border-color: transparent;
  background: rgba(79, 138, 255, 0.2);
  color: #fff;
}

.pill {
  width: 20px;
  height: 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  position: relative;
  transition: all 0.2s ease;
}

.pill.on {
  background: rgba(79, 138, 255, 0.8);
  transform: translateX(8px);
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 40px 20px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(79, 138, 255, 0.2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.2);
  border-radius: 16px;
  color: var(--negative);
}

.error-title {
  font-weight: 600;
  font-size: 1.1rem;
  margin: 0;
}

.error-message {
  color: var(--text-dim);
  margin: 0;
}

.success-banner {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #22c55e;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 0.9rem;
  text-align: center;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.card {
  background: var(--surface-2);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.card header > div {
  flex: 1;
}

.card h2 {
  margin: 4px 0 0;
  font-size: 1.1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.9rem;
  color: #d5dae5;
  font-weight: 500;
}

.email-input,
.select-input {
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  color: #fff;
  font-size: 0.95rem;
}

.email-input:focus,
.select-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(79, 138, 255, 0.1);
}

.entities-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
}

.entity-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.entity-checkbox:hover {
  background: rgba(79, 138, 255, 0.1);
}

.entity-checkbox input {
  cursor: pointer;
}

.entity-name {
  flex: 1;
  font-size: 0.95rem;
}

.empty-state {
  padding: 20px;
  text-align: center;
  color: var(--text-dim);
  font-size: 0.9rem;
}

.summary {
  grid-column: 1 / -1;
}

.summary h3 {
  margin: 0 0 16px;
  font-size: 1.1rem;
}

.summary ul {
  list-style: none;
  margin: 0 0 20px;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary li {
  margin: 0;
  padding-left: 24px;
  position: relative;
  color: #d5dae5;
  line-height: 1.6;
  font-size: 0.95rem;
}

.summary li:before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--positive);
  font-weight: 600;
}

.primary {
  padding: 12px 24px;
  background: rgba(79, 138, 255, 0.1);
  border: 1px solid var(--accent);
  color: var(--accent);
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  align-self: flex-start;
}

.primary:hover:not(:disabled) {
  background: rgba(79, 138, 255, 0.2);
}

.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .hero {
    flex-direction: column;
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
