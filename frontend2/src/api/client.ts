// frontend/src/api/client.ts
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8003/api/v1';

export type RiskLevel = 'high' | 'medium' | 'low';

export interface PostAnalysis {
  id?: number;
  post_id: number;
  topic_id?: number | null;
  emotion?: number;
  tonality?: number;
  relevance?: number;
  sentiment_label?: string;
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
  
  // Для совместимости и отображения
  risk_level?: RiskLevel;
  risk?: RiskLevel;
  risk_type?: 'политический' | 'экономический' | 'социальный';
  tonality?: number;
  sentiment_label?: 'positive' | 'negative' | 'neutral';
  topic_name?: string;
  topic_id?: number;
  emotion?: number;
  relevance?: number;
  
  // Для расширенного использования
  relatedEntityIds?: number[];
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

export const api = {
  // Получить список новостей
  async getNews(params?: {
    page?: number;
    page_size?: number;
    risk_level?: string;
    source?: string;
    search?: string;
  }): Promise<{ items: News[]; total: number }> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params?.page) queryParams.append('page', String(params.page));
      if (params?.page_size) queryParams.append('page_size', String(params.page_size));
      if (params?.search) queryParams.append('search', params.search);
      if (params?.risk_level) queryParams.append('risk_level', params.risk_level);
      if (params?.source) queryParams.append('source', params.source);

      const qs = queryParams.toString();
      const url = `${API_BASE}/posts${qs ? '?' + qs : ''}`;
      
      console.log('🔍 Fetching posts from:', url);
      
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`API error: ${res.status} ${res.statusText}`);
      }
      
      const data = await res.json();
      
      // Нормализуем данные: если приходит { post, analysis, entities }, извлекаем post
      const items = Array.isArray(data.items) 
        ? data.items.map((item: any) => item.post || item)
        : [];
      
      console.log('✅ Loaded news:', items.length);
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
      const newsItem = data.post || data;
      
      // Добавляем анализ если есть
      if (data.analysis) {
        newsItem.tonality = data.analysis.tonality;
        newsItem.sentiment_label = data.analysis.sentiment_label;
        newsItem.emotion = data.analysis.emotion;
        newsItem.relevance = data.analysis.relevance;
        if (data.analysis.topic) {
          newsItem.topic_name = data.analysis.topic.name;
          newsItem.topic_id = data.analysis.topic.id;
        }
      }
      
      // Добавляем связанные сущности
      if (data.entities) {
        newsItem.relatedEntityIds = data.entities.map((e: any) => e.id);
      }
      
      console.log('✅ Loaded post:', newsItem.id);
      return newsItem;
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

  // Получить список сущностей (фиксированный список из темы или поиск)
  async getEntities(): Promise<Entity[]> {
    // Это заглушка, т.к. бэкенд не предоставляет публичный endpoint для списка всех сущностей
    // В реальном приложении можно использовать упоминания из постов
    return [];
  },

  // Получить сущность по ID через упоминания
  async getEntityById(id: number): Promise<Entity> {
    try {
      // Используем endpoint упоминаний, чтобы получить информацию о сущности
      const mentions = await this.getEntityMentions(id);
      
      if (mentions.length === 0 || !mentions[0].entity) {
        throw new Error(`Entity ${id} not found`);
      }
      
      const entity = mentions[0].entity;
      return {
        id: entity.id,
        name: entity.name,
        type: 'Company', // можно определить по entity_type
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
};