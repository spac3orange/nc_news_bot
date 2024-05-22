from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Запустить', callback_data='monitoring_start')
    kb_builder.button(text='Остановить', callback_data='monitoring_stop')
    kb_builder.button(text='Режимы', callback_data='work_modes')
    kb_builder.button(text='API Keys', callback_data='api_keys')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def modes_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Активный', callback_data='set_active_mode')
    kb_builder.button(text='Пассивный', callback_data='set_passive_mode')
    kb_builder.button(text='Назад', callback_data='back_to_main')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def handled_post_menu(message_id, image_name=None):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Отправить', callback_data=f'send_handled_post_{message_id}')
    kb_builder.button(text='Редактировать', callback_data=f'edit_handled_post_{message_id}_{image_name}')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def keys_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data=f'add_api_key')
    kb_builder.button(text='Удалить', callback_data=f'del_api_key')
    kb_builder.button(text='Статус', callback_data=f'get_keys_status')
    kb_builder.button(text='Назад', callback_data=f'back_to_main')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def del_key(keys):
    kb_builder = InlineKeyboardBuilder()

    # Add buttons for each key
    for key in keys:
        kb_builder.button(text=key, callback_data=f'delkey_{key}')
    kb_builder.button(text='Назад', callback_data=f'back_to_main')
    kb_builder.adjust(1)

    return kb_builder.as_markup(resize_keyboard=True)