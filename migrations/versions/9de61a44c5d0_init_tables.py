"""init tables

Revision ID: 9de61a44c5d0
Revises: 
Create Date: 2025-10-26 01:03:02.335446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9de61a44c5d0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=191), nullable=False),
        sa.Column("capital", sa.String(length=191), nullable=True),
        sa.Column("region", sa.String(length=64), nullable=True),
        sa.Column("population", sa.BigInteger(), nullable=False),
        sa.Column("currency_code", sa.String(length=16), nullable=True),
        sa.Column("exchange_rate", sa.Float(), nullable=True),
        sa.Column("estimated_gdp", sa.Float(), nullable=True),
        sa.Column("flag_url", sa.String(length=512), nullable=True),
        sa.Column("last_refreshed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_countries_name", "countries", ["name"], unique=True)
    op.create_index("ix_countries_last_refreshed_at", "countries", ["last_refreshed_at"], unique=False)

    op.create_table(
        "meta_cache",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("last_refreshed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_table("meta_cache")
    op.drop_index("ix_countries_last_refreshed_at", table_name="countries")
    op.drop_index("ix_countries_name", table_name="countries")
    op.drop_table("countries")
