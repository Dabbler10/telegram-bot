from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.for_questions import make_row_kb

subject_list = ['Матан', 'Тервер', 'Алгем']
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

@router.message(Command("add"))
async def cmd_add(message: Message):
    await message.answer(
        "Выбери предмет из списка или добавь свой",
        reply_markup=make_row_kb(subject_list)
    )

@router.message(F.text.lower() == "алгем")
async def answer_yes(message: Message):
    await message.answer(
        "Это здорово!",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "матан")
async def answer_no(message: Message):
    await message.answer(
        "Жаль...",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "тервер")
async def answer_no(message: Message):
    await message.answer(
        "Жаль...",
        reply_markup=ReplyKeyboardRemove()
    )

