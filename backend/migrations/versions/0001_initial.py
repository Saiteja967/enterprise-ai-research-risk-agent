from alembic import op
from sqlalchemy import text
from backend.risk.schema_v1 import meta

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    meta.create_all(conn)

def downgrade() -> None:
    meta.drop_all(op.get_bind())

