"""Runtime state must land in one fixed place.

Credentials and logs used to default to ".creds" and ".logs" relative to the
working directory, so a service wrote somewhere different depending on where it
was launched from -- and a token saved by one service was invisible to the next.
"""

from pathlib import Path

from coreutils import CredentialsManager, Logger, creds_dir, data_dir, logs_dir


def test_data_dir_follows_mechadealer_home(monkeypatch, tmp_path):
    monkeypatch.setenv("MECHADEALER_HOME", str(tmp_path / "state"))

    assert data_dir() == tmp_path / "state"
    assert creds_dir() == tmp_path / "state" / "creds"
    assert logs_dir() == tmp_path / "state" / "logs"


def test_data_dir_defaults_to_home_not_cwd(monkeypatch):
    monkeypatch.delenv("MECHADEALER_HOME", raising=False)

    resolved = data_dir()

    assert resolved.is_absolute()
    assert resolved == Path.home() / ".mechadealer"


def test_credentials_round_trip(tmp_path):
    store = CredentialsManager(creds_dir=tmp_path / "creds")
    store.set_credential("upstox.token", "abc123")

    assert store.get_credential("upstox.token") == "abc123"


def test_credentials_are_encrypted_at_rest(tmp_path):
    store = CredentialsManager(creds_dir=tmp_path / "creds")
    store.set_credential("upstox.token", "super-secret-value")

    raw = (tmp_path / "creds" / "credentials.json").read_bytes()

    assert b"super-secret-value" not in raw


def test_credentials_survive_a_new_manager(tmp_path):
    CredentialsManager(creds_dir=tmp_path / "creds").set_credential("k", "v")

    assert CredentialsManager(creds_dir=tmp_path / "creds").get_credential("k") == "v"


def test_credentials_delete(tmp_path):
    store = CredentialsManager(creds_dir=tmp_path / "creds")
    store.set_credential("k", "v")
    store.delete_credential("k")

    assert store.get_credential("k") is None


def test_logger_writes_under_mechadealer_home(monkeypatch, tmp_path):
    monkeypatch.setenv("MECHADEALER_HOME", str(tmp_path / "state"))

    logger = Logger("unit-test")

    assert Path(logger.log_file_path).parent == tmp_path / "state" / "logs"
