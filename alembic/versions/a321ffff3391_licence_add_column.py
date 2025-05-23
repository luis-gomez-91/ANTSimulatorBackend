"""Licence add column

Revision ID: a321ffff3391
Revises: c6294661b1a4
Create Date: 2025-04-29 12:58:44.781336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a321ffff3391'
down_revision: Union[str, None] = 'c6294661b1a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('licence_types', sa.Column('enable', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('licence_types', 'enable')
    # ### end Alembic commands ###
