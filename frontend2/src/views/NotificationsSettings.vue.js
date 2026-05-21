import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { api as apiClient } from '../api/client';
import AddEntityModal from '../components/AddEntityModal.vue';
const router = useRouter();
const statusEnabled = ref(true);
const loading = ref(true);
const error = ref(null);
const saveSuccess = ref(false);
const isAuthenticated = ref(false);
// Модальное окно для добавления сущности
const showAddEntityModal = ref(false);
const addEntityType = ref('ORG');
// Данные
const allOrganizations = ref([]);
const allPersons = ref([]);
const selectedOrganizations = ref(new Set());
const selectedPersons = ref(new Set());
// Поиск
const orgSearchQuery = ref('');
const personSearchQuery = ref('');
// Настройки уведомлений
const email = ref('');
const digestFrequency = ref('instant'); // instant, daily, weekly
// IDs триггеров и каналов для обновления
const orgTriggersMap = ref(new Map());
const personTriggersMap = ref(new Map());
let emailChannelId = null;
let notificationSettingsId = null;
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
        // Загружаем конфиг, организации и персон параллельно (только первые 30 для быстрой загрузки)
        let [config, orgs, persons_list] = await Promise.all([
            apiClient.getNotificationConfig(),
            apiClient.getOrganizations(30), // Уменьили с 100 на 30
            apiClient.getPersons(30), // Уменьили с 100 на 30
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
        }
        else {
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
                });
                config.channels = [newChannel];
                emailChannelId = newChannel.id;
            }
            catch (e) {
                console.error('❌ Failed to create email channel:', e);
            }
        }
        else if (config.channels.length > 0 && config.channels[0].channel_type === 'email') {
            emailChannelId = config.channels[0].id;
        }
        // Загружаем настройки
        const settings = config.settings;
        statusEnabled.value = settings.enabled;
        digestFrequency.value = settings.digest_frequency || 'instant';
        // Восстанавливаем сохраненные триггеры
        const enabledOrgIds = new Set();
        const enabledPersonIds = new Set();
        config.triggers.forEach(trigger => {
            if (trigger.enabled) {
                if (trigger.trigger_type === 'organization') {
                    const orgId = parseInt(trigger.trigger_value);
                    enabledOrgIds.add(orgId);
                    orgTriggersMap.value.set(orgId, trigger.id);
                }
                else if (trigger.trigger_type === 'person') {
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
    }
    catch (e) {
        error.value = e.message || 'Ошибка загрузки';
        console.error('❌ Error:', e);
    }
    finally {
        loading.value = false;
    }
});
const toggleOrganization = (id) => {
    const next = new Set(selectedOrganizations.value);
    if (next.has(id)) {
        next.delete(id);
    }
    else {
        next.add(id);
    }
    selectedOrganizations.value = next;
};
const togglePerson = (id) => {
    const next = new Set(selectedPersons.value);
    if (next.has(id)) {
        next.delete(id);
    }
    else {
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
            });
            console.log('✅ Email channel updated');
        }
        else {
            // Создаем новый канал, если его нет
            const newChannel = await apiClient.createNotificationChannel({
                channel_type: 'email',
                channel_address: email.value,
                enabled: true,
            });
            emailChannelId = newChannel.id;
            console.log('✅ Email channel created');
        }
        // 3. Синхронизируем триггеры для организаций
        // Получаем все текущие триггеры
        const config = await apiClient.getNotificationConfig();
        const currentOrgTriggers = new Map();
        const currentPersonTriggers = new Map();
        config.triggers.forEach(trigger => {
            if (trigger.trigger_type === 'organization') {
                const orgId = parseInt(trigger.trigger_value);
                currentOrgTriggers.set(orgId, trigger.id);
            }
            else if (trigger.trigger_type === 'person') {
                const personId = parseInt(trigger.trigger_value);
                currentPersonTriggers.set(personId, trigger.id);
            }
        });
        // Обновляем или создаем триггеры для организаций
        for (const orgId of selectedOrganizations.value) {
            if (currentOrgTriggers.has(orgId)) {
                // Обновляем существующий триггер
                const triggerId = currentOrgTriggers.get(orgId);
                await apiClient.updateNotificationTrigger(triggerId, {
                    enabled: true,
                });
                console.log(`✅ Org trigger ${orgId} updated`);
            }
            else {
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
                });
                console.log(`✅ Org trigger ${orgId} disabled`);
            }
        }
        // Обновляем или создаем триггеры для персон
        for (const personId of selectedPersons.value) {
            if (currentPersonTriggers.has(personId)) {
                // Обновляем существующий триггер
                const triggerId = currentPersonTriggers.get(personId);
                await apiClient.updateNotificationTrigger(triggerId, {
                    enabled: true,
                });
                console.log(`✅ Person trigger ${personId} updated`);
            }
            else {
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
                });
                console.log(`✅ Person trigger ${personId} disabled`);
            }
        }
        saveSuccess.value = true;
        console.log('✅ All settings saved successfully');
        setTimeout(() => {
            saveSuccess.value = false;
        }, 3000);
    }
    catch (e) {
        error.value = e.message || 'Ошибка сохранения';
        console.error('❌ Error saving:', e);
    }
    finally {
        loading.value = false;
    }
};
const handleOpenAddEntityModal = (type) => {
    addEntityType.value = type;
    showAddEntityModal.value = true;
};
const handleEntityAdded = async (newEntity) => {
    console.log('✅ New entity added:', newEntity);
    // Добавляем новую сущность в соответствующий список
    const entity = {
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
    }
    else if (newEntity.entity_type === 'PER') {
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
    }
    catch (e) {
        error.value = e.message || 'Ошибка отправки тестового письма';
        console.error('❌ Error sending test email:', e);
    }
    finally {
        loading.value = false;
    }
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['icon-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['icon-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['status-toggle']} */ ;
/** @type {__VLS_StyleScopedClasses['status-toggle']} */ ;
/** @type {__VLS_StyleScopedClasses['pill']} */ ;
/** @type {__VLS_StyleScopedClasses['error-state']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['email-input']} */ ;
/** @type {__VLS_StyleScopedClasses['select-input']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-checkbox']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-checkbox']} */ ;
/** @type {__VLS_StyleScopedClasses['search-input']} */ ;
/** @type {__VLS_StyleScopedClasses['search-input']} */ ;
/** @type {__VLS_StyleScopedClasses['summary']} */ ;
/** @type {__VLS_StyleScopedClasses['summary']} */ ;
/** @type {__VLS_StyleScopedClasses['summary']} */ ;
/** @type {__VLS_StyleScopedClasses['summary']} */ ;
/** @type {__VLS_StyleScopedClasses['add-entity-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['add-entity-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['add-entity-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['hero']} */ ;
/** @type {__VLS_StyleScopedClasses['settings-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['button-group']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['secondary']} */ ;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "notify-page" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)({
    ...{ class: "page-header" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.router.push('/');
        } },
    ...{ class: "logo" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span)({
    ...{ class: "dot" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "header-actions" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.router.push('/search');
        } },
    ...{ class: "icon-btn" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
    viewBox: "0 0 24 24",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
    d: "M11 4a7 7 0 0 1 5.6 11.2l3.6 3.6-1.4 1.4-3.6-3.6A7 7 0 1 1 11 4Z",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ class: "icon-btn" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
    viewBox: "0 0 24 24",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
    d: "M12 2a6 6 0 0 0-6 6v3.4l-.9 2.2a1 1 0 0 0 1 1.4h11.8a1 1 0 0 0 1-.6 1 1 0 0 0 0-.8L18 11.4V8a6 6 0 0 0-6-6Z",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
    d: "M9 18a3 3 0 0 0 6 0",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ class: "icon-btn profile" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "hero" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
    ...{ class: "overline" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
    ...{ class: "subtitle" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
    ...{ class: "status-toggle" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.statusEnabled = !__VLS_ctx.statusEnabled;
        } },
    type: "button",
    ...{ class: ({ active: __VLS_ctx.statusEnabled }) },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span)({
    ...{ class: "pill" },
    ...{ class: ({ on: __VLS_ctx.statusEnabled }) },
});
(__VLS_ctx.statusEnabled ? 'Включено' : 'Выключено');
if (__VLS_ctx.loading) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "loading-state" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "spinner" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
}
else if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "error-state" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "error-title" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "error-message" },
    });
    (__VLS_ctx.error);
}
if (__VLS_ctx.saveSuccess) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "success-banner" },
    });
}
if (!__VLS_ctx.loading && !__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "settings-grid" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
        ...{ class: "card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "overline" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "form-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        type: "email",
        placeholder: "your.email@example.com",
        ...{ class: "email-input" },
    });
    (__VLS_ctx.email);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "form-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
        value: (__VLS_ctx.digestFrequency),
        ...{ class: "select-input" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "instant",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "daily",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "weekly",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
        ...{ class: "card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "overline" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    (__VLS_ctx.selectedOrgsCount);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                if (!(!__VLS_ctx.loading && !__VLS_ctx.error))
                    return;
                __VLS_ctx.handleOpenAddEntityModal('ORG');
            } },
        ...{ class: "add-entity-btn" },
        title: "Добавить новую организацию",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "search-box" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        value: (__VLS_ctx.orgSearchQuery),
        type: "text",
        placeholder: "🔍 Поиск организации...",
        ...{ class: "search-input" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "entities-list" },
    });
    if (__VLS_ctx.filteredOrganizations.length === 0) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "empty-state" },
        });
        (__VLS_ctx.orgSearchQuery ? 'Организации не найдены' : 'Организации не загружены');
    }
    for (const [org] of __VLS_getVForSourceType((__VLS_ctx.filteredOrganizations))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
            key: (org.id),
            ...{ class: "entity-checkbox" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
            ...{ onChange: (...[$event]) => {
                    if (!(!__VLS_ctx.loading && !__VLS_ctx.error))
                        return;
                    __VLS_ctx.toggleOrganization(org.id);
                } },
            type: "checkbox",
            checked: (__VLS_ctx.selectedOrganizations.has(org.id)),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            ...{ class: "entity-name" },
        });
        (org.name);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
        ...{ class: "card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "overline" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    (__VLS_ctx.selectedPersonsCount);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                if (!(!__VLS_ctx.loading && !__VLS_ctx.error))
                    return;
                __VLS_ctx.handleOpenAddEntityModal('PER');
            } },
        ...{ class: "add-entity-btn" },
        title: "Добавить новую персону",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "search-box" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        value: (__VLS_ctx.personSearchQuery),
        type: "text",
        placeholder: "🔍 Поиск персоны...",
        ...{ class: "search-input" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "entities-list" },
    });
    if (__VLS_ctx.filteredPersons.length === 0) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "empty-state" },
        });
        (__VLS_ctx.personSearchQuery ? 'Персоны не найдены' : 'Персоны не загружены');
    }
    for (const [person] of __VLS_getVForSourceType((__VLS_ctx.filteredPersons))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
            key: (person.id),
            ...{ class: "entity-checkbox" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
            ...{ onChange: (...[$event]) => {
                    if (!(!__VLS_ctx.loading && !__VLS_ctx.error))
                        return;
                    __VLS_ctx.togglePerson(person.id);
                } },
            type: "checkbox",
            checked: (__VLS_ctx.selectedPersons.has(person.id)),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            ...{ class: "entity-name" },
        });
        (person.name);
    }
}
if (!__VLS_ctx.loading && !__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "summary card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.ul, __VLS_intrinsicElements.ul)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({});
    (__VLS_ctx.selectedOrgsCount);
    (__VLS_ctx.selectedPersonsCount);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({});
    (__VLS_ctx.email);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({});
    (__VLS_ctx.digestFrequency === 'instant' ? 'Сразу же' : __VLS_ctx.digestFrequency === 'daily' ? 'Ежедневно' : 'Еженедельно');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "button-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.handleSaveSettings) },
        ...{ class: "primary" },
        disabled: (__VLS_ctx.loading),
    });
    (__VLS_ctx.loading ? 'Сохраняем...' : 'Сохранить настройки');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.handleSendTestEmail) },
        ...{ class: "secondary" },
        disabled: (__VLS_ctx.loading || !__VLS_ctx.email),
        title: "Отправить тестовое письмо на указанный email",
    });
}
/** @type {[typeof AddEntityModal, ]} */ ;
// @ts-ignore
const __VLS_0 = __VLS_asFunctionalComponent(AddEntityModal, new AddEntityModal({
    ...{ 'onClose': {} },
    ...{ 'onEntityAdded': {} },
    isOpen: (__VLS_ctx.showAddEntityModal),
}));
const __VLS_1 = __VLS_0({
    ...{ 'onClose': {} },
    ...{ 'onEntityAdded': {} },
    isOpen: (__VLS_ctx.showAddEntityModal),
}, ...__VLS_functionalComponentArgsRest(__VLS_0));
let __VLS_3;
let __VLS_4;
let __VLS_5;
const __VLS_6 = {
    onClose: (...[$event]) => {
        __VLS_ctx.showAddEntityModal = false;
    }
};
const __VLS_7 = {
    onEntityAdded: (__VLS_ctx.handleEntityAdded)
};
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['notify-page']} */ ;
/** @type {__VLS_StyleScopedClasses['page-header']} */ ;
/** @type {__VLS_StyleScopedClasses['logo']} */ ;
/** @type {__VLS_StyleScopedClasses['dot']} */ ;
/** @type {__VLS_StyleScopedClasses['header-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['icon-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['icon-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['icon-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['profile']} */ ;
/** @type {__VLS_StyleScopedClasses['hero']} */ ;
/** @type {__VLS_StyleScopedClasses['overline']} */ ;
/** @type {__VLS_StyleScopedClasses['subtitle']} */ ;
/** @type {__VLS_StyleScopedClasses['status-toggle']} */ ;
/** @type {__VLS_StyleScopedClasses['pill']} */ ;
/** @type {__VLS_StyleScopedClasses['loading-state']} */ ;
/** @type {__VLS_StyleScopedClasses['spinner']} */ ;
/** @type {__VLS_StyleScopedClasses['error-state']} */ ;
/** @type {__VLS_StyleScopedClasses['error-title']} */ ;
/** @type {__VLS_StyleScopedClasses['error-message']} */ ;
/** @type {__VLS_StyleScopedClasses['success-banner']} */ ;
/** @type {__VLS_StyleScopedClasses['settings-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['overline']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['email-input']} */ ;
/** @type {__VLS_StyleScopedClasses['form-group']} */ ;
/** @type {__VLS_StyleScopedClasses['select-input']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['overline']} */ ;
/** @type {__VLS_StyleScopedClasses['add-entity-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['search-box']} */ ;
/** @type {__VLS_StyleScopedClasses['search-input']} */ ;
/** @type {__VLS_StyleScopedClasses['entities-list']} */ ;
/** @type {__VLS_StyleScopedClasses['empty-state']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-checkbox']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-name']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['overline']} */ ;
/** @type {__VLS_StyleScopedClasses['add-entity-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['search-box']} */ ;
/** @type {__VLS_StyleScopedClasses['search-input']} */ ;
/** @type {__VLS_StyleScopedClasses['entities-list']} */ ;
/** @type {__VLS_StyleScopedClasses['empty-state']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-checkbox']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-name']} */ ;
/** @type {__VLS_StyleScopedClasses['summary']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['button-group']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['secondary']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            AddEntityModal: AddEntityModal,
            router: router,
            statusEnabled: statusEnabled,
            loading: loading,
            error: error,
            saveSuccess: saveSuccess,
            showAddEntityModal: showAddEntityModal,
            selectedOrganizations: selectedOrganizations,
            selectedPersons: selectedPersons,
            orgSearchQuery: orgSearchQuery,
            personSearchQuery: personSearchQuery,
            email: email,
            digestFrequency: digestFrequency,
            filteredOrganizations: filteredOrganizations,
            filteredPersons: filteredPersons,
            toggleOrganization: toggleOrganization,
            togglePerson: togglePerson,
            handleSaveSettings: handleSaveSettings,
            handleOpenAddEntityModal: handleOpenAddEntityModal,
            handleEntityAdded: handleEntityAdded,
            selectedOrgsCount: selectedOrgsCount,
            selectedPersonsCount: selectedPersonsCount,
            handleSendTestEmail: handleSendTestEmail,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
