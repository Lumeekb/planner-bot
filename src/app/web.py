import asyncio
import contextlib
from fastapi import FastAPI

from .bot import bot, dp
from .handlers import (
    start, settings_handler, mit, review, status, payment, focus,
    weekly, export, ics, plan_horizon, subtasks, commands_ref, guide,
    analytics,  # ← добавили
)
from .db import init_db
from .scheduler import startup_scheduler

app = FastAPI()

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

@app.on_event("startup")
async def on_startup():
    await init_db()
    setup()
    await startup_scheduler()
    # запускаем бота фоном в этом же event loop
    app.state.bot_task = asyncio.create_task(dp.start_polling(bot))

@app.on_event("shutdown")
async def on_shutdown():
    task = getattr(app.state, "bot_task", None)
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

@app.get("/")
async def health():
    return {"ok": True}

