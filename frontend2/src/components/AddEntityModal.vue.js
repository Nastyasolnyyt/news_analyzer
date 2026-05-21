import { ref } from 'vue';
import { api } from '../api/client';
const props = withDefaults(defineProps(), {
    isOpen: false,
});
const emit = defineEmits();
const entityName = ref('');
const entityType = ref('ORG');
const loading = ref(false);
const checking = ref(false);
const error = ref(null);
const isDuplicate = ref(false);
// Проверяем существование сущности через backend вместо загрузки всех
const checkDuplicate = async (name, type) => {
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
    }
    catch (e) {
        console.error('Error checking duplicate:', e);
        isDuplicate.value = false;
    }
    finally {
        checking.value = false;
    }
};
const handleNameInput = async (event) => {
    const target = event.target;
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
    }
    catch (e) {
        if (e.message && e.message.includes('Сущность')) {
            error.value = e.message.replace(/^❌\s*/, '');
        }
        else {
            error.value = e.message || 'Ошибка при добавлении сущности';
        }
        console.error('❌ Error:', e);
    }
    finally {
        loading.value = false;
    }
};
const handleClose = () => {
    entityName.value = '';
    error.value = null;
    isDuplicate.value = false;
    emit('close');
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_withDefaultsArg = (function (t) { return t; })({
    isOpen: false,
});
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['modal-header']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['checking-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-content']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-header']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-header']} */ ;
/** @type {__VLS_StyleScopedClasses['close-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-body']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['duplicate-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['input-error']} */ ;
/** @type {__VLS_StyleScopedClasses['error-message']} */ ;
/** @type {__VLS_StyleScopedClasses['warning-message']} */ ;
/** @type {__VLS_StyleScopedClasses['info-text']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-footer']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-content']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-header']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-header']} */ ;
/** @type {__VLS_StyleScopedClasses['close-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['close-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-body']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['error-message']} */ ;
/** @type {__VLS_StyleScopedClasses['info-text']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-footer']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
// CSS variable injection 
// CSS variable injection end 
if (__VLS_ctx.isOpen) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ onClick: (__VLS_ctx.handleClose) },
        ...{ class: "modal-overlay" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ onClick: () => { } },
        ...{ class: "modal-content" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)({
        ...{ class: "modal-header" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.handleClose) },
        ...{ class: "close-btn" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "modal-body" },
    });
    if (__VLS_ctx.error) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "error-message" },
        });
        (__VLS_ctx.error);
    }
    if (__VLS_ctx.isDuplicate) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "warning-message" },
        });
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "form-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
        for: "entity-name",
    });
    if (__VLS_ctx.isDuplicate) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            ...{ class: "duplicate-badge" },
        });
    }
    if (__VLS_ctx.checking) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            ...{ class: "checking-badge" },
        });
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        ...{ onInput: (__VLS_ctx.handleNameInput) },
        id: "entity-name",
        value: (__VLS_ctx.entityName),
        type: "text",
        placeholder: "Например: ООО Компания или Иван Петров",
        ...{ class: "input-field" },
        disabled: (__VLS_ctx.loading),
        ...{ class: ({ 'input-error': __VLS_ctx.isDuplicate }) },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "form-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
        for: "entity-type",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
        ...{ onChange: (__VLS_ctx.handleTypeChange) },
        id: "entity-type",
        value: (__VLS_ctx.entityType),
        ...{ class: "input-field" },
        disabled: (__VLS_ctx.loading),
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "ORG",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "PER",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "info-text" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.footer, __VLS_intrinsicElements.footer)({
        ...{ class: "modal-footer" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.handleClose) },
        ...{ class: "btn-secondary" },
        disabled: (__VLS_ctx.loading),
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.handleAddEntity) },
        ...{ class: "btn-primary" },
        disabled: (__VLS_ctx.loading || !__VLS_ctx.entityName.trim() || __VLS_ctx.isDuplicate || __VLS_ctx.checking),
    });
    (__VLS_ctx.isDuplicate ? '❌ Уже существует' : __VLS_ctx.loading ? 'Добавляем...' : 'Добавить');
}
/** @type {__VLS_StyleScopedClasses['modal-overlay']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-content']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-header']} */ ;
/** @type {__VLS_StyleScopedClasses['close-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-body']} */ ;
/** @type {__VLS_StyleScopedClasses['error-message']} */ ;
/** @type {__VLS_StyleScopedClasses['warning-message']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['duplicate-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['checking-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['info-text']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-footer']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-primary']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            entityName: entityName,
            entityType: entityType,
            loading: loading,
            checking: checking,
            error: error,
            isDuplicate: isDuplicate,
            handleNameInput: handleNameInput,
            handleTypeChange: handleTypeChange,
            handleAddEntity: handleAddEntity,
            handleClose: handleClose,
        };
    },
    __typeEmits: {},
    __typeProps: {},
    props: {},
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
    __typeEmits: {},
    __typeProps: {},
    props: {},
});
; /* PartiallyEnd: #4569/main.vue */
