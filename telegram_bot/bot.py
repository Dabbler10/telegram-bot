from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

from config import settings


bot = Bot(settings.bot_token)
dp = Dispatcher()

#-------------------------------------------Команды-------------------------------------------
async def send_message_to_moderator(text: str, reply_markup: InlineKeyboardMarkup):
        await bot.send_message(chat_id=settings.moder_chat_id, text=text, reply_markup=reply_markup)


async def send_document_to_moderator(text: str, reply_markup: InlineKeyboardMarkup, file_id: str):
    await bot.send_document(chat_id=settings.moder_chat_id, caption=text, reply_markup=reply_markup, document=file_id)


async def send_message_to_user(text: str, user_id: int, reply_markup: InlineKeyboardMarkup = None):
    await bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)


async def get_user_state(user_id: int):
    return FSMContext(dp.storage, StorageKey(bot_id=bot.id, user_id=user_id, chat_id=user_id))