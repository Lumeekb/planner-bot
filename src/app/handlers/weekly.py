from aiogram import Router, types
from aiogram.filters import Command
from ..services.weekly import build_weekly_report

router = Router()

@router.message(Command("weekly"))
async def weekly_cmd(m: types.Message):
    text = await build_weekly_report(m.from_user.id)
    await m.answer(text)


