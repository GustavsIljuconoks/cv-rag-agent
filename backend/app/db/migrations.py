from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.config import settings

PROJECT_TABLES = {
    "applications",
    "candidate_profiles",
    "job_matches",
    "jobs",
}


def run_migrations() -> None:
    config = _build_alembic_config()
    engine = create_engine(settings.database_url, future=True)

    try:
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())
    finally:
        engine.dispose()

    has_version_table = "alembic_version" in table_names
    has_existing_project_tables = bool(PROJECT_TABLES.intersection(table_names))

    if has_version_table:
        command.upgrade(config, "head")
        return

    if has_existing_project_tables:
        command.stamp(config, "head")
        return

    command.upgrade(config, "head")


def _build_alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[2]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config


if __name__ == "__main__":
    run_migrations()
