"""rename posts to articles and add risk table

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-03-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: rename posts to articles, add risk table."""
    # 1. Add new columns to posts before renaming
    op.add_column('posts', sa.Column('link', sa.Text(), nullable=True))
    op.add_column('posts', sa.Column('pub_date', sa.DateTime(), nullable=True))
    op.add_column('posts', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('posts', sa.Column('text', sa.Text(), nullable=True))
    
    # 2. Migrate content to text if text is null
    op.execute("""
        UPDATE posts 
        SET text = content 
        WHERE text IS NULL
    """)
    
    # 3. Make text NOT NULL
    op.alter_column('posts', 'text', nullable=False)
    
    # 4. Drop content column (no longer needed)
    op.drop_column('posts', 'content')
    
    # 5. Drop author column (not needed for articles)
    op.drop_column('posts', 'author')
    
    # 6. Rename posts table to articles
    op.rename_table('posts', 'articles')
    
    # 7. Rename foreign key constraints in post_analysis
    op.drop_constraint('post_analysis_post_id_fkey', 'post_analysis', type_='foreignkey')
    op.create_foreign_key(
        'post_analysis_post_id_fkey',
        'post_analysis',
        'articles',
        ['post_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # 8. Rename foreign key constraints in post_entities
    op.drop_constraint('post_entities_post_id_fkey', 'post_entities', type_='foreignkey')
    op.create_foreign_key(
        'post_entities_post_id_fkey',
        'post_entities',
        'articles',
        ['post_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # 9. Create risks table
    op.create_table(
        'risks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('risk_type', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 10. Create index on article_id for risks table
    op.create_index('ix_risks_article_id', 'risks', ['article_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop risks table
    op.drop_index('ix_risks_article_id', table_name='risks')
    op.drop_table('risks')
    
    # Rename articles back to posts
    op.rename_table('articles', 'posts')
    
    # Restore foreign key constraints
    op.drop_constraint('post_analysis_post_id_fkey', 'post_analysis', type_='foreignkey')
    op.create_foreign_key(
        'post_analysis_post_id_fkey',
        'post_analysis',
        'posts',
        ['post_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    op.drop_constraint('post_entities_post_id_fkey', 'post_entities', type_='foreignkey')
    op.create_foreign_key(
        'post_entities_post_id_fkey',
        'post_entities',
        'posts',
        ['post_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Restore columns
    op.add_column('posts', sa.Column('author', sa.String(length=255), nullable=False, server_default='unknown'))
    op.add_column('posts', sa.Column('content', sa.Text(), nullable=False))
    
    # Migrate text back to content
    op.execute("""
        UPDATE posts 
        SET content = text 
        WHERE content IS NULL
    """)
    
    # Remove new columns
    op.drop_column('posts', 'text')
    op.drop_column('posts', 'updated_at')
    op.drop_column('posts', 'pub_date')
    op.drop_column('posts', 'link')
