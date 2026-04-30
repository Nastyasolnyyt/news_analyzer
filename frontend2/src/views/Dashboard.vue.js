import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import HeaderBar from '../components/HeaderBar.vue';
import StatsWidget from '../components/StatsWidget.vue';
import TopEntities from '../components/TopEntities.vue';
import EventFeed from '../components/EventFeed.vue';
import RiskLegend from '../components/RiskLegend.vue';
import ActionPanel from '../components/ActionPanel.vue';
import { api } from '../api/client';
const router = useRouter();
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8003';
// Реальные данные из API
const newsData = ref([]);
const loading = ref(true);
const error = ref(null);
// Статистика
const stats = computed(() => ({
    relevantNews: newsData.value.length,
}));
// Сущности для отображения (генерируем из новостей для демо)
const topEntities = computed(() => {
    const entities = [];
    const seen = new Set();
    // Парсим названия компаний из источников
    const sources = new Map();
    newsData.value.forEach(news => {
        if (news.source) {
            sources.set(news.source, (sources.get(news.source) || 0) + 1);
        }
    });
    // Берём топ источники как сущности
    Array.from(sources.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .forEach((entry, idx) => {
        const [source, count] = entry;
        if (!seen.has(source)) {
            entities.push({
                id: idx + 1,
                name: source,
                changePercent: Math.floor(Math.random() * 20 - 10),
                direction: Math.random() > 0.5 ? 'up' : 'down',
                category: 'Источник',
            });
            seen.add(source);
        }
    });
    return entities;
});
// События для ленты (последние новости)
const events = computed(() => {
    return newsData.value.slice(0, 4).map((n) => ({
        id: n.id,
        title: n.title,
        date: n.pub_date || n.date || new Date().toISOString(),
        source: n.source,
        summary: n.summary || n.text?.slice(0, 200),
        risk: n.risk_level || 'low',
        riskType: n.risk_type || null, // ✅ Добавляем тип риска
    }));
});
const riskLegend = [
    { level: 'high', label: 'Высокий риск', description: 'Требует немедленной реакции' },
    { level: 'medium', label: 'Средний риск', description: 'Нужен мониторинг' },
    { level: 'low', label: 'Низкий риск', description: 'Информация к сведению' },
];
// Загрузка данных при монтировании
onMounted(async () => {
    try {
        loading.value = true;
        console.log('📊 Loading dashboard data...');
        const data = await api.getNews({
            page: 1,
            page_size: 20,
        });
        newsData.value = data.items;
        console.log('✅ Dashboard loaded:', data.items.length, 'items');
    }
    catch (e) {
        error.value = e.message || 'Ошибка загрузки данных';
        console.error('❌ Dashboard error:', error.value);
    }
    finally {
        loading.value = false;
    }
});
const handleEntityClick = (entityId) => {
    router.push(`/entity/${entityId}`);
};
const handleNewsClick = (newsId) => {
    router.push(`/news/${newsId}`);
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['layout']} */ ;
/** @type {__VLS_StyleScopedClasses['secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['secondary']} */ ;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "dashboard" },
});
/** @type {[typeof HeaderBar, ]} */ ;
// @ts-ignore
const __VLS_0 = __VLS_asFunctionalComponent(HeaderBar, new HeaderBar({}));
const __VLS_1 = __VLS_0({}, ...__VLS_functionalComponentArgsRest(__VLS_0));
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
    (__VLS_ctx.API_URL);
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.main, __VLS_intrinsicElements.main)({
        ...{ class: "layout" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "primary" },
    });
    /** @type {[typeof StatsWidget, ]} */ ;
    // @ts-ignore
    const __VLS_3 = __VLS_asFunctionalComponent(StatsWidget, new StatsWidget({
        count: (__VLS_ctx.stats.relevantNews),
    }));
    const __VLS_4 = __VLS_3({
        count: (__VLS_ctx.stats.relevantNews),
    }, ...__VLS_functionalComponentArgsRest(__VLS_3));
    /** @type {[typeof TopEntities, ]} */ ;
    // @ts-ignore
    const __VLS_6 = __VLS_asFunctionalComponent(TopEntities, new TopEntities({
        ...{ 'onEntityClick': {} },
        entities: (__VLS_ctx.topEntities),
    }));
    const __VLS_7 = __VLS_6({
        ...{ 'onEntityClick': {} },
        entities: (__VLS_ctx.topEntities),
    }, ...__VLS_functionalComponentArgsRest(__VLS_6));
    let __VLS_9;
    let __VLS_10;
    let __VLS_11;
    const __VLS_12 = {
        onEntityClick: (__VLS_ctx.handleEntityClick)
    };
    var __VLS_8;
    /** @type {[typeof EventFeed, ]} */ ;
    // @ts-ignore
    const __VLS_13 = __VLS_asFunctionalComponent(EventFeed, new EventFeed({
        ...{ 'onNewsClick': {} },
        events: (__VLS_ctx.events),
    }));
    const __VLS_14 = __VLS_13({
        ...{ 'onNewsClick': {} },
        events: (__VLS_ctx.events),
    }, ...__VLS_functionalComponentArgsRest(__VLS_13));
    let __VLS_16;
    let __VLS_17;
    let __VLS_18;
    const __VLS_19 = {
        onNewsClick: (__VLS_ctx.handleNewsClick)
    };
    var __VLS_15;
    __VLS_asFunctionalElement(__VLS_intrinsicElements.aside, __VLS_intrinsicElements.aside)({
        ...{ class: "secondary" },
    });
    /** @type {[typeof RiskLegend, ]} */ ;
    // @ts-ignore
    const __VLS_20 = __VLS_asFunctionalComponent(RiskLegend, new RiskLegend({
        levels: (__VLS_ctx.riskLegend),
    }));
    const __VLS_21 = __VLS_20({
        levels: (__VLS_ctx.riskLegend),
    }, ...__VLS_functionalComponentArgsRest(__VLS_20));
    /** @type {[typeof ActionPanel, ]} */ ;
    // @ts-ignore
    const __VLS_23 = __VLS_asFunctionalComponent(ActionPanel, new ActionPanel({}));
    const __VLS_24 = __VLS_23({}, ...__VLS_functionalComponentArgsRest(__VLS_23));
}
/** @type {__VLS_StyleScopedClasses['dashboard']} */ ;
/** @type {__VLS_StyleScopedClasses['loading-state']} */ ;
/** @type {__VLS_StyleScopedClasses['error-state']} */ ;
/** @type {__VLS_StyleScopedClasses['layout']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['secondary']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            HeaderBar: HeaderBar,
            StatsWidget: StatsWidget,
            TopEntities: TopEntities,
            EventFeed: EventFeed,
            RiskLegend: RiskLegend,
            ActionPanel: ActionPanel,
            API_URL: API_URL,
            loading: loading,
            error: error,
            stats: stats,
            topEntities: topEntities,
            events: events,
            riskLegend: riskLegend,
            handleEntityClick: handleEntityClick,
            handleNewsClick: handleNewsClick,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
