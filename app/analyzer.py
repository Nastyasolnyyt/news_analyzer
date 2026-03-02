import pandas as pd
from sqlalchemy import text
from datetime import datetime, timedelta

# использовать logger можно следующим образом: logger.info("Сообщение об информации"), logger.error("Сообщение об ошибке") и т.д. 
# - для отслеживания работы алгоритмов и выявления проблем при выполнении запросов к БД или при анализе данных.

class AnomalyAnalyzer:
    def __init__(self, engine):
        self.engine = engine

    def _load(self, query, params):
        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)

    # Z-Score для упоминаний сущностей: выявляем дни, когда упоминания конкретной сущности резко выросли по сравнению с ее обычным уровнем за последние N дней.
    def analyze_entity_mentions(self, days, threshold):
        start_date = datetime.now() - timedelta(days=days)
        query = """
            SELECT DATE(a.pub_date) as day, e.text as name, MIN(e.id) as e_id, COUNT(e.id) as cnt
            FROM entities e JOIN articles a ON e.article_id = a.id
            WHERE a.pub_date >= :sd GROUP BY DATE(a.pub_date), e.text
        """
        df = self._load(query, {'sd': start_date})
        results = []
        
        if df.empty: return results

        for name, group in df.groupby("name"):
            # !!! поменять обратно на 3
            if len(group) < 3: continue
            mean = group['cnt'].mean()
            std = group['cnt'].std()
            if std > 0:
                group['z'] = (group['cnt'] - mean) / std
                for _, row in group[abs(group['z']) > threshold].iterrows():
                    results.append({
                        'entity_id': int(row['e_id']),
                        'anomaly_type': 'entity_spike',
                        'description': f"Всплеск '{name}': {row['cnt']} уп. (норма {mean:.1f})",
                        'score': float(abs(row['z'])),
                        'severity': 'high' if abs(row['z']) > 3 else 'medium'
                    })
        return results

    # IQR для рисков: выявляем дни, когда количество упоминаний конкретного риска резко выросло по сравнению с его обычным уровнем за последние N дней.(IQR)
    def analyze_risk_distribution(self, days):
        start_date = datetime.now() - timedelta(days=days)
        query = """
            SELECT DATE(created_at) as day, risk_type, COUNT(*) as cnt
            FROM risks WHERE created_at >= :sd GROUP BY DATE(created_at), risk_type
        """
        df = self._load(query, {'sd': start_date})
        results = []

        for r_type, group in df.groupby("risk_type"):
            # !!! поменять обратно на 5
            if len(group) < 5: continue
            q1, q3 = group['cnt'].quantile([0.25, 0.75])
            upper = q3 + 1.5 * (q3 - q1)
            for _, row in group[group['cnt'] > upper].iterrows():
                results.append({
                    'risk_type': r_type,
                    'anomaly_type': 'risk_outlier',
                    'description': f"Рост риска '{r_type}': {row['cnt']} за день",
                    'score': 0.8,
                    'severity': 'high'
                })
        return results