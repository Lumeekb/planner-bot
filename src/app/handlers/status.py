from aiogram import Router, types
from aiogram.filters import Command
from ..services.mits import list_mits_today

router = Router()

@router.message(Command("status"))
async def status_cmd(m: types.Message):
    rows = await list_mits_today(m.from_user.id)
    mit_str = " | ".join([r.title or "—" for r in rows]) if rows else "— | — | —"
    await m.answer(f"Сегодняшние MIT: {mit_str}")

