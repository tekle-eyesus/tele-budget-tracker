import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from datetime import datetime

# 1. Setup Database URL
DATABASE_URL = "sqlite+aiosqlite:///./expense.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

# 2. Define the Expense Model
class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)  # Telegram User ID
    amount: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# 3. Init DB Function
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)