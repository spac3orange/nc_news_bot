import asyncio
import random
import os
import glob
from config import logger, aiogram_bot, config_aiogram
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bs4 import BeautifulSoup
import aiohttp
import aiofiles
from pathlib import Path
import json
from .parser import BaseParser
from . import ds_ai, edit_mode
from keyboards import kb_admin
import datetime
from environs import Env


dskey = 'sk-3b39353acab64b429c6cd049bbc43639'
allowed_sites = [
            'https://happycoin.club',
            'https://coinspot.io',
            'https://coinlife.com',
            'https://hashtelegraph.com',
            'https://bitjournal.media/'

        ]



async def cleanup(file_path, images_folder):
    try:
        files = glob.glob(os.path.join(images_folder, '*'))
        for f in files:
            os.remove(f)
        print(f"All files in {images_folder} have been deleted.")

    except Exception as e:
        print(f"An error occurred while deleting files in {images_folder}: {e}")

    try:
        links = read_known_links(file_path)
        if not isinstance(links, list):
            raise ValueError(f"Data in {file_path} is not a list")
        if len(links) > 20:
            links = links[-20:]
        with open(file_path, 'w') as file:
            json.dump(links, file, indent=4)

        print(f"Cleanup successful: {file_path} now contains only the last 20 links.")
    except Exception as e:
        print(f"An error occurred: {e}")


async def delayed_execution(delay, admin_id, channel_id, handled, img_name, with_image=True):
    logger.info(f'post will execute in {delay} seconds')
    await asyncio.sleep(delay)
    try:
        if with_image:
            img_fila = await send_image(img_name)
            await aiogram_bot.send_photo(channel_id, img_fila, caption=handled)

        else:
            await aiogram_bot.send_message(channel_id, text=handled)

    except Exception as e:
        logger.error(e)


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


async def save_page(text):
    # Укажите путь и имя файла для сохранения страницы
    file_path = 'utils/pages/testpage.html'

    # Сохранение содержимого страницы в файл асинхронным способом
    async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
        await file.write(text)

    print(f"Страница успешно сохранена в файл: {file_path}")


# Функция для чтения известных ссылок из файла
def read_known_links(file_path):
    if Path(file_path).exists():
        with open(file_path, 'r', encoding='utf-8') as file:
            return set(json.load(file))
    return set()


# Функция для записи известных ссылок в файл
def write_known_links(links, file_path):
    filtered_links = [link for link in links if link != '']
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(filtered_links, file)


async def parse_news():
    try:
        logger.info('parsing news from coinlenta...')
        file_path = 'utils/pages/known_links.json'
        # Считываем уже известные ссылки из файла
        known_links = read_known_links(file_path)
        url = 'https://coinlenta.ru/feed/today/'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()
                print(f"HTTP Status: {response.status}")
                soup = BeautifulSoup(text, 'lxml')
                current_links = {sublink['href'] for sublink in soup.find_all('a', class_='news-wrapper__clause-link article-link')}
                current_links = {link for link in current_links if link != ''}
                # Находим новые ссылки
                new_links = current_links - known_links
                if new_links:
                    new_links = [link for link in new_links if any(link.startswith(prefix) for prefix in allowed_sites)]
                    logger.info(f'found {len(new_links)} new links')
                    for n, link in enumerate(new_links, 1):
                        if link == '':
                            continue
                        try:
                            logger.info(f'parsing {link}')
                            parser = BaseParser(link)
                            result = await parser.fetch_news()
                            if result:
                                if len(result) == 2:
                                    img_name, news_text = result
                                else:
                                    news_text = result
                                handled = await ds_ai.get_req(news_text)
                                if handled:
                                    admin_id = config_aiogram.admin_id
                                    mode = edit_mode.get_mode()
                                    if mode == 'Модерация включена':
                                        if len(result) == 2:
                                            if isinstance(admin_id, list):
                                                for admin in admin_id:
                                                    try:
                                                        admin = int(admin)
                                                        img_fila = await send_image(img_name)
                                                        message = await aiogram_bot.send_photo(admin, img_fila, caption=handled)
                                                        reply_markup = kb_admin.handled_post_menu(message.message_id, image_name=img_name)
                                                        await aiogram_bot.edit_message_reply_markup(chat_id=admin, message_id=message.message_id,
                                                                                                    reply_markup=reply_markup)
                                                        await delete_image(img_fila)
                                                    except Exception as e:
                                                        logger.error(e)
                                                        continue
                                            else:
                                                img_fila = await send_image(img_name)
                                                message = await aiogram_bot.send_photo(admin_id, img_fila, caption=handled)
                                                reply_markup = kb_admin.handled_post_menu(message.message_id, image_name=img_name)
                                                await aiogram_bot.edit_message_reply_markup(chat_id=admin_id, message_id=message.message_id,
                                                                                            reply_markup=reply_markup)
                                                await delete_image(img_fila)

                                        else:
                                            if isinstance(admin_id, list):
                                                for admin in admin_id:
                                                    try:
                                                        admin = int(admin)
                                                        message = await aiogram_bot.send_message(admin, text=handled)
                                                        reply_markup = kb_admin.handled_post_menu(message.message_id)
                                                        await aiogram_bot.edit_message_reply_markup(chat_id=admin, message_id=message.message_id,
                                                                                                    reply_markup=reply_markup)
                                                    except Exception as e:
                                                        logger.error(e)
                                                        continue

                                        print(handled)
                                    if mode == 'Модерация отключена':
                                        env = Env()
                                        channel_id = env.int('TARGET_CHANNEL_ID')
                                        if len(result) == 2:
                                            if isinstance(admin_id, list):
                                                if n > 2:
                                                    logger.warning('n > 2')
                                                    continue
                                                if n > 1:
                                                    timing = random.randint(5, 10)
                                                    timing = timing * 60
                                                    task = asyncio.create_task(delayed_execution(timing, admin_id,
                                                                                                channel_id, handled,
                                                                                                img_name, with_image=True))
                                                else:
                                                    img_fila = await send_image(img_name)
                                                    await aiogram_bot.send_photo(channel_id, img_fila, caption=handled)
                                                    logger.info('post sent')

                                        else:
                                            if isinstance(admin_id, list):
                                                if n > 2:
                                                    logger.warning('n > 2')
                                                    continue
                                                if n > 1:
                                                    timing = random.randint(5, 10)
                                                    timing = timing * 60
                                                    task = asyncio.create_task(delayed_execution(timing, admin_id,
                                                                                                channel_id, handled,
                                                                                                img_name, with_image=False))
                                                else:
                                                    await aiogram_bot.send_message(channel_id, text=handled)
                                                    logger.info('post sent')

                                # break
                            await asyncio.sleep(2)
                        except Exception as e:
                            logger.error(e)
                else:
                    print("Новых ссылок не обнаружено.")

                # Обновляем список известных ссылок, если есть новые
                if new_links:
                    write_known_links(current_links, file_path)
                    logger.warning(f'links updated in {file_path}')
    except Exception as e:
        logger.error(e)


class Monitor:
    def __init__(self):
        env = Env()
        self.scheduler = AsyncIOScheduler()
        self.monitoring_enabled = False
        self.interval = env.int('MON_INTERVAL')
        logger.info('scheduler initialized but not started')

    async def start_monitoring(self):
        if self.monitoring_enabled:
            logger.info('monitoring already enabled')
        else:
            self.scheduler.add_job(parse_news, 'interval', minutes=self.interval,
                                   next_run_time=datetime.datetime.now())
            if not self.scheduler.running:
                self.scheduler.start()
            self.monitoring_enabled = True
            logger.info('monitoring started')

    async def stop_monitoring(self):
        if not self.monitoring_enabled:
            logger.info('monitoring already disabled')
        else:
            # Удалить все задачи из планировщика
            for job in self.scheduler.get_jobs():
                job.remove()
                logger.warning('job removed')

            # Остановить планировщик
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info('scheduler stopped')

            # Сбросить флаг включения мониторинга
            self.monitoring_enabled = False
            logger.info('monitoring disabled')

    async def get_status(self):
        return self.monitoring_enabled


class Cleanup:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def plan_cleanup(self):
        self.scheduler.add_job(cleanup, 'cron', hour=0, minute=10, args=('utils/pages/known_links.json', 'utils/images/',))
        self.scheduler.start()
        logger.info('cleanup scheduler started')


monitor = Monitor()
clean = Cleanup()

# asyncio.run(parse_news())


