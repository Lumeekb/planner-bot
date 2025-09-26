import asyncio
from .bot import bot, dp
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
    analytics,  # импортируем
)
from .db import init_db
from .scheduler import startup_scheduler

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
    dp.include_router(analytics.router)  # ← САМЫЙ ПОСЛЕДНИЙ

async def main():
    await init_db()
    setup()
    await startup_scheduler()
    print("Bot polling started. Press Ctrl+C to stop.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

