import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_reader import config
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)')
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.answer("Привет!\nЯ бот!")

@dp.message(Command('add_to_list'))
async def cmd_add_to_list(message: types.Message, myList: list[int]):
    myList.append(7)
    await message.answer("Добавлено число 7")

@dp.message(Command('show_list'))
async def cmd_add_to_list(message: types.Message, myList: list[int]):
    await message.answer(f"Ваш  список: {myList}")

async def main():
    await dp.start_polling(bot, myList=[1,2,3])

if __name__ == '__main__':
    asyncio.run(main())