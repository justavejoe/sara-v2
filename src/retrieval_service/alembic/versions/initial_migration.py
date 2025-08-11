"""Initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2025-08-11 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
# Import VectorType for pgvector support in migrations
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # Create documents table
    op.create_table('documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('authors', sa.Text(), nullable=True),
        sa.Column('publication_date', sa.String(length=50), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        # Ensure the dimension matches the embedding model (768 for text-embedding-004)
        sa.Column('embedding', Vector(dim=768), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    # Drop documents table
    op.drop_table('documents')
    
    # Disable pgvector extension (optional)
    # op.execute("DROP EXTENSION IF EXISTS vector")