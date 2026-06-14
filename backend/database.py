"""数据库连接与会话管理。"""

from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'ferment.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy 声明基类。"""


def get_db():
    """FastAPI 依赖：提供数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def write_change_log(db, operation: str, entity: str, entity_id: int, summary: str):
    """写入一条变更记录。"""
    import models

    log = models.ChangeLog(
        operation=operation,
        entity=entity,
        entity_id=entity_id,
        summary=summary,
        created_at=datetime.utcnow(),
    )
    db.add(log)
