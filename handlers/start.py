from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from config import logger
from keyboards import kb_admin
from filters import IsAdmin
router = Router()
router.message.filter(IsAdmin(F))


@router.message(Command(commands='start'))
async def process_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Добро пожаловать', reply_markup=kb_admin.start_btns())
    logger.info(f'user {message.from_user.username} connected')


@router.callback_query(F.data == 'back_to_main')
async def back_to_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Добро пожаловать', reply_markup=kb_admin.start_btns())
    await call.answer()


