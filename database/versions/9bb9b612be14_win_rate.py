"""add created_by fields

Revision ID: 9bb9b612be14
Revises: e338207ef60a
Create Date: 2023-06-12 22:08:06.013868

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "9bb9b612be14"
down_revision = "e338207ef60a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    statements = """
    ALTER TABLE players
        ADD games_won REAL;
    ALTER TABLE players
        ADD win_rate REAL;
    """.split(
        ";"
    )
    for q in statements:
        conn.execute(text(q))


def downgrade() -> None:
    pass
