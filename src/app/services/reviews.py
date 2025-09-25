import datetime as dt
from sqlalchemy import select, delete
from ..db import AsyncSessionLocal
from ..models import Review, User

async def save_review(tg_id: int, wins_text: str, blockers: str, lessons: str):
    """Сохраняет отчёт за сегодня. wins_text — строка 'победа1 | победа2 | победа3'."""
    wins = [w.strip() for w in (wins_text or "").split("|") if w.strip()]
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        today = dt.date.today()
        # перезаписываем отчёт на сегодня
        await s.execute(delete(Review).where(Review.user_id == u.id, Review.for_date == today))
        s.add(Review(user_id=u.id, for_date=today, wins=wins, blockers=blockers or "", lessons=lessons or ""))
        await s.commit()

