from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from config import logger
from keyboards import kb_admin
from utils import edit_mode
router = Router()


@router.callback_query(F.data == 'work_modes')
async def p_work_modes(call: CallbackQuery):
    mode = edit_mode.get_mode()
    await call.message.answer(f'<b>Текущий режим работы:</b> {mode}', reply_markup=kb_admin.modes_menu())
    await call.answer()


@router.callback_query(F.data == 'set_active_mode')
async def p_set_active_mode(call: CallbackQuery):
    mode = edit_mode.get_mode()
    if mode == 'Модерация отключена':
        mode = edit_mode.change_mode()
        await call.message.answer('Модерация постов запущена.')
    else:
        await call.message.answer('Модерация постов уже запущена.')
    await call.answer()


@router.callback_query(F.data == 'set_passive_mode')
async def p_set_passive_mode(call: CallbackQuery):
    mode = edit_mode.get_mode()
    if mode == 'Модерация отключена':
        await call.message.answer('Модерация постов уже отключена.')
    else:
        mode = edit_mode.change_mode()
        await call.message.answer('Модерация постов отключена.')
    await call.answer()