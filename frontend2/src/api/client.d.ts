export type RiskLevel = 'high' | 'medium' | 'low';
export interface PostAnalysis {
    id?: number;
    post_id: number;
    topic_id?: number | null;
    emotion?: number;
    tonality?: number;
    relevance?: number;
    sentiment_label?: 'positive' | 'negative' | 'neutral' | string;
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
    risk_level?: RiskLevel;
    risk?: RiskLevel;
    risk_type?: 'политический' | 'экономический' | 'социальный';
    risk_confidence?: number;
    risk_type_confidence?: number;
    tonality?: number;
    sentiment_label?: 'positive' | 'negative' | 'neutral';
    emotion?: number;
    relevance?: number;
    confidence?: number;
    topic_name?: string;
    topic_id?: number;
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
    identifiers?: Array<{
        label: string;
        value: string;
    }>;
    registryInfo?: {
        address: string;
        registry: string;
        founded: string;
    };
    linkedEntityIds?: number[];
    mentions?: Array<{
        week: string;
        count: number;
        note?: string;
    }>;
}
export interface NewsResponse {
    post: News;
    analysis?: PostAnalysis & {
        topic?: Topic;
    };
    entities: NamedEntity[];
}
export interface NewsListResponse {
    items: (News | NewsResponse)[];
    total: number;
    page: number;
    page_size: number;
}
export declare const api: {
    getNews(params?: {
        page?: number;
        page_size?: number;
        risk_level?: string;
        risk_type?: string;
        source?: string;
        search?: string;
    }): Promise<{
        items: News[];
        total: number;
    }>;
    getNewsById(id: number): Promise<News>;
    getEntityMentions(entityId: number, params?: {
        start?: string;
        end?: string;
    }): Promise<any[]>;
    getEntityProfile(entityId: number): Promise<{
        entity: Entity;
        mentions: any[];
        chartData: Array<{
            week: string;
            count: number;
            note?: string;
        }>;
        relatedEntities: Array<{
            id: number;
            name: string;
            type: string;
            relation: string;
        }>;
        news: News[];
    }>;
    getTopEntities24h(params?: {
        limit?: number;
    }): Promise<Array<{
        id: number;
        name: string;
        entity_type: string;
        changePercent: number;
        direction: "up" | "down" | "flat";
        category: string;
    }>>;
    getEntities(params?: {
        limit?: number;
    }): Promise<Array<Entity & {
        recentMentions: number;
        previousMentions: number;
        topicCount: number;
    }>>;
    getEntityById(id: number): Promise<Entity>;
    getEntitiesByIds(ids: number[]): Promise<Entity[]>;
    getHighRiskNews(params?: {
        page?: number;
        page_size?: number;
    }): Promise<{
        items: News[];
        total: number;
    }>;
    searchNews(query: string, params?: {
        page?: number;
        page_size?: number;
    }): Promise<{
        items: News[];
        total: number;
    }>;
};
