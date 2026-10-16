"""add_missing_indexes

Revision ID: 4c947237d0bc
Revises: 02b478656721
Create Date: 2026-10-16 11:20:14.733760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c947237d0bc'
down_revision: Union[str, Sequence[str], None] = '02b478656721'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(op.f('ix_notificaciones_perfil_id'), 'notificaciones', ['perfil_id'], unique=False, postgresql_concurrently=True, if_not_exists=True)
        op.create_index('idx_oferta_fecha', 'precios_historicos', ['oferta_id', 'fecha'], unique=False, postgresql_concurrently=True, if_not_exists=True)
        op.drop_index(op.f('ix_productos_slug'), table_name='productos', postgresql_concurrently=True, if_exists=True)
        op.create_index(op.f('ix_productos_slug'), 'productos', ['slug'], unique=True, postgresql_concurrently=True, if_not_exists=True)


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(op.f('ix_productos_slug'), table_name='productos', postgresql_concurrently=True, if_exists=True)
        op.create_index(op.f('ix_productos_slug'), 'productos', ['slug'], unique=False, postgresql_concurrently=True, if_not_exists=True)
        op.drop_index('idx_oferta_fecha', table_name='precios_historicos', postgresql_concurrently=True, if_exists=True)
        op.drop_index(op.f('ix_notificaciones_perfil_id'), table_name='notificaciones', postgresql_concurrently=True, if_exists=True)
