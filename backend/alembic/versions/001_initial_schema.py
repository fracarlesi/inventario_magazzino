"""Initial schema with items and movements tables

Revision ID: 001
Revises:
Create Date: 2025-11-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    T009-T012: Create initial schema with:
    - PostgreSQL extensions (uuid-ossp, pg_trgm)
    - items table with CHECK constraints
    - movements table with CHECK constraints and FK
    - Performance indexes
    - current_stock view for computed stock
    """

    # T011: Enable PostgreSQL extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # T009: Create items table
    op.create_table(
        'items',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=False, server_default='pz'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('min_stock', sa.Numeric(precision=10, scale=3), nullable=False, server_default='0'),
        sa.Column('unit_cost', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('min_stock >= 0', name='chk_items_min_stock_positive'),
        sa.CheckConstraint('unit_cost >= 0', name='chk_items_unit_cost_positive'),
        sa.CheckConstraint('LENGTH(TRIM(name)) > 0', name='chk_items_name_not_empty'),
    )

    # T011: Create indexes for items
    op.create_index('idx_items_name_trgm', 'items', ['name'], unique=False, postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})
    op.create_index('idx_items_category', 'items', ['category'], unique=False)
    op.create_index('idx_items_created_at', 'items', ['created_at'], unique=False, postgresql_using='btree')

    # T010: Create movements table
    op.create_table(
        'movements',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('movement_type', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column('movement_date', sa.Date(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('unit_cost_override', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        # Validation constraints
        sa.CheckConstraint('quantity != 0', name='chk_movements_quantity_nonzero'),
        sa.CheckConstraint("movement_type IN ('IN', 'OUT', 'ADJUSTMENT')", name='chk_movements_type_valid'),
        sa.CheckConstraint("movement_type != 'IN' OR quantity > 0", name='chk_movements_in_positive'),
        sa.CheckConstraint("movement_type != 'OUT' OR quantity < 0", name='chk_movements_out_negative'),
        sa.CheckConstraint("movement_type != 'ADJUSTMENT' OR (note IS NOT NULL AND LENGTH(TRIM(note)) > 0)", name='chk_movements_adjustment_note'),
        sa.CheckConstraint('unit_cost_override IS NULL OR unit_cost_override >= 0', name='chk_movements_cost_positive'),
    )

    # T011: Create indexes for movements
    op.create_index('idx_movements_item_id', 'movements', ['item_id'], unique=False)
    op.create_index('idx_movements_timestamp', 'movements', ['timestamp'], unique=False, postgresql_using='btree', postgresql_ops={'timestamp': 'DESC'})
    op.create_index('idx_movements_movement_date', 'movements', ['movement_date'], unique=False, postgresql_using='btree')
    op.create_index('idx_movements_type', 'movements', ['movement_type'], unique=False)
    op.create_index('idx_movements_item_date', 'movements', ['item_id', 'movement_date'], unique=False, postgresql_using='btree', postgresql_ops={'movement_date': 'DESC'})

    # T012: Create current_stock view (computed from movements)
    op.execute("""
        CREATE VIEW current_stock AS
        SELECT
            i.id AS item_id,
            i.name,
            i.category,
            i.unit,
            i.min_stock,
            i.unit_cost,
            COALESCE(SUM(m.quantity), 0) AS stock_quantity,
            COALESCE(SUM(m.quantity), 0) * i.unit_cost AS stock_value,
            (COALESCE(SUM(m.quantity), 0) < i.min_stock) AS is_under_min_stock,
            MAX(m.timestamp) AS last_movement_at
        FROM items i
        LEFT JOIN movements m ON m.item_id = i.id
        GROUP BY i.id, i.name, i.category, i.unit, i.min_stock, i.unit_cost
    """)


def downgrade() -> None:
    """Rollback migration."""
    # Drop view
    op.execute('DROP VIEW IF EXISTS current_stock')

    # Drop movements table (cascade will drop indexes)
    op.drop_table('movements')

    # Drop items table (cascade will drop indexes)
    op.drop_table('items')

    # Drop extensions
    op.execute('DROP EXTENSION IF EXISTS "pg_trgm"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
