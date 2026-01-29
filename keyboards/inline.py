from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import SERVERS, ADMIN_MAP

def get_main_kb():
    builder = InlineKeyboardBuilder()
    for db_id, name in SERVERS.items():
        builder.button(text=name, callback_data=f"select_{db_id}")
    builder.adjust(2)
    return builder.as_markup()

def get_server_options_kb(db_name):
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Лист админов", callback_data=f"list_{db_name}")
    builder.button(text="🔙 К списку серверов", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()

def get_admin_choice_kb(online_admins, db_name):
    builder = InlineKeyboardBuilder()
    for admin in online_admins:
        tg_id = ADMIN_MAP.get(admin['steam'])
        if tg_id:
            builder.button(text=f"🔴 Warn: {admin['name']}", callback_data=f"warnuser_{tg_id}")
    builder.button(text="🔙 Назад", callback_data=f"select_{db_name}")
    builder.adjust(1)
    return builder.as_markup()
