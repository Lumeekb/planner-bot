from aiogram import Router, types
from aiogram.filters import Command
from ..services.focus import start_focus_cycle

router = Router()

@router.message(Command("sprint"))
async def sprint_cmd(m: types.Message):
    """
    Формат:
      /sprint            -> 50 10
      /sprint 25         -> 25 5
      /sprint 40 10      -> 40 10
    """
    payload = m.text.replace("/sprint", "", 1).strip()
    parts = [p for p in payload.split() if p.isdigit()]

    if len(parts) == 0:
        work, brk = 50, 10
    elif len(parts) == 1:
        work, brk = int(parts[0]), 5
    else:
        work, brk = int(parts[0]), int(parts[1])

    # Ограничим разумные диапазоны
    work = max(1, min(work, 180))
    brk  = max(1, min(brk, 60))

    await start_focus_cycle(m.from_user.id, work, brk)
    await m.answer(f"✅ Запущен спринт: {work} мин фокус → {brk} мин перерыв.")

