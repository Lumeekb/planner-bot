from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo
from .services.reminders import send_morning_prompt, send_evening_prompt, send_weekly_prompt
from .services.users import iter_users

scheduler = AsyncIOScheduler()

async def schedule_user_jobs(tg_id: int, tz: str, morning: str, evening: str):
    # Снимаем старые
    for job_id in (f"morning_{tg_id}", f"evening_{tg_id}", f"weekly_{tg_id}"):
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass

    h, m = map(int, morning.split(":"))
    scheduler.add_job(
        send_morning_prompt,
        CronTrigger(hour=h, minute=m, timezone=ZoneInfo(tz)),
        args=[tg_id], id=f"morning_{tg_id}", replace_existing=True
    )

    h2, m2 = map(int, evening.split(":"))
    scheduler.add_job(
        send_evening_prompt,
        CronTrigger(hour=h2, minute=m2, timezone=ZoneInfo(tz)),
        args=[tg_id], id=f"evening_{tg_id}", replace_existing=True
    )

    # Пятничный weekly — по вечернему времени
    scheduler.add_job(
        send_weekly_prompt,
        CronTrigger(day_of_week="fri", hour=h2, minute=m2, timezone=ZoneInfo(tz)),
        args=[tg_id], id=f"weekly_{tg_id}", replace_existing=True
    )

async def startup_scheduler():
    async for u in iter_users():
        await schedule_user_jobs(u.tg_id, u.tz, u.morning_time, u.evening_time)
    scheduler.start()

