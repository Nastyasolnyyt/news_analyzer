type RiskLevel = 'high' | 'medium' | 'low';
interface EventItem {
    id: number;
    title: string;
    date: string;
    source: string;
    summary: string;
    risk: RiskLevel;
    riskType?: string | null;
}
type __VLS_Props = {
    events: EventItem[];
};
declare const _default: import("vue").DefineComponent<__VLS_Props, {}, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {} & {
    "news-click": (id: number) => any;
}, string, import("vue").PublicProps, Readonly<__VLS_Props> & Readonly<{
    "onNews-click"?: ((id: number) => any) | undefined;
}>, {}, {}, {}, {}, string, import("vue").ComponentProvideOptions, false, {}, any>;
export default _default;
