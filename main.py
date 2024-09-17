import asyncio
from aiogram import Bot, Dispatcher
from config import settings
from handlers import questions
from database.models import create_tables


# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)')
bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher()
dp.include_routers(questions.router)

async def main():
    await create_tables()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())