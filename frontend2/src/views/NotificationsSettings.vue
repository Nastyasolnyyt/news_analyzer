<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { api as apiClient, type Entity } from '../api/client';
import AddEntityModal from '../components/AddEntityModal.vue';

const router = useRouter();

const statusEnabled = ref(true);
const loading = ref(true);
const error = ref<string | null>(null);
const saveSuccess = ref(false);
const isAuthenticated = ref(false);

// Модальное окно для добавления сущности
const showAddEntityModal = ref(false);
const addEntityType = ref<'ORG' | 'PER'>('ORG');

// Данные
const allOrganizations = ref<Entity[]>([]);
const allPersons = ref<Entity[]>([]);
const selectedOrganizations = ref<Set<number>>(new Set());
const selectedPersons = ref<Set<number>>(new Set());

// Поиск
const orgSearchQuery = ref('');
const personSearchQuery = ref('');

// Настройки уведомлений
const email = ref('');
const digestFrequency = ref('instant'); // instant, daily, weekly

// IDs триггеров и каналов для обновления
const orgTriggersMap = ref<Map<number, number>>(new Map());
const personTriggersMap = ref<Map<number, number>>(new Map());
let emailChannelId: number | null = null;
let notificationSettingsId: number | null = null;

// Проверка аутентификации
const checkAuth = () => {
  const token = localStorage.getItem('accessToken');
  if (!token) {
    router.push('/auth');
    return false;
  }
  isAuthenticated.value = true;
  return true;
};

// Вычисляемые свойства для фильтрации
const filteredOrganizations = computed(() => {
  const query = orgSearchQuery.value.toLowerCase();
  return query ? allOrganizations.value.filter(org => org.name.toLowerCase().includes(query)) : allOrganizations.value;
});

const filteredPersons = computed(() => {
  const query = personSearchQuery.value.toLowerCase();
  return query ? allPersons.value.filter(person => person.name.toLowerCase().includes(query)) : allPersons.value;
});

// Загрузить данные
onMounted(async () => {
  if (!checkAuth()) {
    return;
  }

  try {
    loading.value = true;
    error.value = null;

    // Загружаем конфиг, организации и персон параллельно
    let [config, orgs, persons_list] = await Promise.all([
      apiClient.getNotificationConfig(),
      apiClient.getOrganizations(100),
      apiClient.getPersons(100),
    ]);

    // Сохраняем организации и персон
    allOrganizations.value = orgs;
    allPersons.value = persons_list;

    // Инициализируем основные настройки, если их нет
    if (!config.settings || !config.settings.id) {
      console.log('⚠️ Settings not initialized, creating...');
      const newSettings = await apiClient.updateNotificationSettings({
        enabled: true,
        digest_frequency: 'instant',
      });
      config.settings = newSettings;
      notificationSettingsId = newSettings.id;
    } else {
      notificationSettingsId = config.settings.id;
    }

    // Инициализируем email канал, если его нет
    if (!config.channels || config.channels.length === 0) {
      console.log('⚠️ Email channel not found, creating...');
      try {
        const newChannel = await apiClient.createNotificationChannel({
          channel_type: 'email',
          channel_address: '',
          enabled: true,
        } as any);
        config.channels = [newChannel];
        emailChannelId = newChannel.id;
      } catch (e) {
        console.error('❌ Failed to create email channel:', e);
      }
    } else if (config.channels.length > 0 && config.channels[0].channel_type === 'email') {
      emailChannelId = config.channels[0].id;
    }

    // Загружаем настройки
    const settings = config.settings;
    statusEnabled.value = settings.enabled;
    digestFrequency.value = settings.digest_frequency || 'instant';

    // Восстанавливаем сохраненные триггеры
    const enabledOrgIds = new Set<number>();
    const enabledPersonIds = new Set<number>();
    
    config.triggers.forEach(trigger => {
      if (trigger.enabled) {
        if (trigger.trigger_type === 'organization') {
          const orgId = parseInt(trigger.trigger_value);
          enabledOrgIds.add(orgId);
          orgTriggersMap.value.set(orgId, trigger.id);
        } else if (trigger.trigger_type === 'person') {
          const personId = parseInt(trigger.trigger_value);
          enabledPersonIds.add(personId);
          personTriggersMap.value.set(personId, trigger.id);
        }
      }
    });
    
    selectedOrganizations.value = enabledOrgIds;
    selectedPersons.value = enabledPersonIds;

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

    // 1. Обновляем основные настройки
    if (notificationSettingsId) {
      await apiClient.updateNotificationSettings({
        enabled: statusEnabled.value,
        digest_frequency: digestFrequency.value,
      });
      console.log('✅ Settings updated');
    }

    // 2. Обновляем email канал
    if (emailChannelId) {
      await apiClient.updateNotificationChannel(emailChannelId, {
        channel_address: email.value,
        enabled: true,
      } as any);
      console.log('✅ Email channel updated');
    } else {
      // Создаем новый канал, если его нет
      const newChannel = await apiClient.createNotificationChannel({
        channel_type: 'email',
        channel_address: email.value,
        enabled: true,
      } as any);
      emailChannelId = newChannel.id;
      console.log('✅ Email channel created');
    }

    // 3. Синхронизируем триггеры для организаций
    // Получаем все текущие триггеры
    const config = await apiClient.getNotificationConfig();
    const currentOrgTriggers = new Map<number, number>();
    const currentPersonTriggers = new Map<number, number>();
    
    config.triggers.forEach(trigger => {
      if (trigger.trigger_type === 'organization') {
        const orgId = parseInt(trigger.trigger_value);
        currentOrgTriggers.set(orgId, trigger.id);
      } else if (trigger.trigger_type === 'person') {
        const personId = parseInt(trigger.trigger_value);
        currentPersonTriggers.set(personId, trigger.id);
      }
    });

    // Обновляем или создаем триггеры для организаций
    for (const orgId of selectedOrganizations.value) {
      if (currentOrgTriggers.has(orgId)) {
        // Обновляем существующий триггер
        const triggerId = currentOrgTriggers.get(orgId)!;
        await apiClient.updateNotificationTrigger(triggerId, {
          enabled: true,
        } as any);
        console.log(`✅ Org trigger ${orgId} updated`);
      } else {
        // Создаем новый триггер
        const org = allOrganizations.value.find(o => o.id === orgId);
        if (org) {
          await apiClient.createNotificationTrigger({
            name: `Watch ${org.name}`,
            trigger_type: 'organization',
            trigger_value: String(orgId),
            enabled: true,
          });
          console.log(`✅ Org trigger ${orgId} created`);
        }
      }
    }

    // Отключаем триггеры для невыбранных организаций
    for (const [orgId, triggerId] of currentOrgTriggers) {
      if (!selectedOrganizations.value.has(orgId)) {
        await apiClient.updateNotificationTrigger(triggerId, {
          enabled: false,
        } as any);
        console.log(`✅ Org trigger ${orgId} disabled`);
      }
    }

    // Обновляем или создаем триггеры для персон
    for (const personId of selectedPersons.value) {
      if (currentPersonTriggers.has(personId)) {
        // Обновляем существующий триггер
        const triggerId = currentPersonTriggers.get(personId)!;
        await apiClient.updateNotificationTrigger(triggerId, {
          enabled: true,
        } as any);
        console.log(`✅ Person trigger ${personId} updated`);
      } else {
        // Создаем новый триггер
        const person = allPersons.value.find(p => p.id === personId);
        if (person) {
          await apiClient.createNotificationTrigger({
            name: `Watch ${person.name}`,
            trigger_type: 'person',
            trigger_value: String(personId),
            enabled: true,
          });
          console.log(`✅ Person trigger ${personId} created`);
        }
      }
    }

    // Отключаем триггеры для невыбранных персон
    for (const [personId, triggerId] of currentPersonTriggers) {
      if (!selectedPersons.value.has(personId)) {
        await apiClient.updateNotificationTrigger(triggerId, {
          enabled: false,
        } as any);
        console.log(`✅ Person trigger ${personId} disabled`);
      }
    }

    saveSuccess.value = true;
    console.log('✅ All settings saved successfully');

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

const handleOpenAddEntityModal = (type: 'ORG' | 'PER') => {
  addEntityType.value = type;
  showAddEntityModal.value = true;
};

const handleEntityAdded = async (newEntity: any) => {
  console.log('✅ New entity added:', newEntity);
  
  // Добавляем новую сущность в соответствующий список
  const entity: Entity = {
    id: newEntity.id,
    name: newEntity.name,
    type: newEntity.entity_type === 'PER' ? 'Person' : 'Company',
    entity_type: newEntity.entity_type,
    description: `${newEntity.name} — ${newEntity.entity_type}`,
  };
  
  if (newEntity.entity_type === 'ORG') {
    // Добавляем в начало списка организаций
    allOrganizations.value.unshift(entity);
    // Автоматически выбираем новую сущность
    selectedOrganizations.value.add(newEntity.id);
  } else if (newEntity.entity_type === 'PER') {
    // Добавляем в начало списка персон
    allPersons.value.unshift(entity);
    // Автоматически выбираем новую сущность
    selectedPersons.value.add(newEntity.id);
  }
  
  saveSuccess.value = true;
  setTimeout(() => {
    saveSuccess.value = false;
  }, 3000);
};

const selectedOrgsCount = computed(() => selectedOrganizations.value.size);
const selectedPersonsCount = computed(() => selectedPersons.value.size);

const handleSendTestEmail = async () => {
  try {
    loading.value = true;
    error.value = null;

    const response = await fetch('/api/v1/notifications/test-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to send test email');
    }

    const data = await response.json();
    saveSuccess.value = true;
    console.log('✅ Test email sent successfully:', data);

    setTimeout(() => {
      saveSuccess.value = false;
    }, 3000);
  } catch (e: any) {
    error.value = e.message || 'Ошибка отправки тестового письма';
    console.error('❌ Error sending test email:', e);
  } finally {
    loading.value = false;
  }
};
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
      <p class="error-title">Ошибка</p>
      <p class="error-message">{{ error }}</p>
    </div>

    <div v-if="saveSuccess" class="success-banner">
      Настройки успешно сохранены!
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
          <button 
            class="add-entity-btn"
            @click="handleOpenAddEntityModal('ORG')"
            title="Добавить новую организацию"
          >
            + Добавить
          </button>
        </header>
        <div class="search-box">
          <input
            v-model="orgSearchQuery"
            type="text"
            placeholder="🔍 Поиск организации..."
            class="search-input"
          />
        </div>
        <div class="entities-list">
          <div v-if="filteredOrganizations.length === 0" class="empty-state">
            {{ orgSearchQuery ? 'Организации не найдены' : 'Организации не загружены' }}
          </div>
          <label v-for="org in filteredOrganizations" :key="org.id" class="entity-checkbox">
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
          <button 
            class="add-entity-btn"
            @click="handleOpenAddEntityModal('PER')"
            title="Добавить новую персону"
          >
            + Добавить
          </button>
        </header>
        <div class="search-box">
          <input
            v-model="personSearchQuery"
            type="text"
            placeholder="🔍 Поиск персоны..."
            class="search-input"
          />
        </div>
        <div class="entities-list">
          <div v-if="filteredPersons.length === 0" class="empty-state">
            {{ personSearchQuery ? 'Персоны не найдены' : 'Персоны не загружены' }}
          </div>
          <label v-for="person in filteredPersons" :key="person.id" class="entity-checkbox">
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
      <div class="button-group">
        <button class="primary" :disabled="loading" @click="handleSaveSettings">
          {{ loading ? 'Сохраняем...' : 'Сохранить настройки' }}
        </button>
        <button 
          class="secondary" 
          :disabled="loading || !email" 
          @click="handleSendTestEmail"
          title="Отправить тестовое письмо на указанный email"
        >
          📧 Тестовое письмо
        </button>
      </div>
    </section>

    <!-- Add Entity Modal -->
    <AddEntityModal
      :is-open="showAddEntityModal"
      @close="showAddEntityModal = false"
      @entity-added="handleEntityAdded"
    />
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

.search-box {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.search-input {
  flex: 1;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  color: #fff;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(79, 138, 255, 0.1);
  background: rgba(255, 255, 255, 0.12);
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

.add-entity-btn {
  padding: 8px 14px;
  background: rgba(79, 138, 255, 0.15);
  border: 1px solid rgba(79, 138, 255, 0.3);
  color: var(--accent);
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.add-entity-btn:hover {
  background: rgba(79, 138, 255, 0.25);
  border-color: var(--accent);
  box-shadow: 0 2px 8px rgba(79, 138, 255, 0.2);
}

.add-entity-btn:active {
  transform: scale(0.95);
}

.add-entity-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.button-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.secondary {
  padding: 12px 24px;
  background: rgba(168, 85, 247, 0.1);
  border: 1px solid rgba(168, 85, 247, 0.5);
  color: #d8b4fe;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.95rem;
}

.secondary:hover:not(:disabled) {
  background: rgba(168, 85, 247, 0.2);
  border-color: rgba(168, 85, 247, 0.8);
}

.secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .hero {
    flex-direction: column;
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }

  .button-group {
    flex-direction: column;
  }

  .primary, .secondary {
    align-self: stretch;
  }
}
</style>
