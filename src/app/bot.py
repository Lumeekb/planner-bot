# src/app/bot.py
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import settings

# В aiogram 3.7+ parse_mode передаётся через default=
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

# FSM для диалогов (кнопка "Поставить MIT на завтра" и т.п.)
dp = Dispatcher(storage=MemoryStorage())

