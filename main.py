import asyncio
from aiogram import Bot, Dispatcher, types
from config_reader import config
import logging
from handlers import questions

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)')
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()
dp.include_routers(questions.router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())