import sqlalchemy
import datetime
from sqlalchemy import select, update
from database.models import async_session, Users, Files, Categories



#-------------------------------------------Пользователи-------------------------------------------
async def set_user(user_id: int, username: str, firstname: str):
    async with async_session() as session:
        user = await session.scalar(select(Users).where(Users.user_id == user_id))
        if user and user.firstname != firstname:
            session.scalar(update(Users).values(firstname=firstname).where(Users.user_id == user_id))
            await session.commit()
        elif not user:
            session.add(Users(user_id=user_id, username=username, firstname=firstname ))
            await session.commit()


async def get_user(user_id: int):
    async with async_session() as session:
        return await session.scalar(select(Users).where(Users.user_id == user_id))


#-------------------------------------------Файлы-------------------------------------------
async def add_file(file_id: str, file_name: str, category_name: str, user_id: int):
    async with async_session() as session:
        file = await session.scalar(select(Files).where(Files.file_id == file_id))

        if not file:
            category_id = await get_category_id(category_name)
            session.add(Files(file_id=file_id, name=file_name, creator_id=user_id, category_id=category_id))
            await session.commit()


async def set_file_moderation(name: str):
    async with async_session() as session:
        file = await session.scalar(select(Files).where(Files.name == name))
        if not file:
            return
        file.is_moderated = True
        await session.commit()


async def set_filename(filename: str, id: str):
    async with async_session() as session:
        file = await session.scalar(select(Files).where(Files.file_id == id))
        if not file:
            return
        file.name_by_user = filename
        await session.commit()


async def get_file(name: str):
    async with async_session() as session:
        return await session.scalar(select(Files).where(Files.name == name))


async def get_moderation_files(category_name: str):
    async with async_session() as session:
        category_id = await get_category_id(category_name)
        files = list(await session.scalars(select(Files).where(Files.is_moderated).where(Files.category_id == category_id)
                                            .where(Files.is_private == False).order_by(Files.created_at)))
        return files

async def get_moderation_files_with_name(category_name: str):
    async with async_session() as session:
        category_id = await get_category_id(category_name)
        files = list (await session.scalars(select(Files).where(Files.is_moderated).where(Files.category_id == category_id)
                                            .where(Files.is_private == False).where(Files.name_by_user.isnot(None)).order_by(Files.created_at)))
        return files


async def get_all_files():
    async with async_session() as session:
        files = list(await session.scalars(select(Files).where(Files.is_moderated).where(Files.is_private == False)))
        files.sort(key=lambda file: file.created_at)
        return files

async def get_files_by_name(name: str, category_name: str):
    async with async_session() as session:
        category_id = await get_category_id(category_name)
        files = list(await session.scalars(select(Files).where(Files.is_moderated).where(Files.is_private == False)
                                           .where(Files.name_by_user == name).where(Files.category_id == category_id)))
        return files

async def get_files_by_date(date_str: str):
    async with async_session() as session:
        date = datetime.datetime.strptime(date_str, '%d.%m.%Y')
        next_date = date + datetime.timedelta(days=1)
        files = list(await session.scalars(select(Files).where(Files.is_moderated).where(Files.is_private == False)
                                           .where(Files.created_at >= date).where(Files.created_at < next_date)))
        return files

async def delete_file(name: str):
    async with async_session() as session:
        query = sqlalchemy.delete(Files).where(Files.name == name)
        await session.execute(query)


#-------------------------------------------Приватные-файлы-------------------------------------
async def add_private_file(file_id: str, file_name: str, user_id: int):
    async with async_session() as session:
        file = await session.scalar(select(Files).where(Files.file_id == file_id))

        if not file:
            session.add(Files(file_id=file_id, name=file_name, creator_id=user_id, is_private=True))
            await session.commit()


async def get_private_files(user_id: int):
    async with async_session() as session:
        return list(await session.scalars(select(Files).where(Files.creator_id == user_id).where(Files.is_private == True)))


#-------------------------------------------Категории-------------------------------------------
async def set_category(name: str):
    async with async_session() as session:
        category = await session.scalar(select(Categories).where(Categories.name == name))

        if not category:
            session.add(Categories(name=name))
            await session.commit()


async def get_category_id(name: str):
    async with async_session() as session:
        return await session.scalar(select(Categories.id).where(Categories.name == name))


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Categories))
