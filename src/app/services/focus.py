import datetime as dt
from zoneinfo import ZoneInfo
from apscheduler.triggers.date import DateTrigger

from ..bot import bot
from ..scheduler import scheduler
from ..services.users import get_user_by_tg

async def start_focus_cycle(tg_id: int, work_min: int = 50, break_min: int = 10):
    """Запускает спринт: work_min работы, break_min перерыв."""
    user = await get_user_by_tg(tg_id)
    tz = ZoneInfo(user.tz if user and user.tz else "Europe/Helsinki")
    now = dt.datetime.now(tz)

    await bot.send_message(tg_id, f"⏱ Спринт начат: {work_min} мин фокуса. Телефон — в сторону.")

    # Сообщение о начале перерыва
    work_end = now + dt.timedelta(minutes=work_min)
    scheduler.add_job(
        bot.send_message,
        trigger=DateTrigger(run_date=work_end),
        args=[tg_id, f"🧘 Перерыв {break_min} мин. Встань, разминка/вода/глаза."]
    )

    # Сообщение о завершении перерыва
    break_end = work_end + dt.timedelta(minutes=break_min)
    scheduler.add_job(
        bot.send_message,
        trigger=DateTrigger(run_date=break_end),
        args=[tg_id, "🚀 Перерыв окончен. Возвращайся к фокусу."]
    )

