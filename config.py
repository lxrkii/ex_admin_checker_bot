import os
from dotenv import load_dotenv
from aiogram import Bot

load_dotenv()

TOKEN_MAIN = os.getenv("BOT_TOKEN")
TOKEN_WARN = os.getenv("SECOND_BOT_TOKEN")
DB_PASS = os.getenv("DB_PASSWORD")

raw_allowed = os.getenv("TG_ALLOWED")
ALLOWED_USERS = [int(u.strip()) for u in raw_allowed.split(",")] if raw_allowed else []

raw_map = os.getenv("ADMIN_MAP")
ADMIN_MAP = {}
if raw_map:
    for item in raw_map.split(","):
        if "=" in item:
            s_id, t_id = item.split("=")
            ADMIN_MAP[s_id.strip()] = t_id.strip()

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
    "computer67": "🇩🇪 NS + RAPID FIRE | DE ",
}

bot_main = Bot(token=TOKEN_MAIN)
bot_warn = Bot(token=TOKEN_WARN)