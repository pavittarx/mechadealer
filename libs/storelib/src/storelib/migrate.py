"""Forward-only SQL migrations.

`init_db()` calls SQLAlchemy's create_all, which creates missing tables but
never alters existing ones, so there was previously no way to change a column
on a database that already had data.

Migrations are numbered .sql files under migrations/ at the repository root.
Each runs once, inside a transaction, and is recorded in schema_migrations.
"""

from pathlib import Path

from sqlalchemy import text

from ._setup import get_engine

MIGRATIONS_DIR = Path(__file__).resolve().parents[4] / "migrations"

_TRACKING_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     TEXT PRIMARY KEY,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""


def _discover(directory: Path) -> list[Path]:
    if not directory.is_dir():
        raise RuntimeError(f"No migrations directory at {directory}")

    return sorted(directory.glob("*.sql"))


def applied_versions() -> set[str]:
    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text(_TRACKING_TABLE))
        rows = conn.execute(text("SELECT version FROM schema_migrations")).fetchall()

    return {row[0] for row in rows}


def pending(directory: Path | None = None) -> list[Path]:
    done = applied_versions()
    return [m for m in _discover(directory or MIGRATIONS_DIR) if m.stem not in done]


def migrate(directory: Path | None = None) -> list[str]:
    """Apply every migration that has not run yet. Returns what was applied."""
    engine = get_engine()
    ran: list[str] = []

    for path in pending(directory):
        sql = path.read_text().strip()

        # One transaction per migration: a failure leaves the database on the
        # last good version rather than half-way through this one.
        with engine.begin() as conn:
            conn.execute(text(sql))
            conn.execute(
                text("INSERT INTO schema_migrations (version) VALUES (:v)"),
                {"v": path.stem},
            )

        ran.append(path.stem)

    return ran


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv()

    ran = migrate()

    if ran:
        for version in ran:
            print(f"applied {version}")
    else:
        print("no pending migrations")


if __name__ == "__main__":
    main()
