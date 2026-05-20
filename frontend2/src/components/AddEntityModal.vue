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
const checking = ref(false);
const error = ref<string | null>(null);
const isDuplicate = ref(false);

// Проверяем существование сущности через backend вместо загрузки всех
const checkDuplicate = async (name: string, type: string) => {
  if (!name.trim()) {
    isDuplicate.value = false;
    return;
  }

  try {
    checking.value = true;
    // Используем поиск через limit=1 и search-подобный параметр
    const results = await api.searchEntity(name.trim(), type);
    isDuplicate.value = results.length > 0;
    if (isDuplicate.value) {
      console.log('⚠️ Entity found:', results[0]);
    }
  } catch (e) {
    console.error('Error checking duplicate:', e);
    isDuplicate.value = false;
  } finally {
    checking.value = false;
  }
};

const handleNameInput = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  // Дебаунс: проверяем после набора текста
  await checkDuplicate(target.value, entityType.value);
};

const handleTypeChange = async () => {
  await checkDuplicate(entityName.value, entityType.value);
};

const handleAddEntity = async () => {
  if (!entityName.value.trim()) {
    error.value = 'Пожалуйста, введите название сущности';
    return;
  }

  if (isDuplicate.value) {
    error.value = `❌ Сущность '${entityName.value}' типа '${entityType.value === 'ORG' ? 'Организация' : 'Персона'}' уже существует в системе`;
    return;
  }

  // ДВОЙНАЯ ПРОВЕРКА: перед отправкой проверяем еще раз
  try {
    loading.value = true;
    error.value = null;
    
    console.log(`🔍 Double-checking for duplicates before submit...`);
    const finalCheck = await api.searchEntity(entityName.value.trim(), entityType.value);
    
    if (finalCheck.length > 0) {
      error.value = `❌ Сущность '${entityName.value}' типа '${entityType.value === 'ORG' ? 'Организация' : 'Персона'}' уже существует в системе`;
      console.warn('⚠️ Duplicate detected on final check:', finalCheck);
      return;
    }

    const newEntity = await api.createEntity({
      name: entityName.value.trim(),
      entity_type: entityType.value,
    });

    console.log('✅ Entity created successfully:', newEntity);
    emit('entityAdded', newEntity);

    // Очищаем форму
    entityName.value = '';
    entityType.value = 'ORG';
    isDuplicate.value = false;

    emit('close');
  } catch (e: any) {
    if (e.message && e.message.includes('Сущность')) {
      error.value = e.message.replace(/^❌\s*/, '');
    } else {
      error.value = e.message || 'Ошибка при добавлении сущности';
    }
    console.error('❌ Error:', e);
  } finally {
    loading.value = false;
  }
};

const handleClose = () => {
  entityName.value = '';
  error.value = null;
  isDuplicate.value = false;
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

        <div v-if="isDuplicate" class="warning-message">
          ⚠️ Такая сущность уже существует в системе!
        </div>

        <div class="form-group">
          <label for="entity-name">
            Название сущности *
            <span v-if="isDuplicate" class="duplicate-badge">уже существует</span>
            <span v-if="checking" class="checking-badge">⏳ проверка...</span>
          </label>
          <input
            id="entity-name"
            v-model="entityName"
            type="text"
            placeholder="Например: ООО Компания или Иван Петров"
            class="input-field"
            :disabled="loading"
            :class="{ 'input-error': isDuplicate }"
            @input="handleNameInput"
          />
        </div>

        <div class="form-group">
          <label for="entity-type">Тип сущности *</label>
          <select
            id="entity-type"
            v-model="entityType"
            class="input-field"
            :disabled="loading"
            @change="handleTypeChange"
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
          :disabled="loading || !entityName.trim() || isDuplicate || checking"
        >
          {{ isDuplicate ? '❌ Уже существует' : loading ? 'Добавляем...' : 'Добавить' }}
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
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
}

.modal-body {
  padding: 20px;
  flex: 1;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.duplicate-badge,
.checking-badge {
  display: inline-block;
  background: #fee;
  color: #c33;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-left: 8px;
  font-weight: normal;
}

.checking-badge {
  background: #ffeaa7;
  color: #d63031;
}

.input-field {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.input-field:focus {
  outline: none;
  border-color: #0066cc;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

.input-error {
  border-color: #cc3333;
  background-color: #fff5f5;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
  border-left: 4px solid #c33;
}

.warning-message {
  background-color: #ffeaa7;
  color: #d63031;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
  border-left: 4px solid #fdcb6e;
}

.info-text {
  color: #666;
  font-size: 13px;
  margin: 12px 0 0 0;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #0066cc;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0052a3;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background: #e0e0e0;
}


.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
}

.modal-body {
  padding: 20px;
  flex: 1;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.duplicate-badge {
  display: inline-block;
  background: #fee;
  color: #c33;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-left: 8px;
  font-weight: normal;
}

.input-field {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.input-field:focus {
  outline: none;
  border-color: #0066cc;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

.input-error {
  border-color: #cc3333;
  background-color: #fff5f5;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
  border-left: 4px solid #c33;
}

.warning-message {
  background-color: #ffeaa7;
  color: #d63031;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
  border-left: 4px solid #fdcb6e;
}

.info-text {
  color: #666;
  font-size: 13px;
  margin: 12px 0 0 0;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #0066cc;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0052a3;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background: #e0e0e0;
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
