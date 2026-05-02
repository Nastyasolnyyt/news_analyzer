// frontend/src/api/client.ts
const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';
// ✅ MOCK DATA FALLBACK
import { entities as mockEntities, news as mockNews } from '../mockData';
// Вспомогательная функция: извлекает риск и тональность из analysis и добавляет в news
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
        // ИСПРАВЛЕНО: берем тональность из анализа
        tonality: news.tonality ?? analysis.tonality ?? 0,
        sentiment_label: (news.sentiment_label || analysis.sentiment_label || 'neutral'),
        emotion: news.emotion ?? analysis.emotion ?? 0,
        relevance: news.relevance ?? analysis.relevance ?? 0,
        // confidence есть только в PostAnalysis, но нет в News - не добавляем его
        // ИСПРАВЛЕНО: проверяем, что topic существует
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
                if (res.status === 404) {
                    console.warn('⚠️ Posts endpoint not found, using mock data');
                    // ✅ FALLBACK на mock-данные
                    const pageSize = params?.page_size || 20;
                    return {
                        items: mockNews.slice(0, pageSize).map(n => ({
                            id: n.id,
                            title: n.title,
                            text: n.fullText?.join('\n') || '',
                            source: n.source,
                            pub_date: n.date,
                            date: n.date,
                            risk_level: n.riskLevel,
                            risk_type: ['политический', 'экономический', 'социальный'][Math.floor(Math.random() * 3)],
                            summary: n.summary,
                        })),
                        total: mockNews.length,
                    };
                }
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
            // ✅ FALLBACK на mock-данные если пустой результат
            if (items.length === 0) {
                console.warn('⚠️ API returned empty news list, using mock data');
                const pageSize = params?.page_size || 20;
                return {
                    items: mockNews.slice(0, pageSize).map(n => ({
                        id: n.id,
                        title: n.title,
                        text: n.fullText?.join('\n') || '',
                        source: n.source,
                        pub_date: n.date,
                        date: n.date,
                        risk_level: n.riskLevel,
                        risk_type: ['политический', 'экономический', 'социальный'][Math.floor(Math.random() * 3)],
                        summary: n.summary,
                    })),
                    total: mockNews.length,
                };
            }
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
            // ✅ FINAL FALLBACK
            console.warn('⚠️ Using mock data as final fallback');
            const pageSize = params?.page_size || 20;
            return {
                items: mockNews.slice(0, pageSize).map(n => ({
                    id: n.id,
                    title: n.title,
                    text: n.fullText?.join('\n') || '',
                    source: n.source,
                    pub_date: n.date,
                    date: n.date,
                    risk_level: n.riskLevel,
                    risk_type: ['политический', 'экономический', 'социальный'][Math.floor(Math.random() * 3)],
                    summary: n.summary,
                })),
                total: mockNews.length,
            };
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
            // Используем новый эндпоинт /details вместо /mentions
            const url = `${API_BASE}/entities/${entityId}/details`;
            console.log('🔍 Fetching entity details from:', url);
            const res = await fetch(url);
            if (!res.ok) {
                const errorText = await res.text();
                throw new Error(`Entity ${entityId} not found: ${res.status} ${errorText}`);
            }
            const data = await res.json();
            console.log('✅ Entity details response:', data);
            // Преобразуем ответ бэкенда в формат, ожидаемый фронтендом
            const entity = {
                id: data.id,
                name: data.name,
                type: data.entity_type === 'PER' || data.entity_type?.toLowerCase().includes('person') ? 'Person' : 'Company',
                entity_type: data.entity_type,
                description: data.description || undefined,
                jurisdiction: data.jurisdiction || undefined,
                identifiers: data.identifiers ? Object.entries(data.identifiers).map(([label, value]) => ({ label, value: String(value) })) : [],
                registryInfo: data.identifiers?.type ? {
                    address: '',
                    registry: data.identifiers.type,
                    founded: '',
                } : undefined,
                linkedEntityIds: [],
                mentions: [],
            };
            // Преобразуем статистику упоминаний из формата бэкенда
            const chartData = (data.mentions_stats || []).map((stat) => ({
                week: stat.week,
                count: stat.count,
                note: stat.note,
            }));
            // Преобразуем связанные сущности
            const relatedEntities = (data.related_entities || []).map((rel) => ({
                id: rel.id,
                name: rel.name,
                type: rel.entity_type || rel.type || 'ORG',
                relation: rel.role || 'Связанная сущность',
            }));
            // Преобразуем новости
            const news = (data.recent_news || []).map((n) => ({
                id: n.id,
                title: n.title || `Новость #${n.id}`,
                text: n.summary || n.text || '',
                source: n.source || 'система',
                pub_date: n.date,
                date: n.date,
                risk_level: n.risk_level,
            }));
            console.log('✅ Loaded entity profile:', entity.name, {
                chartPoints: chartData.length,
                relatedEntities: relatedEntities.length,
                newsCount: news.length,
            });
            return {
                entity,
                mentions: [],
                chartData,
                relatedEntities,
                news,
            };
        }
        catch (error) {
            console.error('❌ Error fetching entity profile:', error);
            throw error;
        }
    },
    // Получить топ сущностей за 24 часа по росту интереса
    async getTopEntities24h(params) {
        try {
            const limit = params?.limit || 5;
            const url = `${API_BASE}/entities/top/24h?limit=${limit}`;
            console.log('🔍 Fetching top entities 24h from:', url);
            const res = await fetch(url);
            if (!res.ok) {
                if (res.status === 404) {
                    console.warn('⚠️ Top entities endpoint not found, returning empty list');
                    return [];
                }
                throw new Error(`API error: ${res.status}`);
            }
            const data = await res.json();
            const entities = Array.isArray(data) ? data : [];
            console.log('✅ Loaded top entities 24h:', entities.length);
            return entities.map((e) => ({
                id: e.id,
                name: e.name,
                entity_type: e.entity_type,
                changePercent: e.change_percent,
                direction: e.direction,
                category: e.entity_type || 'Сущность',
            }));
        }
        catch (error) {
            console.error('❌ Error fetching top entities 24h:', error);
            return [];
        }
    },
    // Получить список сущностей с их статистикой
    async getEntities(params) {
        try {
            const limit = params?.limit || 10;
            const url = `${API_BASE}/entities?limit=${limit}`;
            console.log('🔍 Fetching entities from:', url);
            const res = await fetch(url);
            if (!res.ok) {
                if (res.status === 404) {
                    console.warn('⚠️ Entities endpoint not found, using mock data');
                    return mockEntities.slice(0, limit).map((e) => ({
                        id: e.id,
                        name: e.name,
                        type: e.type,
                        entity_type: e.category,
                        description: e.description,
                        recentMentions: Math.random() * 50 | 0, // Случайное кол-во недавних упоминаний
                        previousMentions: Math.random() * 30 | 0,
                        topicCount: 3,
                    }));
                }
                throw new Error(`API error: ${res.status}`);
            }
            const data = await res.json();
            const entities = Array.isArray(data) ? data : data.items || [];
            // ✅ Fallback на mock-данные если API вернул пустой список
            if (entities.length === 0) {
                console.warn('⚠️ API returned empty entities list, using mock data');
                return mockEntities.slice(0, limit).map((e) => ({
                    id: e.id,
                    name: e.name,
                    type: e.type,
                    entity_type: e.category,
                    description: e.description,
                    recentMentions: Math.random() * 50 | 0,
                    previousMentions: Math.random() * 30 | 0,
                    topicCount: 3,
                }));
            }
            console.log('✅ Loaded entities:', entities.length);
            return entities.map((e) => ({
                id: e.id,
                name: e.name,
                type: e.entity_type?.includes('PER') ? 'Person' : 'Company',
                entity_type: e.entity_type,
                description: e.description,
                recentMentions: e.recent_mentions || 0,
                previousMentions: e.previous_mentions || 0,
                topicCount: e.topic_count || 0,
            }));
        }
        catch (error) {
            console.error('❌ Error fetching entities:', error);
            // ✅ Final fallback на mock-данные
            console.warn('⚠️ Using mock data as final fallback');
            return mockEntities.slice(0, params?.limit || 10).map((e) => ({
                id: e.id,
                name: e.name,
                type: e.type,
                entity_type: e.category,
                description: e.description,
                recentMentions: e.changePercent ? 50 : 20,
                previousMentions: 30,
                topicCount: 3,
            }));
        }
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
