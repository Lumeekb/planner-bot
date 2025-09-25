import datetime as dt
from sqlalchemy import select
from ..db import AsyncSessionLocal
from ..models import User, MIT

def _ical_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")

async def ics_today_mits(tg_id: int) -> str:
    today = dt.date.today()
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        res = await s.execute(select(MIT).where(MIT.user_id == u.id, MIT.for_date == today).order_by(MIT.id))
        mits = res.scalars().all()

    lines = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//PlannerBot//EN"]
    for i, m in enumerate(mits, start=1):
        dtstamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        d = today.strftime("%Y%m%d")
        summary = _ical_escape(f"MIT: {m.title or '(без названия)'}")
        uid = f"{d}-{i}@plannerbot"
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART;VALUE=DATE:{d}",
            f"DTEND;VALUE=DATE:{d}",
            f"SUMMARY:{summary}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)

