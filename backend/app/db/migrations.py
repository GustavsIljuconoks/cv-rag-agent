import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect

from app.config import settings

BACKEND_ROOT = Path(__file__).resolve().parents[2]
_ORIGINAL_SYS_PATH = list(sys.path)

try:
    sys.path = [
        entry
        for entry in sys.path
        if Path(entry or ".").resolve() != BACKEND_ROOT
    ]
    from alembic import command
    from alembic.config import Config
finally:
    sys.path = _ORIGINAL_SYS_PATH

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
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config


if __name__ == "__main__":
    run_migrations()
