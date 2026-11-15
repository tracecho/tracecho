"""Alembic environment configuration."""
from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# ---------------------------------------------------------------------------
# Ensure the regintel package root is on sys.path so our models are importable
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_pkg_root = os.path.dirname(_here)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

# ---------------------------------------------------------------------------
# Import Base and all models so Alembic sees them for autogenerate
# ---------------------------------------------------------------------------
from db.database import Base  # noqa: E402
import db.models  # noqa: E402, F401  — registers all ORM models on Base.metadata

# ---------------------------------------------------------------------------
# Alembic Config object (access to alembic.ini values)
# ---------------------------------------------------------------------------
config = context.config

# Override sqlalchemy.url with environment variable if set
_db_url = os.environ.get("DATABASE_URL")
if _db_url:
    config.set_main_option("sqlalchemy.url", _db_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
