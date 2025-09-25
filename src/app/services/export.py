import io, csv, datetime as dt
from sqlalchemy import select
from ..db import AsyncSessionLocal
from ..models import User, MIT, Review, HorizonTask, Subtask

def first_day_of_month(today: dt.date | None = None) -> dt.date:
    d = today or dt.date.today()
    return dt.date(d.year, d.month, 1)

def monday_of_week(today: dt.date | None = None) -> dt.date:
    d = today or dt.date.today()
    return d - dt.timedelta(days=d.weekday())  # понедельник ISO

async def build_full_csv_month_week_days(tg_id: int) -> bytes:
    """CSV в порядке: MONTH -> WEEK -> DAY (с SUBTASK). Дни с 1-го числа текущего месяца по сегодня."""
    today = dt.date.today()
    month_anchor = first_day_of_month(today)
    week_anchor = monday_of_week(today)

    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()

        # Месяц (текущий)
        month_rows = (await s.execute(
            select(HorizonTask)
            .where(HorizonTask.user_id == u.id,
                   HorizonTask.horizon == "month",
                   HorizonTask.anchor_date == month_anchor)
            .order_by(HorizonTask.id)
        )).scalars().all()

        # Неделя (текущая, с понедельника)
        week_rows = (await s.execute(
            select(HorizonTask)
            .where(HorizonTask.user_id == u.id,
                   HorizonTask.horizon == "week",
                   HorizonTask.anchor_date == week_anchor)
            .order_by(HorizonTask.id)
        )).scalars().all()

        # Дни (с 1-го числа месяца по сегодня) — MIT + Subtasks
        mits_rows = (await s.execute(
            select(MIT)
            .where(MIT.user_id == u.id, MIT.for_date >= month_anchor, MIT.for_date <= today)
            .order_by(MIT.for_date, MIT.id)
        )).scalars().all()

        # Соберём подзадачи по mit_id
        mit_ids = [m.id for m in mits_rows]
        subtasks_map = {mid: [] for mid in mit_ids}
        if mit_ids:
            subs = (await s.execute(
                select(Subtask).where(Subtask.mit_id.in_(mit_ids)).order_by(Subtask.id)
            )).scalars().all()
            for s_obj in subs:
                subtasks_map.setdefault(s_obj.mit_id, []).append(s_obj)

    # Пишем CSV
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([
        "section",          # MONTH | WEEK | DAY | SUBTASK
        "anchor_or_date",   # YYYY-MM-DD (месяц=1-е число, неделя=понедельник, день=дата)
        "horizon",          # month/week/'' (для DAY/SUBTASK — пусто)
        "mit_index",        # 1..3 для DAY (индекс MIT в дне)
        "cat",              # A/B/C (для DAY)
        "title",            # текст задачи
        "done",             # 0/1
        "notes",            # заметки (для MONTH/WEEK можно не пусто)
        "parent_mit_index", # для SUBTASK: к какому MIT относится
        "sub_index"         # порядковый № подзадачи в MIT
    ])

    # 1) MONTH
    for t in month_rows:
        w.writerow(["MONTH", month_anchor.isoformat(), "month", "", "", t.title, 1 if t.done else 0, (t.notes or ""), "", ""])

    # 2) WEEK
    for t in week_rows:
        w.writerow(["WEEK", week_anchor.isoformat(), "week", "", "", t.title, 1 if t.done else 0, (t.notes or ""), "", ""])

    # 3) DAYS (с подзадачами)
    # сгруппируем по дате
    by_date = {}
    for m in mits_rows:
        by_date.setdefault(m.for_date, []).append(m)

    for d in sorted(by_date.keys()):
        day_mits = by_date[d]
        # вычислим индекс 1..3 в порядке id
        for idx, m in enumerate(day_mits, start=1):
            w.writerow(["DAY", d.isoformat(), "", idx, m.cat, m.title or "", 1 if m.done else 0, "", "", ""])
            subs = subtasks_map.get(m.id, [])
            for s_idx, s in enumerate(subs, start=1):
                w.writerow(["SUBTASK", d.isoformat(), "", "", "", s.title or "", 1 if s.done else 0, "", idx, s_idx])

    return buf.getvalue().encode("utf-8")

# Старую функцию на 7 дней оставим (если вызывалась где-то), но можно не использовать.
async def build_week_csv(tg_id: int) -> bytes:
    days = [dt.date.today() - dt.timedelta(days=i) for i in range(6, -1, -1)]
    start, end = days[0], days[-1]
    async with AsyncSessionLocal() as s:
        u = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one()
        mits = (await s.execute(
            select(MIT).where(MIT.user_id == u.id, MIT.for_date >= start, MIT.for_date <= end)
        )).scalars().all()
        reviews = (await s.execute(
            select(Review).where(Review.user_id == u.id, Review.for_date >= start, Review.for_date <= end)
        )).scalars().all()
    # простой CSV за неделю — как было
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["date", "mit_A", "mit_B", "mit_C", "wins", "blockers", "lessons"])
    mit_map = {d: {"A": "", "B": "", "C": ""} for d in days}
    for m in mits:
        mit_map.setdefault(m.for_date, {"A": "", "B": "", "C": ""})
        mit_map[m.for_date][m.cat] = m.title or ""
    review_map = {r.for_date: r for r in reviews}
    for d in days:
        mrow = mit_map.get(d, {"A": "", "B": "", "C": ""})
        rev = review_map.get(d)
        wins = " | ".join(rev.wins) if rev and isinstance(rev.wins, list) else ""
        blockers = rev.blockers if rev else ""
        lessons = rev.lessons if rev else ""
        w.writerow([d.isoformat(), mrow["A"], mrow["B"], mrow["C"], wins, blockers, lessons])
    return buf.getvalue().encode("utf-8")

