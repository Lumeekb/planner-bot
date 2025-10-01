# src/app/web.py
import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, Response

from .bot import bot, dp
from .db import init_db
from .scheduler import startup_scheduler

# Импортируем ВСЕ роутеры handlers, включая version (и startday, если он есть)
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
    guide,    # если файла нет — удали эту строку
    version,     # ОБЯЗАТЕЛЬНО есть
    analytics,   # analytics — последним подключаем в dp (ниже)
)

app = FastAPI()


def setup():
    """Подключаем роутеры в нужном порядке."""
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
    dp.include_router(guide.router)   # если нет startday — закомментируй
    dp.include_router(version.router)    # ← теперь version точно импортирован
    dp.include_router(analytics.router)  # analytics — САМЫМ ПОСЛЕДНИМ


@app.on_event("startup")
async def on_startup():
    await init_db()
    setup()

    # Флажок, чтобы можно было «усыпить» бота на Render
    if os.getenv("DISABLE_BOT") == "1":
        print("[bot] Disabled via DISABLE_BOT=1 (polling & scheduler are off)")
        return

    await startup_scheduler()
    app.state.bot_task = asyncio.create_task(dp.start_polling(bot))


@app.on_event("shutdown")
async def on_shutdown():
    task = getattr(app.state, "bot_task", None)
    if task:
        task.cancel()


# Health endpoints для UptimeRobot/Render
@app.api_route("/", methods=["GET", "HEAD"])
async def health_root():
    return PlainTextResponse("ok")

@app.api_route("/healthz", methods=["GET", "HEAD"])
async def healthz():
    return PlainTextResponse("ok")

@app.get("/favicon.ico")
async def favicon():
    return Response(content=b"", media_type="image/x-icon")

@app.get("/version")
async def version_ep():
    return {"version": os.getenv("APP_VERSION", "dev")}

