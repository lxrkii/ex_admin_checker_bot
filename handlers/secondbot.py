from aiogram import Router, types
from aiogram.filters import Command
from database import get_warnings_count

router = Router()

@router.message(Command("mywarns"))
async def check_self_warns(message: types.Message):
    count = await get_warnings_count(message.from_user.id)
    text = (
        f"👤 <b>Ваш профиль администратора</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"📊 Количество предупреждений: <b>{count}</b>\n\n"
        f"<i>Если вы считаете, что варнинг выдан по ошибке, обратитесь к руководству.</i>"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(Command("start"))
async def cmd_start_second(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот системы уведомлений.\n"
        "Здесь вы будете получать предупреждения. \n"
        "Используйте /mywarns, чтобы узнать свою статистику."
    )