# src/app/handlers/mitt_cmd.py
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

def _strip_leading_command(text: str) -> str:
    t = (text or "").strip()
    # если пользователь по привычке прислал "/mitt A | B"
    if t.lower().startswith("/mitt"):
        t = t[5:].strip()
    return t

def _parse_titles(payload: str) -> list[str]:
    payload = _strip_leading_command(payload)
    return [t.strip() for t in payload.split("|") if t.strip()][:3]

def _parse_date(token: str | None, default: dt.date) -> dt.date:
    if not token:
        return default
    t = token.strip().lower()
    if t in ("tomorrow", "завтра"):
        return default
    if t in ("today", "сегодня"):
        return dt.date.today()
    try:
        return dt.date.fromisoformat(t)  # YYYY-MM-DD
    except Exception:
        return default

@router.message(Command("mitt"))
async def mitt_cmd(m: types.Message):
    """
    /mitt A | B | C                → сохранить MIT на завтра
    /mitt 2025-10-05 A | B | C     → на конкретную дату
    /mitt today A | B | C          → на сегодня
    """
    text = (m.text or "")
    payload = text.replace("/mitt", "", 1).strip()
    if not payload:
        await m.answer(
            "Поставь MIT:\n"
            "<code>/mitt Задача1 | Задача2 | Задача3</code>\n"
            "Или на дату: <code>/mitt 2025-10-05 Задача1 | Задача2</code>",
            parse_mode="HTML",
        )
        return

    # Если первым токеном идёт дата/слово — используем его
    head, *rest = payload.split(maxsplit=1)
    default_date = dt.date.today() + dt.timedelta(days=1)
    parsed = None
    try:
        parsed = _parse_date(head, None)  # type: ignore[arg-type]
    except Exception:
        parsed = None

    if parsed:
        target = parsed
        titles_str = rest[0] if rest else ""
    else:
        target = default_date
        titles_str = payload

    titles = _parse_titles(titles_str)
    if not titles:
        await m.answer(
            "Нужно указать хотя бы одну задачу. Пример:\n"
            "<code>/mitt A | B | C</code>",
            parse_mode="HTML",
        )
        return

    user = await get_or_create_user(m.from_user.id)

    async with AsyncSessionLocal() as s:
        # Перезапишем MIT на нужную дату
        await s.execute(delete(MIT).where(MIT.user_id == user.id, MIT.for_date == target))
        # ВАЖНО: заполняем cat, чтобы не ловить NOT NULL
        s.add_all([MIT(user_id=user.id, title=t, for_date=target, cat="day") for t in titles])
        await s.commit()

        res = await s.execute(select(MIT).where(MIT.user_id == user.id, MIT.for_date == target))
        rows = res.scalars().all()
        try:
            rows.sort(key=lambda r: getattr(r, "id"))
        except Exception:
            pass

    lines = [f"<b>MIT на {target.isoformat()} сохранены:</b>"]
    for i, r in enumerate(rows[:3], start=1):
        lines.append(f"{i}) {_esc(getattr(r, 'title', ''))}")
    await m.answer("\n".join(lines), parse_mode="HTML")

@router.message(Command("mitshow"))
async def mitshow_cmd(m: types.Message):
    """
    /mitshow                 → показать MIT на завтра
    /mitshow today|tomorrow  → на сегодня/завтра
    /mitshow YYYY-MM-DD      → на дату
    """
    token = (m.text or "").replace("/mitshow", "", 1).strip()
    target = _parse_date(token, dt.date.today() + dt.timedelta(days=1))

    user = await get_or_create_user(m.from_user.id)
    async with AsyncSessionLocal() as s:
        res = await s.execute(select(MIT).where(MIT.user_id == user.id, MIT.for_date == target))
        rows = res.scalars().all()
        try:
            rows.sort(key=lambda r: getattr(r, "id"))
        except Exception:
            pass

    if not rows:
        await m.answer(f"На {target.isoformat()} MIT ещё нет.")
        return

    lines = [f"<b>MIT на {target.isoformat()}:</b>"]
    for i, r in enumerate(rows[:3], start=1):
        lines.append(f"{i}) {_esc(getattr(r, 'title', ''))}")
    await m.answer("\n".join(lines), parse_mode="HTML")

