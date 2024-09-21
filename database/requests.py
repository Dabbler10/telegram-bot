from sqlalchemy import select, update

from database.models import async_session, Users, Files, Categories

async def set_user(user_id, username, firstname):
    async with async_session() as session:
        user = await session.scalar(select(Users).where(Users.user_id == user_id))
        if user and user.firstname != firstname:
            session.scalar(update(Users).values(firstname=firstname).where(Users.user_id == user_id))
            await session.commit()
        elif not user:
            session.add(Users(user_id=user_id, username=username, firstname=firstname ))
            await session.commit()

async def get_user(user_id):
    async with async_session() as session:
        return await session.scalar(select(Users).where(Users.user_id == user_id))


async def add_file(file_id, file_name, category_name, user_id):
    async with async_session() as session:
        file = await session.scalar(select(Files).where(Files.file_id == file_id))

        if not file:
            category_id = await get_category_id(category_name)
            session.add(Files(file_id=file_id, name=file_name, creator_id=user_id, category_id=category_id))
            await session.commit()

async def get_file():
    async with async_session() as session:
        return await session.scalar(select(Files.file_id))

async def get_files(category_name):
    async with async_session() as session:
        category_id = await get_category_id(category_name)
        return await session.scalars(select(Files.file_id).where(Files.category_id == category_id))

async def set_category(name):
    async with async_session() as session:
        category = await session.scalar(select(Categories).where(Categories.name == name))

        if not category:
            session.add(Categories(name=name))
            await session.commit()


async def get_category_id(name):
    async with async_session() as session:
        return await session.scalar(select(Categories.id).where(Categories.name == name))

async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Categories))
