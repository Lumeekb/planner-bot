# src/app/handlers/subtasks.py
import datetime as dt
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


def _usage_sub() -> str:
    return (
        "Добавить подзадачу:\n"
        "<code>/sub &lt;MIT#&gt; &lt;текст&gt;</code>\n"
        "Напр.: <code>/sub 1 Напечатать чек-лист</code>"
    )


def _usage_done() -> str:
    return (
        "Отметить подзадачу выполненной:\n"
        "<code>/subdone &lt;MIT#&gt; &lt;№_подзадачи&gt;</code>\n"
        "Напр.: <code>/subdone 1 2</code>"
    )


def _usage_del() -> str:
    return (
        "Удалить подзадачу:\n"
        "<code>/subdel &lt;MIT#&gt; &lt;№_подзадачи&gt;</code>\n"
        "Напр.: <code>/subdel 2 1</code>"
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
    """ Показать подзадачи на сегодня с НАЗВАНИЯМИ родительских MIT. """
    # метка, чтобы убедиться, что срабатывает НОВЫЙ обработчик (можно удалить позже)
    await m.answer("🆕 SUBS v2")

    user = await get_or_create_user(m.from_user.id)
    today = dt.date.today()

    # 1) Названия MIT на сегодня
    async with AsyncSessionLocal() as s:
        result = await s.execute(
            select(MIT)
            .where(MIT.user_id == user.id, MIT.for_date == today)
            .order_by(MIT.index)
        )
        mits = result.scalars().all()

    mit_titles = {mi.index: (mi.title or f"MIT #{mi.index}") for mi in mits}

    if not mit_titles:
        await m.answer("На сегодня MIT ещё не созданы. Добавь их командой:\n/mit Задача1 | Задача2 | Задача3")
        return

    # 2) Подзадачи dict: {1: [Sub], 2: [...], 3: [...]}
    data = await list_subs_for_today(m.from_user.id) or {}

    # 3) Формируем вывод
    lines: list[str] = []
    for i in (1, 2, 3):
        parent_title = mit_titles.get(i, f"MIT #{i}")
        lines.append(f"<b>MIT #{i} — {parent_title}</b>")
        items = data.get(i, [])
        if not items:
            lines.append("  — подзадач пока нет")
        else:
            for j, s in enumerate(items, start=1):
                # поддержим и объекты, и словари
                done = getattr(s, "done", None)
                if done is None and isinstance(s, dict):
                    done = s.get("done", False)
                title = getattr(s, "title", None)
                if title is None and isinstance(s, dict):
                    title = s.get("title", "")
                mark = "✅" if done else "⬜️"
                lines.append(f"  {j}. {mark} {title}")
        lines.append("")  # пустая строка между блоками

    # Подсказки
    lines.append(_usage_sub())
    lines.append(_usage_done())
    lines.append(_usage_del())

    await m.answer("\n".join(lines))


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

