from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from ..services.users import get_or_create_user, get_user_by_tg

router = Router()

def main_kbd() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/mit"), KeyboardButton(text="/sprint"), KeyboardButton(text="/close")],
            [KeyboardButton(text="/weekly"), KeyboardButton(text="/export"), KeyboardButton(text="/status")],
            [KeyboardButton(text="/commands"), KeyboardButton(text="/guide")],
        ],
        resize_keyboard=True
    )

WELCOME = (
    "👋 <b>Привет!</b> Это твой личный бот-планнер.\n\n"
    "Я помогу навести порядок: от целей на месяц/неделю — до понятного дня из 3 главных задач.\n\n"

    "📅 <b>Как работать со мной (пошагово)</b>\n"
    "1️⃣ <u>Определи цели на месяц или неделю</u>\n"
    "   • /plan month Цель1 | Цель2 | Цель3 — записать цели месяца\n"
    "   • /plan week Задача1 | Задача2 | Задача3 — записать задачи недели\n"
    "   • Посмотреть: /goals month  или  /goals week\n\n"

    "2️⃣ <u>Сделай день ясным: выбери 3 самые важные задачи</u>\n"
    "   • Команда: /mit Задача1 | Задача2 | Задача3\n"
    "   • Это твои MIT (Most Important Tasks) — максимум три, чтобы не распыляться.\n\n"

    "3️⃣ <u>Разбей крупное на маленькое</u>\n"
    "   • Добавить подзадачу к 1-й задаче: /sub 1 Маленький шаг (≤10–15 минут)\n"
    "   • Посмотреть подзадачи: /subs\n\n"

    "4️⃣ <u>Работай фокус-спринтами</u>\n"
    "   • /sprint 50 10 — 50 минут работы, 10 минут отдых\n"
    "   • Можно мягче начать: /sprint 25 5\n\n"

    "5️⃣ <u>Вечером закрой день</u>\n"
    "   • Подсказка: /close\n"
    "   • Быстрый отчёт: /review Победа1 | Победа2 | Победа3 | что мешало | уроки\n\n"

    "6️⃣ <u>Раз в неделю — обзор</u>\n"
    "   • /weekly — отчёт за 7 дней (где были провалы/победы)\n"
    "   • /export — выгрузка всех задач в CSV (Месяц → Неделя → Дни + подзадачи)\n\n"

    "📚 <b>Подсказки</b>\n"
    "• /commands — полный список команд\n"
    "• /guide — подробный гайд с примерами и советами\n\n"

    "⚙️ <b>Настройки</b>\n"
    "• /timezone Europe/Helsinki  (или Europe/Moscow, Asia/Yekaterinburg)\n"
    "• /morning 09:15 — время утреннего напоминания\n"
    "• /evening 21:30 — время вечернего напоминания\n\n"

    "🚀 <b>Начни сейчас</b>\n"
    "Напиши свои 3 главные задачи на сегодня:\n"
    "/mit Задача1 | Задача2 | Задача3"
)

@router.message(CommandStart())
async def on_start(m: types.Message):
    await get_or_create_user(m.from_user.id)
    u = await get_user_by_tg(m.from_user.id)
    tz = u.tz if u else "Europe/Helsinki"
    await m.answer(f"{WELCOME}\n\nТекущие настройки: TZ = <b>{tz}</b>.", reply_markup=main_kbd())

@router.message(Command("help"))
async def on_help(m: types.Message):
    u = await get_user_by_tg(m.from_user.id)
    tz = u.tz if u else "Europe/Helsinki"
    await m.answer(f"{WELCOME}\n\nТекущие настройки: TZ = <b>{tz}</b>.", reply_markup=main_kbd())

