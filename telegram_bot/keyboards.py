from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requests import get_categories

class CategoriesCallbackFactory(CallbackData, prefix="fabcat"):
    action: str
    name: Optional[str] = None

class ModerationCallbackFactory(CallbackData, prefix="mdr"):
    action: str
    type: str
    user_id: int
    name: Optional[str] = None

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

async def make_category_moderation_kb(name: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить", callback_data=ModerationCallbackFactory(action="accept", name=name, user_id=user_id, type="category").pack())
    builder.button(text="Отклонить", callback_data=ModerationCallbackFactory(action="reject", user_id=user_id, type="category").pack())
    return builder.as_markup()

async def make_document_moderation_kb(name: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить", callback_data=ModerationCallbackFactory(action="accept", name=name, user_id=user_id, type="document").pack())
    builder.button(text="Отклонить", callback_data=ModerationCallbackFactory(action="reject", user_id=user_id, type="document").pack())
    return builder.as_markup()