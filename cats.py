#https://tg05-lesson-cat-proba.onrender.com

import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import requests
import ssl
import os

from config import TOKEN, THE_CAT_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://tg05-lesson-cat-proba.onrender.com" + WEBHOOK_PATH

def get_cat_breeds():
    url = "https://api.thecatapi.com/v1/breeds"
    headers = {"x-api-key": THE_CAT_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

def get_cat_image_by_breed(breed_id):
    url = f"https://api.thecatapi.com/v1/images/search?breed_ids={breed_id}"
    headers = {"x-api-key": THE_CAT_API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data[0]['url']

def get_breed_info(breed_name):
    breeds = get_cat_breeds()
    for breed in breeds:
        if breed['name'].lower() == breed_name.lower():
            return breed
    return None

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Напиши мне название породы кошки, и я пришлю тебе её фото и описание.")

@dp.message()
async def send_cat_info(message: Message):
    breed_name = message.text
    breed_info = get_breed_info(breed_name)
    if breed_info:
        cat_image_url = get_cat_image_by_breed(breed_info['id'])
        info = (
            f"Порода - {breed_info['name']}\n"
            f"Описание - {breed_info['description']}\n"
            f"Продолжительность жизни - {breed_info['life_span']} лет"
        )
        await message.answer_photo(photo=cat_image_url, caption=info)
    else:
        await message.answer("Порода не найдена. Попробуйте еще раз.")

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

async def main():
    # Если запускаем локально - используем polling
    import os
    if os.getenv("RENDER"):
        # Настройка webhook для Render
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        await on_startup(bot)
        return app
    else:
        # Локальный запуск с polling
        await dp.start_polling(bot)

if __name__ == '__main__':
    # Проверяем, запущен ли код на Render
    if os.getenv("RENDER"):
        # Запуск asyncio event loop для webhook
        app = asyncio.run(main())
        web.run_app(app, host="0.0.0.0", port=10000)
    else:
        # Локальный запуск
        asyncio.run(main())
