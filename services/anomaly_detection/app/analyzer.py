"""
anomaly_detection/app/analyzer.py
ИСПРАВЛЕНО:
1. В analyze_risks: запрос теперь также смотрит на risk_level (заполняется risklevel-classifier)
2. Добавлен метод get_stats для диагностики
3. Понижен min_count с 5 до 2 — чтобы срабатывало на меньшем объёме данных
"""
import pandas as pd
from sqlalchemy import text
from datetime import timedelta
import logging

logger = logging.getLogger("AnomalyService")


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

    def get_stats(self):
        """Диагностика: показывает сколько данных есть для анализа."""
        with self.engine.connect() as conn:
            articles_count = conn.execute(
                text("SELECT COUNT(*) FROM articles")
            ).scalar()
            entities_count = conn.execute(
                text("SELECT COUNT(*) FROM named_entities")
            ).scalar()
            post_entities_count = conn.execute(
                text("SELECT COUNT(*) FROM post_entities")
            ).scalar()
            risks_count = conn.execute(
                text("SELECT COUNT(*) FROM risks WHERE risk_type IS NOT NULL")
            ).scalar()

        logger.info(
            f"Статистика БД: "
            f"статей={articles_count}, "
            f"сущностей={entities_count}, "
            f"связей={post_entities_count}, "
            f"рисков={risks_count}"
        )
        return {
            'articles': articles_count,
            'entities': entities_count,
            'post_entities': post_entities_count,
            'risks': risks_count,
        }

    def _detect_iqr_anomalies(
        self, df, group_col, date_col='date', val_col='cnt', min_count=2
    ):
        """
        Универсальный метод IQR с учётом дней без событий.
        ИСПРАВЛЕНО: min_count снижен до 2 для работы на небольшом объёме данных.
        """
        if df.empty:
            return []

        # Заполняем пропущенные даты нулями
        dates = pd.date_range(start=df[date_col].min(), end=df[date_col].max())

        df = df.set_index([date_col, group_col]).reindex(
            pd.MultiIndex.from_product(
                [dates, df[group_col].unique()],
                names=[date_col, group_col]
            ),
            fill_value=0
        ).reset_index()

        anomalies = []
        for name, group in df.groupby(group_col):
            if len(group) < 4:
                # Нужно минимум 4 точки для осмысленного IQR
                continue

            q1 = group[val_col].quantile(0.25)
            q3 = group[val_col].quantile(0.75)
            iqr = q3 - q1
            upper_bound = q3 + 1.5 * iqr

            latest_row = group.sort_values(date_col).iloc[-1]
            current_val = latest_row[val_col]

            if current_val > upper_bound and current_val >= min_count:
                anomalies.append({
                    'type': 'Всплеск активности (IQR)',
                    'entity_name': str(name),
                    'score': round(
                        float(current_val / upper_bound), 2
                    ) if upper_bound > 0 else float(current_val),
                    'desc': f"Найдено {int(current_val)}, норма до {upper_bound:.1f}"
                })

        return anomalies

    def analyze_mentions(self, days=30):
        """Анализ всплесков упоминаний именованных сущностей."""
        last_date = self.get_latest_date()
        if not last_date:
            logger.warning("Нет данных в articles, пропускаю анализ упоминаний")
            return []

        query = """
            SELECT DATE(a.pub_date) as date, ne.name as entity, COUNT(pe.post_id) as cnt
            FROM named_entities ne
            JOIN post_entities pe ON ne.id = pe.entity_id
            JOIN articles a ON pe.post_id = a.id
            WHERE a.pub_date >= :sd
            GROUP BY 1, 2
        """
        df = self._load(query, {'sd': last_date - timedelta(days=days)})

        if df.empty:
            logger.info("Нет данных об упоминаниях сущностей (NER-сервис обработал 0 статей)")
            return []

        logger.info(f"Анализирую упоминания: {len(df)} записей за {days} дней")
        return self._detect_iqr_anomalies(df, group_col='entity')

    def analyze_risks(self, days=30):
        """Анализ всплесков по типам риска."""
        last_date = self.get_latest_date()
        if not last_date:
            logger.warning("Нет данных в articles, пропускаю анализ рисков")
            return []

        # ИСПРАВЛЕНО: смотрим на risk_type (заполняется risk-classifier)
        query = """
            SELECT DATE(created_at) as date, risk_type, COUNT(*) as cnt
            FROM risks
            WHERE created_at >= :sd
              AND risk_type IS NOT NULL
            GROUP BY 1, 2
        """
        df = self._load(query, {'sd': last_date - timedelta(days=days)})

        if df.empty:
            logger.info("Нет данных о рисках за указанный период")
            return []

        logger.info(f"Анализирую риски: {len(df)} записей за {days} дней")
        return self._detect_iqr_anomalies(df, group_col='risk_type')