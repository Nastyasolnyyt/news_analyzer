import { ref, computed, onMounted } from 'vue';
import { api } from '../api/client';
const news = ref([]);
const loading = ref(true);
const error = ref(null);
// Фильтры
const riskFilter = ref('all');
const sentimentFilter = ref('all');
const riskTypeFilter = ref('all');
const selectedNewsIds = ref(new Set());
const selectMode = ref('all');
const riskLevels = {
    high: { label: 'Высокий риск', color: '#ff6464' },
    medium: { label: 'Средний риск', color: '#ffa500' },
    low: { label: 'Низкий риск', color: '#4ade80' },
};
// Отфильтрованные новости
const filteredNews = computed(() => {
    return news.value.filter(item => {
        const riskMatch = riskFilter.value === 'all' || item.risk_level === riskFilter.value;
        const sentimentMatch = sentimentFilter.value === 'all' || item.sentiment_label === sentimentFilter.value;
        const riskTypeMatch = riskTypeFilter.value === 'all' || item.risk_type === riskTypeFilter.value;
        return riskMatch && sentimentMatch && riskTypeMatch;
    });
});
// Новости для отчета (все или выбранные вручную)
const reportNews = computed(() => {
    if (selectMode.value === 'all') {
        return filteredNews.value;
    }
    else {
        return filteredNews.value.filter((item) => selectedNewsIds.value.has(item.id));
    }
});
// Статистика по рискам
const riskStats = computed(() => {
    const stats = { high: 0, medium: 0, low: 0 };
    reportNews.value.forEach(item => {
        const risk = (item.risk_level || 'low');
        if (risk in stats) {
            stats[risk]++;
        }
    });
    return stats;
});
// Статистика по источникам
const sourceStats = computed(() => {
    const sources = new Map();
    reportNews.value.forEach(item => {
        if (item.source) {
            sources.set(item.source, (sources.get(item.source) || 0) + 1);
        }
    });
    return Array.from(sources.entries())
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10);
});
// Статистика по тональности
const sentimentStats = computed(() => {
    const stats = { positive: 0, neutral: 0, negative: 0 };
    reportNews.value.forEach(item => {
        const sentiment = (item.sentiment_label || 'neutral');
        if (sentiment in stats) {
            stats[sentiment]++;
        }
    });
    return stats;
});
// Статистика по типам риска
const riskTypeStats = computed(() => {
    const typeMap = new Map();
    reportNews.value.forEach(item => {
        if (item.risk_type) {
            typeMap.set(item.risk_type, (typeMap.get(item.risk_type) || 0) + 1);
        }
    });
    return Array.from(typeMap.entries())
        .map(([type, count]) => ({ type, count }))
        .sort((a, b) => b.count - a.count);
});
// Средние значения
const averageMetrics = computed(() => ({
    tonality: reportNews.value.length > 0
        ? (reportNews.value.reduce((sum, n) => sum + (n.tonality || 0), 0) / reportNews.value.length).toFixed(2)
        : 0,
    emotion: reportNews.value.length > 0
        ? (reportNews.value.reduce((sum, n) => sum + (n.emotion || 0), 0) / reportNews.value.length).toFixed(2)
        : 0,
    relevance: reportNews.value.length > 0
        ? (reportNews.value.reduce((sum, n) => sum + (n.relevance || 0), 0) / reportNews.value.length).toFixed(2)
        : 0,
}));
onMounted(async () => {
    try {
        loading.value = true;
        console.log('Loading reports data...');
        const data = await api.getNews({
            page: 1,
            page_size: 500, // Увеличили лимит до 500 новостей
        });
        news.value = data.items;
        console.log('Reports loaded:', data.items.length, 'items');
    }
    catch (e) {
        error.value = e.message || 'Ошибка загрузки отчёта';
        console.error('Reports error:', error.value);
    }
    finally {
        loading.value = false;
    }
});
const handleExport = (format) => {
    const reportData = {
        exportDate: new Date().toISOString(),
        totalItems: reportNews.value.length,
        filters: {
            risk: riskFilter.value,
            sentiment: sentimentFilter.value,
        },
        statistics: {
            risks: riskStats.value,
            sentiments: sentimentStats.value,
            riskTypes: riskTypeStats.value,
            sources: sourceStats.value,
            averageMetrics: averageMetrics.value,
        },
        items: reportNews.value,
    };
    if (format === 'json') {
        const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `report-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
    }
    else if (format === 'csv') {
        // CSV export
        let csv = 'Дата,Заголовок,Источник,Уровень риска,Тональность\n';
        reportNews.value.forEach(item => {
            const date = new Date(item.pub_date || item.date || '').toLocaleDateString('ru-RU');
            const title = `"${item.title.replace(/"/g, '""')}"`;
            const source = item.source || '';
            const risk = item.risk_level || 'unknown';
            const sentiment = item.sentiment_label || 'unknown';
            csv += `${date},${title},${source},${risk},${sentiment}\n`;
        });
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `report-${new Date().toISOString().split('T')[0]}.csv`;
        link.click();
        URL.revokeObjectURL(url);
    }
};
const resetFilters = () => {
    riskFilter.value = 'all';
    sentimentFilter.value = 'all';
    riskTypeFilter.value = 'all';
    selectMode.value = 'all';
    selectedNewsIds.value.clear();
};
const toggleNewsSelection = (id) => {
    if (selectedNewsIds.value.has(id)) {
        selectedNewsIds.value.delete(id);
    }
    else {
        selectedNewsIds.value.add(id);
    }
};
const selectAllFiltered = () => {
    reportNews.value.forEach(item => selectedNewsIds.value.add(item.id));
};
const clearSelection = () => {
    selectedNewsIds.value.clear();
};
const reloadPage = () => {
    location.reload();
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['page-header']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['loading-state']} */ ;
/** @type {__VLS_StyleScopedClasses['error-state']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-group']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-select']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-reset']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-info']} */ ;
/** @type {__VLS_StyleScopedClasses['metric']} */ ;
/** @type {__VLS_StyleScopedClasses['detail-card']} */ ;
/** @type {__VLS_StyleScopedClasses['radio-label']} */ ;
/** @type {__VLS_StyleScopedClasses['selection-info']} */ ;
/** @type {__VLS_StyleScopedClasses['news-item']} */ ;
/** @type {__VLS_StyleScopedClasses['news-item']} */ ;
/** @type {__VLS_StyleScopedClasses['news-checkbox']} */ ;
/** @type {__VLS_StyleScopedClasses['news-content']} */ ;
/** @type {__VLS_StyleScopedClasses['news-meta']} */ ;
/** @type {__VLS_StyleScopedClasses['news-meta']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['type-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['sample-news']} */ ;
/** @type {__VLS_StyleScopedClasses['sample-header']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-label']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-high']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-label']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-label']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-low']} */ ;
/** @type {__VLS_StyleScopedClasses['page-header']} */ ;
/** @type {__VLS_StyleScopedClasses['header-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['header-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['filters-section']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-group']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-select']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-info']} */ ;
/** @type {__VLS_StyleScopedClasses['stats-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['logo']} */ ;
/** @type {__VLS_StyleScopedClasses['header-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['icon-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['icon-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['icon-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['hero']} */ ;
/** @type {__VLS_StyleScopedClasses['pill']} */ ;
/** @type {__VLS_StyleScopedClasses['news-card']} */ ;
/** @type {__VLS_StyleScopedClasses['remove']} */ ;
/** @type {__VLS_StyleScopedClasses['actions']} */ ;
/** @type {__VLS_StyleScopedClasses['cta-buttons']} */ ;
/** @type {__VLS_StyleScopedClasses['cta-buttons']} */ ;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "reports-page" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)({
    ...{ class: "page-header" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
    ...{ class: "subtitle" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "header-actions" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.handleExport('json');
        } },
    ...{ class: "btn-secondary" },
    disabled: (__VLS_ctx.loading),
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.handleExport('csv');
        } },
    ...{ class: "btn-secondary" },
    disabled: (__VLS_ctx.loading),
});
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
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    (__VLS_ctx.error);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.reloadPage) },
        ...{ class: "btn-secondary" },
    });
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "report-content" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "filters-section" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "filter-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
        value: (__VLS_ctx.riskFilter),
        ...{ class: "filter-select" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "all",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "high",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "medium",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "low",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "filter-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
        value: (__VLS_ctx.sentimentFilter),
        ...{ class: "filter-select" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "all",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "positive",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "neutral",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "negative",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "filter-group" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
        value: (__VLS_ctx.riskTypeFilter),
        ...{ class: "filter-select" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "all",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "политический",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "экономический",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "социальный",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.resetFilters) },
        ...{ class: "btn-reset" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "filter-info" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.reportNews.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.news.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "selection-section" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "selection-controls" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
        ...{ class: "radio-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        type: "radio",
        value: "all",
    });
    (__VLS_ctx.selectMode);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
        ...{ class: "radio-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        type: "radio",
        value: "manual",
    });
    (__VLS_ctx.selectMode);
    if (__VLS_ctx.selectMode === 'manual') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "manual-controls" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
            ...{ onClick: (__VLS_ctx.selectAllFiltered) },
            ...{ class: "btn-secondary" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
            ...{ onClick: (__VLS_ctx.clearSelection) },
            ...{ class: "btn-secondary" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            ...{ class: "selection-info" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (__VLS_ctx.selectedNewsIds.size);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "stats-grid" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "stat-card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "stat-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "stat-value" },
    });
    (__VLS_ctx.reportNews.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "stat-hint" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "stat-card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "stat-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "risk-bars" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "risk-bar" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-badge high" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "risk-bar-fill-container" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-bar-fill" },
        ...{ style: ({ width: __VLS_ctx.riskStats.high + __VLS_ctx.riskStats.medium + __VLS_ctx.riskStats.low > 0 ? (__VLS_ctx.riskStats.high / (__VLS_ctx.riskStats.high + __VLS_ctx.riskStats.medium + __VLS_ctx.riskStats.low) * 100) + '%' : '0%' }) },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-count" },
    });
    (__VLS_ctx.riskStats.high);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "risk-bar" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-badge medium" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "risk-bar-fill-container" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-bar-fill medium" },
        ...{ style: ({ width: __VLS_ctx.riskStats.high + __VLS_ctx.riskStats.medium + __VLS_ctx.riskStats.low > 0 ? (__VLS_ctx.riskStats.medium / (__VLS_ctx.riskStats.high + __VLS_ctx.riskStats.medium + __VLS_ctx.riskStats.low) * 100) + '%' : '0%' }) },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-count" },
    });
    (__VLS_ctx.riskStats.medium);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "risk-bar" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-badge low" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "risk-bar-fill-container" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-bar-fill low" },
        ...{ style: ({ width: __VLS_ctx.riskStats.high + __VLS_ctx.riskStats.medium + __VLS_ctx.riskStats.low > 0 ? (__VLS_ctx.riskStats.low / (__VLS_ctx.riskStats.high + __VLS_ctx.riskStats.medium + __VLS_ctx.riskStats.low) * 100) + '%' : '0%' }) },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-count" },
    });
    (__VLS_ctx.riskStats.low);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "stat-card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "stat-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sentiment-bars" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sentiment-bar" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-badge positive" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sentiment-bar-fill-container" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-bar-fill" },
        ...{ style: ({ width: __VLS_ctx.sentimentStats.positive + __VLS_ctx.sentimentStats.neutral + __VLS_ctx.sentimentStats.negative > 0 ? (__VLS_ctx.sentimentStats.positive / (__VLS_ctx.sentimentStats.positive + __VLS_ctx.sentimentStats.neutral + __VLS_ctx.sentimentStats.negative) * 100) + '%' : '0%' }) },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-count" },
    });
    (__VLS_ctx.sentimentStats.positive);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sentiment-bar" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-badge neutral" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sentiment-bar-fill-container" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-bar-fill neutral" },
        ...{ style: ({ width: __VLS_ctx.sentimentStats.positive + __VLS_ctx.sentimentStats.neutral + __VLS_ctx.sentimentStats.negative > 0 ? (__VLS_ctx.sentimentStats.neutral / (__VLS_ctx.sentimentStats.positive + __VLS_ctx.sentimentStats.neutral + __VLS_ctx.sentimentStats.negative) * 100) + '%' : '0%' }) },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-count" },
    });
    (__VLS_ctx.sentimentStats.neutral);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sentiment-bar" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-badge negative" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sentiment-bar-fill-container" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-bar-fill negative" },
        ...{ style: ({ width: __VLS_ctx.sentimentStats.positive + __VLS_ctx.sentimentStats.neutral + __VLS_ctx.sentimentStats.negative > 0 ? (__VLS_ctx.sentimentStats.negative / (__VLS_ctx.sentimentStats.positive + __VLS_ctx.sentimentStats.neutral + __VLS_ctx.sentimentStats.negative) * 100) + '%' : '0%' }) },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-count" },
    });
    (__VLS_ctx.sentimentStats.negative);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "stat-card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "stat-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metrics-list" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.averageMetrics.tonality);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.averageMetrics.emotion);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.averageMetrics.relevance);
    if (__VLS_ctx.riskTypeStats.length > 0) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
            ...{ class: "detail-card" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "risk-types-list" },
        });
        for (const [type, idx] of __VLS_getVForSourceType((__VLS_ctx.riskTypeStats))) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                key: (idx),
                ...{ class: "risk-type-item" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: "type-name" },
            });
            (type.type);
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: "type-count" },
            });
            (type.count);
        }
    }
    if (__VLS_ctx.sourceStats.length > 0) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
            ...{ class: "detail-card" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "sources-list" },
        });
        for (const [source, idx] of __VLS_getVForSourceType((__VLS_ctx.sourceStats))) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                key: (idx),
                ...{ class: "source-item" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: "source-name" },
            });
            (source.name);
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: "source-bar" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: "bar-fill" },
                ...{ style: ({ width: __VLS_ctx.sourceStats.length > 0 ? (source.count / __VLS_ctx.sourceStats[0].count * 100) + '%' : '0%' }) },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: "source-count" },
            });
            (source.count);
        }
    }
    if (__VLS_ctx.reportNews.length > 0) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
            ...{ class: "detail-card" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "news-samples" },
        });
        for (const [item, idx] of __VLS_getVForSourceType((__VLS_ctx.reportNews.slice(0, 5)))) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
                key: (idx),
                ...{ class: "sample-news" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                ...{ class: "sample-header" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.h4, __VLS_intrinsicElements.h4)({});
            (item.title);
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: (['risk-label', `risk-${item.risk_level}`]) },
            });
            (__VLS_ctx.riskLevels[item.risk_level || 'low']?.label || 'Неизвестно');
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                ...{ class: "sample-meta" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
            (item.source);
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
            (new Date(item.pub_date || item.date || '').toLocaleDateString('ru-RU'));
        }
    }
    if (__VLS_ctx.selectMode === 'manual') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
            ...{ class: "detail-card" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "news-list-selection" },
        });
        for (const [item] of __VLS_getVForSourceType((__VLS_ctx.filteredNews))) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
                ...{ onClick: (...[$event]) => {
                        if (!!(__VLS_ctx.loading))
                            return;
                        if (!!(__VLS_ctx.error))
                            return;
                        if (!(__VLS_ctx.selectMode === 'manual'))
                            return;
                        __VLS_ctx.toggleNewsSelection(item.id);
                    } },
                key: (item.id),
                ...{ class: (['news-item', { selected: __VLS_ctx.selectedNewsIds.has(item.id) }]) },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                ...{ class: "news-checkbox" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
                type: "checkbox",
                checked: (__VLS_ctx.selectedNewsIds.has(item.id)),
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                ...{ class: "news-content" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.h4, __VLS_intrinsicElements.h4)({});
            (item.title);
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                ...{ class: "news-meta" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: "source" },
            });
            (item.source);
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: "date" },
            });
            (new Date(item.pub_date || item.date || '').toLocaleDateString('ru-RU'));
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: (['risk-badge', `risk-${item.risk_level}`]) },
            });
            (item.risk_level || 'unknown');
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: (['sentiment-badge', `sentiment-${item.sentiment_label}`]) },
            });
            (item.sentiment_label || 'neutral');
            if (item.risk_type) {
                __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                    ...{ class: "type-badge" },
                });
                (item.risk_type);
            }
        }
    }
}
/** @type {__VLS_StyleScopedClasses['reports-page']} */ ;
/** @type {__VLS_StyleScopedClasses['page-header']} */ ;
/** @type {__VLS_StyleScopedClasses['subtitle']} */ ;
/** @type {__VLS_StyleScopedClasses['header-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['loading-state']} */ ;
/** @type {__VLS_StyleScopedClasses['spinner']} */ ;
/** @type {__VLS_StyleScopedClasses['error-state']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['report-content']} */ ;
/** @type {__VLS_StyleScopedClasses['filters-section']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-group']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-select']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-group']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-select']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-group']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-select']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-reset']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-info']} */ ;
/** @type {__VLS_StyleScopedClasses['selection-section']} */ ;
/** @type {__VLS_StyleScopedClasses['selection-controls']} */ ;
/** @type {__VLS_StyleScopedClasses['radio-label']} */ ;
/** @type {__VLS_StyleScopedClasses['radio-label']} */ ;
/** @type {__VLS_StyleScopedClasses['manual-controls']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['selection-info']} */ ;
/** @type {__VLS_StyleScopedClasses['stats-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-card']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-label']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-value']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-hint']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-card']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-label']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-bars']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-bar']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['high']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-bar-fill-container']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-bar-fill']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-count']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-bar']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['medium']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-bar-fill-container']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-bar-fill']} */ ;
/** @type {__VLS_StyleScopedClasses['medium']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-count']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-bar']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['low']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-bar-fill-container']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-bar-fill']} */ ;
/** @type {__VLS_StyleScopedClasses['low']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-count']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-card']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-label']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-bars']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-bar']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['positive']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-bar-fill-container']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-bar-fill']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-count']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-bar']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['neutral']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-bar-fill-container']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-bar-fill']} */ ;
/** @type {__VLS_StyleScopedClasses['neutral']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-count']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-bar']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['negative']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-bar-fill-container']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-bar-fill']} */ ;
/** @type {__VLS_StyleScopedClasses['negative']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-count']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-card']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-label']} */ ;
/** @type {__VLS_StyleScopedClasses['metrics-list']} */ ;
/** @type {__VLS_StyleScopedClasses['metric']} */ ;
/** @type {__VLS_StyleScopedClasses['metric']} */ ;
/** @type {__VLS_StyleScopedClasses['metric']} */ ;
/** @type {__VLS_StyleScopedClasses['detail-card']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-types-list']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-type-item']} */ ;
/** @type {__VLS_StyleScopedClasses['type-name']} */ ;
/** @type {__VLS_StyleScopedClasses['type-count']} */ ;
/** @type {__VLS_StyleScopedClasses['detail-card']} */ ;
/** @type {__VLS_StyleScopedClasses['sources-list']} */ ;
/** @type {__VLS_StyleScopedClasses['source-item']} */ ;
/** @type {__VLS_StyleScopedClasses['source-name']} */ ;
/** @type {__VLS_StyleScopedClasses['source-bar']} */ ;
/** @type {__VLS_StyleScopedClasses['bar-fill']} */ ;
/** @type {__VLS_StyleScopedClasses['source-count']} */ ;
/** @type {__VLS_StyleScopedClasses['detail-card']} */ ;
/** @type {__VLS_StyleScopedClasses['news-samples']} */ ;
/** @type {__VLS_StyleScopedClasses['sample-news']} */ ;
/** @type {__VLS_StyleScopedClasses['sample-header']} */ ;
/** @type {__VLS_StyleScopedClasses['sample-meta']} */ ;
/** @type {__VLS_StyleScopedClasses['detail-card']} */ ;
/** @type {__VLS_StyleScopedClasses['news-list-selection']} */ ;
/** @type {__VLS_StyleScopedClasses['news-checkbox']} */ ;
/** @type {__VLS_StyleScopedClasses['news-content']} */ ;
/** @type {__VLS_StyleScopedClasses['news-meta']} */ ;
/** @type {__VLS_StyleScopedClasses['source']} */ ;
/** @type {__VLS_StyleScopedClasses['date']} */ ;
/** @type {__VLS_StyleScopedClasses['type-badge']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            news: news,
            loading: loading,
            error: error,
            riskFilter: riskFilter,
            sentimentFilter: sentimentFilter,
            riskTypeFilter: riskTypeFilter,
            selectedNewsIds: selectedNewsIds,
            selectMode: selectMode,
            riskLevels: riskLevels,
            filteredNews: filteredNews,
            reportNews: reportNews,
            riskStats: riskStats,
            sourceStats: sourceStats,
            sentimentStats: sentimentStats,
            riskTypeStats: riskTypeStats,
            averageMetrics: averageMetrics,
            handleExport: handleExport,
            resetFilters: resetFilters,
            toggleNewsSelection: toggleNewsSelection,
            selectAllFiltered: selectAllFiltered,
            clearSelection: clearSelection,
            reloadPage: reloadPage,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
