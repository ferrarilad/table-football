"""init

Revision ID: e338207ef60a
Revises: f78853fab192
Create Date: 2023-05-12 14:31:19.937289

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'e338207ef60a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    statements = """
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alias TEXT UNIQUE,
        elo INTEGER,
        games_played INTEGER
    );
    
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        locale TEXT,
        blue_team_att TEXT,
        blue_team_def TEXT,
        red_team_att TEXT,
        red_team_def TEXT,
        match_type TEXT,
        blue_score INTEGER,
        red_score INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """.split(";")
    for q in statements:
        conn.execute(
            text(
                q
            )
        )


def downgrade() -> None:
    pass
