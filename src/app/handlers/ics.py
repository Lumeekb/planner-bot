from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
import datetime as dt
from ..services.ics import ics_today_mits

router = Router()

@router.message(Command("ics"))
async def ics_cmd(m: types.Message):
    text = await ics_today_mits(m.from_user.id)
    fname = f"planner_today_{dt.date.today().isoformat()}.ics"
    await m.answer_document(BufferedInputFile(text.encode("utf-8"), filename=fname), caption="iCal для сегодняшних MIT")

