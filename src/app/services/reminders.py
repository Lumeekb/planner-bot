from ..bot import bot
from .weekly import build_weekly_report

async def send_morning_prompt(tg_id: int):
    text = (""Старт дня:\n"
        "• Выбери 1–3 MIT (главные задачи на сегодня).\n"
        "• Для MIT #1 запиши следующий физический шаг.\n"
        "• Заблокируй время в календаре/планере на сегодня.\n"
        "• Убери телефон на первый фокус-спринт (25 мин)."")
    await bot.send_message(tg_id, text)

async def send_evening_prompt(tg_id: int):
    text = ("Закрой день: 3 победы → что мешало → чему научился; Done; 1–3 MIT на завтра.")
    await bot.send_message(tg_id, text)

async def send_weekly_prompt(tg_id: int):
    header = "🧭 Время еженедельного обзора! Отчёт за 7 дней ниже:"
    report = await build_weekly_report(tg_id)
    await bot.send_message(tg_id, f"{header}\n\n{report}")

