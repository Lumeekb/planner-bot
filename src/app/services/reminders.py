# src/app/services/reminders.py
from ..bot import bot  # используем общий экземпляр бота

def build_morning_text() -> str:
    return (
        "Старт дня:\n"
        "• Выбери 1–3 MIT (главные задачи на сегодня).\n"
        "• Для MIT #1 запиши следующий физический шаг.\n"
        "• Заблокируй время в календаре/планере на сегодня.\n"
        "• Убери телефон на первый фокус-спринт (25 мин)."
    )

async def send_morning_prompt(chat_id: int):
    await bot.send_message(chat_id, build_morning_text())

def build_evening_text() -> str:
    return (
        "Закрытие дня:\n"
        "• Запиши 3 победы.\n"
        "• Что мешало сегодня?\n"
        "• Чему научился(ась).\n"
        "• Отметь день как Done.\n"
        "• Поставь 1–3 MIT на завтра."
    )

async def send_evening_prompt(chat_id: int):
    await bot.send_message(chat_id, build_evening_text())

def build_weekly_text() -> str:
    return (
        "Еженедельная проверка:\n"
        "• Обнови CAPEX/OPEX и статус целей.\n"
        "• Отметь прогресс по недельной вехе.\n"
        "• Сформируй следующие шаги на следующую неделю."
    )

async def send_weekly_prompt(chat_id: int):
    await bot.send_message(chat_id, build_weekly_text())

