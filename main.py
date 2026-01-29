import asyncio
import aiomysql
import logging
import os
from dotenv import load_dotenv
load_dotenv()
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
TOKEN = os.getenv("BOT_TOKEN")
DB_PASS = os.getenv("DB_PASSWORD")

DB_BASE_CONFIG = {
    'host': 'web5.maze-host.ru',
    'port': 3306,
    'user': 'computer67',
    'password': DB_PASS,
    'autocommit': True,
}

SERVERS = {
    "s1_scout": "🎯 Scout",
    "s2_nospread": "🔫 NoSpread",
    "s3_nixware": "🛠 Nixware",
    "s4_arena": "⚔️ Arena",
    "s5_descout": "🏹 DeScout",
    "s6_denospread": "💣 DeNoSpread",
    "computer67": "Test Shit",
}

ADMIN_STEAM_IDS = ["STEAM_1:0:570112213",
                   "STEAM_1:0:110219151"]

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

async def get_server_data(db_name):
    """Подключается к конкретной базе и тянет инфу."""
    config = DB_BASE_CONFIG.copy()
    config['db'] = db_name # Устанавливаем имя базы для этого запроса
    
    conn = await aiomysql.connect(**config)
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # Игроки за сегодня
            await cursor.execute("SELECT COUNT(*) as cnt FROM lvl_base WHERE lastconnect >= UNIX_TIMESTAMP(CURDATE())")
            count_today = (await cursor.fetchone())['cnt']

            # Админы онлайн
            placeholders = ', '.join(['%s'] * len(ADMIN_STEAM_IDS))
            query_admins = f"SELECT name FROM lvl_base WHERE online > 0 AND steam IN ({placeholders})"
            await cursor.execute(query_admins, ADMIN_STEAM_IDS)
            admins = [row['name'] for row in await cursor.fetchall()]

            return count_today, admins
    finally:
        conn.close()

# --- КЛАВИАТУРА ---

def get_server_kb():
    builder = InlineKeyboardBuilder()
    for db_id, name in SERVERS.items():
        # callback_data поможет боту понять, какую базу юзер нажал
        builder.button(text=name, callback_data=f"check_{db_id}")
    builder.adjust(2) # Кнопки в 2 ряда
    return builder.as_markup()

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Выберите сервер для проверки статистики:", reply_markup=get_server_kb())

@dp.callback_query(F.data.startswith("check_"))
async def handle_server_check(callback: types.CallbackQuery):
    db_name = callback.data.split("_", 1)[1] # Извлекаем имя базы (например, s1_scout)
    server_label = SERVERS.get(db_name, db_name)
    
    # Редактируем сообщение, чтобы юзер видел, что бот думает
    await callback.message.edit_text(f"⏳ Получаю данные с {server_label}...")

    try:
        count, admins = await get_server_data(db_name)
        
        text = (
            f"🖥 <b>Сервер: {server_label}</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"👥 Игроков сегодня: <code>{count}</code>\n"
            f"👨‍💻 Админы онлайн: " + (f"<b>{', '.join(admins)}</b>" if admins else "<i>нет в сети</i>")
        )
        
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_server_kb())
    except Exception as e:
        logging.error(e)
        await callback.message.edit_text(f"❌ Ошибка базы {db_name}. Проверь доступы.", reply_markup=get_server_kb())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())