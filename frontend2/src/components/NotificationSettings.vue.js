import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../api/client';
const router = useRouter();
const statusEnabled = ref(true);
const loading = ref(true);
const error = ref(null);
// Реальные данные
const triggers = ref([]);
const sources = ref([]);
const channels = ref([]);
const selectedTriggers = ref(new Set());
const selectedSources = ref(new Set());
const selectedChannels = ref(new Set());
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
    }
    catch (e) {
        error.value = e.message || 'Ошибка загрузки настроек уведомлений';
        console.error('❌ Error:', error.value);
    }
    finally {
        loading.value = false;
    }
});
const toggleSetValue = (target, value) => {
    const next = new Set(target.value);
    if (next.has(value)) {
        next.delete(value);
    }
    else {
        next.add(value);
    }
    target.value = next;
};
const handleTriggerToggle = (value) => {
    toggleSetValue(selectedTriggers, value);
};
const handleSourceToggle = (value) => {
    toggleSetValue(selectedSources, value);
};
const handleChannelToggle = (value) => {
    toggleSetValue(selectedChannels, value);
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
            });
        }
        // Обновляем источники
        for (const source of sources.value) {
            await api.updateNotificationSource(source.id, {
                enabled: selectedSources.value.has(source.id),
            });
        }
        // Обновляем каналы
        for (const channel of channels.value) {
            await api.updateNotificationChannel(channel.id, {
                enabled: selectedChannels.value.has(channel.id),
            });
        }
        console.log('✅ Settings saved successfully');
        error.value = null;
        alert('Настройки успешно сохранены!');
    }
    catch (e) {
        error.value = e.message || 'Ошибка сохранения настроек';
        console.error('❌ Error saving settings:', error.value);
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
/** @type {__VLS_StyleScopedClasses['checklist']} */ ;
/** @type {__VLS_StyleScopedClasses['checklist']} */ ;
/** @type {__VLS_StyleScopedClasses['checklist']} */ ;
/** @type {__VLS_StyleScopedClasses['checklist']} */ ;
/** @type {__VLS_StyleScopedClasses['pill-list']} */ ;
/** @type {__VLS_StyleScopedClasses['pill-list']} */ ;
/** @type {__VLS_StyleScopedClasses['channel-list']} */ ;
/** @type {__VLS_StyleScopedClasses['channel-list']} */ ;
/** @type {__VLS_StyleScopedClasses['summary']} */ ;
/** @type {__VLS_StyleScopedClasses['summary']} */ ;
/** @type {__VLS_StyleScopedClasses['summary']} */ ;
/** @type {__VLS_StyleScopedClasses['summary']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['hero']} */ ;
/** @type {__VLS_StyleScopedClasses['settings-grid']} */ ;
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
    'aria-label': "search",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
    viewBox: "0 0 24 24",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
    d: "M11 4a7 7 0 0 1 5.6 11.2l3.6 3.6-1.4 1.4-3.6-3.6A7 7 0 1 1 11 4Z",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ class: "icon-btn" },
    'aria-label': "notifications",
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
    'aria-label': "profile",
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
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                if (!!(__VLS_ctx.loading))
                    return;
                if (!(__VLS_ctx.error))
                    return;
                __VLS_ctx.location.reload();
            } },
        ...{ class: "outline" },
    });
}
else {
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
    __VLS_asFunctionalElement(__VLS_intrinsicElements.ul, __VLS_intrinsicElements.ul)({
        ...{ class: "checklist" },
    });
    for (const [trigger] of __VLS_getVForSourceType((__VLS_ctx.triggers))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({
            key: (trigger.id),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
            ...{ onChange: (...[$event]) => {
                    if (!!(__VLS_ctx.loading))
                        return;
                    if (!!(__VLS_ctx.error))
                        return;
                    __VLS_ctx.handleTriggerToggle(trigger.id);
                } },
            type: "checkbox",
            checked: (__VLS_ctx.selectedTriggers.has(trigger.id)),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (trigger.label);
        if (trigger.description) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
            (trigger.description);
        }
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
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "pill-list" },
    });
    for (const [source] of __VLS_getVForSourceType((__VLS_ctx.sources))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
            ...{ onClick: (...[$event]) => {
                    if (!!(__VLS_ctx.loading))
                        return;
                    if (!!(__VLS_ctx.error))
                        return;
                    __VLS_ctx.handleSourceToggle(source.id);
                } },
            key: (source.id),
            type: "button",
            ...{ class: ({ selected: __VLS_ctx.selectedSources.has(source.id) }) },
        });
        (source.label);
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
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "channel-list" },
    });
    for (const [channel] of __VLS_getVForSourceType((__VLS_ctx.channels))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
            key: (channel.id),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
            ...{ onChange: (...[$event]) => {
                    if (!!(__VLS_ctx.loading))
                        return;
                    if (!!(__VLS_ctx.error))
                        return;
                    __VLS_ctx.handleChannelToggle(channel.id);
                } },
            type: "checkbox",
            checked: (__VLS_ctx.selectedChannels.has(channel.id)),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        (channel.label);
    }
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "summary card" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.ul, __VLS_intrinsicElements.ul)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (__VLS_ctx.handleSaveSettings) },
    ...{ class: "primary" },
    disabled: (__VLS_ctx.loading),
});
(__VLS_ctx.loading ? 'Сохраняем...' : 'Сохранить настройки');
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
/** @type {__VLS_StyleScopedClasses['outline']} */ ;
/** @type {__VLS_StyleScopedClasses['settings-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['overline']} */ ;
/** @type {__VLS_StyleScopedClasses['checklist']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['overline']} */ ;
/** @type {__VLS_StyleScopedClasses['pill-list']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['overline']} */ ;
/** @type {__VLS_StyleScopedClasses['channel-list']} */ ;
/** @type {__VLS_StyleScopedClasses['summary']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            router: router,
            statusEnabled: statusEnabled,
            loading: loading,
            error: error,
            triggers: triggers,
            sources: sources,
            channels: channels,
            selectedTriggers: selectedTriggers,
            selectedSources: selectedSources,
            selectedChannels: selectedChannels,
            handleTriggerToggle: handleTriggerToggle,
            handleSourceToggle: handleSourceToggle,
            handleChannelToggle: handleChannelToggle,
            handleSaveSettings: handleSaveSettings,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
