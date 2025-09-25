from aiogram import Router, types
from aiogram.filters import Command
from ..services.mits import (
    set_mits_for_today,
    list_mits_today,
    delete_mit_today_by_index,
    clear_mits_today,
)

router = Router()

@router.message(Command("mit"))
async def mit_cmd(m: types.Message):
    # формат: /mit задача1 | задача2 | задача3
    payload = m.text.replace("/mit", "", 1).strip()
    parts = [p.strip(" |") for p in payload.split("|")] if payload else []
    while len(parts) < 3:
        parts.append("")
    m1, m2, m3 = parts[:3]
    await set_mits_for_today(m.from_user.id, m1, m2, m3)
    rows = await list_mits_today(m.from_user.id)
    text = "MIT на сегодня:\n" + "\n".join([f"{i+1}) {r.title or '—'}" for i, r in enumerate(rows)])
    await m.answer(text)

@router.message(Command("delmit"))
async def del_mit(m: types.Message):
    parts = m.text.split()
    if len(parts) != 2 or parts[1] not in ("1","2","3"):
        await m.answer("Используй: /delmit <1|2|3>, напр. /delmit 2")
        return
    ok = await delete_mit_today_by_index(m.from_user.id, int(parts[1]))
    await m.answer("Удалено." if ok else "Не найдено. Проверь: /status")

@router.message(Command("clearmit"))
async def clear_mit(m: types.Message):
    n = await clear_mits_today(m.from_user.id)
    await m.answer(f"Удалено задач на сегодня: {n}")

