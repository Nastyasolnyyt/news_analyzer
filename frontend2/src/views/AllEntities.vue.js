import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../api/client';
const router = useRouter();
const entities = ref([]);
const loading = ref(true);
const error = ref(null);
const searchQuery = ref('');
// Пагинация
const currentPage = ref(1);
const pageSize = 50;
const totalEntities = ref(0);
const isLoadingMore = ref(false);
// Кэш для всех загруженных сущностей
const allLoadedEntities = ref(new Map());
// Фильтрованные сущности для текущей страницы
const filteredEntities = computed(() => {
    const query = searchQuery.value.toLowerCase();
    const allEntities = Array.from(allLoadedEntities.value.values());
    const filtered = query
        ? allEntities.filter(entity => entity.name.toLowerCase().includes(query))
        : allEntities;
    return filtered.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize);
});
const totalPages = computed(() => {
    const allEntities = Array.from(allLoadedEntities.value.values());
    const query = searchQuery.value.toLowerCase();
    const filtered = query
        ? allEntities.filter(entity => entity.name.toLowerCase().includes(query))
        : allEntities;
    return Math.ceil(filtered.length / pageSize);
});
onMounted(async () => {
    await loadEntities();
});
const loadEntities = async () => {
    try {
        loading.value = true;
        error.value = null;
        console.log('🚀 Loading first page of entities...');
        // ФАЗА 1: Загружаем первую страницу и показываем её немедленно
        try {
            const firstPageResult = await api.getEntities({
                limit: pageSize,
                page: 1,
            });
            console.log(`📄 Loaded page 1: ${firstPageResult.items.length} entities (total: ${firstPageResult.total})`);
            // Добавляем первую страницу в кэш
            firstPageResult.items.forEach(entity => {
                if (entity && entity.id) {
                    allLoadedEntities.value.set(entity.id, entity);
                }
            });
            totalEntities.value = firstPageResult.total;
            entities.value = Array.from(allLoadedEntities.value.values());
            // Показываем первую страницу немедленно
            loading.value = false;
            // ФАЗА 2: Загружаем остальные страницы в фоне (не блокируя UI)
            if (firstPageResult.total > pageSize) {
                console.log('📊 Starting background loading of remaining pages...');
                const totalPages = Math.ceil(firstPageResult.total / pageSize);
                // Загружаем оставшиеся страницы асинхронно
                (async () => {
                    for (let page = 2; page <= totalPages; page++) {
                        try {
                            const result = await api.getEntities({
                                limit: pageSize,
                                page: page,
                            });
                            // Добавляем в кэш
                            result.items.forEach(entity => {
                                if (entity && entity.id) {
                                    allLoadedEntities.value.set(entity.id, entity);
                                }
                            });
                            console.log(`📄 Loaded page ${page}/${totalPages}: ${result.items.length} entities`);
                        }
                        catch (pageError) {
                            console.error(`⚠️ Error loading page ${page}:`, pageError);
                            // Продолжаем со следующей страницы
                        }
                    }
                    // После загрузки всех страниц обновляем список
                    const allLoaded = Array.from(allLoadedEntities.value.values());
                    entities.value = allLoaded;
                    console.log(`✅ Background loading complete: ${allLoaded.length} total entities`);
                })();
            }
        }
        catch (firstPageError) {
            console.error('❌ Error loading first page:', firstPageError);
            error.value = firstPageError instanceof Error ? firstPageError.message : 'Ошибка загрузки сущностей';
            loading.value = false;
            throw firstPageError;
        }
    }
    catch (e) {
        if (!error.value) {
            error.value = e.message || 'Ошибка загрузки сущностей';
        }
        console.error('❌ Error:', e);
        loading.value = false;
    }
};
const handleSearch = () => {
    currentPage.value = 1; // Сбрасываем на первую страницу при поиске
};
const handleEntityClick = (entityId) => {
    router.push(`/entity/${entityId}`);
};
const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};
const nextPage = () => {
    if (currentPage.value < totalPages.value) {
        currentPage.value++;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};
const prevPage = () => {
    if (currentPage.value > 1) {
        currentPage.value--;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};
const reloadPage = async () => {
    allLoadedEntities.value.clear();
    currentPage.value = 1;
    await loadEntities();
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['back-button']} */ ;
/** @type {__VLS_StyleScopedClasses['page-header']} */ ;
/** @type {__VLS_StyleScopedClasses['loading-state']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['search-section']} */ ;
/** @type {__VLS_StyleScopedClasses['search-input']} */ ;
/** @type {__VLS_StyleScopedClasses['no-results']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-card']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-card']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-header']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-view']} */ ;
/** @type {__VLS_StyleScopedClasses['pagination-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['pagination-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['entities-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['page-header']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-card']} */ ;
/** @type {__VLS_StyleScopedClasses['pagination']} */ ;
/** @type {__VLS_StyleScopedClasses['pagination-btn']} */ ;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "all-entities-page" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)({
    ...{ class: "page-header" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "back-nav" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.router.back();
        } },
    ...{ class: "back-button" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
    ...{ class: "description" },
});
if (__VLS_ctx.loading) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "loading-state" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "spinner" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "loading-hint" },
    });
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
                __VLS_ctx.loadEntities();
            } },
        ...{ class: "btn-secondary" },
    });
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "content" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "search-section" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        ...{ onInput: (__VLS_ctx.handleSearch) },
        value: (__VLS_ctx.searchQuery),
        type: "text",
        placeholder: "Поиск по названию...",
        ...{ class: "search-input" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "search-count" },
    });
    (__VLS_ctx.filteredEntities.length);
    (__VLS_ctx.entities.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "entities-section" },
    });
    if (__VLS_ctx.filteredEntities.length === 0) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "no-results" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    }
    else {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "entities-grid" },
        });
        for (const [entity] of __VLS_getVForSourceType((__VLS_ctx.filteredEntities))) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
                ...{ onClick: (...[$event]) => {
                        if (!!(__VLS_ctx.loading))
                            return;
                        if (!!(__VLS_ctx.error))
                            return;
                        if (!!(__VLS_ctx.filteredEntities.length === 0))
                            return;
                        __VLS_ctx.handleEntityClick(entity.id);
                    } },
                ...{ onKeydown: (...[$event]) => {
                        if (!!(__VLS_ctx.loading))
                            return;
                        if (!!(__VLS_ctx.error))
                            return;
                        if (!!(__VLS_ctx.filteredEntities.length === 0))
                            return;
                        __VLS_ctx.handleEntityClick(entity.id);
                    } },
                key: (entity.id),
                ...{ class: "entity-card" },
                role: "button",
                tabindex: "0",
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                ...{ class: "entity-header" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
            (entity.name);
            if (entity.entity_type) {
                __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                    ...{ class: "entity-type" },
                });
                (entity.entity_type);
            }
            if (entity.description) {
                __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                    ...{ class: "entity-description" },
                });
                (entity.description);
            }
            if (entity.recentMentions || entity.topicCount) {
                __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                    ...{ class: "entity-stats" },
                });
                if (entity.recentMentions) {
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                        ...{ class: "stat" },
                    });
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                        ...{ class: "stat-label" },
                    });
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                        ...{ class: "stat-value" },
                    });
                    (entity.recentMentions);
                }
                if (entity.topicCount) {
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                        ...{ class: "stat" },
                    });
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                        ...{ class: "stat-label" },
                    });
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                        ...{ class: "stat-value" },
                    });
                    (entity.topicCount);
                }
            }
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
                ...{ class: "btn-view" },
            });
        }
    }
    if (__VLS_ctx.filteredEntities.length > 0) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "pagination" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
            ...{ onClick: (__VLS_ctx.prevPage) },
            ...{ class: "pagination-btn" },
            disabled: (__VLS_ctx.currentPage === 1),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            ...{ class: "pagination-info" },
        });
        (__VLS_ctx.currentPage);
        (__VLS_ctx.totalPages);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
            ...{ onClick: (__VLS_ctx.nextPage) },
            ...{ class: "pagination-btn" },
            disabled: (__VLS_ctx.currentPage === __VLS_ctx.totalPages),
        });
    }
}
/** @type {__VLS_StyleScopedClasses['all-entities-page']} */ ;
/** @type {__VLS_StyleScopedClasses['page-header']} */ ;
/** @type {__VLS_StyleScopedClasses['back-nav']} */ ;
/** @type {__VLS_StyleScopedClasses['back-button']} */ ;
/** @type {__VLS_StyleScopedClasses['description']} */ ;
/** @type {__VLS_StyleScopedClasses['loading-state']} */ ;
/** @type {__VLS_StyleScopedClasses['spinner']} */ ;
/** @type {__VLS_StyleScopedClasses['loading-hint']} */ ;
/** @type {__VLS_StyleScopedClasses['error-state']} */ ;
/** @type {__VLS_StyleScopedClasses['error-title']} */ ;
/** @type {__VLS_StyleScopedClasses['error-message']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-secondary']} */ ;
/** @type {__VLS_StyleScopedClasses['content']} */ ;
/** @type {__VLS_StyleScopedClasses['search-section']} */ ;
/** @type {__VLS_StyleScopedClasses['search-input']} */ ;
/** @type {__VLS_StyleScopedClasses['search-count']} */ ;
/** @type {__VLS_StyleScopedClasses['entities-section']} */ ;
/** @type {__VLS_StyleScopedClasses['no-results']} */ ;
/** @type {__VLS_StyleScopedClasses['entities-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-card']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-header']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-type']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-description']} */ ;
/** @type {__VLS_StyleScopedClasses['entity-stats']} */ ;
/** @type {__VLS_StyleScopedClasses['stat']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-label']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-value']} */ ;
/** @type {__VLS_StyleScopedClasses['stat']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-label']} */ ;
/** @type {__VLS_StyleScopedClasses['stat-value']} */ ;
/** @type {__VLS_StyleScopedClasses['btn-view']} */ ;
/** @type {__VLS_StyleScopedClasses['pagination']} */ ;
/** @type {__VLS_StyleScopedClasses['pagination-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['pagination-info']} */ ;
/** @type {__VLS_StyleScopedClasses['pagination-btn']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            router: router,
            entities: entities,
            loading: loading,
            error: error,
            searchQuery: searchQuery,
            currentPage: currentPage,
            filteredEntities: filteredEntities,
            totalPages: totalPages,
            loadEntities: loadEntities,
            handleSearch: handleSearch,
            handleEntityClick: handleEntityClick,
            nextPage: nextPage,
            prevPage: prevPage,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
