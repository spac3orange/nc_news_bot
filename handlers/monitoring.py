from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from config import logger
from keyboards import kb_admin
from utils import monitor, edit_mode

router = Router()


@router.callback_query(F.data == 'monitoring_start')
async def p_mon_start(call: CallbackQuery):
    await monitor.start_monitoring()
    await call.message.answer('Мониторинг запущен')
    await call.answer()


@router.callback_query(F.data == 'monitoring_stop')
async def p_mon_start(call: CallbackQuery):
    await monitor.stop_monitoring()
    await call.message.answer('Мониторинг выключен')
    await call.answer()


@router.message(Command('get_status'))
async def p_get_status(message: Message):
    status = await monitor.get_status()
    mode = edit_mode.get_mode()
    if status:
        await message.answer('Мониторинг запущен'
                             f'\n{mode}')
    else:
        await message.answer('Мониторинг выключен'
                             f'\n{mode}')
