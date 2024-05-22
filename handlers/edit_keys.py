import os
from aiogram.types import FSInputFile
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import states.states
from config import logger, aiogram_bot, config_aiogram
from keyboards import kb_admin
from utils import monitor, ds_ai
from environs import Env
from states import states
import json
router = Router()


# Ensure the utils/ds_keys.json file exists
async def ensure_file_exists():
    if not os.path.exists('utils/ds_keys.json'):
        os.makedirs('utils', exist_ok=True)
        with open('utils/ds_keys.json', 'w') as file:
            json.dump([], file)


# Load keys from the JSON file
async def load_keys():
    await ensure_file_exists()
    with open('utils/ds_keys.json', 'r') as file:
        return json.load(file)


# Save keys to the JSON file
async def save_keys(keys):
    with open('utils/ds_keys.json', 'w') as file:
        json.dump(keys, file)


async def p_apk_msg(message: Message):
    keys = await load_keys()
    await message.answer(f'API Ключей: {len(keys)}', reply_markup=kb_admin.keys_menu())


@router.callback_query(F.data == 'api_keys')
async def p_api_keys(call: CallbackQuery):
    await ensure_file_exists()
    keys = await load_keys()
    await call.message.answer(f'API Ключей: {len(keys)}', reply_markup=kb_admin.keys_menu())
    await call.answer()


@router.callback_query(F.data == 'add_api_key')
async def p_input_apik(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите api ключ: ')
    await state.set_state(states.AddKey.input_key)


@router.message(states.AddKey.input_key)
async def p_save_apik(message: Message, state: FSMContext):
    new_key = message.text
    keys = await load_keys()
    if new_key in keys:
        await message.answer('Ошибка. Такой ключ уже существует.')
        await state.clear()
        return
    keys.append(new_key)
    await save_keys(keys)
    await message.answer(f'Ключ {new_key} сохранен')
    await state.clear()
    await p_apk_msg(message)


@router.callback_query(F.data == 'del_api_key')
async def p_input_del_key(call: CallbackQuery, state: FSMContext):
    keys = await load_keys()
    await call.message.answer('Выберите ключ для удаления: ', reply_markup=kb_admin.del_key(keys))
    await call.answer()


@router.callback_query(F.data.startswith('delkey_'))
async def p_delkey(call: CallbackQuery):
    print(call.data)
    key = call.data.split('_')[-1]
    keys = await load_keys()
    if key in keys:
        keys.remove(key)
        await save_keys(keys)
        await call.message.answer('Ключ удален')
    else:
        await call.answer('Ошибка. Ключ не найден.')
    await call.answer()


@router.callback_query(F.data == 'get_keys_status')
async def p_get_kstatus(call: CallbackQuery):
    keys = await load_keys()
    for key in keys:
        req = await ds_ai.get_req('Привет, как дела?', api_key=key)
        if req is None:
            await call.message.answer(f'Ключ {key}\nСтатус: 🔴')
        else:
            await call.message.answer(f'Ключ {key}\nСтатус: 🟢')
    await call.answer()
