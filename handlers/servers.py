from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import SERVERS, bot_warn
from database import get_extended_stats, add_warning, get_warnings_count
from keyboards.inline import get_main_kb, get_server_options_kb, get_admin_choice_kb

router = Router()

class WarnStates(StatesGroup):
    waiting_for_reason = State()

@router.callback_query(F.data.startswith("select_"))
async def handle_server_select(callback: types.CallbackQuery):
    db_name = callback.data.split("_")[1]
    server_label = SERVERS.get(db_name, db_name)
    await callback.message.edit_caption(caption=f"⏳ Загрузка статистики {server_label}...")
    
    try:
        today, week, online_admins = await get_extended_stats(db_name)
        admin_names = [a['name'] for a in online_admins]
        text = (
            f"🖥 <b>Сервер: {server_label}</b>\n━━━━━━━━━━━━━━\n"
            f"📅 Игроков за неделю: <code>{week}</code>\n"
            f"☀️ Игроков сегодня: <code>{today}</code>\n━━━━━━━━━━━━━━\n"
            f"👨‍💻 Админы онлайн: " + (f"<b>{', '.join(admin_names)}</b>" if admin_names else "<i>никого</i>")
        )
        await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=get_server_options_kb(db_name))
    except:
        await callback.message.edit_caption(caption="❌ Ошибка БД.", reply_markup=get_main_kb())

@router.callback_query(F.data.startswith("list_"))
async def show_admin_list(callback: types.CallbackQuery):
    db_name = callback.data.split("_")[1]
    _, _, online_admins = await get_extended_stats(db_name)
    if not online_admins:
        await callback.answer("❌ На сервере сейчас нет админов из списка.", show_alert=True)
        return
    await callback.message.edit_caption(caption="Выберите админа для выдачи <b>предупреждения</b>:", parse_mode="HTML", reply_markup=get_admin_choice_kb(online_admins, db_name))

@router.callback_query(F.data.startswith("warnuser_"))
async def start_warn_process(callback: types.CallbackQuery, state: FSMContext):
    target_id = callback.data.split("_")[1]
    await state.update_data(target_id=target_id)
    await state.set_state(WarnStates.waiting_for_reason)
    await callback.message.answer("📝 Введите причину предупреждения:")
    await callback.answer()

@router.message(WarnStates.waiting_for_reason)
async def confirm_warn_reason(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("target_id")
    reason = message.text

    await add_warning(target_id, reason)
    count = await get_warnings_count(target_id)

    try:
        msg_text = (
            f"⚠️ <b>ВАМ ВЫДАНО ПРЕДУПРЕЖДЕНИЕ!</b>\n\n"
            f"📄 Причина: <code>{reason}</code>\n"
            f"📊 Всего варнингов: <b>{count}</b>"
        )
        await bot_warn.send_message(chat_id=target_id, text=msg_text, parse_mode="HTML")
        await message.answer(f"✅ Предупреждение доставлено. Всего у админа: {count}")
    except:
        await message.answer("❌ Бот не смог отправить сообщение админу (возможно, он его заблокировал).")
    
    await state.clear()

@router.callback_query(F.data == "back_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_caption(caption="Выберите сервер:", reply_markup=get_main_kb())

@router.callback_query(F.data.startswith("warnuser_"))
async def start_warn_process(callback: types.CallbackQuery, state: FSMContext):
    target_id = callback.data.split("_")[1]
    
    # Отправляем новое сообщение и сохраняем его ID, чтобы потом удалить
    prompt_msg = await callback.message.answer("📝 Введите причину предупреждения:")
    
    await state.update_data(
        target_id=target_id, 
        last_menu_msg_id=callback.message.message_id, # ID сообщения с фото/меню
        prompt_msg_id=prompt_msg.message_id          # ID сообщения "Введите причину"
    )
    await state.set_state(WarnStates.waiting_for_reason)
    await callback.answer()

@router.message(WarnStates.waiting_for_reason)
async def confirm_warn_reason(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("target_id")
    menu_msg_id = data.get("last_menu_msg_id")
    prompt_msg_id = data.get("prompt_msg_id")
    reason = message.text

    # Сохраняем в БД
    await add_warning(target_id, reason)
    count = await get_warnings_count(target_id)

    # 1. Удаляем сообщение "Введите причину"
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_msg_id)
    except: pass

    # 2. Удаляем сообщение пользователя с текстом причины
    try:
        await message.delete()
    except: pass

    # 3. Уведомляем админа через второго бота
    try:
        msg_text = (
            f"⚠️ <b>ВАМ ВЫДАНО ПРЕДУПРЕЖДЕНИЕ!</b>\n\n"
            f"📄 Причина: <code>{reason}</code>\n"
            f"📊 Всего варнингов: <b>{count}</b>"
        )
        await bot_warn.send_message(chat_id=target_id, text=msg_text, parse_mode="HTML")
        alert_text = f"✅ Предупреждение доставлено. У админа теперь {count} пред-й."
    except:
        alert_text = "❌ Бот не смог отправить сообщение админу."

    # 4. Возвращаем меню выбора серверов
    # Мы редактируем то самое сообщение, где было фото и кнопки серверов
    await message.bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=menu_msg_id,
        caption=f"{alert_text}\n\nВыберите сервер:",
        reply_markup=get_main_kb()
    )
    
    await state.clear()