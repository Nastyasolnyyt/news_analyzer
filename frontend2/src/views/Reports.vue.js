import { ref, computed, onMounted } from 'vue';
import { api } from '../api/client';
const news = ref([]);
const loading = ref(true);
const error = ref(null);
const riskLevels = {
    high: { label: 'Высокий риск', color: '#ff6464' },
    medium: { label: 'Средний риск', color: '#ffa500' },
    low: { label: 'Низкий риск', color: '#4ade80' },
};
// Статистика по рискам
const riskStats = computed(() => {
    const stats = { high: 0, medium: 0, low: 0 };
    news.value.forEach(item => {
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
    news.value.forEach(item => {
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
    news.value.forEach(item => {
        const sentiment = (item.sentiment_label || 'neutral');
        if (sentiment in stats) {
            stats[sentiment]++;
        }
    });
    return stats;
});
// Средние значения
const averageMetrics = computed(() => ({
    tonality: news.value.length > 0
        ? (news.value.reduce((sum, n) => sum + (n.tonality || 0), 0) / news.value.length).toFixed(2)
        : 0,
    emotion: news.value.length > 0
        ? (news.value.reduce((sum, n) => sum + (n.emotion || 0), 0) / news.value.length).toFixed(2)
        : 0,
    relevance: news.value.length > 0
        ? (news.value.reduce((sum, n) => sum + (n.relevance || 0), 0) / news.value.length).toFixed(2)
        : 0,
}));
onMounted(async () => {
    try {
        loading.value = true;
        console.log('📊 Loading reports data...');
        const data = await api.getNews({
            page: 1,
            page_size: 100, // Берём больше для аналитики
        });
        news.value = data.items;
        console.log('✅ Reports loaded:', data.items.length, 'items');
    }
    catch (e) {
        error.value = e.message || 'Ошибка загрузки отчёта';
        console.error('❌ Reports error:', error.value);
    }
    finally {
        loading.value = false;
    }
});
const handleExport = (format) => {
    if (format === 'json') {
        const data = {
            exportDate: new Date().toISOString(),
            totalItems: news.value.length,
            riskStats: riskStats.value,
            sourceStats: sourceStats.value,
            sentimentStats: sentimentStats.value,
            averageMetrics: averageMetrics.value,
            items: news.value,
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `report-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
    }
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['logo']} */ ;
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
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "header-actions" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.handleExport('json');
        } },
    ...{ class: "action-btn" },
    disabled: (__VLS_ctx.loading),
});
if (__VLS_ctx.loading) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "loading-state" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
}
else if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "error-state" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    (__VLS_ctx.error);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ style: {} },
    });
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "reports-grid" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "stat-card card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "stat-value" },
    });
    (__VLS_ctx.news.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "stat-card card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "risk-distribution" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "risk-item" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-count" },
    });
    (__VLS_ctx.riskStats.high);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "risk-item" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-count" },
    });
    (__VLS_ctx.riskStats.medium);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "risk-item" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "risk-count" },
    });
    (__VLS_ctx.riskStats.low);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "stat-card card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sentiment-distribution" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sentiment-item" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-count" },
    });
    (__VLS_ctx.sentimentStats.positive);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sentiment-item" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-count" },
    });
    (__VLS_ctx.sentimentStats.neutral);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sentiment-item" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "sentiment-count" },
    });
    (__VLS_ctx.sentimentStats.negative);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "stat-card card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metrics" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric-item" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "metric-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "metric-value" },
    });
    (__VLS_ctx.averageMetrics.tonality);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric-item" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "metric-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "metric-value" },
    });
    (__VLS_ctx.averageMetrics.emotion);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric-item" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "metric-label" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "metric-value" },
    });
    (__VLS_ctx.averageMetrics.relevance);
    if (__VLS_ctx.sourceStats.length > 0) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
            ...{ class: "sources-card card" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "sources-list" },
        });
        for (const [source] of __VLS_getVForSourceType((__VLS_ctx.sourceStats))) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                key: (source.name),
                ...{ class: "source-item" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: "source-name" },
            });
            (source.name);
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: "source-count" },
            });
            (source.count);
        }
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "news-list-card card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "news-list" },
    });
    for (const [item] of __VLS_getVForSourceType((__VLS_ctx.news.slice(0, 10)))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
            key: (item.id),
            ...{ class: "news-item" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "news-meta" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            ...{ class: "news-title" },
        });
        (item.title);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            ...{ class: (['risk-badge', `risk-${item.risk_level || 'low'}`]) },
        });
        (__VLS_ctx.riskLevels[item.risk_level]?.label || 'Неизвестно');
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "news-details" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            ...{ class: "source" },
        });
        (item.source);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            ...{ class: "date" },
        });
        (new Date(item.pub_date || item.date || '').toLocaleDateString('ru-RU'));
        if (item.sentiment_label) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                ...{ class: "sentiment" },
            });
            (item.sentiment_label);
        }
    }
    if (__VLS_ctx.news.length > 10) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
            ...{ class: "more-items" },
        });
        (__VLS_ctx.news.length - 10);
    }
}
/** @type {__VLS_StyleScopedClasses['reports-page']} */ ;
/** @type {__VLS_StyleScopedClasses['page-header']} */ ;
/** @type {__VLS_StyleScopedClasses['header-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['action-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['loading-state']} */ ;
/** @type {__VLS_StyleScopedClasses['error-state']} */ ;
/** @type {__VLS_StyleScopedClasses['reports-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-card']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-value']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-card']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-distribution']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-item']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-label']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-count']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-item']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-label']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-count']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-item']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-label']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-count']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-card']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-distribution']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-item']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-label']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-count']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-item']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-label']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-count']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-item']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-label']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment-count']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-card']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['metrics']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-item']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-label']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-value']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-item']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-label']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-value']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-item']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-label']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-value']} */ ;
/** @type {__VLS_StyleScopedClasses['sources-card']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['sources-list']} */ ;
/** @type {__VLS_StyleScopedClasses['source-item']} */ ;
/** @type {__VLS_StyleScopedClasses['source-name']} */ ;
/** @type {__VLS_StyleScopedClasses['source-count']} */ ;
/** @type {__VLS_StyleScopedClasses['news-list-card']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['news-list']} */ ;
/** @type {__VLS_StyleScopedClasses['news-item']} */ ;
/** @type {__VLS_StyleScopedClasses['news-meta']} */ ;
/** @type {__VLS_StyleScopedClasses['news-title']} */ ;
/** @type {__VLS_StyleScopedClasses['news-details']} */ ;
/** @type {__VLS_StyleScopedClasses['source']} */ ;
/** @type {__VLS_StyleScopedClasses['date']} */ ;
/** @type {__VLS_StyleScopedClasses['sentiment']} */ ;
/** @type {__VLS_StyleScopedClasses['more-items']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            news: news,
            loading: loading,
            error: error,
            riskLevels: riskLevels,
            riskStats: riskStats,
            sourceStats: sourceStats,
            sentimentStats: sentimentStats,
            averageMetrics: averageMetrics,
            handleExport: handleExport,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
