import os
from aiogram.types import FSInputFile
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from config import logger, aiogram_bot, config_aiogram
from keyboards import kb_admin
from utils import monitor
from environs import Env
from states import states
router = Router()


async def send_image(filename):
    path = f'utils/images/{filename}'
    if os.path.exists(path):
        file = FSInputFile(path)
        return file
    return False


async def delete_image(filename):
    path = f'utils/images/{filename}'
    if os.path.exists(path):
        os.remove(path)
        logger.info(f'image {filename} deleted')
        return True
    return False


@router.callback_query(F.data.startswith('send_handled_post'))
async def p_send_handled(call: CallbackQuery):
    env = Env()
    channel_id = env('TARGET_CHANNEL_ID')
    message_id = int(call.data.split('_')[-1])
    if len(channel_id) > 14:
        channel_id = channel_id.split(',')
    try:
        if isinstance(channel_id, list):
            for channel in channel_id:
                await aiogram_bot.copy_message(
                    chat_id=int(channel),
                    from_chat_id=call.from_user.id,
                    message_id=message_id
                )
                await call.message.answer('Сообщение успешно отправлено в канал!')
        else:
            await aiogram_bot.copy_message(
                chat_id=int(channel_id),
                from_chat_id=call.from_user.id,
                message_id=message_id
            )
            await call.message.answer('Сообщение успешно отправлено в канал!')
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        await call.message.answer('Произошла ошибка при попытке отправить сообщение.')

    await call.answer()


@router.callback_query(F.data.startswith('edit_handled_post'))
async def p_edit_handled(call: CallbackQuery, state: FSMContext):
    await call.answer()
    img_name = call.data.split('_')[-1]
    await call.message.answer('Введите отредактированный пост: ')
    await state.set_state(states.EditHandledPost.input_post)
    await state.update_data(img_name=img_name)


@router.message(states.EditHandledPost.input_post)
async def p_edited(message: Message, state: FSMContext):
    uid = message.from_user.id
    post_text = message.text
    post_image = (await state.get_data())['img_name']
    await state.clear()
    if post_image is None:
        await message.answer('Предпросмотр:')
        message = await message.answer(post_text)
        reply_markup = kb_admin.handled_post_menu(message.message_id)
        await aiogram_bot.edit_message_reply_markup(chat_id=uid, message_id=message.message_id, reply_markup=reply_markup)
    if post_image:
        await message.answer('Предпросмотр:')
        photo_file = await send_image(post_image)
        message = await message.answer_photo(photo=photo_file, caption=post_text)
        reply_markup = kb_admin.handled_post_menu(message.message_id)
        await aiogram_bot.edit_message_reply_markup(chat_id=uid, message_id=message.message_id, reply_markup=reply_markup)


