# MEMORY_ID: TASK_METALS_KITCO
# TIMESTAMP: 2025-11-09T20:00:00+01:00
# AUTHOR: Cursor_Omega

"""
Persistência via SQLAlchemy para cotações Kitco.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, List

import sqlalchemy as sa  # type: ignore
from sqlalchemy.orm import Session, declarative_base, sessionmaker  # type: ignore

from .Config import DB_STRING
from .Logger import get_logger

logger = get_logger("prometheus.kitco.repository")

Base = declarative_base()
engine = sa.create_engine(DB_STRING, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class MetalPrice(Base):
    __tablename__ = "metal_prices"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    metal = sa.Column(sa.String(32), nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    source = sa.Column(sa.String(32), nullable=False)
    collected_at = sa.Column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


def create_database() -> None:
    logger.info("Verificando estrutura da base Kitco (%s)", DB_STRING)
    Base.metadata.create_all(engine)


def persist_prices(prices: Iterable[dict]) -> int:
    """
    Persiste lista de preços.
    Retorna quantidade de registros inseridos.
    """

    items: List[MetalPrice] = []
    for item in prices:
        price = MetalPrice(
            metal=item["metal"],
            price=item["price"],
            source=item.get("source", "kitco"),
            collected_at=item.get("collected_at", datetime.now(timezone.utc)),
        )
        items.append(price)

    if not items:
        logger.info("Nenhum dado a persistir.")
        return 0

    with SessionLocal() as session:  # type: Session
        session.add_all(items)
        session.commit()
        logger.info("Persistidos %d registros de metais.", len(items))

    return len(items)


def fetch_recent(limit: int = 100) -> List[MetalPrice]:
    with SessionLocal() as session:
        stmt = sa.select(MetalPrice).order_by(MetalPrice.collected_at.desc()).limit(limit)
        records = session.execute(stmt).scalars().all()
        return list(records)

