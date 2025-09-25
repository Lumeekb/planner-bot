import datetime as dt
from sqlalchemy import select, delete
from ..db import AsyncSessionLocal
from ..models import User, HorizonTask

def month_anchor(today: dt.date | None = None) -> dt.date:
    d = today or dt.date.today()
    return dt.date(d.year, d.month, 1)

def week_anchor(today: dt.date | None = None) -> dt.date:
    d = today or dt.date.today()
    return d - dt.timedelta(days=d.weekday())

async def add_horizon_tasks(tg_id: int, horizon: str, titles: list[str]):
    assert horizon in ("month", "week")
    anchor = month_anchor() if horizon == "month" else week_anchor()
    titles = [t.strip() for t in titles if t.strip()]
    if not titles:
        return 0
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        recs = [HorizonTask(user_id=u.id, horizon=horizon, anchor_date=anchor, title=t) for t in titles]
        s.add_all(recs)
        await s.commit()
        return len(recs)

async def list_horizon_tasks(tg_id: int, horizon: str):
    assert horizon in ("month", "week")
    anchor = month_anchor() if horizon == "month" else week_anchor()
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        res = await s.execute(
            select(HorizonTask).where(
                HorizonTask.user_id == u.id,
                HorizonTask.horizon == horizon,
                HorizonTask.anchor_date == anchor
            ).order_by(HorizonTask.id)
        )
        return res.scalars().all()

async def delete_horizon_task_by_index(tg_id: int, horizon: str, index_1based: int) -> bool:
    if horizon not in ("month", "week") or index_1based < 1:
        return False
    anchor = month_anchor() if horizon == "month" else week_anchor()
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        res = await s.execute(
            select(HorizonTask).where(
                HorizonTask.user_id == u.id,
                HorizonTask.horizon == horizon,
                HorizonTask.anchor_date == anchor
            ).order_by(HorizonTask.id)
        )
        rows = res.scalars().all()
        if len(rows) < index_1based:
            return False
        target = rows[index_1based - 1]
        await s.execute(delete(HorizonTask).where(HorizonTask.id == target.id))
        await s.commit()
        return True

async def clear_horizon_tasks(tg_id: int, horizon: str) -> int:
    if horizon not in ("month", "week"):
        return 0
    anchor = month_anchor() if horizon == "month" else week_anchor()
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        res = await s.execute(
            select(HorizonTask.id).where(
                HorizonTask.user_id == u.id,
                HorizonTask.horizon == horizon,
                HorizonTask.anchor_date == anchor
            )
        )
        ids = [rid for (rid,) in res.all()]
        if not ids:
            return 0
        await s.execute(delete(HorizonTask).where(HorizonTask.id.in_(ids)))
        await s.commit()
        return len(ids)

