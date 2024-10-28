import asyncio
from database.models import create_tables
from telegram_bot.bot import bot, dp
from telegram_bot.handlers import router


async def main():
    await create_tables()
    dp.include_routers(router)
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted')