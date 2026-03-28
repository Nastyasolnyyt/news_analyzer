"""
alembic/versions/xxx_update_risks_with_levels.py
Миграция для добавления полей risk_level и risk_type_confidence
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'g8h9i0j1k2l3'
down_revision = 'f5f6g7h8i9j0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema: добавляем разделение risk_level и risk_type"""
    
    # 1. Добавляем поле risk_level (уровень: high/medium/low от risklevel-classifier)
    op.add_column(
        'risks',
        sa.Column('risk_level', sa.String(), nullable=True)
    )
    
    # 2. Переименовываем confidence в risk_confidence (уверенность уровня)
    # Сначала добавляем новую колонку
    op.add_column(
        'risks',
        sa.Column('risk_confidence', sa.Float(), nullable=True)
    )
    
    # 3. Копируем данные из confidence в risk_confidence (если confidence заполнена)
    op.execute("""
        UPDATE risks 
        SET risk_confidence = confidence 
        WHERE confidence IS NOT NULL
    """)
    
    # 4. Добавляем поле для уверенности типа риска
    op.add_column(
        'risks',
        sa.Column('risk_type_confidence', sa.Float(), nullable=True)
    )
    
    # 5. Обновляем существующие risk_type в risk_level если они там есть
    # (переводим политический/экономический/социальный в низ)
    op.execute("""
        UPDATE risks 
        SET risk_type = risk_type,
            risk_level = 'low'
        WHERE risk_type IS NOT NULL 
        AND risk_level IS NULL
    """)
    
    # 6. Создаём уникальный индекс на article_id если его нет
    try:
        op.create_unique_constraint(
            'uq_risks_article_id',
            'risks',
            ['article_id']
        )
    except:
        pass  # Индекс уже существует


def downgrade() -> None:
    """Downgrade schema"""
    
    # Копируем данные обратно
    op.execute("""
        UPDATE risks 
        SET confidence = risk_confidence 
        WHERE risk_confidence IS NOT NULL
    """)
    
    # Удаляем новые колонки
    op.drop_column('risks', 'risk_type_confidence')
    op.drop_column('risks', 'risk_confidence')
    op.drop_column('risks', 'risk_level')
    
    # Удаляем индекс
    try:
        op.drop_constraint('uq_risks_article_id', 'risks', type_='unique')
    except:
        pass