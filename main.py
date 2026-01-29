import asyncio
import aiomysql
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile

# --- КОНФИГУРАЦИЯ ---
TOKEN = os.getenv("BOT_TOKEN")
DB_PASS = os.getenv("DB_PASSWORD")
raw_allowed = os.getenv("TG_ALLOWED")
if raw_allowed:
    ALLOWED_USERS = [int(user_id.strip()) for user_id in raw_allowed.split(",")]
else:
    ALLOWED_USERS = []

DB_BASE_CONFIG = {
    'host': 'web5.maze-host.ru',
    'port': 3306,
    'user': 'computer67',
    'password': DB_PASS,
    'autocommit': True,
}

SERVERS = {
    "s1_scout": "🇷🇺 SCOUT ONLY | MSK",
    "s2_nospread": "🇷🇺 NS + RAPID FIRE | MSK",
    "s3_nixware": "🇷🇺 NIXWARE | MSK ",
    "s4_arena": "🇷🇺 ARENA 1X1 | MSK ",
    "s5_descout": "🇩🇪 SCOUT ONLY | DE",
    "s6_denospread": "🇩🇪 NS + RAPID FIRE | DE ",
    "computer67": "Test Shit",
}

ADMIN_STEAM_IDS = ["STEAM_1:0:570112213", "STEAM_1:0:110219151"]

class AccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
    
        if user.id not in ALLOWED_USERS:
            log_entry = (
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"ОТКАЗ: ID {user.id} | Username: @{user.username} | "
                f"Name: {user.full_name} | Lang: {user.language_code}\n"
            )

            with open("log.txt", "a", encoding="utf-8") as f:
                f.write(log_entry)

            return 
        return await handler(event, data)

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.message.outer_middleware(AccessMiddleware())
dp.callback_query.outer_middleware(AccessMiddleware())

logging.basicConfig(level=logging.INFO)

async def get_server_data(db_name):
    config = DB_BASE_CONFIG.copy()
    config['db'] = db_name
    
    conn = await aiomysql.connect(**config)
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT COUNT(*) as cnt FROM lvl_base WHERE lastconnect >= UNIX_TIMESTAMP(CURDATE())")
            count_today = (await cursor.fetchone())['cnt']

            placeholders = ', '.join(['%s'] * len(ADMIN_STEAM_IDS))
            query_admins = f"SELECT name FROM lvl_base WHERE online > 0 AND steam IN ({placeholders})"
            await cursor.execute(query_admins, ADMIN_STEAM_IDS)
            admins = [row['name'] for row in await cursor.fetchall()]

            return count_today, admins
    finally:
        conn.close()

def get_server_kb():
    builder = InlineKeyboardBuilder()
    for db_id, name in SERVERS.items():
        builder.button(text=name, callback_data=f"check_{db_id}")
    builder.adjust(2)
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    photo_path = os.path.join("source", "header.jpg")

    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(
            photo=photo,
            caption=f"✅ Доступ разрешен. {username} Выберите сервер для проверки статистики:",
            reply_markup=get_server_kb()
        )
    else:
        await message.answer(
            f"✅ Доступ разрешен! {username} выберите сервер (фото header.jpg не найдено):", 
            reply_markup=get_server_kb()
        )
@dp.callback_query(F.data.startswith("check_"))
async def handle_server_check(callback: types.CallbackQuery):
    db_name = callback.data.split("_", 1)[1]
    server_label = SERVERS.get(db_name, db_name)
    
    # Если мы работаем с фото, нужно редактировать Caption (подпись)
    await callback.message.edit_caption(caption=f"⏳ Получаю данные с {server_label}...")

    try:
        count, admins = await get_server_data(db_name)
        
        text = (
            f"🖥 <b>Сервер: {server_label}</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"👥 Игроков сегодня: <code>{count}</code>\n"
            f"👨‍💻 Админы онлайн: " + (f"<b>{', '.join(admins)}</b>" if admins else "<i>нет в сети</i>")
        )
        
        await callback.message.edit_caption(
            caption=text, 
            parse_mode="HTML", 
            reply_markup=get_server_kb()
        )
    except Exception as e:
        logging.error(e)
        await callback.message.edit_caption(
            caption=f"❌ Ошибка базы {db_name}.", 
            reply_markup=get_server_kb()
        )
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())