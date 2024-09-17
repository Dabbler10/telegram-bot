from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from config import settings

engine = create_async_engine(url=settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    firstname: Mapped[str]
    # created_at: Mapped[datetime] = mapped_column(server_default=text('TIMEZONE("utc", now()))'))
    # updated_at: Mapped[datetime] = mapped_column(
    #     server_default=text('TIMEZONE("utc", now()))'),
    #     onupdate=datetime.utcnow)
