from aiogram import Router, types
from aiogram.filters import Command
from ..services.users import update_user_times, update_user_tz, get_user_by_tg

router = Router()

@router.message(Command("timezone"))
async def set_timezone(m: types.Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        await m.answer("Укажи таймзону, например: /timezone Europe/Helsinki")
        return
    tz = parts[1].strip()
    try:
        await update_user_tz(m.from_user.id, tz)
        await m.answer(f"Таймзона обновлена: {tz}")
    except Exception:
        await m.answer("Некорректная таймзона. Примеры: Europe/Helsinki, Asia/Almaty, Europe/Moscow")

@router.message(Command("morning"))
async def set_morning(m: types.Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2 or ":" not in parts[1]:
        await m.answer("Укажи время: /morning 09:15")
        return
    await update_user_times(m.from_user.id, morning=parts[1].strip())
    await m.answer(f"Утреннее напоминание: {parts[1].strip()} ✓")

@router.message(Command("evening"))
async def set_evening(m: types.Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2 or ":" not in parts[1]:
        await m.answer("Укажи время: /evening 21:30")
        return
    await update_user_times(m.from_user.id, evening=parts[1].strip())
    await m.answer(f"Вечернее напоминание: {parts[1].strip()} ✓")

