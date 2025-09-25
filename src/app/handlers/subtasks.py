from aiogram import Router, types
from aiogram.filters import Command
from ..services.subtasks import add_sub_for_today_index, list_subs_for_today, toggle_sub_done, delete_sub, clear_subs_for_today_index

router = Router()

@router.message(Command("sub"))
async def sub_add(m: types.Message):
    payload = m.text.replace("/sub", "", 1).strip()
    if not payload or payload.split()[0] not in ("1", "2", "3"):
        await m.answer("Используй: /sub 1 Текст подзадачи (1, 2 или 3 — номер MIT на сегодня)")
        return
    parts = payload.split(maxsplit=1)
    idx = int(parts[0])
    title = parts[1] if len(parts) > 1 else ""
    ok = await add_sub_for_today_index(m.from_user.id, idx, title)
    await m.answer("Подзадача добавлена." if ok else "Не получилось: убедись, что MIT на сегодня заданы (/mit ...)")

@router.message(Command("subs"))
async def subs_list(m: types.Message):
    data = await list_subs_for_today(m.from_user.id)
    lines = []
    for i in (1,2,3):
        items = data.get(i, [])
        if not items:
            lines.append(f"MIT #{i}: —")
        else:
            for j, s in enumerate(items, start=1):
                mark = "✅" if s.done else "⬜️"
                lines.append(f"MIT #{i}.{j}: {mark} {s.title}")
    await m.answer("\n".join(lines) if lines else "Подзадач нет.")

@router.message(Command("subdone"))
async def sub_done(m: types.Message):
    parts = m.text.split()
    if len(parts) != 3 or parts[1] not in ("1","2","3"):
        await m.answer("Используй: /subdone <mit#> <sub#>, напр. /subdone 1 2")
        return
    ok = await toggle_sub_done(m.from_user.id, int(parts[1]), int(parts[2]))
    await m.answer("Готово." if ok else "Не найдено. Проверь номера: /subs")

@router.message(Command("subdel"))
async def sub_del(m: types.Message):
    parts = m.text.split()
    if len(parts) != 3 or parts[1] not in ("1","2","3"):
        await m.answer("Используй: /subdel <mit#> <sub#>, напр. /subdel 1 2")
        return
    ok = await delete_sub(m.from_user.id, int(parts[1]), int(parts[2]))
    await m.answer("Удалено." if ok else "Не найдено. Проверь номера: /subs")

@router.message(Command("subclear"))
async def sub_clear(m: types.Message):
    parts = m.text.split()
    if len(parts) != 2 or parts[1] not in ("1","2","3"):
        await m.answer("Используй: /subclear <mit#>, напр. /subclear 2")
        return
    n = await clear_subs_for_today_index(m.from_user.id, int(parts[1]))
    await m.answer(f"Удалено подзадач: {n}")

