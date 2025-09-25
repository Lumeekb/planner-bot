import datetime as dt
from sqlalchemy import select, delete
from ..db import AsyncSessionLocal
from ..models import User, MIT, Subtask

async def add_sub_for_today_index(tg_id: int, index_1based: int, title: str):
    if index_1based not in (1, 2, 3):
        return False
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        today = dt.date.today()
        res = await s.execute(select(MIT).where(MIT.user_id == u.id, MIT.for_date == today).order_by(MIT.id))
        mits = res.scalars().all()
        if len(mits) < index_1based:
            return False
        target = mits[index_1based - 1]
        s.add(Subtask(user_id=u.id, mit_id=target.id, title=title.strip()))
        await s.commit()
        return True

async def list_subs_for_today(tg_id: int):
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        today = dt.date.today()
        res = await s.execute(select(MIT).where(MIT.user_id == u.id, MIT.for_date == today).order_by(MIT.id))
        mits = res.scalars().all()
        result = {1: [], 2: [], 3: []}
        for i, m in enumerate(mits[:3], start=1):
            subres = await s.execute(select(Subtask).where(Subtask.mit_id == m.id).order_by(Subtask.id))
            result[i] = subres.scalars().all()
        return result

async def toggle_sub_done(tg_id: int, mit_index: int, sub_index: int) -> bool:
    if mit_index not in (1,2,3) or sub_index < 1:
        return False
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        today = dt.date.today()
        res = await s.execute(select(MIT).where(MIT.user_id == u.id, MIT.for_date == today).order_by(MIT.id))
        mits = res.scalars().all()
        if len(mits) < mit_index:
            return False
        target_mit = mits[mit_index - 1]
        subs_res = await s.execute(select(Subtask).where(Subtask.mit_id == target_mit.id).order_by(Subtask.id))
        subs = subs_res.scalars().all()
        if len(subs) < sub_index:
            return False
        s_obj = subs[sub_index - 1]
        s_obj.done = not s_obj.done
        await s.commit()
        return True

async def delete_sub(tg_id: int, mit_index: int, sub_index: int) -> bool:
    if mit_index not in (1,2,3) or sub_index < 1:
        return False
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        today = dt.date.today()
        res = await s.execute(select(MIT).where(MIT.user_id == u.id, MIT.for_date == today).order_by(MIT.id))
        mits = res.scalars().all()
        if len(mits) < mit_index:
            return False
        target_mit = mits[mit_index - 1]
        subs_res = await s.execute(select(Subtask).where(Subtask.mit_id == target_mit.id).order_by(Subtask.id))
        subs = subs_res.scalars().all()
        if len(subs) < sub_index:
            return False
        del_obj = subs[sub_index - 1]
        await s.execute(delete(Subtask).where(Subtask.id == del_obj.id))
        await s.commit()
        return True

async def clear_subs_for_today_index(tg_id: int, mit_index: int) -> int:
    if mit_index not in (1,2,3):
        return 0
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        today = dt.date.today()
        res = await s.execute(select(MIT).where(MIT.user_id == u.id, MIT.for_date == today).order_by(MIT.id))
        mits = res.scalars().all()
        if len(mits) < mit_index:
            return 0
        target_mit = mits[mit_index - 1]
        subs_res = await s.execute(select(Subtask).where(Subtask.mit_id == target_mit.id))
        subs = subs_res.scalars().all()
        count = len(subs)
        if count:
            await s.execute(delete(Subtask).where(Subtask.mit_id == target_mit.id))
            await s.commit()
        return count

