import os
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from keyboards.inline import get_main_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    photo_path = os.path.join("source", "header.jpg")
    text = "✅ Доступ разрешен. Выберите сервер:"
    
    if os.path.exists(photo_path):
        await message.answer_photo(photo=FSInputFile(photo_path), caption=text, reply_markup=get_main_kb())
    else:
        await message.answer(text, reply_markup=get_main_kb())