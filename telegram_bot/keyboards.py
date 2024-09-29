from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime

from database.requests import get_categories, get_moderation_files_with_name, get_all_files


#-------------------------------------------Callback-фабрики-------------------------------------
class CategoriesCallbackFactory(CallbackData, prefix="fabcat"):
    action: str
    name: str | None = None


class FileNameCallbackFactory(CallbackData, prefix="flnm"):
    action: str

class FileCallbackFactory(CallbackData, prefix="fls"):
    name: str

class DateCallbackFactory(CallbackData, prefix="dt"):
    date: str


class ModerationCategoryCallbackFactory(CallbackData, prefix="mdrct"):
    action: str
    user_id: int
    name: str | None = None


class ModerationFileCallbackFactory(CallbackData, prefix="mdrfl"):
    action: str
    user_id: int
    name: str | None = None


class ModerationFilenameCallbackFactory(CallbackData, prefix="mdrnm"):
    action: str
    user_id: int
    name: str | None = None


#-------------------------------------------Клавиатуры-------------------------------------
async def make_categories_add_kb() -> InlineKeyboardMarkup:
    categories = await get_categories()
    builder = InlineKeyboardBuilder()
    if categories:
        for category in categories:
            builder.add(InlineKeyboardButton(text=category.name,
                                             callback_data=CategoriesCallbackFactory(action="chosen",
                                                                                     name=category.name).pack()))
    builder.adjust(4)
    builder.add(InlineKeyboardButton(text="Добавить", callback_data=CategoriesCallbackFactory(action="add", name="add").pack()))
    return builder.as_markup()


async def make_categories_get_kb() -> InlineKeyboardMarkup:
    categories = await get_categories()
    builder = InlineKeyboardBuilder()
    if categories:
        for category in categories:
            builder.add(InlineKeyboardButton(text=category.name, callback_data=CategoriesCallbackFactory(action="chosen", name=category.name).pack()))
    builder.adjust(4)
    return builder.as_markup()


async def make_filename_add_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Да",
                   callback_data=FileNameCallbackFactory(action="yes").pack())
    builder.button(text="Нет",
                   callback_data=FileNameCallbackFactory(action="no").pack())
    return builder.as_markup()


#-------------------------------------------Клавиатуры-Модераторские------------------------------------
async def make_category_moderation_kb(name: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить",
                   callback_data=ModerationCategoryCallbackFactory(action="accept", name=name, user_id=user_id).pack())
    builder.button(text="Отклонить",
                   callback_data=ModerationCategoryCallbackFactory(action="reject", user_id=user_id).pack())
    return builder.as_markup()


async def make_document_moderation_kb(name: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить",
                   callback_data=ModerationFileCallbackFactory(action="accept", name=name, user_id=user_id).pack())
    builder.button(text="Отклонить",
                   callback_data=ModerationFileCallbackFactory(action="reject", name=name, user_id=user_id).pack())
    return builder.as_markup()


async def make_filename_moderation_kb(name: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить",
                   callback_data=ModerationFilenameCallbackFactory(action="accept", name=name, user_id=user_id).pack())
    builder.button(text="Отклонить",
                   callback_data=ModerationFilenameCallbackFactory(action="reject", user_id=user_id).pack())
    return builder.as_markup()


async def make_file_by_name_kb(category_name: str) -> InlineKeyboardMarkup:
    files = await get_moderation_files_with_name(category_name)
    builder = InlineKeyboardBuilder()
    if len(files) != 0:
        for file in files:
            builder.button(text=file.name_by_user, callback_data=FileCallbackFactory(name=file.name_by_user))
    builder.button(text="Все файлы", callback_data=FileCallbackFactory(name="all"))
    builder.adjust(1)
    return builder.as_markup()


async def make_file_by_date_kb() -> InlineKeyboardMarkup:
    files = await get_all_files()
    dates = set(list(map(lambda file: file.created_at.strftime('%d.%m.%Y'), files)))
    print(dates)
    builder = InlineKeyboardBuilder()
    if len(files) != 0:
        for date in dates:
            builder.button(text=date, callback_data=DateCallbackFactory(date=date))
    builder.adjust(1)
    return builder.as_markup()