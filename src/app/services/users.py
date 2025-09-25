from sqlalchemy import select
from ..db import AsyncSessionLocal
from ..models import User

async def get_user_by_tg(tg_id: int):
    async with AsyncSessionLocal() as s:
        res = await s.execute(select(User).where(User.tg_id == tg_id))
        return res.scalar_one_or_none()

async def get_or_create_user(tg_id: int):
    async with AsyncSessionLocal() as s:
        res = await s.execute(select(User).where(User.tg_id == tg_id))
        u = res.scalar_one_or_none()
        if not u:
            u = User(tg_id=tg_id)
            s.add(u)
            await s.commit()
            await s.refresh(u)
        return u

async def update_user_tz(tg_id: int, tz: str):
    # простая валидация TZ
    from zoneinfo import ZoneInfo
    _ = ZoneInfo(tz)  # бросит исключение если TZ некорректна
    async with AsyncSessionLocal() as s:
        res = await s.execute(select(User).where(User.tg_id == tg_id))
        u = res.scalar_one_or_none()
        if not u:
            u = User(tg_id=tg_id, tz=tz)
            s.add(u)
        else:
            u.tz = tz
        await s.commit()
        # локальный импорт, чтобы избежать циклического
        from ..scheduler import schedule_user_jobs
        await schedule_user_jobs(u.tg_id, u.tz, u.morning_time, u.evening_time)

async def update_user_times(tg_id: int, morning: str | None = None, evening: str | None = None):
    async with AsyncSessionLocal() as s:
        res = await s.execute(select(User).where(User.tg_id == tg_id))
        u = res.scalar_one_or_none()
        if not u:
            u = User(tg_id=tg_id)
            s.add(u)
        if morning:
            u.morning_time = morning
        if evening:
            u.evening_time = evening
        await s.commit()
        from ..scheduler import schedule_user_jobs
        await schedule_user_jobs(u.tg_id, u.tz, u.morning_time, u.evening_time)

async def iter_users():
    async with AsyncSessionLocal() as s:
        res = await s.execute(select(User))
        for u in res.scalars().all():
            yield u

