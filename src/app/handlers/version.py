# src/app/handlers/version.py
import os
import hashlib
from aiogram import Router, types
from aiogram.filters import Command

from ..config import settings
from ..services.reminders import build_morning_text
from . import subtasks as subtasks_module  # чтобы показать путь файла

router = Router()

def _token_fingerprint(token: str) -> str:
    # показываем безопасный отпечаток, чтобы убедиться, что это тот самый токен
    if not token:
        return "none"
    tail = token[-6:]
    sha = hashlib.sha1(token.encode("utf-8")).hexdigest()[:8]
    return f"...{tail} (sha1:{sha})"

@router.message(Command("ver"))
async def ver_cmd(m: types.Message):
    app_ver = os.getenv("APP_VERSION", "dev")
    disabled = os.getenv("DISABLE_BOT", "")
    tz = settings.TZ
    db = settings.DATABASE_URL.split("?")[0]
    token_fp = _token_fingerprint(settings.BOT_TOKEN)

    # первые строки утреннего текста, чтобы увидеть текущую версию текста
    morning_preview = build_morning_text().splitlines()[:2]
    morning_preview = " / ".join(morning_preview)

    # путь файла, где реализован /subs
    subs_path = getattr(subtasks_module, "__file__", "unknown")

    text = (
        "<b>Version</b>\n"
        f"APP_VERSION: <code>{app_ver}</code>\n"
        f"TZ: <code>{tz}</code>\n"
        f"DISABLE_BOT: <code>{disabled or '0'}</code>\n"
        f"DATABASE_URL: <code>{db}</code>\n"
        f"BOT_TOKEN FP: <code>{token_fp}</code>\n"
        f"/subs file: <code>{subs_path}</code>\n"
        f"Morning preview: <i>{morning_preview}</i>\n"
    )
    await m.answer(text)

