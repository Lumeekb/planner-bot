# src/app/run_polling.py
import os
import asyncio

from .bot import bot, dp
from .db import init_db
from .scheduler import startup_scheduler

# Импортируем роутеры (ВАЖНО: version должен быть тут)
from .handlers import (
    start,
    settings_handler,
    mit,
    review,
    status,
    payment,
    focus,
    weekly,
    export,
    ics,
    plan_horizon,
    subtasks,
    commands_ref,
    guide,
    version,     # ← добавлен
    analytics,   # analytics подключаем последним
)

def setup():
    dp.include_router(start.router)
    dp.include_router(settings_handler.router)
    dp.include_router(mit.router)
    dp.include_router(review.router)
    dp.include_router(status.router)
    dp.include_router(payment.router)
    dp.include_router(focus.router)
    dp.include_router(weekly.router)
    dp.include_router(export.router)
    dp.include_router(ics.router)
    dp.include_router(plan_horizon.router)
    dp.include_router(subtasks.router)
    dp.include_router(commands_ref.router)
    dp.include_router(guide.router)
    dp.include_router(version.router)     # ← теперь определён
    dp.include_router(analytics.router)   # ← последним

async def main():
    await init_db()
    setup()

    if os.getenv("DISABLE_BOT") == "1":
        print("[bot] Disabled via DISABLE_BOT=1 (polling & scheduler are off)")
        return

    await startup_scheduler()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

