<script setup lang="ts">
import { ref, type Ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

interface TriggerItem {
  id: string;
  label: string;
  description?: string;
}

interface SourceItem {
  id: string;
  label: string;
}

const statusEnabled = ref(true);

const triggers: TriggerItem[] = [
  { id: 'gazprom', label: 'Упоминание «Газпром»', description: 'Следить за новыми сообщениями о компании' },
  { id: 'sanctions', label: 'События с тегом «санкции»' },
  { id: 'gov-category', label: 'Новые сущности в категории «госструктуры»' },
];

const sources: SourceItem[] = [
  { id: 'telegram', label: 'Telegram' },
  { id: 'vk', label: 'VK' },
  { id: 'email', label: 'Email-дайджест' },
];

const channels: SourceItem[] = [
  { id: 'app', label: 'Внутри системы' },
  { id: 'email-channel', label: 'Email' },
  { id: 'tg-channel', label: 'Telegram Bot' },
];

const selectedTriggers = ref(new Set<string>(['gazprom', 'sanctions', 'gov-category']));
const selectedSources = ref(new Set<string>(['telegram', 'vk']));
const selectedChannels = ref(new Set<string>(['app', 'tg-channel']));

const toggleSetValue = (target: Ref<Set<string>>, value: string) => {
  const next = new Set(target.value);
  if (next.has(value)) {
    next.delete(value);
  } else {
    next.add(value);
  }
  target.value = next;
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

    <section class="settings-grid">
      <article class="card">
        <header>
          <div>
            <p class="overline">Триггеры</p>
            <h2>Что отслеживаем</h2>
          </div>
          <button class="outline">Добавить правило</button>
        </header>
        <ul class="checklist">
          <li v-for="trigger in triggers" :key="trigger.id">
            <label>
              <input
                type="checkbox"
                :checked="selectedTriggers.has(trigger.id)"
                @change="toggleSetValue(selectedTriggers, trigger.id)"
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
            @click="toggleSetValue(selectedSources, source.id)"
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
              @change="toggleSetValue(selectedChannels, channel.id)"
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
      <button class="primary">Сохранить настройки</button>
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
  width: 36px;
  height: 18px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  position: relative;
  transition: background 0.2s ease;
}

.pill::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  top: 1px;
  left: 1px;
  border-radius: 50%;
  background: #fff;
  transition: transform 0.2s ease;
}

.pill.on {
  background: var(--accent);
}

.pill.on::after {
  transform: translateX(18px);
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.card {
  background: var(--surface-2);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 20px;
}

.card header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.outline {
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  padding: 6px 12px;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.checklist {
  list-style: none;
  margin: 16px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checklist label {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.checklist strong {
  display: block;
}

.checklist p {
  margin: 4px 0 0;
  color: var(--text-dim);
  font-size: 0.9rem;
}

.pill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}

.pill-list button {
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: transparent;
  color: inherit;
  padding: 8px 16px;
  cursor: pointer;
}

.pill-list button.selected {
  background: var(--accent);
  color: #fff;
  border-color: transparent;
}

.channel-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 16px;
}

.channel-list label {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary ul {
  margin: 0;
  padding-left: 18px;
  color: var(--text-dim);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.primary {
  align-self: flex-start;
  border: none;
  border-radius: 14px;
  padding: 12px 22px;
  background: var(--accent);
  color: white;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 10px 24px rgba(79, 138, 255, 0.3);
}

@media (max-width: 800px) {
  .hero {
    flex-direction: column;
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }

  .primary {
    width: 100%;
    text-align: center;
  }
}
</style>

