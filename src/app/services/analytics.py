import os
import datetime as dt
from sqlalchemy import select, func
from ..db import AsyncSessionLocal
from ..models import UserEvent
from ..services.users import get_or_create_user

# Опционально считаем total по таблице users, если она есть
try:
    from ..models import User  # type: ignore
    HAS_USER = True
except Exception:
    User = None  # type: ignore
    HAS_USER = False

def _admin_ids() -> set[int]:
    raw = os.getenv("ADMIN_IDS", "").strip()
    ids: set[int] = set()
    for part in raw.split(","):
        p = part.strip()
        if not p:
            continue
        try:
            ids.add(int(p))
        except ValueError:
            pass
    return ids

def is_admin(tg_id: int) -> bool:
    return tg_id in _admin_ids()

async def log_event(tg_id: int, text: str | None):
    """Логируем каждое входящее сообщение/команду."""
    user = await get_or_create_user(tg_id)
    typ = "cmd" if (text or "").startswith("/") else "msg"
    payload = (text or "")[:255]
    async with AsyncSessionLocal() as s:
        s.add(UserEvent(user_id=user.id, type=typ, payload=payload))
        await s.commit()

async def get_stats():
    """Глобальные метрики: total, active7, active30, new7."""
    now = dt.datetime.utcnow()
    d7 = now - dt.timedelta(days=7)
    d30 = now - dt.timedelta(days=30)
    async with AsyncSessionLocal() as s:
        # всего пользователей
        if HAS_USER:
            total = (await s.execute(select(func.count()).select_from(User))).scalar_one()
        else:
            total = (await s.execute(select(func.count(func.distinct(UserEvent.user_id))))).scalar_one()

        # активные за 7 и 30
        active7 = (await s.execute(
            select(func.count(func.distinct(UserEvent.user_id))).where(UserEvent.ts >= d7)
        )).scalar_one()

        active30 = (await s.execute(
            select(func.count(func.distinct(UserEvent.user_id))).where(UserEvent.ts >= d30)
        )).scalar_one()

        # новые за 7 дней
        if HAS_USER and hasattr(User, "created_at"):
            new7 = (await s.execute(
                select(func.count()).select_from(User).where(User.created_at >= d7)  # type: ignore[attr-defined]
            )).scalar_one()
        else:
            first_event_subq = (
                select(UserEvent.user_id, func.min(UserEvent.ts).label("first_ts"))
                .group_by(UserEvent.user_id)
                .subquery()
            )
            new7 = (await s.execute(
                select(func.count()).select_from(first_event_subq).where(first_event_subq.c.first_ts >= d7)
            )).scalar_one()

        return {"total": total, "active7": active7, "active30": active30, "new7": new7}

