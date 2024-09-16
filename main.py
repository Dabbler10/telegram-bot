import asyncio
from aiogram import Bot, Dispatcher, types
import os
import logging
from handlers import questions
from dotenv import load_dotenv


load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)')
bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()
dp.include_routers(questions.router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())