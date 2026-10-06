from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# ------------------------------------------------------------
# Our database configuration
# ------------------------------------------------------------

from app.database import Base, DATABASE_URL
from app import models


# ------------------------------------------------------------
# Alembic Config object
# ------------------------------------------------------------

config = context.config


# ------------------------------------------------------------
# Put our DATABASE_URL into Alembic configuration
#
# DATABASE_URL comes from .env through database.py
# So we do NOT store the PostgreSQL password in alembic.ini
# ------------------------------------------------------------

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.replace("%", "%%")
)


# ------------------------------------------------------------
# Configure Python logging
# ------------------------------------------------------------

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ------------------------------------------------------------
# SQLAlchemy metadata
#
# Alembic uses this to compare:
#
# Existing PostgreSQL database
#            VS
# SQLAlchemy models
# ------------------------------------------------------------

target_metadata = Base.metadata


# ------------------------------------------------------------
# OFFLINE MIGRATIONS
# ------------------------------------------------------------

def run_migrations_offline() -> None:

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():

        context.run_migrations()


# ------------------------------------------------------------
# ONLINE MIGRATIONS
# ------------------------------------------------------------

def run_migrations_online() -> None:

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():

            context.run_migrations()


# ------------------------------------------------------------
# Start migration
# ------------------------------------------------------------

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()