# src/app/handlers/mit.py
import datetime as dt
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select, delete

from ..db import AsyncSessionLocal
from ..models import MIT
from ..services.users import get_or_create_user

router = Router()

def _esc(s: str | None) -> str:
    s = s or ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _parse_titles(payload: str) -> list[str]:
    return [t.strip() for t in payload.split("|") if t.strip()][:3]

@router.message(Command("mit"))
async def mit_today(m: types.Message):
    """
    /mit A | B | C     → сохранить 1–3 MIT на СЕГОДНЯ
    """
    text = (m.text or "")
    payload = text.replace("/mit", "", 1).strip()

    if not payload:
        await m.answer(
            "Поставь MIT на сегодня:\n"
            "<code>/mit Задача1 | Задача2 | Задача3</code>",
            parse_mode="HTML",
        )
        return

    titles = _parse_titles(payload)
    if not titles:
        await m.answer(
            "Нужно хотя бы одно название. Пример:\n"
            "<code>/mit A | B | C</code>",
            parse_mode="HTML",
        )
        return

    user = await get_or_create_user(m.from_user.id)
    target = dt.date.today()

    async with AsyncSessionLocal() as s:
        # чистим ТОЛЬКО дневные MIT за сегодня
        await s.execute(
            delete(MIT).where(
                MIT.user_id == user.id,
                MIT.for_date == target,
                MIT.cat == "day",
            )
        )
        # записываем новые, ОБЯЗАТЕЛЬНО cat="day"
        s.add_all([MIT(user_id=user.id, title=t, for_date=target, cat="day") for t in titles])
        await s.commit()

        res = await s.execute(
            select(MIT).where(MIT.user_id == user.id, MIT.for_date == target, MIT.cat == "day")
        )
        rows = res.scalars().all()
        try:
            rows.sort(key=lambda r: getattr(r, "id"))
        except Exception:
            pass

    lines = [f"<b>MIT на сегодня сохранены:</b>"]
    for i, r in enumerate(rows[:3], start=1):
        lines.append(f"{i}) {_esc(getattr(r, 'title', ''))}")
    await m.answer("\n".join(lines), parse_mode="HTML")

