import json
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
import logging
from handlers import questions

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)')

bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()
dp.include_routers(questions.router)


async def handler(event, context):
    update = json.loads(event['body'])
    my_update = types.Update(update_id=update['update_id'], message=update['message'])
    await dp.feed_update(bot=bot, update=my_update)

    return {
        'statusCode': 200,
        'body': 'ok!'
    }