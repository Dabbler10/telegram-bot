from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

from config import settings


bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher()


async def send_message_to_moderator(text: str, reply_markup: InlineKeyboardMarkup):
        await bot.send_message(chat_id=settings.MODER_CHAT_ID, text=text, reply_markup=reply_markup)


async def send_message_to_user(text: str, user_id):
    await bot.send_message(chat_id=user_id, text=text)

async def get_user_state(user_id):
    return FSMContext(dp.storage, StorageKey(bot_id=bot.id, user_id=user_id, chat_id=user_id))