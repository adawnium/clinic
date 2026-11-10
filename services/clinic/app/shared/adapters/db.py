"""The SQLAlchemy engine, the session factory and the declarative base of every table."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DATABASE_URL

args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=args)
SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def enforce_foreign_keys(dbapi_connection, _) -> None:
        """SQLite ignores foreign keys unless told otherwise: deleting a patient must take the
        patient's appointments along (ON DELETE CASCADE). Recipe from sqlalchemy/dialects/sqlite/base.py."""
        autocommit = dbapi_connection.autocommit
        dbapi_connection.autocommit = True
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        dbapi_connection.autocommit = autocommit
