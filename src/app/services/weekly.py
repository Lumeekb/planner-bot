import datetime as dt
from sqlalchemy import select
from ..db import AsyncSessionLocal
from ..models import User, MIT, Review

def _days_last_7():
    today = dt.date.today()
    return [today - dt.timedelta(days=i) for i in range(6, -1, -1)]

def _fmt(d: dt.date) -> str:
    return d.strftime("%d.%m")

async def build_weekly_report(tg_id: int) -> str:
    days = _days_last_7()
    start, end = days[0], days[-1]

    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        mits = (await s.execute(
            select(MIT).where(MIT.user_id == u.id, MIT.for_date >= start, MIT.for_date <= end)
        )).scalars().all()
        reviews = (await s.execute(
            select(Review).where(Review.user_id == u.id, Review.for_date >= start, Review.for_date <= end)
        )).scalars().all()

    mit_by_day = {d: [] for d in days}
    for m in mits:
        mit_by_day.setdefault(m.for_date, []).append(m.title)

    wins_all = []
    review_days = set()
    for r in reviews:
        review_days.add(r.for_date)
        if isinstance(r.wins, list):
            wins_all.extend([w for w in r.wins if w])

    mit_days = {d for d, lst in mit_by_day.items() if lst}
    missing_mit = [d for d in days if d not in mit_days]
    missing_reviews = [d for d in days if d not in review_days]

    header = f"📅 Weekly ({_fmt(start)}–{_fmt(end)}):"
    kpi = f"• Дни с MIT: {len(mit_days)}/7  |  Дни с отчётом: {len(review_days)}/7"
    wins_block = "• Топ побед:\n" + ("\n".join([f"  – {w}" for w in wins_all[:5]]) if wins_all else "  – (нет данных)")

    missing_parts = []
    if missing_mit:
        missing_parts.append("• Нет MIT: " + ", ".join(_fmt(d) for d in missing_mit))
    if missing_reviews:
        missing_parts.append("• Нет отчёта дня: " + ", ".join(_fmt(d) for d in missing_reviews))
    if not missing_parts:
        missing_parts.append("• Пробелов нет — так держать!")

    next_steps = (
        "➡️ Следующие шаги:\n"
        "  1) Выбери 1–3 MIT на понедельник: /mit Задача1 | Задача2 | Задача3\n"
        "  2) Запланируй первый фокус-спринт: /sprint 50 10\n"
        "  3) Вечером — /close и /review «победа1 | победа2 | победа3 | что мешало | уроки»"
    )

    return "\n".join([header, kpi, wins_block, *missing_parts, next_steps])

