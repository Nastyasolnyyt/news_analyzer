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
export interface CreateEntityDTO {
    name: string;
    entity_type: string;
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
    getNotificationConfig(): Promise<NotificationConfig>;
    getNotificationSettings(): Promise<NotificationSettings>;
    updateNotificationSettings(data: Partial<NotificationSettings>): Promise<NotificationSettings>;
    getNotificationTriggers(): Promise<NotificationTrigger[]>;
    createNotificationTrigger(data: Omit<NotificationTrigger, "id" | "created_at" | "updated_at">): Promise<NotificationTrigger>;
    updateNotificationTrigger(id: number, data: Partial<NotificationTrigger>): Promise<NotificationTrigger>;
    deleteNotificationTrigger(id: number): Promise<void>;
    getNotificationChannels(): Promise<NotificationChannel[]>;
    createNotificationChannel(data: Omit<NotificationChannel, "id" | "created_at" | "updated_at">): Promise<NotificationChannel>;
    updateNotificationChannel(id: number, data: Partial<NotificationChannel>): Promise<NotificationChannel>;
    deleteNotificationChannel(id: number): Promise<void>;
    getNotificationSources(): Promise<NotificationSource[]>;
    createNotificationSource(data: Omit<NotificationSource, "id" | "created_at" | "updated_at">): Promise<NotificationSource>;
    updateNotificationSource(id: number, data: Partial<NotificationSource>): Promise<NotificationSource>;
    sendTestEmail(): Promise<{
        message: string;
        to: string;
        status: string;
    }>;
    login(credentials: LoginRequest): Promise<TokenResponse>;
    register(data: RegisterRequest): Promise<UserDTO>;
    getCurrentUser(): Promise<UserDTO>;
    logout(): void;
    createEntity(data: CreateEntityDTO): Promise<NamedEntity>;
    getOrganizations(limit?: number): Promise<Entity[]>;
    getPersons(limit?: number): Promise<Entity[]>;
    getUserReports(): Promise<any[]>;
    deleteReport(reportId: number): Promise<void>;
};
