from aiogram.types import BotCommand


async def set_commands_menu(bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Главное меню'),
        BotCommand(command='/get_status',
                   description='Статус мониторинга'),

    ]

    await bot.set_my_commands(main_menu_commands)
