<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../api/client';

const router = useRouter();

interface TriggerItem {
  id: number;
  label: string;
  description?: string;
}

interface SourceItem {
  id: number;
  label: string;
}

const statusEnabled = ref(true);
const loading = ref(true);
const error = ref<string | null>(null);

// Реальные данные
const triggers = ref<TriggerItem[]>([]);
const sources = ref<SourceItem[]>([]);
const channels = ref<SourceItem[]>([]);

const selectedTriggers = ref(new Set<number>());
const selectedSources = ref(new Set<number>());
const selectedChannels = ref(new Set<number>());

// Загрузить данные при монтировании
onMounted(async () => {
  try {
    loading.value = true;
    error.value = null;
    
    const config = await api.getNotificationConfig();
    
    // Загружаем триггеры
    triggers.value = config.triggers.map(t => ({
      id: t.id,
      label: t.name,
      description: t.description,
    }));
    selectedTriggers.value = new Set(config.triggers.filter(t => t.enabled).map(t => t.id));
    
    // Загружаем источники
    sources.value = config.sources.map(s => ({
      id: s.id,
      label: s.source_type,
    }));
    selectedSources.value = new Set(config.sources.filter(s => s.enabled).map(s => s.id));
    
    // Загружаем каналы
    channels.value = config.channels.map(c => ({
      id: c.id,
      label: c.channel_type,
    }));
    selectedChannels.value = new Set(config.channels.filter(c => c.enabled).map(c => c.id));
    
    // Загружаем статус
    statusEnabled.value = config.settings.enabled;
    
    console.log('✅ Notification config loaded');
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки настроек уведомлений';
    console.error('❌ Error:', error.value);
  } finally {
    loading.value = false;
  }
});

const toggleSetValue = (target: ref<Set<number>>, value: number) => {
  const next = new Set(target.value);
  if (next.has(value)) {
    next.delete(value);
  } else {
    next.add(value);
  }
  target.value = next;
};

const handleTriggerToggle = (value: number) => {
  toggleSetValue(selectedTriggers as any, value);
};

const handleSourceToggle = (value: number) => {
  toggleSetValue(selectedSources as any, value);
};

const handleChannelToggle = (value: number) => {
  toggleSetValue(selectedChannels as any, value);
};

const handleSaveSettings = async () => {
  try {
    loading.value = true;
    
    // Обновляем статус
    await api.updateNotificationSettings({
      enabled: statusEnabled.value,
    });
    
    // Обновляем триггеры
    for (const trigger of triggers.value) {
      await api.updateNotificationTrigger(trigger.id, {
        enabled: selectedTriggers.value.has(trigger.id),
      } as any);
    }
    
    // Обновляем источники
    for (const source of sources.value) {
      await api.updateNotificationSource(source.id, {
        enabled: selectedSources.value.has(source.id),
      } as any);
    }
    
    // Обновляем каналы
    for (const channel of channels.value) {
      await api.updateNotificationChannel(channel.id, {
        enabled: selectedChannels.value.has(channel.id),
      } as any);
    }
    
    console.log('✅ Settings saved successfully');
    error.value = null;
    alert('Настройки успешно сохранены!');
  } catch (e: any) {
    error.value = e.message || 'Ошибка сохранения настроек';
    console.error('❌ Error saving settings:', error.value);
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
        <button class="icon-btn" aria-label="search" @click="router.push('/search')">
          <svg viewBox="0 0 24 24"><path d="M11 4a7 7 0 0 1 5.6 11.2l3.6 3.6-1.4 1.4-3.6-3.6A7 7 0 1 1 11 4Z" /></svg>
        </button>
        <button class="icon-btn" aria-label="notifications">
          <svg viewBox="0 0 24 24">
            <path d="M12 2a6 6 0 0 0-6 6v3.4l-.9 2.2a1 1 0 0 0 1 1.4h11.8a1 1 0 0 0 1-.6 1 1 0 0 0 0-.8L18 11.4V8a6 6 0 0 0-6-6Z" />
            <path d="M9 18a3 3 0 0 0 6 0" />
          </svg>
        </button>
        <button class="icon-btn profile" aria-label="profile">
          <span>AK</span>
        </button>
      </div>
    </header>

    <section class="hero">
      <div>
        <p class="overline">Настройки уведомлений</p>
        <h1>Триггеры и каналы</h1>
        <p class="subtitle">
          Управляйте тем, какие события нужно отслеживать и куда отправлять уведомления.
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
      <button class="outline" @click="location.reload()">Попробовать снова</button>
    </div>

    <section v-else class="settings-grid">
      <article class="card">
        <header>
          <div>
            <p class="overline">Триггеры</p>
            <h2>Что отслеживаем</h2>
          </div>
        </header>
        <ul class="checklist">
          <li v-for="trigger in triggers" :key="trigger.id">
            <label>
              <input
                type="checkbox"
                :checked="selectedTriggers.has(trigger.id)"
                @change="handleTriggerToggle(trigger.id)"
              />
              <div>
                <strong>{{ trigger.label }}</strong>
                <p v-if="trigger.description">{{ trigger.description }}</p>
              </div>
            </label>
          </li>
        </ul>
      </article>

      <article class="card">
        <header>
          <div>
            <p class="overline">Источники</p>
            <h2>Где ищем события</h2>
          </div>
        </header>
        <div class="pill-list">
          <button
            v-for="source in sources"
            :key="source.id"
            type="button"
            :class="{ selected: selectedSources.has(source.id) }"
            @click="handleSourceToggle(source.id)"
          >
            {{ source.label }}
          </button>
        </div>
      </article>

      <article class="card">
        <header>
          <div>
            <p class="overline">Каналы</p>
            <h2>Куда отправлять уведомления</h2>
          </div>
        </header>
        <div class="channel-list">
          <label v-for="channel in channels" :key="channel.id">
            <input
              type="checkbox"
              :checked="selectedChannels.has(channel.id)"
              @change="handleChannelToggle(channel.id)"
            />
            <span>{{ channel.label }}</span>
          </label>
        </div>
      </article>
    </section>

    <section class="summary card">
      <h3>Что вы получите</h3>
      <ul>
        <li>Push и Telegram при упоминании ключевых сущностей и тегов.</li>
        <li>Email-дайджест с ежедневным обзором найденных событий.</li>
        <li>Возможность быстро перейти в профиль или новость из уведомления.</li>
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
  background: rgba(248, 113, 113, 0.05);
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

.outline {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--text-base);
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  white-space: nowrap;
}

.checklist {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checklist label {
  display: flex;
  gap: 12px;
  cursor: pointer;
}

.checklist input {
  flex-shrink: 0;
  margin-top: 2px;
}

.checklist strong {
  display: block;
  font-weight: 600;
}

.checklist p {
  margin: 4px 0 0;
  color: var(--text-dim);
  font-size: 0.9rem;
}

.pill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pill-list button {
  padding: 8px 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  background: transparent;
  color: var(--text-base);
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-list button.selected {
  background: rgba(79, 138, 255, 0.2);
  border-color: var(--accent);
  color: var(--accent);
}

.channel-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.channel-list label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.channel-list input {
  cursor: pointer;
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
