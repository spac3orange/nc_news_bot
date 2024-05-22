import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import aiogram_bot
from config.logger import logger
from keyboards import set_commands_menu
from handlers import start, work_modes, monitoring, edit_handled, edit_keys
from utils import monitor


async def start_params() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start.router)
    dp.include_router(work_modes.router)
    dp.include_router(monitoring.router)
    dp.include_router(edit_handled.router)
    dp.include_router(edit_keys.router)

    logger.info('Bot started')

    # Регистрируем меню команд
    await set_commands_menu(aiogram_bot)

    # инициализирем БД

    # Пропускаем накопившиеся апдейты и запускаем polling
    await aiogram_bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(aiogram_bot)


async def main():
    task1 = asyncio.create_task(start_params())
    task2 = asyncio.create_task(monitor.start_monitoring())
    await asyncio.gather(task1, task2)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning('Bot stopped')
    except Exception as e:
        logger.error(e)

