from alembic import context

from backend.risk.db import database

with database().begin() as connection:
    context.configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()
