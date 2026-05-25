"""Alembic environment – liest DATABASE_URL aus der Umgebungsvariable."""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Damit Alembic unsere Models und database.py findet
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Base  # noqa: E402  – importiert engine/metadata
import models  # noqa: F401 – registriert alle Tabellen in Base.metadata

# Alembic-Config-Objekt (liest alembic.ini)
config = context.config

# Logging aus alembic.ini aktivieren
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ziel-Metadaten für autogenerate
target_metadata = Base.metadata


def get_url() -> str:
    """Liest DATABASE_URL aus der Umgebung – wird von docker-compose gesetzt."""
    url = os.getenv("DATABASE_URL")
    if not url:
        # Fallback für lokale Ausführung ohne Docker
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD") or os.getenv("MYSQL_ROOT_PASSWORD", "")
        host = os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("MYSQL_PORT", "3306")
        db = os.getenv("MYSQL_DATABASE", "smart_kitchen")
        url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    return url


def run_migrations_offline() -> None:
    """Offline-Modus: generiert SQL-Skript ohne echte DB-Verbindung."""
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Online-Modus: führt Migrationen direkt gegen die DB aus."""
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,         # Typ-Änderungen erkennen
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
