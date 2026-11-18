"""add_pg_trgm_extension

Revision ID: e1b2c3d4e5f6
Revises: 4c947237d0bc
Create Date: 2026-11-18 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '4c947237d0bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Habilita la extensión pg_trgm de forma idempotente en PostgreSQL."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def downgrade() -> None:
    """No eliminamos pg_trgm automáticamente en downgrade por seguridad
    ante posibles dependencias compartidas de índices o funciones."""
    pass
