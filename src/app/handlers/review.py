from aiogram import Router, types
from aiogram.filters import Command
from ..services.reviews import save_review

router = Router()

@router.message(Command("close"))
async def close_cmd(m: types.Message):
    await m.answer(
        "Закрой день: 3 победы → что мешало → чему научился → Done → MIT на завтра.\n"
        "Быстрый ввод отчёта (в одной строке):\n"
        "/review победа1 | победа2 | победа3 | что мешало | чему научился"
    )

@router.message(Command("review"))
async def review_cmd(m: types.Message):
    payload = m.text.replace("/review", "", 1).strip()
    parts = [p.strip() for p in payload.split("|")]
    while len(parts) < 5:
        parts.append("")
    wins_text = " | ".join(parts[:3])
    blockers = parts[3]      # внутренняя переменная/поле в БД можно оставить прежним названием
    lessons = parts[4]
    await save_review(m.from_user.id, wins_text, blockers, lessons)
    await m.answer("✅ Отчёт сохранён. Не забудь выбрать 1–3 MIT на завтра: /mit задача1 | задача2 | задача3")

