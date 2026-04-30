type RiskLevel = 'high' | 'medium' | 'low';
interface LegendItem {
    level: RiskLevel;
    label: string;
    description: string;
}
type __VLS_Props = {
    levels: LegendItem[];
};
declare const _default: import("vue").DefineComponent<__VLS_Props, {}, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {}, string, import("vue").PublicProps, Readonly<__VLS_Props> & Readonly<{}>, {}, {}, {}, {}, string, import("vue").ComponentProvideOptions, false, {}, any>;
export default _default;
