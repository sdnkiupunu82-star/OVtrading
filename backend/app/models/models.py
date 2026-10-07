from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Candle(Base):
    __tablename__ = "candles"
    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)

class PaperAccount(Base):
    __tablename__ = "paper_accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), default="Demo Investor")
    cash: Mapped[float] = mapped_column(Float, default=100_000_000)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PaperPosition(Base):
    __tablename__ = "paper_positions"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, index=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    qty: Mapped[int] = mapped_column(Integer, default=0)
    avg_price: Mapped[float] = mapped_column(Float, default=0)

class PaperOrder(Base):
    __tablename__ = "paper_orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, index=True)
    symbol: Mapped[str] = mapped_column(String(16))
    side: Mapped[str] = mapped_column(String(8))
    qty: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="FILLED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Strategy(Base):
    __tablename__ = "strategies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    config_json: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
