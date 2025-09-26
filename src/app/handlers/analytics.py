from aiogram import Router, types
from aiogram.filters import Command
from ..services.analytics import log_event, get_stats, is_admin

router = Router()

@router.message(Command("whoami"))
async def whoami_cmd(m: types.Message):
    await m.answer(f"🆔 Твой Telegram ID: <code>{m.from_user.id}</code>")

@router.message(Command("stats"))
async def stats_cmd(m: types.Message):
    # доступ только для администратора (ID из ADMIN_IDS в .env)
    if not is_admin(m.from_user.id):
        await m.answer("⛔️ Команда /stats доступна только администратору.")
        return
    data = await get_stats()
    text = (
        "📊 <b>Статистика (глобально)</b>\n"
        f"👥 Всего пользователей: <b>{data['total']}</b>\n"
        f"🔥 Активные за 7 дней: <b>{data['active7']}</b>\n"
        f"📆 Активные за 30 дней: <b>{data['active30']}</b>\n"
        f"🆕 Новые за 7 дней: <b>{data['new7']}</b>\n"
    )
    await m.answer(text)

# ЛОГИРУЕМ ЛЮБОЕ входящее сообщение (этот роутер должен быть ПОДКЛЮЧЕН ПОСЛЕДНИМ)
@router.message()
async def _log_everything(m: types.Message):
    try:
        await log_event(m.from_user.id, m.text or "")
    except Exception:
        # не мешаем остальным обработчикам
        pass

