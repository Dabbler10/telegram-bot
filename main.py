import asyncio
from database.models import create_tables
from handlers.bot import bot, dp
from handlers.questions import router


# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)')
# bot = Bot(settings.BOT_TOKEN)
# dp = Dispatcher()
# dp.include_routers(questions.router)


async def main():
    await create_tables()
    dp.include_routers(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())