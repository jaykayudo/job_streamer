"""Alembic environment — wires the project's SQLAlchemy engine and models
into Alembic's migration machinery.

Run via the helper script:   python scripts/migrate.py <command>
Or directly:                 alembic <command>
"""
from __future__ import annotations

import sys
import os

# Ensure the project root is on sys.path so all project imports resolve.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ---------------------------------------------------------------------------
# Load the project's engine and metadata
# ---------------------------------------------------------------------------
from conf.settings import SETTINGS  # noqa: E402 — must come after sys.path fix
from storage.core.engine import engine as project_engine  # noqa: E402

# Import all models so their tables are registered on BaseModel.metadata.
import storage.core.models  # noqa: F401, E402

from storage.core.engine import BaseModel  # noqa: E402

# ---------------------------------------------------------------------------
# Alembic config object
# ---------------------------------------------------------------------------
config = context.config

# Override the sqlalchemy.url with the live project setting.
config.set_main_option("sqlalchemy.url", SETTINGS.DATABASE_URL)

# Set up logging from alembic.ini if present.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = BaseModel.metadata


# ---------------------------------------------------------------------------
# Migration runners
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection needed)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using the project's engine."""
    with project_engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
