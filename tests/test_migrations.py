"""The migration runner.

init_db() calls create_all, which creates missing tables but never alters an
existing one, so a column change could not previously reach a database that
already held data.
"""

import pytest
import storelib.migrate as migrate_mod


def test_migrations_directory_is_found():
    """The path is resolved relative to the installed package, so a wrong
    number of parents silently yields an empty migration set."""
    assert migrate_mod.MIGRATIONS_DIR.is_dir()


def test_migrations_are_discovered():
    found = sorted(p.stem for p in migrate_mod._discover(migrate_mod.MIGRATIONS_DIR))

    assert "0001_drop_capital_remaining" in found


def test_discovery_is_ordered_by_filename(tmp_path):
    for name in ["0003_c.sql", "0001_a.sql", "0002_b.sql"]:
        (tmp_path / name).write_text("SELECT 1;")

    found = [p.stem for p in migrate_mod._discover(tmp_path)]

    assert found == ["0001_a", "0002_b", "0003_c"]


def test_missing_directory_is_an_error(tmp_path):
    with pytest.raises(RuntimeError, match="No migrations directory"):
        migrate_mod._discover(tmp_path / "nope")


def test_drop_migration_covers_both_tables():
    sql = (
        (migrate_mod.MIGRATIONS_DIR / "0001_drop_capital_remaining.sql")
        .read_text()
        .lower()
    )

    assert "alter table users drop column if exists capital_remaining" in sql
    assert "alter table strategies drop column if exists capital_remaining" in sql


def test_column_is_gone_from_the_table_definitions():
    from storelib._tables import strategies, users

    assert "capital_remaining" not in users.c
    assert "capital_remaining" not in strategies.c
    # The quantities it was confused with must still be there.
    assert "capital" in users.c
    assert "capital_used" in users.c


def test_models_no_longer_carry_the_column():
    from storelib import Strategy, User

    assert "capital_remaining" not in User.model_fields
    assert "capital_remaining" not in Strategy.model_fields
