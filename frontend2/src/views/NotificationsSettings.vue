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

// Результаты поиска (только когда есть текст)
const orgSearchResults = computed(() => {
  const query = orgSearchQuery.value.toLowerCase().trim();
  if (!query || query.length < 2) return [];
  return allOrganizations.value.filter(org => org.name.toLowerCase().includes(query)).slice(0, 15);
});

const personSearchResults = computed(() => {
  const query = personSearchQuery.value.toLowerCase().trim();
  if (!query || query.length < 2) return [];
  return allPersons.value.filter(person => person.name.toLowerCase().includes(query)).slice(0, 15);
});

// Получить выбранные сущности объектами
const selectedOrgsObjects = computed(() => {
  return Array.from(selectedOrganizations.value)
    .map(id => allOrganizations.value.find(o => o.id === id))
    .filter(Boolean) as Entity[];
});

const selectedPersonsObjects = computed(() => {
  return Array.from(selectedPersons.value)
    .map(id => allPersons.value.find(p => p.id === id))
    .filter(Boolean) as Entity[];
});

// Настройки уведомлений
const email = ref('');
const digestFrequency = ref('instant');

// IDs триггеров и каналов
const orgTriggersMap = ref<Map<number, number>>(new Map());
const personTriggersMap = ref<Map<number, number>>(new Map());
let emailChannelId: number | null = null;
let notificationSettingsId: number | null = null;

const checkAuth = () => {
  const token = localStorage.getItem('accessToken');
  if (!token) {
    router.push('/auth');
    return false;
  }
  isAuthenticated.value = true;
  return true;
};

// Загрузить все страницы с пагинацией
const loadAllPaginated = async (entityType: 'ORG' | 'PER'): Promise<Entity[]> => {
  const allItems: Entity[] = [];
  let page = 1;
  let hasMore = true;
  
  while (hasMore) {
    try {
      const result = await apiClient.getEntities({
        limit: 100,
        page,
        entity_type: entityType,
      });
      
      allItems.push(...result.items);
      
      if (result.items.length < 100) {
        hasMore = false;
      } else {
        page++;
      }
    } catch (error) {
      console.error(`❌ Error loading ${entityType} page ${page}:`, error);
      hasMore = false;
    }
  }
  
  return allItems;
};

onMounted(async () => {
  if (!checkAuth()) {
    return;
  }

  try {
    loading.value = true;
    error.value = null;

    const configPromise = apiClient.getNotificationConfig();
    const orgsPromise = loadAllPaginated('ORG');
    const personsPromise = loadAllPaginated('PER');
    
    const [config, orgs, persons_list] = await Promise.all([
      configPromise,
      orgsPromise,
      personsPromise,
    ]);

    allOrganizations.value = orgs;
    allPersons.value = persons_list;
    
    console.log(`✅ Loaded ${orgs.length} organizations and ${persons_list.length} persons`);

    if (!config.settings || !config.settings.id) {
      const newSettings = await apiClient.updateNotificationSettings({
        enabled: true,
        digest_frequency: 'instant',
      });
      config.settings = newSettings;
      notificationSettingsId = newSettings.id;
    } else {
      notificationSettingsId = config.settings.id;
    }

    if (!config.channels || config.channels.length === 0) {
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

    const settings = config.settings;
    statusEnabled.value = settings.enabled;
    digestFrequency.value = settings.digest_frequency || 'instant';

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

const addOrganization = (orgId: number) => {
  const next = new Set(selectedOrganizations.value);
  next.add(orgId);
  selectedOrganizations.value = next;
  orgSearchQuery.value = '';
};

const removeOrganization = (orgId: number) => {
  const next = new Set(selectedOrganizations.value);
  next.delete(orgId);
  selectedOrganizations.value = next;
};

const addPerson = (personId: number) => {
  const next = new Set(selectedPersons.value);
  next.add(personId);
  selectedPersons.value = next;
  personSearchQuery.value = '';
};

const removePerson = (personId: number) => {
  const next = new Set(selectedPersons.value);
  next.delete(personId);
  selectedPersons.value = next;
};

const handleSaveSettings = async () => {
  try {
    loading.value = true;
    error.value = null;

    // Сохраняем основные настройки
    await apiClient.updateNotificationSettings({
      enabled: statusEnabled.value,
      digest_frequency: digestFrequency.value,
    });

    // Сохраняем email
    if (emailChannelId && email.value) {
      await apiClient.updateNotificationChannel(emailChannelId, {
        channel_address: email.value,
      } as any);
    }

    // Обновляем триггеры организаций
    const currentOrgTriggers = new Map(orgTriggersMap.value);
    
    for (const orgId of selectedOrganizations.value) {
      if (currentOrgTriggers.has(orgId)) {
        const triggerId = currentOrgTriggers.get(orgId)!;
        await apiClient.updateNotificationTrigger(triggerId, { enabled: true } as any);
      } else {
        const org = allOrganizations.value.find(o => o.id === orgId);
        if (org) {
          await apiClient.createNotificationTrigger({
            name: `Watch ${org.name}`,
            trigger_type: 'organization',
            trigger_value: String(orgId),
            enabled: true,
          });
        }
      }
    }

    for (const [orgId, triggerId] of currentOrgTriggers) {
      if (!selectedOrganizations.value.has(orgId)) {
        await apiClient.updateNotificationTrigger(triggerId, { enabled: false } as any);
      }
    }

    // Обновляем триггеры персон
    const currentPersonTriggers = new Map(personTriggersMap.value);
    
    for (const personId of selectedPersons.value) {
      if (currentPersonTriggers.has(personId)) {
        const triggerId = currentPersonTriggers.get(personId)!;
        await apiClient.updateNotificationTrigger(triggerId, { enabled: true } as any);
      } else {
        const person = allPersons.value.find(p => p.id === personId);
        if (person) {
          await apiClient.createNotificationTrigger({
            name: `Watch ${person.name}`,
            trigger_type: 'person',
            trigger_value: String(personId),
            enabled: true,
          });
        }
      }
    }

    for (const [personId, triggerId] of currentPersonTriggers) {
      if (!selectedPersons.value.has(personId)) {
        await apiClient.updateNotificationTrigger(triggerId, { enabled: false } as any);
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
  const entity: Entity = {
    id: newEntity.id,
    name: newEntity.name,
    type: newEntity.entity_type === 'PER' ? 'Person' : 'Company',
    entity_type: newEntity.entity_type,
    description: `${newEntity.name} — ${newEntity.entity_type}`,
  };
  
  if (newEntity.entity_type === 'ORG') {
    allOrganizations.value.unshift(entity);
    selectedOrganizations.value.add(newEntity.id);
  } else if (newEntity.entity_type === 'PER') {
    allPersons.value.unshift(entity);
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

    saveSuccess.value = true;
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
          Используйте поиск для добавления организаций и персон в мониторинг.
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

      <!-- Organizations Search -->
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

        <!-- Search Input -->
        <div class="search-box">
          <input
            v-model="orgSearchQuery"
            type="text"
            placeholder="🔍 Поиск организации... (минимум 2 символа)"
            class="search-input"
          />
        </div>

        <!-- Search Results -->
        <div v-if="orgSearchQuery.length >= 2 && orgSearchResults.length > 0" class="search-results">
          <div class="results-label">Результаты поиска:</div>
          <button
            v-for="org in orgSearchResults"
            :key="org.id"
            class="result-item"
            @click="addOrganization(org.id)"
          >
            <span class="result-name">{{ org.name }}</span>
            <span class="add-icon">+</span>
          </button>
        </div>

        <!-- Selected Organizations -->
        <div v-if="selectedOrgsObjects.length > 0" class="selected-items">
          <div class="items-label">Выбранные организации:</div>
          <div v-for="org in selectedOrgsObjects" :key="org.id" class="selected-item">
            <span class="item-name">{{ org.name }}</span>
            <button class="remove-btn" @click="removeOrganization(org.id)">✕</button>
          </div>
        </div>

        <div v-else-if="orgSearchQuery.length === 0" class="empty-state">
          Выберите организации через поиск
        </div>
      </article>

      <!-- Persons Search -->
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

        <!-- Search Input -->
        <div class="search-box">
          <input
            v-model="personSearchQuery"
            type="text"
            placeholder="🔍 Поиск персоны... (минимум 2 символа)"
            class="search-input"
          />
        </div>

        <!-- Search Results -->
        <div v-if="personSearchQuery.length >= 2 && personSearchResults.length > 0" class="search-results">
          <div class="results-label">Результаты поиска:</div>
          <button
            v-for="person in personSearchResults"
            :key="person.id"
            class="result-item"
            @click="addPerson(person.id)"
          >
            <span class="result-name">{{ person.name }}</span>
            <span class="add-icon">+</span>
          </button>
        </div>

        <!-- Selected Persons -->
        <div v-if="selectedPersonsObjects.length > 0" class="selected-items">
          <div class="items-label">Выбранные персоны:</div>
          <div v-for="person in selectedPersonsObjects" :key="person.id" class="selected-item">
            <span class="item-name">{{ person.name }}</span>
            <button class="remove-btn" @click="removePerson(person.id)">✕</button>
          </div>
        </div>

        <div v-else-if="personSearchQuery.length === 0" class="empty-state">
          Выберите персон через поиск
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
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.card header div h2 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.add-entity-btn {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid rgba(79, 138, 255, 0.3);
  background: rgba(79, 138, 255, 0.1);
  color: rgba(79, 138, 255, 0.8);
  cursor: pointer;
  font-size: 0.85rem;
  white-space: nowrap;
}

.add-entity-btn:hover {
  background: rgba(79, 138, 255, 0.15);
}

.search-box {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
  color: inherit;
  font-size: 0.9rem;
}

.search-input:focus {
  outline: none;
  border-color: rgba(79, 138, 255, 0.5);
  background: rgba(0, 0, 0, 0.3);
}

.search-results {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 12px;
}

.results-label {
  font-size: 0.8rem;
  color: var(--text-dim);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  margin-bottom: 4px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: transparent;
  color: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
}

.result-item:hover {
  background: rgba(79, 138, 255, 0.1);
  border-color: rgba(79, 138, 255, 0.3);
}

.result-name {
  text-align: left;
  flex: 1;
}

.add-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  background: rgba(79, 138, 255, 0.3);
  font-size: 0.8rem;
  font-weight: bold;
}

.selected-items {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 12px;
}

.items-label {
  font-size: 0.8rem;
  color: var(--text-dim);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.selected-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  margin-bottom: 6px;
  border-radius: 6px;
  background: rgba(79, 138, 255, 0.1);
  border: 1px solid rgba(79, 138, 255, 0.2);
}

.item-name {
  color: #fff;
  font-weight: 500;
}

.remove-btn {
  width: 20px;
  height: 20px;
  border-radius: 3px;
  border: none;
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
  cursor: pointer;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: rgba(248, 113, 113, 0.3);
}

.empty-state {
  color: var(--text-dim);
  font-size: 0.9rem;
  text-align: center;
  padding: 16px 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.85rem;
  color: var(--text-dim);
}

.email-input,
.select-input {
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
  color: inherit;
  font-size: 0.9rem;
}

.email-input:focus,
.select-input:focus {
  outline: none;
  border-color: rgba(79, 138, 255, 0.5);
  background: rgba(0, 0, 0, 0.3);
}

.summary {
  grid-column: 1 / -1;
}

.summary h3 {
  margin: 0 0 12px;
  font-size: 1rem;
}

.summary ul {
  list-style: none;
  padding: 0;
  margin: 0 0 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.9rem;
  color: var(--text-dim);
}

.button-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.primary,
.secondary {
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary {
  background: linear-gradient(120deg, rgba(79, 138, 255, 0.8), rgba(79, 138, 255, 0.6));
  color: #fff;
}

.primary:hover:not(:disabled) {
  background: linear-gradient(120deg, rgba(79, 138, 255, 0.9), rgba(79, 138, 255, 0.7));
}

.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.secondary {
  background: rgba(255, 255, 255, 0.05);
  color: inherit;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.secondary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
