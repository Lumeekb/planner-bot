from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
import datetime as dt
from ..services.export import build_full_csv_month_week_days

router = Router()

@router.message(Command("export"))
async def export_cmd(m: types.Message):
    data = await build_full_csv_month_week_days(m.from_user.id)
    fname = f"planner_full_{dt.date.today().strftime('%Y-%m')}.csv"
    await m.answer_document(BufferedInputFile(data, filename=fname), caption="Экспорт: Месяц → Неделя → Дни (с подзадачами)")

