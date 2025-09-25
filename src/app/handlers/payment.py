from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command('upgrade'))
async def upgrade(m: types.Message):
    await m.answer('Оплата Stars (XTR) — заглушка. Настроишь позже.')
