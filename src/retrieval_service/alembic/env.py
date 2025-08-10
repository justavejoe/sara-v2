from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import the Base from our new, centralized models.py file.
# This is the only custom import needed.
from models import Base


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set our model's metadata for 'autogenerate' support.
target_metadata = Base.metadata
# ADD THIS BLOCK to dynamically configure the database URL
import os
from sqlalchemy.engine.url import URL

# Construct the database URL from environment variables
# Cloud Build will set these variables for us.
db_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASS"),
    database=os.environ.get("DB_NAME"),
    host=os.environ.get("DB_HOST", "127.0.0.1"), # Defaults to localhost for proxy
    port=os.environ.get("DB_PORT", 5432)
)

# Get the existing config section and update the URL
config.set_main_option('sqlalchemy.url', db_url.render_as_string(hide_password=False))
# END OF BLOCK

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
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()