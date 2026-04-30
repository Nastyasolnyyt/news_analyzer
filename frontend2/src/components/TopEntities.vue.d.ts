type TrendDirection = 'up' | 'down' | 'flat';
interface EntityTrend {
    id: number;
    name: string;
    changePercent: number;
    direction: TrendDirection;
    category: string;
}
type __VLS_Props = {
    entities: EntityTrend[];
};
declare const _default: import("vue").DefineComponent<__VLS_Props, {}, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {} & {
    "entity-click": (id: number) => any;
}, string, import("vue").PublicProps, Readonly<__VLS_Props> & Readonly<{
    "onEntity-click"?: ((id: number) => any) | undefined;
}>, {}, {}, {}, {}, string, import("vue").ComponentProvideOptions, false, {}, any>;
export default _default;
