import aiohttp
from bs4 import BeautifulSoup
import aiofiles
import string
import random
from config import logger


async def generate_random_name(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


async def save_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
        filename = url.replace('.', '')
        file_path = f'pages/{filename}.html'

        async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
            await file.write(text)

        print(f"Страница успешно сохранена в файл: {file_path}")


async def write_file(session, link, name_img, webp=False):
    if webp:
        async with aiofiles.open(f'utils/images/{name_img}', 'wb') as file:
            async with session.get(link) as response:
                async for x in response.content.iter_chunked(1024):
                    await file.write(x)
    else:
        async with aiofiles.open(f'utils/images/{name_img}', 'wb') as file:
            async with session.get(link) as response:
                async for x in response.content.iter_chunked(1024):
                    await file.write(x)


class BaseParser:
    def __init__(self, url):
        self.url = url

    async def fetch_news(self):
        parser_map = {
            'https://happycoin.club': self.__parse_happycoin,
            'https://bits.media': self.__parse_bmedia,
            'https://acryptoinvest.news': self.__parse_acrypto,
            'https://cryptocurrency.tech': self.__parse_cctech,
            'https://coinspot.io': self.__parse_cspot,
            'https://www.rbc.ru': self.__parse_rbc,
            'https://coinlife.com': self.__parse_clife,
            'https://hashtelegraph.com': self.__parse_htelegraph,
            'https://xrp-buy.ru': self.__parse_xrpbuy
        }
        for prefix, parser in parser_map.items():
            if self.url.startswith(prefix):
                return await parser()
        else:
            logger.error(f'parser for {self.url} not found')

    async def __parse_happycoin(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    text = await response.text()
                    print(f"HTTP Status: {response.status}")
                    soup = BeautifulSoup(text, 'lxml')
                    news_block = soup.find('div', class_='single-post-text clearfix')
                    image = soup.find('img', class_='img-responsive single-featured-image rsp-img-center')
                    if image:
                        print('image found')
                        img_link = image['src']
                        image_name = img_link[-10:]
                        await write_file(session, img_link, image_name)
                        return image_name, news_block.text
                    else:
                        return news_block.text
        except Exception as e:
            logger.error(e)

    async def __parse_bmedia(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    text = await response.text()
                    print(f"HTTP Status: {response.status}")
                    soup = BeautifulSoup(text, 'lxml')
                    news_block = soup.find('div', class_='articleBody')
                    image = soup.find('img', class_='article-picture')
                    if image:
                        print('image found')
                        img_link = 'https://bits.media' + image['content']
                        image_name = img_link[-10:]
                        await write_file(session, img_link, image_name, webp=True)
                        return image_name, news_block.text
                    else:
                        return news_block.text
        except Exception as e:
            logger.error(e)

    async def __parse_acrypto(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    text = await response.text()
                    print(f"HTTP Status: {response.status}")
                    soup = BeautifulSoup(text, 'lxml')
                    news_block = soup.find('div', class_='td-post-content tagdiv-type')
                    image = soup.find('div', class_='td-post-content tagdiv-type').find('img', class_='entry-thumb td-modal-image')
                    if image:
                        print('image found')
                        img_link = image['src']
                        image_name = img_link[-10:]
                        await write_file(session, img_link, image_name)
                        return image_name, news_block.text
                    else:
                        return news_block.text
        except Exception as e:
            logger.error(e)

    async def __parse_cctech(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    text = await response.text()
                    print(f"HTTP Status: {response.status}")
                    soup = BeautifulSoup(text, 'lxml')
                    news_block = soup.find('div', class_='td-post-content td-pb-padding-side')
                    image = soup.find('div', class_='td-post-featured-image').find('img', class_='entry-thumb')
                    if image:
                        print('image found')
                        img_link = image['src']
                        image_name = img_link[-10:]
                        await write_file(session, img_link, image_name)
                        return image_name, news_block.text
                    else:
                        return news_block.text
        except Exception as e:
            logger.error(e)

    async def __parse_cspot(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    text = await response.text()
                    print(f"HTTP Status: {response.status}")
                    soup = BeautifulSoup(text, 'lxml')
                    news_block = soup.find('div', class_='content-box typography article-content')
                    return news_block.text
        except Exception as e:
            logger.error(e)

    async def __parse_rbc(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    text = await response.text()
                    print(f"HTTP Status: {response.status}")
                    soup = BeautifulSoup(text, 'lxml')
                    news_block = soup.find('div', class_='article__text article__text_free')
                    #image = soup.find('div', class_='article__main-image__wrap').find('img', class_='g-image article__main-image__image')
                    # if image:
                    #     print('image found')
                    #     img_link = image['src']
                    #     image_name = img_link[-10:]
                    #     await write_file(session, img_link, image_name)
                    #     return image_name, news_block.text
                    # else:
                    return news_block.text
        except Exception as e:
            logger.error(e)

    async def __parse_clife(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    text = await response.text()
                    print(f"HTTP Status: {response.status}")
                    soup = BeautifulSoup(text, 'lxml')
                    news_block = soup.find('div', class_='post-content')
                    image = soup.find('div', class_='post-img item-bg')['data-background-image']
                    if image:
                        print('image found')
                        img_link = image
                        image_name = img_link[-10:]
                        await write_file(session, img_link, image_name)
                        return image_name, news_block.text
                    else:
                        return news_block.text
        except Exception as e:
            logger.error(e)

    async def __parse_htelegraph(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    text = await response.text()
                    print(f"HTTP Status: {response.status}")
                    soup = BeautifulSoup(text, 'lxml')
                    news_block = soup.find('div', class_='entry-content')
                    image = soup.find('figure', class_='post-thumbnail').find('img')
                    if image:
                        print('image found')
                        img_link = image['src']
                        image_name = img_link[-10:]
                        await write_file(session, img_link, image_name)
                        return image_name, news_block.text
                    else:
                        return news_block.text
        except Exception as e:
            logger.error(e)

    async def __parse_xrpbuy(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    text = await response.text()
                    print(f"HTTP Status: {response.status}")
                    soup = BeautifulSoup(text, 'lxml')
                    news_block = soup.find('div', class_='entry-content clearfix')
                    image = soup.find('div', class_='entry-thumbnail').find('img')
                    if image:
                        print('image found')
                        img_link = image['src']
                        image_name = img_link[-10:]
                        await write_file(session, img_link, image_name)
                        return image_name, news_block.text
                    else:
                        return news_block.text
        except Exception as e:
            logger.error(e)



# hpc = BaseParser('https://hashtelegraph.com/es-protiv-ii-microsoft-grozit-mnogomilliardnyj-shtraf-za-bing/')
# asyncio.run(hpc.fetch_news())
# asyncio.run(save_page())