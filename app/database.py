import os
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

_engine = None


def load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_engine():
    # The address lives in .env so the password is not written in the code.
    global _engine
    if _engine is not None:
        return _engine

    load_env_file()
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is missing. Add it to the .env file.")

    _engine = create_engine(url)
    return _engine


def create_tables() -> None:
    SQLModel.metadata.create_all(get_engine())


def get_session():
    with Session(get_engine()) as session:
        yield session
