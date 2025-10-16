# src/app/handlers/quick_mitt.py
import datetime as dt
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ForceReply
from sqlalchemy import select, delete

from ..db import AsyncSessionLocal
from ..models import MIT
from ..services.users import get_or_create_user

router = Router()

class MittFlow(StatesGroup):
    waiting_titles = State()

def _esc(s: str | None) -> str:
    s = s or ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _strip_leading_command(text: str) -> str:
    t = (text or "").strip()
    if t.lower().startswith("/mitt"):
        t = t[5:].strip()
    return t

def _parse_titles(payload: str) -> list[str]:
    payload = _strip_leading_command(payload)
    return [t.strip() for t in payload.split("|") if t.strip()][:3]

async def _save_tomorrow_mits(user_id: int, titles: list[str], target: dt.date):
    async with AsyncSessionLocal() as s:
        await s.execute(delete(MIT).where(MIT.user_id == user_id, MIT.for_date == target))
        # ВАЖНО: cat="day"
        s.add_all([MIT(user_id=user_id, title=t, for_date=target, cat="day") for t in titles])
        await s.commit()
        res = await s.execute(select(MIT).where(MIT.user_id == user_id, MIT.for_date == target))
        rows = res.scalars().all()
        try:
            rows.sort(key=lambda r: getattr(r, "id"))
        except Exception:
            pass
        return rows[:3]

@router.callback_query(F.data == "mitt:start")
async def mitt_start(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(MittFlow.waiting_titles)
    await cb.message.answer(
        "Введи 1–3 MIT на завтра в одной строке (через «|»):\n"
        "<code>Задача A | Задача B | Задача C</code>",
        parse_mode="HTML",
        reply_markup=ForceReply(selective=True),
    )
    await cb.answer()

@router.callback_query(F.data == "mitt:show")
async def mitt_show(cb: types.CallbackQuery):
    user = await get_or_create_user(cb.from_user.id)
    target = dt.date.today() + dt.timedelta(days=1)
    async with AsyncSessionLocal() as s:
        res = await s.execute(select(MIT).where(MIT.user_id == user.id, MIT.for_date == target))
        rows = res.scalars().all()
        try:
            rows.sort(key=lambda r: getattr(r, "id"))
        except Exception:
            pass

    if not rows:
        await cb.message.answer(f"На {target.isoformat()} MIT ещё нет.")
    else:
        lines = [f"<b>MIT на {target.isoformat()}:</b>"]
        for i, r in enumerate(rows[:3], start=1):
            lines.append(f"{i}) {_esc(getattr(r, 'title', ''))}")
        await cb.message.answer("\n".join(lines), parse_mode="HTML")
    await cb.answer()

@router.message(MittFlow.waiting_titles)
async def mitt_receive_state(m: types.Message, state: FSMContext):
    titles = _parse_titles(m.text or "")
    if not titles:
        await m.answer("Нужно хотя бы одно название. Пример:\n<code>Название | Вторая | Третья</code>", parse_mode="HTML")
        return

    user = await get_or_create_user(m.from_user.id)
    target = dt.date.today() + dt.timedelta(days=1)
    rows = await _save_tomorrow_mits(user.id, titles, target)

    lines = [f"<b>MIT на {target.isoformat()} сохранены:</b>"]
    for i, r in enumerate(rows, start=1):
        lines.append(f"{i}) {_esc(getattr(r, 'title', ''))}")
    await m.answer("\n".join(lines), parse_mode="HTML")
    await state.clear()

@router.message(
    F.reply_to_message,
    F.reply_to_message.from_user.is_bot == True,
    F.reply_to_message.text.func(lambda t: isinstance(t, str) and "Введи 1–3 MIT на завтра" in t),
)
async def mitt_receive_reply(m: types.Message):
    titles = _parse_titles(m.text or "")
    if not titles:
        await m.answer("Нужно хотя бы одно название. Пример:\n<code>Название | Вторая | Третья</code>", parse_mode="HTML")
        return

    user = await get_or_create_user(m.from_user.id)
    target = dt.date.today() + dt.timedelta(days=1)
    rows = await _save_tomorrow_mits(user.id, titles, target)

    lines = [f"<b>MIT на {target.isoformat()} сохранены:</b>"]
    for i, r in enumerate(rows, start=1):
        lines.append(f"{i}) {_esc(getattr(r, 'title', ''))}")
    await m.answer("\n".join(lines), parse_mode="HTML")

# ВАЖНО: командный /mitt здесь НЕ дублируем — он в mitt_cmd.py

