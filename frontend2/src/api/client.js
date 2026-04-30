// frontend/src/api/client.ts
const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';
// ✅ Вспомогательная функция: извлекает риск из analysis и добавляет в news
function enrichNewsWithRisk(news, analysis) {
    if (!analysis)
        return news;
    return {
        ...news,
        risk_level: news.risk_level || analysis.risk_level,
        risk: news.risk || analysis.risk_level,
        risk_type: news.risk_type || analysis.risk_type,
        risk_confidence: news.risk_confidence || analysis.risk_confidence,
        risk_type_confidence: news.risk_type_confidence || analysis.risk_type_confidence,
        tonality: news.tonality || analysis.tonality,
        // ✅ ИСПРАВЛЕНО: приводим к правильному типу
        sentiment_label: (news.sentiment_label || analysis.sentiment_label),
        emotion: news.emotion || analysis.emotion,
        relevance: news.relevance || analysis.relevance,
        // ✅ ИСПРАВЛЕНО: проверяем, что topic существует
        topic_name: news.topic_name || analysis.topic?.name,
        topic_id: news.topic_id || analysis.topic_id || analysis.topic?.id,
    };
}
export const api = {
    // Получить список новостей
    async getNews(params) {
        try {
            const queryParams = new URLSearchParams();
            if (params?.page)
                queryParams.append('page', String(params.page));
            if (params?.page_size)
                queryParams.append('page_size', String(params.page_size));
            if (params?.search)
                queryParams.append('search', params.search);
            if (params?.risk_level)
                queryParams.append('risk_level', params.risk_level);
            if (params?.risk_type)
                queryParams.append('risk_type', params.risk_type);
            if (params?.source)
                queryParams.append('source', params.source);
            const qs = queryParams.toString();
            const url = `${API_BASE}/posts${qs ? '?' + qs : ''}`;
            console.log('🔍 Fetching posts from:', url);
            const res = await fetch(url);
            if (!res.ok) {
                throw new Error(`API error: ${res.status} ${res.statusText}`);
            }
            const data = await res.json();
            console.log('📦 Raw API response:', {
                total: data.total,
                itemsCount: Array.isArray(data.items) ? data.items.length : 0,
                firstItem: data.items?.[0]
            });
            // ✅ ПРАВИЛЬНО извлекаем и обогащаем данные:
            const items = Array.isArray(data.items)
                ? data.items.map((item) => {
                    // Если приходит { post, analysis, entities }, извлекаем post
                    const newsItem = item.post || item;
                    // ✅ Обогащаем news данными из analysis (включая risk_level и risk_type)
                    return enrichNewsWithRisk(newsItem, item.analysis);
                })
                : [];
            console.log('✅ Loaded news:', items.length, 'items');
            if (items.length > 0) {
                console.log('📊 First item risk:', {
                    risk_level: items[0].risk_level,
                    risk_type: items[0].risk_type,
                });
            }
            return { items, total: data.total || 0 };
        }
        catch (error) {
            console.error('❌ Error fetching news:', error);
            throw error;
        }
    },
    // Получить одну новость по ID
    async getNewsById(id) {
        try {
            const url = `${API_BASE}/posts/${id}`;
            console.log('🔍 Fetching post:', url);
            const res = await fetch(url);
            if (!res.ok)
                throw new Error(`Not found: ${id}`);
            const data = await res.json();
            // Если приходит { post, analysis, entities }, извлекаем post
            const newsItem = data.post || data;
            // ✅ Обогащаем данными из analysis
            const enriched = enrichNewsWithRisk(newsItem, data.analysis);
            // Добавляем связанные сущности
            if (data.entities) {
                enriched.relatedEntityIds = data.entities.map((e) => e.id);
            }
            console.log('✅ Loaded post:', {
                id: enriched.id,
                risk_level: enriched.risk_level,
                risk_type: enriched.risk_type
            });
            return enriched;
        }
        catch (error) {
            console.error('❌ Error fetching news:', error);
            throw error;
        }
    },
    // Получить упоминания сущности
    async getEntityMentions(entityId, params) {
        try {
            const queryParams = new URLSearchParams();
            if (params?.start)
                queryParams.append('start', params.start);
            if (params?.end)
                queryParams.append('end', params.end);
            const qs = queryParams.toString();
            const url = `${API_BASE}/entities/${entityId}/mentions${qs ? '?' + qs : ''}`;
            console.log('🔍 Fetching entity mentions:', url);
            const res = await fetch(url);
            if (!res.ok)
                throw new Error(`Not found: ${entityId}`);
            const data = await res.json();
            console.log('✅ Loaded mentions:', Array.isArray(data) ? data.length : 1);
            return Array.isArray(data) ? data : [data];
        }
        catch (error) {
            console.error('❌ Error fetching mentions:', error);
            return [];
        }
    },
    // Получить полный профиль сущности с графиками и связями
    async getEntityProfile(entityId) {
        try {
            // Получаем упоминания
            const mentions = await this.getEntityMentions(entityId);
            if (mentions.length === 0 || !mentions[0].entity) {
                throw new Error(`Entity ${entityId} not found`);
            }
            const entityInfo = mentions[0].entity;
            // Формируем базовый объект сущности
            const entity = {
                id: entityInfo.id,
                name: entityInfo.name,
                type: entityInfo.entity_type === 'PER' ? 'Person' : 'Company',
                entity_type: entityInfo.entity_type,
                description: entityInfo.description || undefined,
                jurisdiction: entityInfo.jurisdiction || undefined,
                identifiers: entityInfo.identifiers || [],
                registryInfo: entityInfo.registry_info ? {
                    address: entityInfo.registry_info.address || '',
                    registry: entityInfo.registry_info.registry || '',
                    founded: entityInfo.registry_info.founded || '',
                } : undefined,
                linkedEntityIds: entityInfo.linked_entity_ids || [],
                mentions: [],
            };
            // Формируем данные для графика (группируем по неделям)
            const chartMap = new Map();
            const newsList = [];
            mentions.forEach((m) => {
                const date = new Date(m.mentioned_at);
                const weekStart = new Date(date);
                weekStart.setDate(date.getDate() - date.getDay());
                const weekKey = weekStart.toISOString().split('T')[0];
                const existing = chartMap.get(weekKey) || { count: 0, notes: [] };
                existing.count += 1;
                if (m.note)
                    existing.notes.push(m.note);
                chartMap.set(weekKey, existing);
                // Добавляем новость
                newsList.push({
                    id: m.post_id,
                    title: `Упоминание #${m.post_id}`,
                    text: m.text || `Упомянута сущность: ${entityInfo.name}`,
                    source: m.source || 'система',
                    pub_date: m.mentioned_at,
                    date: m.mentioned_at,
                });
            });
            const chartData = Array.from(chartMap.entries())
                .map(([week, data]) => ({
                week,
                count: data.count,
                note: data.notes.length > 0 ? data.notes[0] : undefined,
            }))
                .sort((a, b) => a.week.localeCompare(b.week));
            // Связанные сущности (из первого упоминания или пустой массив)
            const relatedEntities = entityInfo.related_entities || [];
            console.log('✅ Loaded entity profile:', entity.name, {
                mentions: mentions.length,
                chartPoints: chartData.length,
                relatedEntities: relatedEntities.length,
            });
            return {
                entity,
                mentions,
                chartData,
                relatedEntities,
                news: newsList,
            };
        }
        catch (error) {
            console.error('❌ Error fetching entity profile:', error);
            throw error;
        }
    },
    // Получить список сущностей
    async getEntities() {
        return [];
    },
    // Получить сущность по ID
    async getEntityById(id) {
        try {
            const mentions = await this.getEntityMentions(id);
            if (mentions.length === 0 || !mentions[0].entity) {
                throw new Error(`Entity ${id} not found`);
            }
            const entity = mentions[0].entity;
            return {
                id: entity.id,
                name: entity.name,
                type: 'Company',
                entity_type: entity.entity_type,
            };
        }
        catch (error) {
            console.error('❌ Error fetching entity:', error);
            throw error;
        }
    },
    // Получить связанные сущности по ID
    async getEntitiesByIds(ids) {
        if (!ids.length)
            return [];
        const results = await Promise.all(ids.map(id => this.getEntityById(id).catch((e) => {
            console.warn(`Failed to fetch entity ${id}:`, e);
            return null;
        })));
        return results.filter((e) => e !== null);
    },
    // Получить высокорисковые новости
    async getHighRiskNews(params) {
        return this.getNews({
            ...params,
            risk_level: 'high',
        });
    },
    // Поиск новостей по запросу
    async searchNews(query, params) {
        return this.getNews({
            ...params,
            search: query,
        });
    },
};
