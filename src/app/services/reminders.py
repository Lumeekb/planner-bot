from ..bot import bot
from .weekly import build_weekly_report

async def send_morning_prompt(tg_id: int):
    text = ("Начни день: открой бумажный планер, выбери 3 MIT (Кофейня, Lumé, Личное), "
            "запиши следующий физический шаг для MIT #1, заблокируй время на сегодня и убери телефон для первого фокус-спринта.")
    await bot.send_message(tg_id, text)

async def send_evening_prompt(tg_id: int):
    text = ("Закрой день: 3 победы → что мешало → чему научился; Done; 1–3 MIT на завтра.")
    await bot.send_message(tg_id, text)

async def send_weekly_prompt(tg_id: int):
    header = "🧭 Время еженедельного обзора! Отчёт за 7 дней ниже:"
    report = await build_weekly_report(tg_id)
    await bot.send_message(tg_id, f"{header}\n\n{report}")

