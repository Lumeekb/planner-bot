# src/app/handlers/review.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..services.reviews import save_review

router = Router()

def _esc(s: str | None) -> str:
    s = s or ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

@router.message(Command("close"))
async def close_cmd(m: types.Message):
    await m.answer(
        "Закрываем день:\n"
        "• Напиши 3 победы, что мешало, чему научился, отметь Done.\n"
        "• Быстрый ввод одной строкой:\n"
        "<code>/review победа1 | победа2 | победа3 | что мешало | чему научился</code>",
        parse_mode="HTML",
    )

@router.message(Command("review"))
async def review_cmd(m: types.Message):
    # Парсим строку после /review
    text = (m.text or "")
    payload = text.replace("/review", "", 1).strip()

    if not payload:
        await m.answer(
            "Формат быстрого ввода:\n"
            "<code>/review победа1 | победа2 | победа3 | что мешало | чему научился</code>",
            parse_mode="HTML",
        )
        return

    parts = [p.strip() for p in payload.split("|")]
    # Дополним до 5 элементов: 3 победы, 1 «что мешало», 1 «чему научился»
    while len(parts) < 5:
        parts.append("")

    wins_text = " | ".join(parts[:3])
    blockers  = parts[3]
    lessons   = parts[4]

    # Сохраняем в БД
    await save_review(m.from_user.id, wins_text, blockers, lessons)

    # Кнопки для установки MIT на завтра
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поставить MIT на завтра", callback_data="mitt:start")],
        [InlineKeyboardButton(text="Показать MIT на завтра",  callback_data="mitt:show")],
    ])

    # Подтверждение + кнопки
    await m.answer(
        "Отчёт сохранён.\n"
        f"• Победы: <i>{_esc(wins_text)}</i>\n"
        f"• Что мешало: <i>{_esc(blockers)}</i>\n"
        f"• Чему научился: <i>{_esc(lessons)}</i>",
        parse_mode="HTML",
    )
    await m.answer("Теперь поставь 1–3 MIT на завтра кнопкой ниже.", reply_markup=kb)

