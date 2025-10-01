# src/app/handlers/subtasks.py
import datetime as dt
import logging
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select

from ..db import AsyncSessionLocal
from ..models import MIT
from ..services.users import get_or_create_user
from ..services.subtasks import (
    add_sub_for_today_index,
    list_subs_for_today,
    toggle_sub_done,
    delete_sub,
)

router = Router()
log = logging.getLogger(__name__)


def _usage_sub() -> str:
    return (
        "Добавить подзадачу:\n"
        "/sub <MIT#> <текст>\n"
        "Напр.: /sub 1 Напечатать чек-лист"
    )


def _usage_done() -> str:
    return (
        "Отметить подзадачу выполненной:\n"
        "/subdone <MIT#> <№_подзадачи>\n"
        "Напр.: /subdone 1 2"
    )


def _usage_del() -> str:
    return (
        "Удалить подзадачу:\n"
        "/subdel <MIT#> <№_подзадачи>\n"
        "Напр.: /subdel 2 1"
    )


@router.message(Command("sub"))
async def sub_add(m: types.Message):
    """ /sub <MIT#> <текст> """
    text = (m.text or "").strip()
    parts = text.split(maxsplit=2)  # ['/sub', '1', 'текст...']
    if len(parts) < 3:
        await m.answer(_usage_sub())
        return

    mit_token = parts[1]
    if mit_token not in ("1", "2", "3"):
        await m.answer("Номер MIT должен быть 1, 2 или 3.\n" + _usage_sub())
        return

    title = parts[2].strip()
    if not title:
        await m.answer("Нужен текст подзадачи.\n" + _usage_sub())
        return

    ok = await add_sub_for_today_index(m.from_user.id, int(mit_token), title)
    await m.answer("✅ Подзадача добавлена." if ok else "⚠️ Не удалось. Проверь, что MIT на сегодня созданы: /mit")


@router.message(Command("subs"))
async def subs_list(m: types.Message):
    """
    Диагностическая версия /subs (v3):
    - сначала выводит метку и диагностические строки,
    - затем печатает названия MIT и подзадачи.
    Это нужно, чтобы найти реальное имя поля индекса в модели MIT.
    """
    # Маркер, чтобы точно видеть, что сработал новый хэндлер
    await m.answer("🆕 SUBS v3")

    try:
        user = await get_or_create_user(m.from_user.id)
        today = dt.date.today()
        await m.answer(f"diag: user_id={user.id}, tg_id={m.from_user.id}, date={today}")

        # 1) Берём MIT за сегодня (без order_by по неизвестному полю)
        async with AsyncSessionLocal() as s:
            result = await s.execute(
                select(MIT).where(MIT.user_id == user.id, MIT.for_date == today)
            )
            mits = result.scalars().all()

        await m.answer(f"diag: found MITs = {len(mits)}")

        # Покажем, какие поля у каждой записи могут быть номером
        candidates = ("index", "idx", "position", "order", "slot", "num", "i")
        diag_lines = ["diag: MIT fields snapshot:"]
        for mi in mits:
            values = [f"{name}={getattr(mi, name, None)!r}" for name in candidates]
            values.append(f"title={getattr(mi, 'title', None)!r}")
            diag_lines.append("  " + "; ".join(values))
        if len(diag_lines) > 1:
            await m.answer("\n".join(diag_lines))

        # 2) Универсально достанем номера 1..3 и названия
        def _mi_index(mi) -> int | None:
            for name in candidates:
                if hasattr(mi, name):
                    try:
                        val = getattr(mi, name)
                        if val is not None:
                            return int(val)
                    except Exception:
                        continue
            return None

        mit_titles: dict[int, str] = {}
        for mi in mits:
            idx = _mi_index(mi)
            if idx in (1, 2, 3):
                mit_titles[idx] = (getattr(mi, "title", None) or f"MIT #{idx}")

        await m.answer(f"diag: mit_titles keys = {sorted(mit_titles.keys()) or '[]'}")

        if not mit_titles:
            await m.answer("На сегодня MIT ещё не созданы. Добавь их командой:\n/mit Задача1 | Задача2 | Задача3")
            return

        # 3) Подзадачи dict: {1: [Sub], 2: [...], 3: [...]}
        data = await list_subs_for_today(m.from_user.id) or {}
        await m.answer(f"diag: subs buckets = {', '.join(str(k) for k in sorted(data.keys())) or 'none'}")

        # 4) Формируем вывод в порядке 1→2→3
        lines: list[str] = []
        for i in (1, 2, 3):
            parent_title = mit_titles.get(i, f"MIT #{i}")
            lines.append(f"MIT #{i} — {parent_title}")
            items = data.get(i, [])
            if not items:
                lines.append("  — подзадач пока нет")
            else:
                for j, s in enumerate(items, start=1):
                    if isinstance(s, dict):
                        done = s.get("done", False)
                        title = s.get("title", "")
                    else:
                        done = getattr(s, "done", False)
                        title = getattr(s, "title", "")
                    mark = "✅" if done else "⬜️"
                    lines.append(f"  {j}. {mark} {title}")
            lines.append("")

        # Подсказки
        lines.append("Добавить подзадачу:\n/sub <MIT#> <текст>\nНапр.: /sub 1 Напечатать чек-лист")
        lines.append("Отметить выполненной:\n/subdone <MIT#> <№_подзадачи>\nНапр.: /subdone 1 2")
        lines.append("Удалить подзадачу:\n/subdel <MIT#> <№_подзадачи>\nНапр.: /subdel 2 1")

        await m.answer("\n".join(lines))
    except Exception as e:
        log.exception("subs_list failed")
        await m.answer(f"⚠️ subs error: {type(e).__name__}: {e}")


@router.message(Command("subdone"))
async def sub_done(m: types.Message):
    """ /subdone <MIT#> <№_подзадачи> """
    parts = (m.text or "").split()
    if len(parts) != 3:
        await m.answer(_usage_done())
        return

    mit_token, sub_token = parts[1], parts[2]
    if mit_token not in ("1", "2", "3"):
        await m.answer("Номер MIT должен быть 1, 2 или 3.\n" + _usage_done())
        return

    try:
        mit_idx = int(mit_token)
        sub_idx = int(sub_token)
    except ValueError:
        await m.answer("Номера должны быть числами.\n" + _usage_done())
        return

    ok = await toggle_sub_done(m.from_user.id, mit_idx, sub_idx)
    await m.answer("✅ Готово." if ok else "⚠️ Не найдено. Проверь номера: /subs")


@router.message(Command("subdel"))
async def sub_del(m: types.Message):
    """ /subdel <MIT#> <№_подзадачи> """
    parts = (m.text or "").split()
    if len(parts) != 3:
        await m.answer(_usage_del())
        return

    mit_token, sub_token = parts[1], parts[2]
    if mit_token not in ("1", "2", "3"):
        await m.answer("Номер MIT должен быть 1, 2 или 3.\n" + _usage_del())
        return

    try:
        mit_idx = int(mit_token)
        sub_idx = int(sub_token)
    except ValueError:
        await m.answer("Номера должны быть числами.\n" + _usage_del())
        return

    ok = await delete_sub(m.from_user.id, mit_idx, sub_idx)
    await m.answer("🗑 Удалено." if ok else "⚠️ Не найдено. Проверь номера: /subs")

