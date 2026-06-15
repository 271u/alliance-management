import os
from pathlib import Path
from typing import Any

from django.core.exceptions import ImproperlyConfigured


def required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ImproperlyConfigured(f"Missing required environment variable: {name}")

    return value


def build_database_config(base_dir: Path) -> dict[str, dict[str, Any]]:
    database_engine = os.getenv("DATABASE_ENGINE", "sqlite").lower()

    if database_engine == "sqlite":
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": os.getenv("SQLITE_PATH", str(base_dir / "data" / "db.sqlite3")),
            }
        }

    if database_engine in ["postgres", "postgresql"]:
        return {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": required_env("POSTGRES_DB"),
                "USER": required_env("POSTGRES_USER"),
                "PASSWORD": required_env("POSTGRES_PASSWORD"),
                "HOST": os.getenv("POSTGRES_HOST", "db"),
                "PORT": os.getenv("POSTGRES_PORT", "5432"),
                "CONN_MAX_AGE": int(os.getenv("POSTGRES_CONN_MAX_AGE", "60")),
                "CONN_HEALTH_CHECKS": True,
            }
        }

    raise ImproperlyConfigured(
        f"Unsupported DATABASE_ENGINE: {database_engine}. "
        "Use 'sqlite' or 'postgres'."
    )
