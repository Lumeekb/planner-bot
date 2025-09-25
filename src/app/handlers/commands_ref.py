from aiogram import Router, types
from aiogram.filters import Command

router = Router()

TEXT = (
    "<b>Справочник команд</b>\n\n"
    "🟣 <b>Планирование горизонтов</b>\n"
    "• /plan month Задача1 | Задача2 | … — добавить цели месяца\n"
    "• /plan week Задача1 | Задача2 | … — добавить цели недели\n"
    "• /goals month|week — показать цели\n"
    "• /delmonth N, /delweek N — удалить цель по номеру\n"
    "• /clearmonth, /clearweek — очистить все цели\n\n"
    "🟢 <b>День (MIT)</b>\n"
    "• /mit A | B | C — задать 3 ключевых задачи на сегодня\n"
    "• /status — показать текущие MIT\n"
    "• /delmit 1|2|3 — удалить MIT по номеру\n"
    "• /clearmit — очистить все MIT на сегодня\n\n"
    "🟡 <b>Подзадачи</b>\n"
    "• /sub 1|2|3 Текст — добавить подзадачу к MIT #1/2/3\n"
    "• /subs — показать все подзадачи на сегодня\n"
    "• /subdone 1 2 — переключить статус подзадачи #2 у MIT #1\n"
    "• /subdel 1 2 — удалить подзадачу #2 у MIT #1\n"
    "• /subclear 1|2|3 — удалить все подзадачи у MIT\n\n"
    "🔵 <b>Фокус и ритм</b>\n"
    "• /sprint 50 10 — начать спринт (50 мин работы, 10 — перерыв)\n"
    "  (коротко: /sprint 25 → 25/5)\n\n"
    "🟤 <b>Закрытие дня и обзор</b>\n"
    "• /close — подсказка, как закрыть день\n"
    "• /review победа1 | победа2 | победа3 | что мешало | уроки — сохранить дневной отчёт\n"
    "• /weekly — отчёт за 7 дней\n"
    "• /export — CSV: Месяц → Неделя → Дни (с подзадачами)\n"
    "• /ics — iCal на сегодня (MIT как all-day)\n\n"
    "⚙️ <b>Настройки</b>\n"
    "• /timezone Europe/Helsinki — часовой пояс\n"
    "• /morning 09:15 — время утреннего напоминания\n"
    "• /evening 21:30 — время вечернего напоминания\n"
)

@router.message(Command("commands"))
async def show_commands(m: types.Message):
    await m.answer(TEXT)

