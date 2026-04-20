import pandas as pd
from sqlalchemy import text
from datetime import timedelta

class AnomalyAnalyzer:
    def __init__(self, engine):
        self.engine = engine

    def _load(self, query, params=None):
        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)

    def get_latest_date(self):
        query = "SELECT MAX(pub_date) FROM articles"
        with self.engine.connect() as conn:
            return conn.execute(text(query)).scalar()

    def _detect_iqr_anomalies(self, df, group_col, date_col='date', val_col='cnt', min_count=5):
        """Универсальный метод IQR с учетом дней без событий."""
        if df.empty: return []

        # Заполняем пропущенные даты нулями для корректной статистики
        dates = pd.date_range(start=df[date_col].min(), end=df[date_col].max())
        
        df = df.set_index([date_col, group_col]).reindex(
            pd.MultiIndex.from_product([dates, df[group_col].unique()], names=[date_col, group_col]),
            fill_value=0
        ).reset_index()

        anomalies = []
        for name, group in df.groupby(group_col):
            q1 = group[val_col].quantile(0.25)
            q3 = group[val_col].quantile(0.75)
            iqr = q3 - q1
            upper_bound = q3 + 1.5 * iqr
            
            # Проверяем только последнюю актуальную дату
            latest_row = group.sort_values(date_col).iloc[-1]
            current_val = latest_row[val_col]
            
            if current_val > upper_bound and current_val >= min_count:
                anomalies.append({
                    'type': 'Всплеск активности (IQR)',
                    'entity_name': str(name),
                    'score': round(float(current_val / upper_bound), 2) if upper_bound > 0 else current_val,
                    'desc': f"Найдено {int(current_val)}, норма до {upper_bound:.1f}"
                })
        return anomalies

    def analyze_mentions(self, days=30):
        last_date = self.get_latest_date()
        if not last_date: return []
        
        query = """
            SELECT DATE(a.pub_date) as date, ne.name as entity, COUNT(pe.post_id) as cnt
            FROM named_entities ne
            JOIN post_entities pe ON ne.id = pe.entity_id
            JOIN articles a ON pe.post_id = a.id
            WHERE a.pub_date >= :sd
            GROUP BY 1, 2
        """
        df = self._load(query, {'sd': last_date - timedelta(days=days)})
        return self._detect_iqr_anomalies(df, group_col='entity')

    def analyze_risks(self, days=30):
        last_date = self.get_latest_date()
        if not last_date: return []
        
        query = """
            SELECT DATE(created_at) as date, risk_type, COUNT(*) as cnt
            FROM risks
            WHERE created_at >= :sd
            GROUP BY 1, 2
        """
        df = self._load(query, {'sd': last_date - timedelta(days=days)})
        return self._detect_iqr_anomalies(df, group_col='risk_type')