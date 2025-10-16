import datetime as dt
from sqlalchemy import select, delete
from ..db import AsyncSessionLocal
from ..models import MIT, User, Subtask

async def set_mits_for_today(tg_id: int, m1: str, m2: str, m3: str):
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        today = dt.date.today()
        await s.execute(delete(MIT).where(MIT.user_id == u.id, MIT.for_date == today))
        cat = cat or "day"
        recs = [MIT(user_id=u.id, for_date=today, cat=cat, title=title or "")
                for cat, title in zip(["A", "B", "C"], [m1, m2, m3])]
        s.add_all(recs)
        await s.commit()

async def list_mits_today(tg_id: int):
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        today = dt.date.today()
        res = await s.execute(
            select(MIT).where(MIT.user_id == u.id, MIT.for_date == today).order_by(MIT.id)
        )
        return res.scalars().all()

async def delete_mit_today_by_index(tg_id: int, index_1based: int) -> bool:
    if index_1based not in (1,2,3):
        return False
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        today = dt.date.today()
        res = await s.execute(select(MIT).where(MIT.user_id == u.id, MIT.for_date == today).order_by(MIT.id))
        mits = res.scalars().all()
        if len(mits) < index_1based:
            return False
        target = mits[index_1based - 1]
        # удалим подзадачи этого MIT
        await s.execute(delete(Subtask).where(Subtask.mit_id == target.id))
        await s.execute(delete(MIT).where(MIT.id == target.id))
        await s.commit()
        return True

async def clear_mits_today(tg_id: int) -> int:
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        today = dt.date.today()
        res = await s.execute(select(MIT.id).where(MIT.user_id == u.id, MIT.for_date == today))
        ids = [mid for (mid,) in res.all()]
        if not ids:
            return 0
        # remove subtasks for all these MITs
        await s.execute(delete(Subtask).where(Subtask.mit_id.in_(ids)))
        await s.execute(delete(MIT).where(MIT.id.in_(ids)))
        await s.commit()
        return len(ids)

