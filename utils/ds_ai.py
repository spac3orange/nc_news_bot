import random

import requests
import json
from pprint import pprint
import re
import aiohttp
from config import logger
import os


async def ensure_file_exists():
    if not os.path.exists('utils/ds_keys.json'):
        os.makedirs('utils', exist_ok=True)
        with open('utils/ds_keys.json', 'w') as file:
            json.dump([], file)


async def load_keys():
    await ensure_file_exists()
    with open('utils/ds_keys.json', 'r') as file:
        return json.load(file)


async def append_to_text_file(value, filename='responses.txt'):
    # Открываем файл в режиме добавления. Если файл не существует, он будет создан.
    with open(filename, 'a', encoding='utf-8') as file:
        # Добавляем значение на новую строку в файл
        file.write(value + '\n')


async def format_text(resp_text):
    # Регулярное выражение для поиска начала строки, начинающейся с пробелов и 1., 2., 3., 4., или 5.
    if re.match(r"^\s*[1-9]\.", resp_text):
        # Обрезаем начальные символы вида "1. " до первого пробела после точки
        resp_text = re.sub(r"^\s*[1-9]\.\s*", "", resp_text)
    # Проверка и удаление кавычек, если текст полностью заключен в один из видов кавычек
    # Обрабатываем одинарные (' '), двойные (" "), и угловые (« ») кавычки
    if re.match(r"^['\"]", resp_text) and re.search(r"['\"]$", resp_text):
        resp_text = resp_text[1:-1].strip()
    elif re.match(r"^«", resp_text) and re.search(r"»$", resp_text):
        resp_text = resp_text[1:-1].strip()
    return resp_text.strip()


async def get_req(question, api_key=None):
    if not api_key:
        keys = await load_keys()
        api_key = random.choice(keys)
    url = "https://api.deepseek.com/v1/chat/completions"
    print(len(question))
    if len(question) > 1000:
        prompt = '''
        Сделай профессиональный краткий рерайтинг новости на русском языке сократив ее до 2-3 предложений общим размером не более 400 символов.
        Задача сохранить смысл и передать смысл новости максимально сократив объем текста.
        Нам надо выжать самый ключевой смысл из новости максимально уменьшив количество текста.
        Удаляй все ссылки на источники и любую рекламу телеграм каналов или сайтов.
        Добавь короткий интересный заголовок к статье который бы соответствовал контексту новости выделив его с помощью html тэгов <b></b>.
        После заголовка всегда должен быть отступ в одну строку.
        '''
    else:
        prompt = '''
        Сделай профессиональный краткий рерайтинг новости на русском языке сократив ее до 2-3 предложений общим размером не более 250 символов.
        Задача сохранить смысл и передать смысл новости максимально сократив объем текста.
        Нам надо выжать самый ключевой смысл из новости максимально уменьшив количество текста.
        Удаляй все ссылки на источники и любую рекламу телеграм каналов или сайтов.
        Добавь короткий интересный заголовок к статье который бы соответствовал контексту новости выделив его с помощью html тэгов <b></b>.
        После заголовка всегда должен быть отступ в одну строку.
        '''
    full_req = question + prompt
    print('FULL REQ')
    print(full_req)
    payload = json.dumps({
        "messages": [
            {"content": "You are a helpful assistant.", "role": "system"},
            {"content": full_req, "role": "user"}
        ],
        "model": "deepseek-chat",
        "frequency_penalty": 0,
        "max_tokens": 2048,
        "presence_penalty": 0,
        "stop": None,
        "stream": False,
        "temperature": 1,
        "top_p": 1
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                resp = await response.json()
                resp_text = resp["choices"][0]["message"]["content"]
                if resp_text:
                    form_text = await format_text(resp_text)
                    print('COMMENT')
                    print(form_text)
                    return form_text
                else:
                    return None
    except Exception as e:
        logger.error(e)
        return None

#response = get_req(req)
#print(response)