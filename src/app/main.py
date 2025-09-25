from fastapi import FastAPI, Request, HTTPException
from aiogram.types import Update
from .bot import bot, dp
from .config import settings

app = FastAPI(title='Universal Planner Bot')

@app.post('/webhook/{secret}')
async def telegram_webhook(secret: str, request: Request):
    if secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail='Forbidden')
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {'ok': True}

@app.get('/health')
async def health():
    return {'status': 'ok'}
