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
const allEntities = ref([]);
const loading = ref(true);
const error = ref(null);
// Статистика
const stats = computed(() => ({
    relevantNews: newsData.value.length,
}));
// Сущности для отображения (top 5 с расчетом прироста)
const topEntities = computed(() => {
    return allEntities.value.slice(0, 5).map((entity) => {
        // Считаем прирост сущности на основе recent vs previous mentions
        const recent = entity.recentMentions || 0;
        const previous = entity.previousMentions || 1;
        const changePercent = previous > 0 ? Math.round(((recent - previous) / previous) * 100) : 0;
        const direction = changePercent > 0 ? 'up' : changePercent < 0 ? 'down' : 'flat';
        return {
            id: entity.id,
            name: entity.name,
            changePercent: Math.abs(changePercent),
            direction,
            category: entity.entity_type || 'Entity',
        };
    });
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
        // Загружаем новости
        const newsResponse = await api.getNews({
            page: 1,
            page_size: 20,
        });
        newsData.value = newsResponse.items;
        // Загружаем сущности
        const entities = await api.getEntities({ limit: 10 });
        allEntities.value = entities;
        console.log('✅ Dashboard loaded:', {
            newsItems: newsData.value.length,
            entities: allEntities.value.length
        });
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
const handleViewAllEntities = () => {
    router.push('/entities');
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
        ...{ 'onViewAll': {} },
        entities: (__VLS_ctx.topEntities),
    }));
    const __VLS_7 = __VLS_6({
        ...{ 'onEntityClick': {} },
        ...{ 'onViewAll': {} },
        entities: (__VLS_ctx.topEntities),
    }, ...__VLS_functionalComponentArgsRest(__VLS_6));
    let __VLS_9;
    let __VLS_10;
    let __VLS_11;
    const __VLS_12 = {
        onEntityClick: (__VLS_ctx.handleEntityClick)
    };
    const __VLS_13 = {
        onViewAll: (__VLS_ctx.handleViewAllEntities)
    };
    var __VLS_8;
    /** @type {[typeof EventFeed, ]} */ ;
    // @ts-ignore
    const __VLS_14 = __VLS_asFunctionalComponent(EventFeed, new EventFeed({
        ...{ 'onNewsClick': {} },
        events: (__VLS_ctx.events),
    }));
    const __VLS_15 = __VLS_14({
        ...{ 'onNewsClick': {} },
        events: (__VLS_ctx.events),
    }, ...__VLS_functionalComponentArgsRest(__VLS_14));
    let __VLS_17;
    let __VLS_18;
    let __VLS_19;
    const __VLS_20 = {
        onNewsClick: (__VLS_ctx.handleNewsClick)
    };
    var __VLS_16;
    __VLS_asFunctionalElement(__VLS_intrinsicElements.aside, __VLS_intrinsicElements.aside)({
        ...{ class: "secondary" },
    });
    /** @type {[typeof RiskLegend, ]} */ ;
    // @ts-ignore
    const __VLS_21 = __VLS_asFunctionalComponent(RiskLegend, new RiskLegend({
        levels: (__VLS_ctx.riskLegend),
    }));
    const __VLS_22 = __VLS_21({
        levels: (__VLS_ctx.riskLegend),
    }, ...__VLS_functionalComponentArgsRest(__VLS_21));
    /** @type {[typeof ActionPanel, ]} */ ;
    // @ts-ignore
    const __VLS_24 = __VLS_asFunctionalComponent(ActionPanel, new ActionPanel({}));
    const __VLS_25 = __VLS_24({}, ...__VLS_functionalComponentArgsRest(__VLS_24));
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
            handleViewAllEntities: handleViewAllEntities,
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
