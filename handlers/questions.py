from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.for_questions import get_yes_no_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет, я помогу тебе находить, добавлять, редактировать конспекты"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Напишите предмет и я попытаюсь найти конспекты по нему :)"
    )