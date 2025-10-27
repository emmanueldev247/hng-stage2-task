import sqlalchemy as sa
import unicodedata
from alembic import op
from sqlalchemy import select, update
from sqlalchemy.sql import table, column

revision = "424c95a902ee"
down_revision = "9de61a44c5d0"
branch_labels = None
depends_on = None

def _norm(s: str | None) -> str | None:
    if s is None:
        return None
    return unicodedata.normalize("NFKC", s).casefold()

def _has_column(table_name: str, col_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = [c["name"] for c in insp.get_columns(table_name)]
    return col_name in cols

def upgrade():
    if not _has_column("countries", "name_key"):
        op.add_column("countries", sa.Column("name_key", sa.String(length=512), nullable=True))

    countries = table(
        "countries",
        column("id", sa.Integer),
        column("name", sa.String),
        column("name_key", sa.String),
    )

    conn = op.get_bind()
    rows = conn.execute(select(countries.c.id, countries.c.name)).fetchall()
    for nid, name in rows:
        conn.execute(
            update(countries)
            .where(countries.c.id == nid)
            .values(name_key=_norm(name))
        )

    with op.batch_alter_table("countries", recreate="always") as batch_op:
        batch_op.alter_column("name_key", existing_type=sa.String(length=512), nullable=False)
