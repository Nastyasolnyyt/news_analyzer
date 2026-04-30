export type RiskLevel = 'high' | 'medium' | 'low';
export type EntityType = 'Company' | 'Person' | 'Event';
export type TrendDirection = 'up' | 'down' | 'flat';
export interface Entity {
    id: number;
    type: EntityType;
    name: string;
    description: string;
    jurisdiction?: string;
    identifiers?: {
        label: string;
        value: string;
    }[];
    registryInfo?: {
        address: string;
        registry: string;
        founded: string;
    };
    linkedEntityIds: number[];
    mentions?: {
        week: string;
        count: number;
        note?: string;
    }[];
    changePercent?: number;
    direction?: TrendDirection;
    category?: string;
}
export interface News {
    id: number;
    title: string;
    date: string;
    source: string;
    riskLevel: RiskLevel;
    relatedEntityIds: number[];
    summary: string;
    fullText: string[];
    tags?: string[];
}
export interface Report {
    id: number;
    name: string;
    criteria: {
        period: string;
        entities: string[];
        topics: string[];
    };
    newsIds: number[];
}
export declare const entities: Entity[];
export declare const news: News[];
export declare const reports: Report[];
export declare function getEntityById(id: number): Entity | undefined;
export declare function getNewsById(id: number): News | undefined;
export declare function getReportById(id: number): Report | undefined;
export declare function getEntitiesByIds(ids: number[]): Entity[];
export declare function getNewsByIds(ids: number[]): News[];
