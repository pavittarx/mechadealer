import os
from pathlib import Path


def data_dir() -> Path:
    """Root directory for runtime state (credentials, logs).

    Defaults to ~/.mechadealer. These used to be cwd-relative (".creds",
    ".logs"), which meant a service wrote to a different place depending on
    which directory it was launched from -- and broker tokens saved by one
    service were invisible to the next. Override with MECHADEALER_HOME.
    """
    root = os.getenv("MECHADEALER_HOME")
    return Path(root).expanduser() if root else Path.home() / ".mechadealer"


def creds_dir() -> Path:
    return data_dir() / "creds"


def logs_dir() -> Path:
    return data_dir() / "logs"
