#******************************
# API_TOKEN
import logging
from aiogram import Bot, Dispatcher
from keys import API_TOKEN

# Настройки подключения по логину 
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспатчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


#******************************
# Конструкции для обработки и отправки сообщений пользователю
from aiogram import types
import emoji

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply('Hi my dear human friend ^_^',
                        reply_markup=keyboard)

@dp.message_handler()
async def echo(message: types.Message):
    print(message)
    if message.text.lower() == 'weather now':   # если сообщение не 'weather now', то отправить эхо сообщение
        await message.reply(Get_Weather(longitude, latitude))
    else:
        await message.answer(message.text)

# пример сообщения из перемернной message что полуучает бот от меня:
# {"message_id": 115, "from": {"id": 462526663, "is_bot": false, "first_name": "Miss Jenn", "username": "miss_cool_fork", "language_code": "ru"}, "chat": {"id": 462526663, "first_name": "Miss Jenn", "username": "miss_cool_fork", "type": "private"}, "date": 1686937361, "text": "weather now"}

@dp.message_handler(content_types=[types.ContentType.LOCATION])
async def handle_location(message: types.Message):
    global latitude
    latitude = message.location.latitude
    global longitude
    longitude = message.location.longitude
    await message.reply(Get_Weather(latitude, longitude))


#******************************
# Получение данных из сторонних API
import requests
from keys import appid

def Get_Weather(lat, lon):
    print(lat, lon)
    responce = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={appid}')
    return recompile_weather_data(responce.text)


#******************************
# Парсинг данных погоды
import re

def recompile_weather_data(data_row):
    data = re.sub(r'"*;*"*', "", data_row) 
    data = re.sub(',', '/', data)

    try:
        city_match = re.search(r'name:.+/' , data)
        city_name = city_match.group().split(':')[1][:-1]
    except AttributeError:
        city_name = 'No city'

    try:
        country_macth = re.search(r'country:.{2}/', data)
        country_name = country_macth.group().split(':')[1][:-1]
    except AttributeError:
        country_name = '...'

    weather_now_macth = re.search(r'main:.+/', data)
    weather_now = weather_now_macth.group().split(':')[1][:-12]

    if weather_now == 'Clouds':
        weather_emoji = '☁'
    elif weather_now == 'Clear':
        weather_emoji = '☀'
    elif weather_now == 'Rain':
        weather_emoji = '🌧'
        
    weather_description_macth = re.search(r'description:.+/', data)
    weather_description = weather_description_macth.group().split(':')[1][:-5]
    weather_description = weather_description.capitalize()

    if weather_description == 'Overcast clouds':
        description_emoji = '☁'
    elif re.search(r'clouds', weather_description):
        description_emoji = '🌤'
    elif re.search(r'rain', weather_description):
        description_emoji = '🌧'
    else:
        description_emoji = '☀'

    clouds_per_macth = re.search(r'all:.+', data)
    clouds_per_macth_second = re.search(r'\d+', clouds_per_macth.group())
    clouds_per = clouds_per_macth_second.group()

    try:
        rain_v_match = re.search(r'rain:{[^}]+}', data)
        rain_v_match_second = rain_v_match.group().split(':')[-1]
        rain_v = rain_v_match_second.split('}')[0]
    except:
        rain_v = None

    if re.search(r'rain', weather_description):
        clouds_or_rain = f'\nRain volume: {rain_v}mm'
    else:
        clouds_or_rain = f'\nClouds: {clouds_per}%'

    #atmospheric_pressure_macth = re.search()
    #atmospheric_pressure = 'sea_level'
    #Atmospheric pressure: {atmospheric_pressure}\n - вставить в return

    temp_feels_mathc = re.search(r'temp:.+/', data)
    temp_feels_str = temp_feels_mathc.group().split(':')[1][:-14]
    temp_feels = int(temp_feels_str) - 273

    humidity_match = re.search(r'humidity:.+/', data)
    humidity_match_second = re.search(r'\d+', humidity_match.group())
    humidyty = humidity_match_second.group()

    wind_speed_mathc = re.search(r'speed:.*/', data)
    wind_speed_mathc_second = re.search(r'\d\.*\d*', wind_speed_mathc.group())
    wind_speed = wind_speed_mathc_second.group()

    deg_mathc = re.search(r'deg:.*/', data)
    deg_mathc_second = re.search(r'\d+', deg_mathc.group())
    deg = int(deg_mathc_second.group())

    #if deg < 23 and deg > 338:
    #    deg_word = 'North'
    #elif deg >= 23 and deg <= 68:
    #    deg_word = "Norht-East"
    #elif deg > 68 and deg < 113:
    #    deg_word = "East"
    #elif deg >= 113 and deg <= 158:
    #    deg_word = "South-East"
    #elif deg > 158 and deg < 263:
    #    deg_word = "South"
    #elif deg >= 203 and deg <= 245:
    #    deg_word = "South-West"
    #elif deg > 148 and deg < 293:
    #    deg_word = "West"
    #elif deg >= 293 and deg <= 338:
    #    deg_word = "South-East"
    #else:
    #    deg_word = 'ssd'

    from datetime import datetime

    sunrise_timestump_mathc = re.search(r'sunrise:.+/', data)
    sunrise_timestump_str = sunrise_timestump_mathc.group().split(':')[1][:-7]
    sunrise_timestump = int(sunrise_timestump_str)
    sunrise_time = datetime.fromtimestamp(sunrise_timestump)
    sunrise = sunrise_time.strftime('%H:%M')

    sunset_timestump_macth = re.search(r'sunset:.*/', data)
    sunset_timestump_str = sunset_timestump_macth.group().split(':')[1][:-10]
    sunset_time = int(sunset_timestump_str)
    sunset_time = datetime.fromtimestamp(sunset_time)
    sunset = sunset_time.strftime('%H:%M')

    visibility_macth = re.search(r'visibility:.+/', data)
    visibility_macth_second = re.search(r'\d+', visibility_macth.group())
    visibility = visibility_macth_second.group()

    return f'📍Location: {city_name} {country_name}\n\nWeather now: {weather_now}{weather_emoji}\nDescription: {weather_description}{description_emoji}{clouds_or_rain}\n\nTemperature: {temp_feels}°\nHumidyty: {humidyty}%\n\nWind:  {wind_speed}m/s\nAngel: {deg}°\n\nSunrise: 🌝 {sunrise}\nSunset:  🌚 {sunset}\n\nVisibility: {visibility}m'
    #  / {deg_word}


#******************************
# Кнопки
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_weather_now = KeyboardButton('Weather now')
first_button_add = ReplyKeyboardMarkup(resize_keyboard=True).add(button_weather_now)

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
button = types.KeyboardButton(text="Send location", request_location=True)
keyboard.add(button)


#******************************
# Для старта бота
from aiogram import executor

if __name__ == '__main__':
    executor.start_polling(dp)#, skip_updates=True