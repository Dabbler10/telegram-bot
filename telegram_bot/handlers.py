from aiogram import Router, F
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from database.requests import  *
from telegram_bot.keyboards import *
from telegram_bot.bot import send_message_to_moderator, send_message_to_user, get_user_state, send_document_to_moderator

router = Router()

#-------------------------------------------Состояния-------------------------------------------
class AddFile(StatesGroup):
    chose_category = State()
    add_category = State()
    category_moderation = State()
    add_file = State()
    file_moderation = State()
    is_named_file = State()
    add_file_name = State()
    file_name_moderation = State()


class GetFile(StatesGroup):
    chose_category = State()
    get_file = State()


class AddPrivateFile(StatesGroup):
    add_private_file = State()
    is_named_file = State()
    add_file_name = State()


#-------------------------------------------Команды-------------------------------------------
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await message.answer(f"Привет, {message.from_user.first_name}. Я помогу тебе находить, добавлять и редактировать конспекты" )
    await state.set_state(None)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Напиши предмет, и я попытаюсь найти конспекты по нему :)")


@router.message(Command("add"), StateFilter(None))
async def cmd_add(message: Message, state: FSMContext):
    await message.answer(
        "Выбери предмет из списка или добавь свой",
        reply_markup= await make_categories_add_kb()
    )
    await state.set_state(AddFile.chose_category)


@router.message(Command("get"), StateFilter(None))
async def cmd_get(message: Message, state: FSMContext):
    await message.answer(
        "Выбери предмет из списка",
        reply_markup=await make_categories_get_kb()
    )
    await state.set_state(GetFile.chose_category)


@router.message(Command("get_all"), StateFilter(None))
async def cmd_get_all(message: Message):
    files = await get_all_files()
    if len(list(files)) == 0:
        await message.answer("К сожалению пока что нет файлов")
    for file in files:
        await message.answer_document(document=file.file_id,
                                      caption=f"Отправлен {file.created_at.day:02d}-{file.created_at.month:02d}-{file.created_at.year} в {file.created_at.hour:02d}:{file.created_at.minute:02d}.")


@router.message(Command("add_private"), StateFilter(None))
async def cmd_add_private(message: Message, state: FSMContext):
    await message.answer('Отправь документ')
    await state.set_state(AddPrivateFile.add_private_file)


@router.message(Command("get_private"), StateFilter(None))
async def cmd_get_private(message: Message):
    files = await get_private_files(message.from_user.id)
    if len(files) == 0:
        await message.answer("К сожалению пока что здесь нет файлов")
    for file in files:
        await message.answer_document(document=file.file_id,
                                      caption=f"Отправлен {file.created_at.day:02d}-{file.created_at.month:02d}-{file.created_at.year} в {file.created_at.hour:02d}:{file.created_at.minute:02d}.")



@router.message(Command("get_by_name"), StateFilter(None))
async def cmd_get_by_name(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer("Ошибка: не передано имя")
        return

    try:
        name = command.args
    except IndexError:
        await message.answer("Ошибка: неправильный формат команды. Пример:\n"
                             "/get_by_name <name>")
        return
    files = await get_files_by_name(name)
    for file in files:
        await message.answer_document(document=file.file_id,
                                      caption=f"{file.name_by_user}\n"
                                              f"Отправлен {file.created_at.day:02d}-{file.created_at.month:02d}-{file.created_at.year} в {file.created_at.hour:02d}:{file.created_at.minute:02d}.")


#-------------------------------------------Add-Category-диалог-------------------------------------------
@router.callback_query(CategoriesCallbackFactory.filter(F.action == "add"), AddFile.chose_category)
async def answer_callback_query(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Напиши название предмета.")
    await callback.answer()
    await state.set_state(AddFile.add_category)


@router.message(AddFile.add_category, F.text, F.text[0] != '/')
async def category_name_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_category=message.text)
    await state.set_state(AddFile.category_moderation)
    await message.answer("Название ушло на модерацию")
    await send_message_to_moderator(text=f"Пользователь @{message.from_user.username} хочет добавить новый предмет: {message.text}.",
                                    reply_markup= await make_category_moderation_kb(message.text, message.from_user.id))

@router.message(AddFile.add_category)
async def category_name_chosen_incorrectly(message: Message):
    await message.answer("Кажется это не название.\nПожалуйста, напиши название предмета.")


@router.callback_query(ModerationCategoryCallbackFactory.filter(F.action == "accept"))
async def category_moderation_accept(callback: CallbackQuery, callback_data: ModerationCategoryCallbackFactory):
    await set_category(callback_data.name)
    user_state = await get_user_state(callback_data.user_id)
    await send_message_to_user("Название одобрено. Отправьте документ", callback_data.user_id)
    await user_state.set_state(AddFile.add_file)
    await callback.answer()


@router.callback_query(ModerationCategoryCallbackFactory.filter(F.action == "reject"))
async def category_moderation_reject(callback: CallbackQuery, callback_data: ModerationCategoryCallbackFactory):
    user_state = await get_user_state(callback_data.user_id)
    await send_message_to_user("Название отклонено", callback_data.user_id)
    await user_state.set_state(None)
    await callback.answer()


@router.callback_query(CategoriesCallbackFactory.filter(F.action == "chosen"), AddFile.chose_category)
async def add_category_chosen(callback: CallbackQuery, callback_data: CategoriesCallbackFactory, state: FSMContext):
    await state.update_data(chosen_category=callback_data.name)
    await callback.message.answer("Отправь файл")
    await state.set_state(AddFile.add_file)
    await callback.answer()


#-------------------------------------------Add-Document-диалог-------------------------------------------
@router.message(AddFile.add_file, F.document)
async def add_file_handler(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await add_file(message.document.file_id, message.document.file_name, user_data["chosen_category"], message.from_user.id)
    await send_document_to_moderator(
        text=f"Пользователь {message.from_user.username} хочет добавить новый файл.",
        reply_markup=await make_document_moderation_kb(message.document.file_name, message.from_user.id), file_id=message.document.file_id)


@router.message(AddFile.add_file)
async def add_file_incorrectly(message: Message):
    await message.answer("Кажется это не файл.\nПожалуйста, отправь файл.")


@router.callback_query(ModerationFileCallbackFactory.filter(F.action == "accept"))
async def file_moderation_accept(callback: CallbackQuery, callback_data: ModerationFileCallbackFactory):
    user_state = await get_user_state(callback_data.user_id)
    await user_state.update_data(added_file=callback_data.name)
    await set_file_moderation(callback_data.name)
    await user_state.set_state(AddFile.is_named_file)
    await send_message_to_user(text="Документ успешно добавлен. Хочешь назвать его?", user_id=callback_data.user_id, reply_markup= await make_filename_add_kb())
    await callback.answer()


@router.callback_query(ModerationFileCallbackFactory.filter(F.action == "reject"))
async def file_moderation_reject(callback: CallbackQuery, callback_data: ModerationFileCallbackFactory):
    user_state = await get_user_state(callback_data.user_id)
    await delete_file(callback_data.name)
    await send_message_to_user("Документ отклонен", callback_data.user_id)
    await callback.answer()
    await user_state.set_state(None)


#-------------------------------------------Add-FileName-диалог-------------------------------------------
@router.callback_query(FileNameCallbackFactory.filter(F.action == "yes"), AddFile.is_named_file)
async def filename_yes(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Напиши название")
    await callback.answer()
    await state.set_state(AddFile.add_file_name)


@router.callback_query(FileNameCallbackFactory.filter(F.action == "no"), AddFile.is_named_file)
async def filename_no(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Принято")
    await callback.answer()
    await state.set_state(None)


@router.message(AddFile.add_file_name, F.text, F.text[0] != '/')
async def filename_name_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_filename=message.text)
    await state.set_state(AddFile.file_name_moderation)
    await message.answer("Название ушло на модерацию")
    await send_message_to_moderator(text=f"Пользователь @{message.from_user.username} хочет добавить название файла: {message.text}.",
                                    reply_markup= await make_filename_moderation_kb(message.text, message.from_user.id))


@router.message(AddFile.add_file_name)
async def filename_chosen_incorrectly(message: Message):
    await message.answer("Кажется это не название.\nПожалуйста, напиши название файла.")


@router.callback_query(ModerationFilenameCallbackFactory.filter(F.action == "accept"))
async def filename_moderation_accept(callback: CallbackQuery, callback_data: ModerationCategoryCallbackFactory):
    user_state = await get_user_state(callback_data.user_id)
    user_data = await user_state.get_data()
    file = await get_file(user_data["added_file"])
    await set_filename(user_data["chosen_filename"], file.file_id)
    await send_message_to_user("Название одобрено.", callback_data.user_id)
    await user_state.set_state(None)
    await callback.answer()


@router.callback_query(ModerationFilenameCallbackFactory.filter(F.action == "reject"))
async def filename_moderation_reject(callback: CallbackQuery, callback_data: ModerationCategoryCallbackFactory):
    user_state = await get_user_state(callback_data.user_id)
    await send_message_to_user("Название отклонено", callback_data.user_id)
    await user_state.set_state(None)
    await callback.answer()


#-------------------------------------------Get-диалог-------------------------------------------
@router.callback_query(CategoriesCallbackFactory.filter(F.action == "chosen"), GetFile.chose_category)
async def get_category_chosen(callback: CallbackQuery, callback_data: CategoriesCallbackFactory, state: FSMContext):
    files = await get_moderation_files(callback_data.name)
    if len(files) == 0:
        await callback.message.answer("К сожалению пока что здесь нет файлов.")
    for file in files:
        await callback.message.answer_document(document=file.file_id,
                                      caption=f"Отправлен {file.created_at.day:02d}-{file.created_at.month:02d}-{file.created_at.year} в {file.created_at.hour:02d}:{file.created_at.minute:02d}.")
    await state.clear()
    await callback.answer()


#-------------------------------------------Add-Private-диалог-------------------------------------------
@router.message(AddPrivateFile.add_private_file, F.document)
async def add_private_file_handler(message: Message, state: FSMContext):
    await add_private_file(message.document.file_id, message.document.file_name, user_id=message.from_user.id)
    await message.answer(text="Документ успешно добавлен. Хочешь назвать его?", reply_markup= await make_filename_add_kb())
    await state.set_state(AddPrivateFile.is_named_file)
    await state.update_data(private_file=message.document.file_id)


@router.message(AddPrivateFile.add_private_file)
async def add_private_file_incorrectly(message: Message):
    await message.answer("Кажется это не файл.\nПожалуйста, отправь файл.")


#-------------------------------------------Add-FileName-Private-диалог-------------------------------------------
@router.callback_query(FileNameCallbackFactory.filter(F.action == "yes"), AddPrivateFile.is_named_file)
async def filename_private_yes(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Напиши название")
    await callback.answer()
    await state.set_state(AddPrivateFile.add_file_name)


@router.callback_query(FileNameCallbackFactory.filter(F.action == "no"), AddPrivateFile.is_named_file)
async def filename_private_no(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Принято")
    await callback.answer()
    await state.set_state(None)


@router.message(AddPrivateFile.add_file_name, F.text, F.text[0] != '/')
async def add_private_filename(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await set_filename(message.text, user_data["private_file"])
    await message.answer("Файл назван")
    await state.set_state(None)


@router.message(AddPrivateFile.add_file_name)
async def filename_private_chosen_incorrectly(message: Message):
    await message.answer("Кажется это не название.\nПожалуйста, напиши название файла.")

