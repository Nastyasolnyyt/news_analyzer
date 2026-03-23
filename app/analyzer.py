import pandas as pd
from sqlalchemy import text
from datetime import datetime, timedelta

class AnomalyAnalyzer:
    def __init__(self, engine):
        self.engine = engine

    def _load(self, query, params=None):
        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)

    # всплеск упоминаний
    def analyze_entity_mentions(self, days, threshold):
        start_date = datetime.now() - timedelta(days=days)
        query = """
            SELECT DATE(a.pub_date) as day, e.text as name, MIN(e.id) as e_id, MIN(a.id) as a_id, COUNT(e.id) as cnt
            FROM entities e JOIN articles a ON e.article_id = a.id
            WHERE a.pub_date >= :sd GROUP BY DATE(a.pub_date), e.text
        """
        df = self._load(query, {'sd': start_date})
        results = []
        if df.empty: return results

        for name, group in df.groupby("name"):
            if len(group) < 3: continue
            mean, std = group['cnt'].mean(), group['cnt'].std()
            if std > 0:
                group['z'] = (group['cnt'] - mean) / std
                for _, row in group[abs(group['z']) > threshold].iterrows():
                    results.append({
                        'article_id': int(row['a_id']),
                        'entity_id': int(row['e_id']),
                        'anomaly_type': 'mention_spike',
                        'description': f"[{row['day']}] Всплеск '{name}': {row['cnt']} уп.",
                        'score': float(abs(row['z'])),
                        'severity': 'high' if abs(row['z']) > 3 else 'medium'
                    })
        return results
    
    # IQR по рискам
    def analyze_risk_distribution(self, days):
        start_date = datetime.now() - timedelta(days=days)
        query = """
            SELECT DATE(created_at) as day, risk_type, MIN(article_id) as a_id, COUNT(*) as cnt 
            FROM risks WHERE created_at >= :sd GROUP BY DATE(created_at), risk_type
        """
        df = self._load(query, {'sd': start_date})
        results = []
        if df.empty: return results

        for r_type, group in df.groupby("risk_type"):
            if len(group) < 5: continue
            q1, q3 = group['cnt'].quantile([0.25, 0.75])
            upper = q3 + 1.5 * (q3 - q1)
            for _, row in group[group['cnt'] > upper].iterrows():
                results.append({
                    'article_id': int(row['a_id']) if pd.notnull(row['a_id']) else None,
                    'risk_type': r_type,
                    'anomaly_type': 'risk_outlier',
                    'description': f"[{row['day']}] Рост риска '{r_type}': {row['cnt']} за день",
                    'score': 0.8,
                    'severity': 'high'
                })
        return results

    # новые отношения сущностей (нетипичные связи)
    def analyze_unusual_pairs(self):
        query = """
            SELECT er.entity1_id, er.entity2_id, er.article_id, e1.text as n1, e2.text as n2
            FROM entity_relations er
            JOIN entities e1 ON er.entity1_id = e1.id
            JOIN entities e2 ON er.entity2_id = e2.id
            WHERE er.created_at >= NOW() - INTERVAL '1 day'
        """
        new_pairs = self._load(query)
        results = []
        if new_pairs.empty: return results

        for _, row in new_pairs.iterrows():
            check_query = "SELECT COUNT(*) FROM entity_relations WHERE entity1_id = :e1 AND entity2_id = :e2 AND created_at < NOW() - INTERVAL '1 day'"
            with self.engine.connect() as conn:
                count = conn.execute(text(check_query), {'e1': row['entity1_id'], 'e2': row['entity2_id']}).scalar()
            
            if count == 0:
                results.append({
                    'article_id': int(row['article_id']),
                    'anomaly_type': 'unusual_pair',
                    'description': f"Новая связь: {row['n1']} + {row['n2']}",
                    'score': 0.9,
                    'severity': 'medium'
                })
        return results

    # смена тональности
    def analyze_sentiment_shifts(self):
        query = """
            SELECT e.text as name, s.sentiment_label, a.pub_date, a.id as art_id, e.id as ent_id
            FROM sentiments s
            JOIN articles a ON s.article_id = a.id
            JOIN entities e ON e.article_id = a.id
            WHERE a.pub_date >= NOW() - INTERVAL '7 days'
        """
        df = self._load(query)
        results = []
        if df.empty: return results

        for name, group in df.groupby("name"):
            today = group[group['pub_date'] >= datetime.now() - timedelta(days=1)]
            past = group[group['pub_date'] < datetime.now() - timedelta(days=1)]
            
            if not today.empty and not past.empty:
                today_neg = (today['sentiment_label'] == 'negative').mean()
                past_neg = (past['sentiment_label'] == 'negative').mean()
                
                if today_neg > past_neg + 0.5:
                    results.append({
                        'article_id': int(today.iloc[0]['art_id']),
                        'entity_id': int(today.iloc[0]['ent_id']),
                        'anomaly_type': 'sentiment_shift',
                        'description': f"Резкий негатив по '{name}'",
                        'score': 0.7,
                        'severity': 'high'
                    })
        return results