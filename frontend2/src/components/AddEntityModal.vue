<script setup lang="ts">
import { ref } from 'vue';
import { api, type CreateEntityDTO } from '../api/client';

interface Props {
  isOpen: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isOpen: false,
});

const emit = defineEmits<{
  close: [];
  entityAdded: [entity: any];
}>();

const entityName = ref('');
const entityType = ref<'ORG' | 'PER'>('ORG');
const loading = ref(false);
const error = ref<string | null>(null);

const handleAddEntity = async () => {
  if (!entityName.value.trim()) {
    error.value = 'Пожалуйста, введите название сущности';
    return;
  }

  try {
    loading.value = true;
    error.value = null;

    const newEntity = await api.createEntity({
      name: entityName.value.trim(),
      entity_type: entityType.value,
    });

    console.log('✅ Entity created:', newEntity);

    // Эмитим событие с новой сущностью
    emit('entityAdded', newEntity);

    // Очищаем форму
    entityName.value = '';
    entityType.value = 'ORG';

    // Закрываем модальное окно
    emit('close');
  } catch (e: any) {
    error.value = e.message || 'Ошибка при добавлении сущности';
    console.error('❌ Error:', e);
  } finally {
    loading.value = false;
  }
};

const handleClose = () => {
  entityName.value = '';
  error.value = null;
  emit('close');
};
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <header class="modal-header">
        <h2>Добавить новую сущность</h2>
        <button class="close-btn" @click="handleClose">✕</button>
      </header>

      <div class="modal-body">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="form-group">
          <label for="entity-name">Название сущности *</label>
          <input
            id="entity-name"
            v-model="entityName"
            type="text"
            placeholder="Например: ООО Компания или Иван Петров"
            class="input-field"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="entity-type">Тип сущности *</label>
          <select
            id="entity-type"
            v-model="entityType"
            class="input-field"
            :disabled="loading"
          >
            <option value="ORG">Организация</option>
            <option value="PER">Персона</option>
          </select>
        </div>

        <p class="info-text">
          После добавления сущность можно будет отслеживать в списке организаций или персон.
        </p>
      </div>

      <footer class="modal-footer">
        <button
          class="btn-secondary"
          @click="handleClose"
          :disabled="loading"
        >
          Отмена
        </button>
        <button
          class="btn-primary"
          @click="handleAddEntity"
          :disabled="loading || !entityName.trim()"
        >
          {{ loading ? 'Добавляем...' : 'Добавить' }}
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  padding: 24px 24px 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: background 0.2s, color 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.modal-body {
  padding: 24px;
  flex: 1;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.input-field {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-field:disabled {
  background-color: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
}

.error-message {
  padding: 12px;
  margin-bottom: 16px;
  background-color: #fee;
  color: #c91c1c;
  border: 1px solid #fca5a5;
  border-radius: 8px;
  font-size: 14px;
}

.info-text {
  margin-top: 16px;
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 0;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-secondary,
.btn-primary {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary:disabled,
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary:active:not(:disabled) {
  transform: scale(0.98);
}
</style>
