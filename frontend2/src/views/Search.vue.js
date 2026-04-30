import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../api/client';
const router = useRouter();
// ==================== ОПЦИИ ФИЛЬТРОВ ====================
const sourceOptions = [
    { id: 'media', label: 'СМИ' },
    { id: 'telegram', label: 'Telegram' },
    { id: 'registry', label: 'Реестры' },
];
const riskLevelOptions = [
    { id: 'high', label: 'Высокий' },
    { id: 'medium', label: 'Средний' },
    { id: 'low', label: 'Низкий' },
];
const riskTypeOptions = [
    { id: 'политический', label: 'Политический' },
    { id: 'экономический', label: 'Экономический' },
    { id: 'социальный', label: 'Социальный' },
];
const infoChecklist = [
    'Вводите ключевые слова, названия компаний или персон',
    'Комбинируйте фильтры по источникам, темам и рискам',
    'Просматривайте карточки найденных событий',
    'Переходите в полную карточку для деталей и отчётов',
];
// ==================== СОСТОЯНИЕ ====================
const query = ref('');
const loading = ref(false);
const showFilters = ref(true);
const allResults = ref([]);
const selectedArticleId = ref(null);
const displayedCount = ref(20);
const PAGE_SIZE = 20;
const selectedSources = ref([]);
const selectedRiskLevels = ref(['high', 'medium', 'low']);
const selectedRiskTypes = ref([]);
let searchTimeout = null;
// ==================== WATCHERS ДЛЯ ФИЛЬТРОВ ====================
// Перегружаем результаты при изменении фильтров
const applyFilters = () => {
    if (searchTimeout)
        clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        fetchResults();
    }, 300);
};
// ==================== ВЫЧИСЛЯЕМЫЕ СВОЙСТВА ====================
const filteredResults = computed(() => {
    let filtered = allResults.value;
    // Фильтр по тексту поиска
    if (query.value.trim()) {
        const searchLower = query.value.toLowerCase();
        filtered = filtered.filter((item) => (item.title?.toLowerCase() || '').includes(searchLower) ||
            (item.text?.toLowerCase() || '').includes(searchLower) ||
            (item.source?.toLowerCase() || '').includes(searchLower));
    }
    // Фильтр по источнику
    if (selectedSources.value.length > 0) {
        filtered = filtered.filter((item) => {
            const sourceType = getSourceType(item.source || '');
            return selectedSources.value.includes(sourceType);
        });
    }
    // Фильтр по уровню риска
    if (selectedRiskLevels.value.length > 0) {
        filtered = filtered.filter((item) => selectedRiskLevels.value.includes(item.risk_level || 'low'));
    }
    // Фильтр по типу риска
    if (selectedRiskTypes.value.length > 0) {
        filtered = filtered.filter((item) => selectedRiskTypes.value.includes(item.risk_type || ''));
    }
    return filtered;
});
const displayedResults = computed(() => {
    return filteredResults.value.slice(0, displayedCount.value);
});
const canLoadMore = computed(() => {
    return displayedCount.value < filteredResults.value.length;
});
// ==================== ФУНКЦИИ ====================
const getSourceType = (source) => {
    if (source.toLowerCase().includes('telegram'))
        return 'telegram';
    if (source.toLowerCase().includes('реестр') || source.toLowerCase().includes('registry'))
        return 'registry';
    return 'media';
};
const handleSearchInput = (e) => {
    const target = e.target;
    query.value = target.value;
    if (searchTimeout)
        clearTimeout(searchTimeout);
    loading.value = true;
    searchTimeout = setTimeout(() => {
        if (query.value.trim()) {
            fetchResults();
        }
        else {
            fetchAllNews();
        }
    }, 500);
};
const fetchAllNews = async () => {
    try {
        const data = await api.getNews({ page: 1, page_size: 500 });
        allResults.value = data.items;
        displayedCount.value = 20;
        selectedArticleId.value = null;
    }
    catch (error) {
        console.error('Ошибка при загрузке новостей:', error);
        allResults.value = [];
    }
    finally {
        loading.value = false;
    }
};
const fetchResults = async () => {
    try {
        // Собираем параметры фильтрации
        const riskLevelParam = selectedRiskLevels.value.length > 0 && selectedRiskLevels.value.length < 3
            ? selectedRiskLevels.value[0] // Если выбран один уровень, передаем его
            : undefined;
        const riskTypeParam = selectedRiskTypes.value.length > 0
            ? selectedRiskTypes.value[0] // Если выбран один тип, передаем его
            : undefined;
        const data = await api.getNews({
            search: query.value || undefined,
            page: 1,
            page_size: 500,
            risk_level: riskLevelParam,
            risk_type: riskTypeParam,
        });
        allResults.value = data.items;
        displayedCount.value = 20;
        selectedArticleId.value = null;
    }
    catch (error) {
        console.error('Ошибка при поиске:', error);
        allResults.value = [];
    }
    finally {
        loading.value = false;
    }
};
const loadMore = () => {
    displayedCount.value += PAGE_SIZE;
};
const selectArticle = (item) => {
    selectedArticleId.value = item.id;
    router.push(`/news/${item.id}`);
};
const toggleFilters = () => {
    showFilters.value = !showFilters.value;
};
const formatDate = (dateStr) => {
    if (!dateStr)
        return 'Unknown';
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    });
};
const riskLevelLabel = (level) => {
    const map = {
        high: 'Высокий риск',
        medium: 'Средний риск',
        low: 'Низкий риск',
    };
    return map[level || 'low'] || 'Неизвестно';
};
const riskTypeLabel = (type) => {
    const map = {
        политический: 'Политический',
        экономический: 'Экономический',
        социальный: 'Социальный',
    };
    return map[type || ''] || type || 'Неизвестно';
};
// ==================== ИНИЦИАЛИЗАЦИЯ ====================
onMounted(() => {
    fetchAllNews();
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['search-input']} */ ;
/** @type {__VLS_StyleScopedClasses['search-input']} */ ;
/** @type {__VLS_StyleScopedClasses['search-input']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-group']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-group']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-group']} */ ;
/** @type {__VLS_StyleScopedClasses['info-block']} */ ;
/** @type {__VLS_StyleScopedClasses['info-block']} */ ;
/** @type {__VLS_StyleScopedClasses['info-block']} */ ;
/** @type {__VLS_StyleScopedClasses['results']} */ ;
/** @type {__VLS_StyleScopedClasses['result-card']} */ ;
/** @type {__VLS_StyleScopedClasses['result-card']} */ ;
/** @type {__VLS_StyleScopedClasses['result-card']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-high']} */ ;
/** @type {__VLS_StyleScopedClasses['dot']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['dot']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-low']} */ ;
/** @type {__VLS_StyleScopedClasses['dot']} */ ;
/** @type {__VLS_StyleScopedClasses['action-footer']} */ ;
/** @type {__VLS_StyleScopedClasses['action-footer']} */ ;
/** @type {__VLS_StyleScopedClasses['search-page']} */ ;
/** @type {__VLS_StyleScopedClasses['results']} */ ;
/** @type {__VLS_StyleScopedClasses['search-input']} */ ;
/** @type {__VLS_StyleScopedClasses['search-input']} */ ;
/** @type {__VLS_StyleScopedClasses['action-footer']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['filters']} */ ;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "search-page" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "search-panel" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
    ...{ class: "search-input" },
    'aria-label': "Поисковый запрос",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    ...{ onInput: (__VLS_ctx.handleSearchInput) },
    value: (__VLS_ctx.query),
    type: "text",
    placeholder: "Например: санкции, дизельный рынок, Газпром",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (__VLS_ctx.fetchResults) },
    type: "button",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (__VLS_ctx.toggleFilters) },
    ...{ class: "filter-toggle" },
    type: "button",
});
(__VLS_ctx.showFilters ? 'Скрыть фильтры' : 'Показать фильтры');
if (__VLS_ctx.showFilters) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "filters" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "filter-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    for (const [option] of __VLS_getVForSourceType((__VLS_ctx.sourceOptions))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
            key: (option.id),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
            ...{ onChange: (__VLS_ctx.applyFilters) },
            type: "checkbox",
            value: (option.id),
        });
        (__VLS_ctx.selectedSources);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        (option.label);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "filter-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    for (const [option] of __VLS_getVForSourceType((__VLS_ctx.riskLevelOptions))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
            key: (option.id),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
            ...{ onChange: (__VLS_ctx.applyFilters) },
            type: "checkbox",
            value: (option.id),
        });
        (__VLS_ctx.selectedRiskLevels);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        (option.label);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "filter-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    for (const [option] of __VLS_getVForSourceType((__VLS_ctx.riskTypeOptions))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
            key: (option.id),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
            ...{ onChange: (__VLS_ctx.applyFilters) },
            type: "checkbox",
            value: (option.id),
        });
        (__VLS_ctx.selectedRiskTypes);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        (option.label);
    }
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "info-block" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.ul, __VLS_intrinsicElements.ul)({});
for (const [item] of __VLS_getVForSourceType((__VLS_ctx.infoChecklist))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({
        key: (item),
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span)({
        ...{ class: "bullet" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (item);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "results" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
    ...{ class: "overline" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "count" },
});
(__VLS_ctx.filteredResults.length);
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "card-list" },
});
if (__VLS_ctx.loading) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "placeholder" },
    });
}
if (!__VLS_ctx.loading && __VLS_ctx.query.trim() && __VLS_ctx.filteredResults.length === 0) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "placeholder" },
    });
}
if (!__VLS_ctx.loading && !__VLS_ctx.query.trim() && __VLS_ctx.filteredResults.length === 0) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "placeholder" },
    });
}
for (const [item] of __VLS_getVForSourceType((__VLS_ctx.displayedResults))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
        ...{ onClick: (...[$event]) => {
                __VLS_ctx.selectArticle(item);
            } },
        key: (item.id),
        ...{ class: "result-card" },
        tabindex: "0",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "card-top" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h4, __VLS_intrinsicElements.h4)({});
    (item.title || 'Без заголовка');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "date" },
    });
    (__VLS_ctx.formatDate(item.pub_date));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "source" },
    });
    (item.source || 'Unknown');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "summary" },
    });
    ((item.text || '').slice(0, 200));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ style: {} },
    });
    if (item.risk_level) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            ...{ class: "risk-badge" },
            ...{ class: (`risk-${item.risk_level}`) },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span)({
            ...{ class: "dot" },
        });
        (__VLS_ctx.riskLevelLabel(item.risk_level));
    }
    if (item.risk_type) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            ...{ class: "type-badge" },
        });
        (__VLS_ctx.riskTypeLabel(item.risk_type));
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                __VLS_ctx.selectArticle(item);
            } },
        ...{ class: "inline-link" },
    });
}
if (__VLS_ctx.canLoadMore) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ style: {} },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.loadMore) },
        ...{ class: "inline-link" },
    });
    (__VLS_ctx.displayedCount);
    (__VLS_ctx.filteredResults.length);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "action-footer" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h4, __VLS_intrinsicElements.h4)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.router.push('/reports');
        } },
    ...{ class: "primary" },
});
/** @type {__VLS_StyleScopedClasses['search-page']} */ ;
/** @type {__VLS_StyleScopedClasses['search-panel']} */ ;
/** @type {__VLS_StyleScopedClasses['search-input']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-toggle']} */ ;
/** @type {__VLS_StyleScopedClasses['filters']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-group']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-group']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-group']} */ ;
/** @type {__VLS_StyleScopedClasses['info-block']} */ ;
/** @type {__VLS_StyleScopedClasses['bullet']} */ ;
/** @type {__VLS_StyleScopedClasses['results']} */ ;
/** @type {__VLS_StyleScopedClasses['overline']} */ ;
/** @type {__VLS_StyleScopedClasses['count']} */ ;
/** @type {__VLS_StyleScopedClasses['card-list']} */ ;
/** @type {__VLS_StyleScopedClasses['placeholder']} */ ;
/** @type {__VLS_StyleScopedClasses['placeholder']} */ ;
/** @type {__VLS_StyleScopedClasses['placeholder']} */ ;
/** @type {__VLS_StyleScopedClasses['result-card']} */ ;
/** @type {__VLS_StyleScopedClasses['card-top']} */ ;
/** @type {__VLS_StyleScopedClasses['date']} */ ;
/** @type {__VLS_StyleScopedClasses['source']} */ ;
/** @type {__VLS_StyleScopedClasses['summary']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['dot']} */ ;
/** @type {__VLS_StyleScopedClasses['type-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-link']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-link']} */ ;
/** @type {__VLS_StyleScopedClasses['action-footer']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            router: router,
            sourceOptions: sourceOptions,
            riskLevelOptions: riskLevelOptions,
            riskTypeOptions: riskTypeOptions,
            infoChecklist: infoChecklist,
            query: query,
            loading: loading,
            showFilters: showFilters,
            displayedCount: displayedCount,
            selectedSources: selectedSources,
            selectedRiskLevels: selectedRiskLevels,
            selectedRiskTypes: selectedRiskTypes,
            applyFilters: applyFilters,
            filteredResults: filteredResults,
            displayedResults: displayedResults,
            canLoadMore: canLoadMore,
            handleSearchInput: handleSearchInput,
            fetchResults: fetchResults,
            loadMore: loadMore,
            selectArticle: selectArticle,
            toggleFilters: toggleFilters,
            formatDate: formatDate,
            riskLevelLabel: riskLevelLabel,
            riskTypeLabel: riskTypeLabel,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
