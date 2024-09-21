import datetime

from sqlalchemy import ForeignKey, BigInteger, Identity, text, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from config import settings

engine = create_async_engine(url=settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass


async def create_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, Identity(), unique=True)
    username: Mapped[str]
    firstname: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now(), onupdate=datetime.datetime.now)

class Files(Base):
    __tablename__ = 'files'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    # address: Mapped[str]
    creator_id: Mapped[int] = mapped_column(BigInteger, Identity(), ForeignKey('users.user_id'))
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

class Categories(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
