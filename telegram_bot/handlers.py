from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from database.requests import  *
from telegram_bot.keyboards import *
from telegram_bot.bot import send_message_to_moderator, send_message_to_user, get_user_state, send_document_to_moderator

router = Router()

#-------------------------------------------Состояния-------------------------------------------
class AddDocument(StatesGroup):
    chose_category = State()
    add_category = State()
    category_moderation = State()
    add_document = State()
    document_moderation = State()


class GetDocument(StatesGroup):
    chose_category = State()
    get_document = State()


#-------------------------------------------Команды-------------------------------------------
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await message.answer(f"Привет, {message.from_user.first_name}. Я помогу тебе находить, добавлять и редактировать конспекты" )
    await state.clear()


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Напиши предмет и я попытаюсь найти конспекты по нему :)")


@router.message(Command("add"), StateFilter(None))
async def cmd_add(message: Message, state: FSMContext):
    await message.answer(
        "Выбери предмет из списка или добавь свой",
        reply_markup= await make_categories_add_kb()
    )
    await state.set_state(AddDocument.chose_category)


@router.message(Command("get"), StateFilter(None))
async def cmd_get(message: Message, state: FSMContext):
    await message.answer(
        "Выбери предмет из списка",
        reply_markup=await make_categories_get_kb()
    )
    await state.set_state(GetDocument.chose_category)


#-------------------------------------------Add-Category-диалог-------------------------------------------
@router.callback_query(CategoriesCallbackFactory.filter(F.action == "add"), AddDocument.chose_category)
async def answer_callback_query(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Напиши название предмета")
    await callback.answer()
    await state.set_state(AddDocument.add_category)


@router.message(AddDocument.add_category)
async def category_name_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_category=message.text)
    await state.set_state(AddDocument.category_moderation)
    await message.answer("Название ушло на модерацию")
    await send_message_to_moderator(text=f"Пользователь {message.from_user.username} хочет добавить новый предмет: {message.text}.",
                                    reply_markup= await make_category_moderation_kb(message.text, message.from_user.id))


@router.callback_query(ModerationCallbackFactory.filter(F.action == "accept" and F.type == "category"))
async def category_moderation_accept(callback: CallbackQuery, callback_data: ModerationCallbackFactory):
    await set_category(callback_data.name)
    user_state = await get_user_state(callback_data.user_id)
    await send_message_to_user("Название одобрено. Отправьте документ", callback_data.user_id)
    await user_state.set_state(AddDocument.add_document)
    await callback.answer()


@router.callback_query(ModerationCallbackFactory.filter(F.action == "reject" and F.type == "category"))
async def category_moderation_reject(callback: CallbackQuery, callback_data: ModerationCallbackFactory):
    user_state = await get_user_state(callback_data.user_id)
    await send_message_to_user("Название отклонено", callback_data.user_id)
    await user_state.set_state(None)
    await callback.answer()


@router.callback_query(CategoriesCallbackFactory.filter(F.action == "chosen"), AddDocument.chose_category)
async def add_category_chosen(callback: CallbackQuery, callback_data: CategoriesCallbackFactory, state: FSMContext):
    await state.update_data(chosen_category=callback_data.name)
    await callback.message.answer("Отправь документ")
    await state.set_state(AddDocument.add_document)
    await callback.answer()


#-------------------------------------------Add-Document-диалог-------------------------------------------
@router.message(AddDocument.add_document)
async def add_document(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await add_file(message.document.file_id, message.document.file_name, user_data["chosen_category"], message.from_user.id)
    await send_document_to_moderator(
        text=f"Пользователь {message.from_user.username} хочет добавить новый конспект.",
        reply_markup=await make_document_moderation_kb(message.document.file_name, message.from_user.id), file_id=message.document.file_id)


@router.callback_query(ModerationCallbackFactory.filter(F.action == "accept" and F.type == "document"))
async def document_moderation_accept(callback: CallbackQuery, callback_data: ModerationCallbackFactory):
    user_state = await get_user_state(callback_data.user_id)
    await send_message_to_user("Документ успешно добавлен", callback_data.user_id)
    await callback.answer()
    await user_state.set_state(None)

@router.callback_query(ModerationCallbackFactory.filter(F.action == "reject" and F.type == "document"))
async def document_moderation_accept(callback: CallbackQuery, callback_data: ModerationCallbackFactory):
    user_state = await get_user_state(callback_data.user_id)
    await delete_file(callback_data.name)
    await send_message_to_user("Документ отклонен", callback_data.user_id)
    await callback.answer()
    await user_state.set_state(None)


#-------------------------------------------Get-диалог-------------------------------------------
@router.callback_query(CategoriesCallbackFactory.filter(F.action == "chosen"), GetDocument.chose_category)
async def get_category_chosen(callback: CallbackQuery, callback_data: CategoriesCallbackFactory, state: FSMContext):
    files_id = await get_files(callback_data.name)
    for file_id in files_id:
        await callback.message.answer_document(file_id)
    await state.clear()
    await callback.answer()