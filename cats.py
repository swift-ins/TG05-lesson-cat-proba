#https://tg05-lesson-cat-proba.onrender.com

import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import requests
import os
from dotenv import load_dotenv 


# Загрузка токена
load_dotenv()
TOKEN = os.getenv("TOKEN")
THE_CAT_API_KEY = os.getenv("THE_CAT_API_KEY")
API_KEY = THE_CAT_API_KEY
bot = Bot(token=TOKEN)
dp = Dispatcher()

WEBHOOK_PATH = "/webhook"
BASE_WEBHOOK_URL = "https://tg05-lesson-cat-proba.onrender.com"


CITIES = ['Москва', 'Севастополь', 'Рига', 'Лос-Анджелес']


def get_weather_report(city):
    output = f"=== {city} ===\n"

    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"
    weather_resp = requests.get(weather_url).json()

    if 'main' in weather_resp:
        desc = weather_resp['weather'][0]['description'].capitalize()
        temp = weather_resp['main']['temp']
        timezone_offset = weather_resp.get('timezone', 0)
        local_time = datetime.utcnow() + timedelta(seconds=timezone_offset)
        time_str = local_time.strftime('%Y-%m-%d %H:%M')
        output += f"Местное время: {time_str}\n"
        output += f"Сейчас: {desc}, {temp}°C\n"
    else:
        return f"{city}: ошибка погоды: {weather_resp.get('message', 'Нет данных')}"

    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=ru"
    forecast_resp = requests.get(forecast_url).json()

    if 'list' in forecast_resp:
        output += "\nПрогноз на завтра:\n"
        found = False
        timezone_offset = forecast_resp.get('city', {}).get('timezone', timezone_offset)
        tomorrow_date = (datetime.utcnow() + timedelta(days=1)).date()

        for entry in forecast_resp['list']:
            utc_dt = datetime.utcfromtimestamp(entry['dt'])
            local_dt = utc_dt + timedelta(seconds=timezone_offset)

            if local_dt.date() == tomorrow_date:
                time_str = local_dt.strftime('%H:%M')
                desc = entry['weather'][0]['description'].capitalize()
                temp = entry['main']['temp']
                output += f"{time_str} — {desc}, {temp}°C\n"
                found = True

        if not found:
            output += "Нет данных на завтра.\n"
    else:
        output += "\nОшибка прогноза: " + forecast_resp.get('message', 'Нет данных') + "\n"

    return output.strip()


@dp.message(CommandStart())
@dp.message(Command("weather"))
async def handle_start(message: Message):
    await message.answer("Получаю данные, подождите...")
    for city in CITIES:
        try:
            report = get_weather_report(city)
            await message.answer(report)
            await asyncio.sleep(1.2)
        except Exception as e:
            await message.answer(f"Ошибка при получении данных по {city}: {e}")


# === WEBHOOK ===
async def on_startup(bot: Bot):
    if USE_WEBHOOK:
        await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")


async def main():
    app = web.Application()

    # Обработчик webhook-запросов
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    return app









if __name__ == '__main__':
    if os.getenv('RENDER'):
        # Настройка для Render
        app = asyncio.run(main())
        web.run_app(app, host="0.0.0.0", port=10000)
    else:
        # Локальный запуск с polling
        asyncio.run(dp.start_polling(bot))
        
        
        
        