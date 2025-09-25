from aiogram import Router, types
from aiogram.filters import Command
from ..services.plan import add_horizon_tasks, list_horizon_tasks, delete_horizon_task_by_index, clear_horizon_tasks

router = Router()

HELP = (
    "План горизонтов:\n"
    "• Месяц: /plan month задача1 | задача2 | задача3\n"
    "• Неделя: /plan week задача1 | задача2 | задача3\n"
    "Посмотреть: /goals month  или  /goals week\n"
    "Удалить по номеру: /delmonth 2  |  /delweek 1\n"
    "Очистить всё: /clearmonth  |  /clearweek\n"
    "Дальше распиши день: /mit A | B | C"
)

@router.message(Command("plan"))
async def plan_cmd(m: types.Message):
    text = (m.text or "").strip()
    parts = text.split(maxsplit=2)
    if len(parts) == 1:
        await m.answer(HELP)
        return
    horizon = parts[1].lower()
    if horizon not in ("month", "week"):
        await m.answer("Укажи горизонт: /plan month ... или /plan week ...")
        return
    titles_raw = parts[2] if len(parts) >= 3 else ""
    titles = [p.strip() for p in titles_raw.split("|")]
    n = await add_horizon_tasks(m.from_user.id, horizon, titles)
    human = "месяца" if horizon == "month" else "недели"
    await m.answer(f"Добавлено в план {human}: {n}. Посмотреть: /goals {horizon}")

@router.message(Command("goals"))
async def goals_list(m: types.Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        await m.answer("Укажи горизонт: /goals month  или  /goals week")
        return
    horizon = parts[1].strip().lower()
    if horizon not in ("month", "week"):
        await m.answer("Горизонт только: month / week")
        return
    rows = await list_horizon_tasks(m.from_user.id, horizon)
    if not rows:
        await m.answer(f"На текущий {('месяц' if horizon=='month' else 'неделю')} задач пока нет.")
        return
    lines = [f"{i+1}) {r.title}" for i, r in enumerate(rows)]
    await m.answer(f"Задачи на {('месяц' if horizon=='month' else 'неделю')}:\n" + "\n".join(lines))

@router.message(Command("delmonth"))
async def del_month(m: types.Message):
    parts = m.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await m.answer("Используй: /delmonth <номер>, напр. /delmonth 2")
        return
    ok = await delete_horizon_task_by_index(m.from_user.id, "month", int(parts[1]))
    await m.answer("Удалено." if ok else "Не найдено. Посмотри номера: /goals month")

@router.message(Command("delweek"))
async def del_week(m: types.Message):
    parts = m.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await m.answer("Используй: /delweek <номер>, напр. /delweek 1")
        return
    ok = await delete_horizon_task_by_index(m.from_user.id, "week", int(parts[1]))
    await m.answer("Удалено." if ok else "Не найдено. Посмотри номера: /goals week")

@router.message(Command("clearmonth"))
async def clear_month(m: types.Message):
    n = await clear_horizon_tasks(m.from_user.id, "month")
    await m.answer(f"Удалено задач месяца: {n}")

@router.message(Command("clearweek"))
async def clear_week(m: types.Message):
    n = await clear_horizon_tasks(m.from_user.id, "week")
    await m.answer(f"Удалено задач недели: {n}")

