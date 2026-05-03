// frontend/src/api/client.ts
const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

// Helper для получения заголовков с токеном
function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('accessToken');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
}

// ===== AUTH TYPES =====

export interface LoginRequest {
  login: string;
  password: string;
}

export interface RegisterRequest {
  login: string;
  password: string;
  name: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserDTO {
  id: number;
  login: string;
  name: string;
  role: string;
  created_at: string;
}

export type RiskLevel = 'high' | 'medium' | 'low';

export interface PostAnalysis {
  id?: number;
  post_id: number;
  topic_id?: number | null;
  emotion?: number;
  tonality?: number;
  relevance?: number;
  // ИСПРАВЛЕНО: строгая типизация + string для совместимости
  sentiment_label?: 'positive' | 'negative' | 'neutral' | string;
  // ДОБАВЛЕНО: поля из risk-classifier и risklevel-classifier
  risk_level?: 'high' | 'medium' | 'low';
  risk_type?: 'политический' | 'экономический' | 'социальный';
  risk_confidence?: number;
  risk_type_confidence?: number;
}

export interface Topic {
  id: number;
  name: string;
  created_at: string;
}

export interface Topic {
  id: number;
  name: string;
  created_at: string;
}

export interface Risk {
  id: number;
  article_id: number;
  risk_type?: string;
  confidence?: number;
  created_at?: string;
}

export interface News {
  id: number;
  title: string;
  text: string;
  source: string;
  link?: string | null;
  pub_date?: string;
  created_at?: string;
  updated_at?: string;
  
  // Риск — основные поля для отображения
  risk_level?: RiskLevel;
  risk?: RiskLevel; // Для совместимости
  risk_type?: 'политический' | 'экономический' | 'социальный';
  risk_confidence?: number;
  risk_type_confidence?: number;
  
  // Анализ тональности
  tonality?: number;
  sentiment_label?: 'positive' | 'negative' | 'neutral';
  emotion?: number;
  relevance?: number;
  confidence?: number;
  
  // Темы и сущности
  topic_name?: string;
  topic_id?: number;
  relatedEntityIds?: number[];
  
  // Дополнительно
  summary?: string;
  fullText?: string[];
  date?: string;
  tags?: string[];
}

export interface NamedEntity {
  id: number;
  name: string;
  entity_type: string;
  created_at: string;
}

export interface Entity {
  id: number;
  name: string;
  type: 'Company' | 'Person' | 'Event';
  entity_type?: string;
  description?: string;
  jurisdiction?: string;
  identifiers?: Array<{ label: string; value: string }>;
  registryInfo?: { address: string; registry: string; founded: string };
  linkedEntityIds?: number[];
  mentions?: Array<{ week: string; count: number; note?: string }>;
}

export interface NewsResponse {
  post: News;
  analysis?: PostAnalysis & { topic?: Topic };
  entities: NamedEntity[];
}

export interface NewsListResponse {
  items: (News | NewsResponse)[];
  total: number;
  page: number;
  page_size: number;
}

// ===== NOTIFICATION TYPES =====

export interface NotificationTrigger {
  id: number;
  name: string;
  trigger_type: string;
  trigger_value: string;
  description?: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationChannel {
  id: number;
  channel_type: string;
  channel_address?: string;
  enabled: boolean;
  verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationSource {
  id: number;
  source_type: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationSettings {
  id: number;
  enabled: boolean;
  digest_frequency: string;
  quiet_hours_enabled: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  created_at: string;
  updated_at: string;
}

export interface NotificationConfig {
  settings: NotificationSettings;
  triggers: NotificationTrigger[];
  channels: NotificationChannel[];
  sources: NotificationSource[];
}

// Вспомогательная функция: извлекает риск и тональность из analysis и добавляет в news
function enrichNewsWithRisk(news: News, analysis?: PostAnalysis & { topic?: Topic }): News {
  if (!analysis) return news;
  
  return {
    ...news,
    risk_level: news.risk_level || analysis.risk_level,
    risk: news.risk || analysis.risk_level,
    risk_type: news.risk_type || analysis.risk_type,
    risk_confidence: news.risk_confidence || analysis.risk_confidence,
    risk_type_confidence: news.risk_type_confidence || analysis.risk_type_confidence,
    // ИСПРАВЛЕНО: берем тональность из анализа
    tonality: news.tonality ?? analysis.tonality ?? 0,
    sentiment_label: (news.sentiment_label || analysis.sentiment_label || 'neutral') as 'positive' | 'negative' | 'neutral',
    emotion: news.emotion ?? analysis.emotion ?? 0,
    relevance: news.relevance ?? analysis.relevance ?? 0,
    // confidence есть только в PostAnalysis, но нет в News - не добавляем его
    // ИСПРАВЛЕНО: проверяем, что topic существует
    topic_name: news.topic_name || (analysis as any).topic?.name,
    topic_id: news.topic_id || analysis.topic_id || (analysis as any).topic?.id,
  };
}

export const api = {
  // Получить список новостей
  async getNews(params?: {
    page?: number;
    page_size?: number;
    risk_level?: string;
    risk_type?: string;
    source?: string;
    search?: string;
  }): Promise<{ items: News[]; total: number }> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params?.page) queryParams.append('page', String(params.page));
      if (params?.page_size) queryParams.append('page_size', String(params.page_size));
      if (params?.search) queryParams.append('search', params.search);
      if (params?.risk_level) queryParams.append('risk_level', params.risk_level);
      if (params?.risk_type) queryParams.append('risk_type', params.risk_type);
      if (params?.source) queryParams.append('source', params.source);

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
        ? data.items.map((item: any) => {
            // Если приходит { post, analysis, entities }, извлекаем post
            const newsItem: News = item.post || item;
            
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
    } catch (error) {
      console.error('❌ Error fetching news:', error);
      throw error;
    }
  },

  // Получить одну новость по ID
  async getNewsById(id: number): Promise<News> {
    try {
      const url = `${API_BASE}/posts/${id}`;
      console.log('🔍 Fetching post:', url);
      
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Not found: ${id}`);
      
      const data = await res.json();
      
      // Если приходит { post, analysis, entities }, извлекаем post
      const newsItem: News = data.post || data;
      
      // ✅ Обогащаем данными из analysis
      const enriched = enrichNewsWithRisk(newsItem, data.analysis);
      
      // Добавляем связанные сущности
      if (data.entities) {
        enriched.relatedEntityIds = data.entities.map((e: any) => e.id);
      }
      
      console.log('✅ Loaded post:', { 
        id: enriched.id, 
        risk_level: enriched.risk_level,
        risk_type: enriched.risk_type 
      });
      
      return enriched;
    } catch (error) {
      console.error('❌ Error fetching news:', error);
      throw error;
    }
  },

  // Получить упоминания сущности
  async getEntityMentions(entityId: number, params?: {
    start?: string;
    end?: string;
  }): Promise<any[]> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.start) queryParams.append('start', params.start);
      if (params?.end) queryParams.append('end', params.end);
      
      const qs = queryParams.toString();
      const url = `${API_BASE}/entities/${entityId}/mentions${qs ? '?' + qs : ''}`;
      
      console.log('🔍 Fetching entity mentions:', url);
      
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Not found: ${entityId}`);
      
      const data = await res.json();
      console.log('✅ Loaded mentions:', Array.isArray(data) ? data.length : 1);
      return Array.isArray(data) ? data : [data];
    } catch (error) {
      console.error('❌ Error fetching mentions:', error);
      return [];
    }
  },

  // Получить полный профиль сущности с графиками и связями
  async getEntityProfile(entityId: number): Promise<{
    entity: Entity;
    mentions: any[];
    chartData: Array<{ week: string; count: number; note?: string }>;
    relatedEntities: Array<{ id: number; name: string; type: string; relation: string }>;
    news: News[];
  }> {
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
      const entity: Entity = {
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
      const chartData = (data.mentions_stats || []).map((stat: any) => ({
        week: stat.week,
        count: stat.count,
        note: stat.note,
      }));
      
      // Преобразуем связанные сущности
      const relatedEntities = (data.related_entities || []).map((rel: any) => ({
        id: rel.id,
        name: rel.name,
        type: rel.entity_type || rel.type || 'ORG',
        relation: rel.role || 'Связанная сущность',
      }));
      
      // Преобразуем новости
      const news = (data.recent_news || []).map((n: any) => ({
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
    } catch (error) {
      console.error('❌ Error fetching entity profile:', error);
      throw error;
    }
  },

  // Получить топ сущностей за 24 часа по росту интереса
  async getTopEntities24h(params?: { limit?: number }): Promise<Array<{
    id: number;
    name: string;
    entity_type: string;
    changePercent: number;
    direction: 'up' | 'down' | 'flat';
    category: string;
  }>> {
    const limit = params?.limit || 5;
    
    // Поскольку эндпоинт /entities/top/24h отсутствует на сервере,
    // получаем топ сущностей через посты и вычисляем статистику
    try {
      const url = `${API_BASE}/posts?page_size=${limit * 10}`;
      console.log('🔍 Fetching top entities via posts from:', url);
      
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`API error ${res.status}: ${res.statusText}`);
      }
      
      const data = await res.json();
      const items = Array.isArray(data.items) ? data.items : [];
      
      // Считаем упоминания сущностей
      const entityMap = new Map<number, { id: number; name: string; entity_type: string; count: number }>();
      for (const item of items) {
        const entities = item.entities || [];
        for (const entity of entities) {
          if (!entityMap.has(entity.id)) {
            entityMap.set(entity.id, {
              id: entity.id,
              name: entity.name,
              entity_type: entity.entity_type,
              count: 0,
            });
          }
          const e = entityMap.get(entity.id)!;
          e.count += 1;
        }
      }
      
      // Сортируем по количеству упоминаний и берем топ-N
      const sorted = Array.from(entityMap.values())
        .sort((a, b) => b.count - a.count)
        .slice(0, limit);
      
      console.log('✅ Loaded top entities 24h:', sorted.length);
      
      return sorted.map((e) => ({
        id: e.id,
        name: e.name,
        entity_type: e.entity_type,
        changePercent: Math.random() * 50 + 10, // временное значение
        direction: 'up' as const,
        category: e.entity_type === 'PER' ? 'Персона' : e.entity_type === 'LOC' ? 'Локация' : e.entity_type === 'ORG' ? 'Организация' : 'Сущность',
      }));
    } catch (error) {
      console.error('❌ Error fetching top entities:', error);
      throw error;
    }
  },

  // Получить список сущностей с их статистикой
  async getEntities(params?: { limit?: number }): Promise<Array<Entity & { recentMentions: number; previousMentions: number; topicCount: number }>> {
    const limit = params?.limit || 100;
    
    // Получаем сущности через посты, так как отдельного эндпоинта /entities нет
    try {
      const url = `${API_BASE}/posts?page_size=${limit * 5}`;
      console.log('🔍 Fetching entities via posts from:', url);
      
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`API error ${res.status}: ${res.statusText}`);
      }
      
      const data = await res.json();
      const items = Array.isArray(data.items) ? data.items : [];
      
      // Собираем все уникальные сущности из постов
      const entityMap = new Map<number, any>();
      for (const item of items) {
        const entities = item.entities || [];
        for (const entity of entities) {
          if (!entityMap.has(entity.id)) {
            entityMap.set(entity.id, {
              id: entity.id,
              name: entity.name,
              type: entity.entity_type === 'PER' ? 'Person' : entity.entity_type === 'LOC' ? 'Location' : entity.entity_type === 'ORG' ? 'Organization' : 'Company',
              entity_type: entity.entity_type,
              description: `${entity.name} — ${entity.entity_type === 'PER' ? 'Персона' : entity.entity_type === 'LOC' ? 'Локация' : entity.entity_type === 'ORG' ? 'Организация' : 'Сущность'}`,
              recentMentions: 0,
              previousMentions: 0,
              topicCount: 0,
            });
          }
          // Считаем упоминания
          const e = entityMap.get(entity.id);
          e.recentMentions = (e.recentMentions || 0) + 1;
        }
      }
      
      const entities = Array.from(entityMap.values()).slice(0, limit);
      console.log('✅ Loaded entities:', entities.length);
      
      return entities;
    } catch (error) {
      console.error('❌ Error fetching entities:', error);
      throw error;
    }
  },

  // Получить сущность по ID
  async getEntityById(id: number): Promise<Entity> {
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
    } catch (error) {
      console.error('❌ Error fetching entity:', error);
      throw error;
    }
  },

  // Получить связанные сущности по ID
  async getEntitiesByIds(ids: number[]): Promise<Entity[]> {
    if (!ids.length) return [];
    
    const results = await Promise.all(
      ids.map(id => 
        this.getEntityById(id).catch((e) => {
          console.warn(`Failed to fetch entity ${id}:`, e);
          return null;
        })
      )
    );
    
    return results.filter((e): e is Entity => e !== null);
  },

  // Получить высокорисковые новости
  async getHighRiskNews(params?: {
    page?: number;
    page_size?: number;
  }): Promise<{ items: News[]; total: number }> {
    return this.getNews({
      ...params,
      risk_level: 'high',
    });
  },

  // Поиск новостей по запросу
  async searchNews(query: string, params?: {
    page?: number;
    page_size?: number;
  }): Promise<{ items: News[]; total: number }> {
    return this.getNews({
      ...params,
      search: query,
    });
  },

  // ===== NOTIFICATION METHODS =====

  // Получить полную конфигурацию уведомлений
  async getNotificationConfig(): Promise<NotificationConfig> {
    try {
      const url = `${API_BASE}/notifications/config`;
      console.log('🔍 Fetching notification config from:', url);
      
      const res = await fetch(url, {
        headers: getAuthHeaders(),
      });
      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }
      
      const data = await res.json();
      console.log('✅ Loaded notification config');
      return data;
    } catch (error) {
      console.error('❌ Error fetching notification config:', error);
      throw error;
    }
  },

  // Получить настройки уведомлений
  async getNotificationSettings(): Promise<NotificationSettings> {
    try {
      const url = `${API_BASE}/notifications/settings`;
      const res = await fetch(url, {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return await res.json();
    } catch (error) {
      console.error('❌ Error fetching notification settings:', error);
      throw error;
    }
  },

  // Обновить настройки уведомлений
  async updateNotificationSettings(data: Partial<NotificationSettings>): Promise<NotificationSettings> {
    try {
      const url = `${API_BASE}/notifications/settings`;
      const res = await fetch(url, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return await res.json();
    } catch (error) {
      console.error('❌ Error updating notification settings:', error);
      throw error;
    }
  },

  // Получить триггеры уведомлений
  async getNotificationTriggers(): Promise<NotificationTrigger[]> {
    try {
      const url = `${API_BASE}/notifications/triggers`;
      const res = await fetch(url, {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return await res.json();
    } catch (error) {
      console.error('❌ Error fetching notification triggers:', error);
      throw error;
    }
  },

  // Создать триггер
  async createNotificationTrigger(data: Omit<NotificationTrigger, 'id' | 'created_at' | 'updated_at'>): Promise<NotificationTrigger> {
    try {
      const url = `${API_BASE}/notifications/triggers`;
      const res = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return await res.json();
    } catch (error) {
      console.error('❌ Error creating notification trigger:', error);
      throw error;
    }
  },

  // Обновить триггер
  async updateNotificationTrigger(id: number, data: Partial<NotificationTrigger>): Promise<NotificationTrigger> {
    try {
      const url = `${API_BASE}/notifications/triggers/${id}`;
      const res = await fetch(url, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return await res.json();
    } catch (error) {
      console.error('❌ Error updating notification trigger:', error);
      throw error;
    }
  },

  // Удалить триггер
  async deleteNotificationTrigger(id: number): Promise<void> {
    try {
      const url = `${API_BASE}/notifications/triggers/${id}`;
      const res = await fetch(url, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
    } catch (error) {
      console.error('❌ Error deleting notification trigger:', error);
      throw error;
    }
  },

  // Получить каналы уведомлений
  async getNotificationChannels(): Promise<NotificationChannel[]> {
    try {
      const url = `${API_BASE}/notifications/channels`;
      const res = await fetch(url, {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return await res.json();
    } catch (error) {
      console.error('❌ Error fetching notification channels:', error);
      throw error;
    }
  },

  // Создать канал
  async createNotificationChannel(data: Omit<NotificationChannel, 'id' | 'created_at' | 'updated_at'>): Promise<NotificationChannel> {
    try {
      const url = `${API_BASE}/notifications/channels`;
      const res = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return await res.json();
    } catch (error) {
      console.error('❌ Error creating notification channel:', error);
      throw error;
    }
  },

  // Обновить канал
  async updateNotificationChannel(id: number, data: Partial<NotificationChannel>): Promise<NotificationChannel> {
    try {
      const url = `${API_BASE}/notifications/channels/${id}`;
      const res = await fetch(url, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return await res.json();
    } catch (error) {
      console.error('❌ Error updating notification channel:', error);
      throw error;
    }
  },

  // Удалить канал
  async deleteNotificationChannel(id: number): Promise<void> {
    try {
      const url = `${API_BASE}/notifications/channels/${id}`;
      const res = await fetch(url, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
    } catch (error) {
      console.error('❌ Error deleting notification channel:', error);
      throw error;
    }
  },

  // Получить источники уведомлений
  async getNotificationSources(): Promise<NotificationSource[]> {
    try {
      const url = `${API_BASE}/notifications/sources`;
      const res = await fetch(url, {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return await res.json();
    } catch (error) {
      console.error('❌ Error fetching notification sources:', error);
      throw error;
    }
  },

  // Создать источник
  async createNotificationSource(data: Omit<NotificationSource, 'id' | 'created_at' | 'updated_at'>): Promise<NotificationSource> {
    try {
      const url = `${API_BASE}/notifications/sources`;
      const res = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return await res.json();
    } catch (error) {
      console.error('❌ Error creating notification source:', error);
      throw error;
    }
  },

  // Обновить источник
  async updateNotificationSource(id: number, data: Partial<NotificationSource>): Promise<NotificationSource> {
    try {
      const url = `${API_BASE}/notifications/sources/${id}`;
      const res = await fetch(url, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return await res.json();
    } catch (error) {
      console.error('❌ Error updating notification source:', error);
      throw error;
    }
  },

  // ===== AUTH METHODS =====

  // Вход
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    try {
      const url = `${API_BASE}/auth/login`;
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || `API error: ${res.status}`);
      }
      const data = await res.json();
      console.log('✅ Login successful');
      return data;
    } catch (error) {
      console.error('❌ Login error:', error);
      throw error;
    }
  },

  // Регистрация
  async register(data: RegisterRequest): Promise<UserDTO> {
    try {
      const url = `${API_BASE}/auth/register`;
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || `API error: ${res.status}`);
      }
      const user = await res.json();
      console.log('✅ Registration successful');
      return user;
    } catch (error) {
      console.error('❌ Registration error:', error);
      throw error;
    }
  },

  // Получить текущего пользователя
  async getCurrentUser(): Promise<UserDTO> {
    try {
      const url = `${API_BASE}/users/me`;
      const res = await fetch(url, {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return await res.json();
    } catch (error) {
      console.error('❌ Error fetching current user:', error);
      throw error;
    }
  },

  // Выход из системы
  logout(): void {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    console.log('✅ Logout successful');
  },

  // ===== ORGANIZATIONS AND PERSONS =====

  // Получить список всех организаций
  async getOrganizations(limit = 100): Promise<Entity[]> {
    try {
      const url = `${API_BASE}/entities?entity_type=ORG&limit=${limit}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      return Array.isArray(data) ? data : [];
    } catch (error) {
      console.error('❌ Error fetching organizations:', error);
      throw error;
    }
  },

  // Получить список всех персон
  async getPersons(limit = 100): Promise<Entity[]> {
    try {
      const url = `${API_BASE}/entities?entity_type=PER&limit=${limit}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      return Array.isArray(data) ? data : [];
    } catch (error) {
      console.error('❌ Error fetching persons:', error);
      throw error;
    }
  },

  // ===== USER REPORTS =====

  // Получить отчеты пользователя
  async getUserReports(): Promise<any[]> {
    // Если API недоступен, возвращаем пустой массив
    console.warn('⚠️ User reports API not implemented yet');
    return [];
  },

  // Удалить отчет
  async deleteReport(reportId: number): Promise<void> {
    // Если API недоступен, просто логируем предупреждение
    console.warn('⚠️ Delete report API not implemented yet');
    throw new Error('Delete report API not implemented');
  },
};