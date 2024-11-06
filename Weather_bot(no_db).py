#*********************************************************************************************************************************************************************************************************************************
# API_TOKEN
import logging
from aiogram import Bot, Dispatcher
from keys import API_TOKEN

# Пишел логи в консоль
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспатчера
bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher()
    


#*********************************************************************************************************************************************************************************************************************************
# Конструкции для обработки и отправки сообщений пользователю
from aiogram import types
from random import randint
import emoji

from aiogram.types import ReplyKeyboardRemove

# обрабатывается при получении /start
async def send_welcome(message: types.Message):
    # добавить имя пользователя в бд 
    await insert_user_into_table(message.from_user.first_name)

    # добавить кнопки в меню
    await set_commands(bot)

    # ответить и предоставить клавиатуру
    await message.answer('Hi my dear human friend ^_^', reply_markup=await keyboard_get_weather()) 

# обрабатывается при получении /my_locations
async def show_my_loc(message: types.Message):
    # получить список локаций пользователя
    names = await get_locations_from_table(message.from_user.first_name)
        # приходит список словарей где: 
        # [{'user_name': 'Miss Jenn', 'location_name': 'Home', 'latitude': 12.132123, 'longitude': 12.132123}, {'user_name': 'Miss Jenn', 'location_name': "Кам'янське", 'latitude': 12.132123, 'longitude': 12.132123}]

    await message.answer('._.', reply_markup=await menu_my_locations())#I added new keyboard

    keyboard_markup = await build_loc_inline_butt(names)
    await message.answer(f'Your locations:', reply_markup=keyboard_markup)

# обрабатывается при получении остального текста
async def echo(message: types.Message):
    ans = randint(0, 5)
    ans_list = ['🤦🏻‍♀️', '🤦🏼‍♀️', '🤦🏽‍♀️', '🤷🏻‍♀️', '🤷🏼‍♀️', '🤷🏽‍♀️']
    await message.answer(ans_list[ans])



#*********************************************************************************************************************************************************************************************************************************
# Машины состояний
# ... погода 'Weather now'
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

class StepsForm_one(StatesGroup):
    get_loc = State()

async def reply_for_now(message: types.Message, state: FSMContext):
    await message.reply('Ok, just send my your location', reply_markup=await keyboard_send_location())

    # переключение формы на состояние get_loc (сработает только при получении геолокации)
    await state.set_state(StepsForm_one.get_loc)

async def return_weather_now(message: types.Message):
    # получение из геолокации пользоветя широты и долготы
    latitude = message.location.latitude
    longitude = message.location.longitude

    # вызов фунции запроса к API, парсинга данных и собирание их в полноценную строку
    await message.reply(get_weather_data.now(latitude, longitude), reply_markup=await keyboard_get_weather())


# ... погода 'Weather for five days'
class StepsForm_two(StatesGroup):
    get_loc = State()

async def reply_for_five_days(message: types.Message, state: FSMContext):
    await message.reply('Ok, just send my your location', reply_markup=await keyboard_send_location())

    await state.set_state(StepsForm_two.get_loc)

async def return_for_five_days(message: types.Message):
    # получение из геолокации пользоветя широты и долготы
    latitude = message.location.latitude
    longitude = message.location.longitude

    # вызов фунции запроса к API, парсинга данных и собирание их в полноценную строку
    await message.reply(get_weather_data.five_days_every_three_hours(latitude, longitude), reply_markup=await keyboard_get_weather())


# заполнение и сохранение Add new location
class StepsForm_three(StatesGroup):
    get_loc = State()
    get_loc_name = State()

async def reply_save_location(message: types.Message, state: FSMContext):
    #
    await message.reply(f'Ok, send me a location through the button \nor through 📎-> Location', reply_markup=await keyboard_send_location())#, one_time_keyboard=True

    await state.set_state(StepsForm_three.get_loc)

async def reply_get_loc_name(message: types.Message, state: FSMContext):
    # получение 3/4 данных из первого сообщения с локацией
    await state.update_data(
        user_name=message.from_user.first_name, 
        latitude=message.location.latitude,
        longitude=message.location.longitude
    )

    await message.reply('Now write the name of the location')

    await state.set_state(StepsForm_three.get_loc_name)

async def save_loc_in_db(message: types.Message, state: FSMContext):
    loc_name = message.text

    data = await state.get_data()
    user_name = data.get("user_name") 
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    await insert_location_into_table(user_name, loc_name, latitude, longitude)

    await message.reply(f"I've saved this location, now it can be used conveniently 🗺! \n{user_name}\n{latitude}\n{longitude}\n{loc_name}")
    await show_my_loc(message)


# удаление локации из бд по нажатию на Deleted one of the locations



#*********************************************************************************************************************************************************************************************************************************
# Кнопки 
# ... на месте клавиатуры
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
async def keyboard_get_weather():
    kb = ReplyKeyboardBuilder()

    kb.button(text='Weather now')
    kb.button(text='Weather for five days')
    # нахуй вырезан пока бд не будет подключена адекватно kb.button(text='My locations')

    kb.adjust(2, 1)

    return kb.as_markup(resize_keyboard=True)#, one_time_keyboard=True

async def keyboard_send_location():
    kb = ReplyKeyboardBuilder()

    kb.button(text='Send location', request_location=True)

    return kb.as_markup(resize_keyboard=True)#, one_time_keyboard=True

async def menu_my_locations(): # на нажатие кнопок должна срабатывать машина состояний
    kb = ReplyKeyboardBuilder()

    kb.button(text='Add new location')
    kb.button(text='Main menu')

    kb.adjust(2)

    return kb.as_markup(resize_keyboard = True)#, one_time_keyboard=True

# ... меню
from aiogram import Bot
from aiogram.types import BotCommand

async def set_commands(bot: Bot):
    commands = [
    BotCommand(command="start", description="Main menu"),
    ]

    await bot.set_my_commands(commands)

# ... инлайн
from aiogram.filters.callback_data import CallbackData
class LocInline(CallbackData, prefix='loc_name'): #
    user_name: str
    loc_name: str
    lat: float
    lon: float

from aiogram.utils.keyboard import InlineKeyboardBuilder
async def build_loc_inline_butt(loc_list): # вывод списка локаций пользователя ввиде инлайн кнопок
    keyboard_builder = InlineKeyboardBuilder()

    # через цикл добавление нужного количества кнопок 
    for i in loc_list:
        keyboard_builder.button(text=f'{i["location_name"]}', callback_data=LocInline(user_name=i['user_name'], loc_name=i['location_name'], lat=i['latitude'], lon=i['longitude']))
    #                             ^ имя кнопки                  ^ данные что хранит кнопка

    return keyboard_builder.as_markup()
    #                         ^ возврат клавиатуры нужно делать используя эту функцию

from aiogram.types import CallbackQuery
async def reply_loc_inline_butt(call: CallbackQuery, callback_data: LocInline): # инлайн локация пользователя - детально
    user_name = callback_data.user_name
    loc_name = callback_data.loc_name
    lat = callback_data.lat
    lon = callback_data.lon

    # создание телеграмовской геолокоции 
    location = types.Location(latitude=lat, longitude=lon)

    # 1 ряд кнопок
    buttons_1 = [
        types.InlineKeyboardButton(text="Weather Now", callback_data=f"wn|{lat}|{lon}"),
        types.InlineKeyboardButton(text="For 5d every 3h", callback_data=f"w5|{lat}|{lon}"),
        #                                                       ^ callback_data - может передавать только одну строку так что в f строку я добавляю через | все данные что хочу передать
        #                                                       ^ при нажатии на кнопку она вместе с самим событием хранит значение callback_data
    ]
    # 2 ряд кнопок
    buttons_2 = [
        types.InlineKeyboardButton(text='Delete location', callback_data=f'dl_1|{user_name}|{loc_name}')
    ]
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons_1, buttons_2])

    # отправка телеграмовской геолокации пользователю
    await bot.send_location(chat_id=call.message.chat.id, latitude=location.latitude, longitude=location.longitude)
    await call.message.answer(f'Location name: {loc_name}', reply_markup=keyboard)

    #await call.message.answer(f'hi {user_name}, your loc: {loc_name}')
    await call.answer()

async def delete_location_1(call: CallbackQuery): # подтверждение удаления локации через инлайн
    # парсинг строки callback_data
    q = call.data.split('|')
    # ['dl_1', '12.123445', '12.123445']

    buttons = [
        types.InlineKeyboardButton(text='Yes', callback_data=f'dl_2|{q[1]}|{q[2]}'),
        types.InlineKeyboardButton(text='No', callback_data=f'dl_no')
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])

    await call.message.answer('Want to delete the location, sure?', reply_markup=keyboard)

    await call.answer()

async def delete_location_2(call: CallbackQuery): # удаление локации из бд через инлайн
    # парсинг строки callback_data
    q = call.data.split('|')
    # ['dl_2', '12.123445', '12.123445']
    
    await delete_location_from_table(q[1], q[2])

    await send_welcome(call.message)

    await call.answer()

async def no_delete_location(call: CallbackQuery): # передумал удалять локацию
    await send_welcome(call.message)

    await call.answer()

async def get_weather_from_inl(call: types.CallbackQuery): # запрос данных погоды через инлайн кнопку
    # парсинг строки callback_data
    q = call.data.split('|')
    # ['wn', '12.123445', '12.123445']

    if q[0] == 'wn':
        await call.message.reply(get_weather_data.now(q[1], q[2]))
    elif q[0] == 'w5':
        await call.message.reply(get_weather_data.five_days_every_three_hours(q[1], q[2]), reply_markup=await keyboard_get_weather())

    await call.answer()



#*********************************************************************************************************************************************************************************************************************************
# Получение данных из API
import requests
from keys import appid

class get_weather_data:
    def now(lat, lon):
        responce = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={appid}')

        data_raw = re.sub(r'"*;*"*', "", responce.text) 
        data = re.sub(',', '/', data_raw)

        # вернуть готовое сообщение
        return compile_message_form_data.weather_now(data)
    
    def five_days_every_three_hours(lat, lon):
        responce = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={appid}')

        data_raw = re.sub(r'"*;*"*', "", responce.text) 
        data = re.sub(',', '/', data_raw)

        # вернуть готовое сообщение
        return compile_message_form_data.weather_for_five_days(data)



#*********************************************************************************************************************************************************************************************************************************
# Приколы с данными в postgreSQL
import asyncio
import asyncpg

# добавить уникального пользователя в бд
async def insert_user_into_table(user_name):
    # подсключение к бд
    from keys import DATA_BASE
    conn = await asyncpg.connect(DATA_BASE)

    try:
        # сохранить *имя пользователя* в столбец "user_name" (если в столбце "user_name" нет *имя пользователя* )
        await conn.execute('INSERT INTO users(user_name) SELECT ($1) WHERE NOT EXISTS (SELECT user_name FROM users WHERE user_name = $1);', f'{user_name}')
        
    except asyncpg.UndefinedTableError:
        # если ошибка(таблицы не существует) - создать таблицу, где колонки: уникальный pk, имя пользователя
        await conn.execute('CREATE TABLE users(id serial PRIMARY KEY, user_name text)')
        # запустить ещё раз def (типа рекурсия) 
        await insert_user_into_table(user_name)

    # отключится от бд
    await conn.close()

# Получить список локаций пользователя из бд (вернет список словарей(каждый словарь - строка))
async def get_locations_from_table(user_name):
    # подсключение к бд
    from keys import DATA_BASE
    conn = await asyncpg.connect(DATA_BASE)

    # получение значений из бд
    locations = await conn.fetch('SELECT * FROM favorite_locations WHERE user_name = $1', user_name)

    # отключится от бд
    await conn.close()

    # приобразование списка записей БД в список словарей
    locations_dicts = []
    for i in locations:
        s = dict(i)
        locations_dicts.append(s)

    return locations_dicts

# добавить локацию пользователя в бд
async def insert_location_into_table(user_name, loc_name, lat, lon):
    # подсключение к бд
    from keys import DATA_BASE
    conn = await asyncpg.connect(DATA_BASE)

    try:
        # добавить любимую локацию в бд, где указывается pk для имени пользователя из тиблицы users, имя локации, долгота и широта
        await conn.execute('INSERT INTO favorite_locations(user_name, location_name, latitude, longitude) VALUES($1, $2, $3, $4)', user_name, loc_name, lat, lon)

    except asyncpg.UndefinedTableError:
        # если ошибка(таблицы не существует) - создать таблицу
        await conn.execute('CREATE TABLE favorite_locations(user_name text, location_name text, latitude float, longitude float)')
        # запустить ещё раз def (типа рекурсия) 
        await insert_location_into_table(user_name, loc_name, lat, lon)

    # отключится от бд
    await conn.close()

# Удалить локацию пользователя из бд
async def delete_location_from_table(user_name, loc_name):
    # подсключение к бд
    from keys import DATA_BASE
    conn = await asyncpg.connect(DATA_BASE)

    # удалить локацию из бд
    await conn.execute('DELETE FROM favorite_locations WHERE user_name = $1 AND location_name = $2', user_name, loc_name)
    
    # отключится от бд
    await conn.close()



#*********************************************************************************************************************************************************************************************************************************
# Функция собирающая текст для сообщения о погоде на данный момент
import re

class compile_message_form_data:
    # (Погода сейчас)
    def weather_now(data):
        city_name = Search_in_data.find_city_name(data)    
        country_name = Search_in_data.find_country_name(data)
        weather_now = Search_in_data.find_weather_now(data)
        weather_emoji = Emoji_for_variable.choose_weather_emoji(weather_now)
        weather_description = Search_in_data.find_weather_description(data)
        description_emoji = Emoji_for_variable.choose_weather_description_emoji(weather_description)
        clouds_per = Search_in_data.find_clouds(data)
        clouds_or_rain = Clouds_or_rain.big_question(data, weather_description, clouds_per)
        temp_feels = Search_in_data.find_temp(data)
        humidity = Search_in_data.find_humidyty(data)
        wind_speed = Search_in_data.find_wind_speed(data)
        deg = Search_in_data.find_wind_degree(data)
        deg_word = Degree_to_side_of_the_world.wind(deg)
        sunrise = Search_in_data.find_sunrise(data)
        sunset = Search_in_data.find_sunset(data)
        visibility = Search_in_data.find_visibility(data)

        return f'📍Location: {city_name} {country_name}\n\nWeather now: {weather_now}{weather_emoji}\nDescription: {weather_description}{description_emoji}{clouds_or_rain}\n\nTemperature: {temp_feels}°\nHumidity: {humidity}%\n\nWind:  {wind_speed}m/s\nAngel: {deg_word}\n\nSunrise: 🌝 {sunrise}\nSunset:  🌚 {sunset}\n\nVisibility: {visibility}m'

    # (Погода на 5 дней с каждые 3 часа)
    def weather_for_five_days(data_for_five_days):
        from datetime import timedelta
        class data_class:
            def __init__(self, time_emoji, time, temp, weather, weather_emoji, weather_description, humidity, wind, rain_volume):
                self.time_emoji = time_emoji
                self.time = time
                self.temp = temp
                self.weather = weather
                self.weather_emoji = weather_emoji
                self.weather_description = weather_description
                self.humidity = humidity
                self.wind = wind
                self.rain_volume = rain_volume

        # экземпляр класса в котором сохранены нужные данные
        data_objects = []

        # объект данных на конкретный промежуток времени (к примеру все данные на 06:00 05.08.2023)
        time_matches = re.findall(r'\d\d:00:00.{275,350}\d\d\d\d-\d\d-\d\d', data_for_five_days)

        # заполнение уникальных переменных
        location = Search_in_data.find_city_name(data_for_five_days)
        country_name = Search_in_data.find_country_name(data_for_five_days)
        sunrise = Search_in_data.find_sunrise(data_for_five_days)
        sunset = Search_in_data.find_sunset(data_for_five_days)
        date_begin = Search_in_data.find_date(data_for_five_days)

        # заполнение переменных для экземпляров класса
        for data_three_hour in time_matches:
            time = re.search(r'\d\d', data_three_hour).group()
            time_emoji = Emoji_for_variable.choose_time_emoji(time, sunrise, sunset)
            temp = Search_in_data.find_temp(data_three_hour)
            weather = Search_in_data.find_weather_now(data_three_hour)
            waether_description = Search_in_data.find_weather_description(data_three_hour)
            weather_emoji = Emoji_for_variable.choose_weather_emoji(weather)
            wind_speed = Search_in_data.find_wind_speed(data_three_hour)
            humidity = Search_in_data.find_humidyty(data_three_hour)
            if weather == 'Rain':
                rain_volume = Search_in_data.find_rain_volume(data_three_hour)
            elif weather == 'Snow':
                rain_volume = Search_in_data.find_snow_volume(data_three_hour)
            else:
                rain_volume = ''

            obj = data_class(time_emoji, time, temp, weather, weather_emoji, waether_description, humidity, wind_speed, rain_volume)
            data_objects.append(obj)            
        
        # хуйня что собирает из объекта класса нормальную строку с погодой на отрезок в 3 часа# func_str = lambda i: f'{i.time_emoji}{i.time} - {i.temp}° ({i.weather}{i.weather_emoji}) Wind {i.wind}m/s'
        func_str = lambda i: f'{i.time_emoji}{i.time}:00    {i.temp}° ({i.weather_emoji}) {i.humidity}% {i.wind}m/s    {i.rain_volume}'
        
        # подготавливает данные собирая строки данных из разных экземпляров класса
        def for_for_it(data):
            day = ''
            for i in data:
                # если строка что была только что сохранена отвечает за 00 час - нужно начать новый день
                day = day + f'\n{func_str(i)}'
            return day

        # генератор шлюхи (собирает данные погоды и отдает их порционно)
        def day_gen(waether_data):
            mini_data = []
            for i in waether_data:
                mini_data.append(i)
                if int(i.time) == 21:
                    yield for_for_it(mini_data) 
                    mini_data = []
        create_day = day_gen(data_objects)

        # хуйнюшка для прибавления дней к дате запроса данных
        plus_days = lambda x: date_begin + timedelta(days=x)

        # перемога
        mr_return = f'📍{location} {country_name}\n\nToday:{next(create_day)}\n\nTomorrow:{next(create_day)}\n\n{plus_days(2).strftime("%d.%m")}:{next(create_day)}\n\n{plus_days(3).strftime("%d.%m")}:{next(create_day)}'
        
        # фикс бага с тем, что данных собирается всего на 4 дня (появляется если делать запрос в 00:__ времени)
        try:
            # попробовать добавить 5й день, если его нет - то будет всего 4 дня
            mr_return += f'\n\n{plus_days(4).strftime("%d.%m")}:{next(create_day)}'
        except:
            pass

        return mr_return
    


#*********************************************************************************************************************************************************************************************************************************
# Классы обработки данных

# (поиск данных в строке)
class Search_in_data:
    def find_city_name(weather_data):
        try:
            city_match = re.search(r'name:\w+-*\w*/' , weather_data)
            city_name = city_match.group().split(':')[1][:-1]
        except AttributeError:
            city_name = 'No city'

        return city_name
    
    def find_country_name(weather_data):
        try:
            country_macth = re.search(r'country:.{2}/', weather_data)
            country_name = country_macth.group().split(':')[1][:-1]
        except AttributeError:
            country_name = '...'

        return country_name
    
    def find_weather_now(weather_data):
        weather_now_macth = re.search(r'main:\w+/', weather_data)
        weather_now = weather_now_macth.group().split(':')[1][:-1]

        return weather_now
    
    def find_weather_description(weather_data):
        weather_description_macth = re.search(r'description:.+/', weather_data)
        weather_description = weather_description_macth.group().split(':')[1][:-5]
        weather_description = weather_description.capitalize()

        return weather_description
    
    def find_temp(weather_data):
        temp_feels_mathc = re.search(r'temp:\d+', weather_data)
        temp_feels_str = temp_feels_mathc.group().split(':')[1]
        temp_feels = int(temp_feels_str) - 273

        return temp_feels
     
    def find_sunrise(weather_data):
        from datetime import datetime

        sunrise_timestump_mathc = re.search(r'sunrise:\d{10}', weather_data)
        sunrise_timestump_str = sunrise_timestump_mathc.group().split(':')[1]
        sunrise_timestump = int(sunrise_timestump_str)
        sunrise_time = datetime.fromtimestamp(sunrise_timestump)
        sunrise = sunrise_time.strftime('%H:%M')

        return sunrise

    def find_sunset(weather_data):
        from datetime import datetime

        sunset_timestump_macth = re.search(r'sunset:\d{10}', weather_data)
        sunset_timestump_str = sunset_timestump_macth.group().split(':')[1]
        sunset_time = int(sunset_timestump_str)
        sunset_time = datetime.fromtimestamp(sunset_time)
        sunset = sunset_time.strftime('%H:%M')

        return sunset
    
    def find_visibility(weather_data):
        visibility_macth = re.search(r'visibility:.+/', weather_data)
        visibility_macth_second = re.search(r'\d+', visibility_macth.group())
        visibility = visibility_macth_second.group()

        return visibility
    
    def find_humidyty(weather_data):
        humidity_match = re.search(r'humidity:.+/', weather_data)
        humidity_match_second = re.search(r'\d+', humidity_match.group())
        humidyty = humidity_match_second.group()

        return humidyty
    
    def find_wind_speed(weather_data):
        wind_speed_mathc = re.search(r'speed:.*/', weather_data)
        wind_speed_mathc_second = re.search(r'\d\.*\d*', wind_speed_mathc.group())
        wind_speed = wind_speed_mathc_second.group()

        return wind_speed
    
    def find_wind_degree(weather_data):
        deg_mathc = re.search(r'deg:.*/', weather_data)
        deg_mathc_second = re.search(r'\d+', deg_mathc.group())
        deg = int(deg_mathc_second.group())

        return deg
    
    def find_clouds(weather_data):
        clouds_per_macth = re.search(r'all:.+', weather_data)
        clouds_per_macth_second = re.search(r'\d+', clouds_per_macth.group())
        clouds_per = clouds_per_macth_second.group()

        return clouds_per
    
    def find_date(weather_data):
        from datetime import datetime

        date_raw = re.search(r'^.{325,375}\d\d-\d\d', weather_data)
        date = date_raw.group().split(':')
        date = datetime.strptime(date[-1], '%Y-%m-%d')

        return date
    
    def find_rain_volume(weather_data):
        try:
            rain_volume_match = re.search(r'rain:....\d.\d\d', weather_data)
            rain_volume = rain_volume_match.group().split(':')[-1]
            rain = f'({rain_volume}mm)'   
        except:
            rain = ''

        return rain
    
    def find_snow_volume(weather_data):
        try:
            snow_volume_match = re.search(r'snow:....\d.\d\d', weather_data)
            snow_volume = snow_volume_match.group().split(':')[-1]
            snow = f'({snow_volume}mm)'   
        except:
            snow = ''

        return snow
       
# (подбор нужного эмоджи)
class Emoji_for_variable:
    def choose_weather_description_emoji(weather_description):
        if weather_description == 'Overcast clouds':
            description_emoji = '☁'
        elif re.search(r'clouds', weather_description):
            description_emoji = '🌤'
        elif re.search(r'rain', weather_description):
            description_emoji = '🌧'
        else:
            description_emoji = '☀'

        return description_emoji

    def choose_weather_emoji(weather_now):
        if weather_now == 'Clouds':
            weather_emoji = '☁'
        elif weather_now == 'Clear':
            weather_emoji = '☀'
        elif weather_now == 'Rain':
            weather_emoji = '☔️'
        elif weather_now == 'Snow':
            weather_emoji = '❄️' #'🌨'
        else:
            weather_emoji = weather_now

        return weather_emoji

    def choose_time_emoji(time, sunrise_str, sunset_str):
        from datetime import datetime, timedelta

        time = datetime.strptime(time, "%H")
        sunrise = datetime.strptime(sunrise_str, "%H:%M")
        sunset = datetime.strptime(sunset_str, "%H:%M")

        if time < sunrise:
            return '🌃'
        elif time > sunrise and time < sunrise + timedelta(hours=2):
            return '🌅'
        elif time > sunrise + timedelta(hours=2) and time < sunset:
            return '🏙'
        elif time > sunset and time < sunset + timedelta(hours=2):
            return '🌇'
        elif time > sunset + timedelta(hours=2):
            return '🌃'
        else:
            return '🌁'
    
# (подбор стороны света на основе угла ветра)
class Degree_to_side_of_the_world:
    def wind(deg):
        if deg < 23 or deg > 338:
            deg_word = 'North'
        elif deg >= 23 or deg <= 68:
            deg_word = "North - East"
        elif deg > 68 or deg < 113:
            deg_word = "East"
        elif deg >= 113 or deg <= 158:
            deg_word = "South - East"
        elif deg > 158 or deg < 263:    
            deg_word = "South"
        elif deg >= 203 or deg <= 245:
            deg_word = "South - West"
        elif deg > 148 or deg < 293:
            deg_word = "West"
        elif deg >= 293 or deg <= 338:
            deg_word = "South - East"
        else:
            deg_word = 'ssd'

        return deg_word

# (определение идет дождь(возврат >0mm количества осадков) или нет(возврат 0%-100% облаков в небе) )
class Clouds_or_rain:
    def big_question(weather_data, weather_description, clouds_per):
        try:
            rain_v_match = re.search(r'rain:{[^}]+}', weather_data)
            rain_v_match_second = rain_v_match.group().split(':')[-1]
            rain_v = rain_v_match_second.split('}')[0]
        except:
            rain_v = None

        if re.search(r'rain', weather_description):
            clouds_or_rain = f'\nRain volume: {rain_v}mm'
        else:
            clouds_or_rain = f'\nClouds: {clouds_per}%'

        return clouds_or_rain



#*********************************************************************************************************************************************************************************************************************************
# Для старта бота
from aiogram import F

async def Main():
    # middwares:
    
    # default handlers:
    dp.message.register(send_welcome, F.text == '/start')                           # при первом старте бота
    dp.message.register(send_welcome, F.text == 'Main menu')                        # ^ или при нажатии кнопки возврат в меню
    
    dp.message.register(reply_for_now, F.text == 'Weather now')                     # дефолт кнопка
    dp.message.register(return_weather_now, F.location, StepsForm_one.get_loc)      # "StepsForm_one.get_loc_1" - запустится только из состояния "get_loc_1" которое задается в хэндлере "async def reply_for_now"

    dp.message.register(reply_for_five_days, F.text == 'Weather for five days')     # дефолт кнопка
    dp.message.register(return_for_five_days, F.location, StepsForm_two.get_loc)    # "StepsForm_one.get_loc_2" - запустится только из состояния "get_loc_2" которое задается в хэндлере "async def reply_for_five_days"

    dp.message.register(show_my_loc, F.text == 'My locations')                      # кнопка меню - список моих локаций
    dp.callback_query.register(reply_loc_inline_butt, LocInline.filter())           # обработчик инлайн кнопок с локациями пользователя

    dp.callback_query.register(get_weather_from_inl, F.data.contains('wn'))         # если при событии - нажатие инлайн кнопки в строке callback_data есть 'wn' - выполнить функцию "func_name"
    dp.callback_query.register(get_weather_from_inl, F.data.contains('w5'))         # ^ тоже самое
    dp.callback_query.register(delete_location_1, F.data.contains('dl_1'))          # подтверждение удаления локации
    dp.callback_query.register(delete_location_2, F.data.contains('dl_2'))          # удаления локации
    dp.callback_query.register(no_delete_location, F.data.contains('dl_no'))        # если передумал удалять локацию

    dp.message.register(reply_save_location, F.text == 'Add new location')          # запуск формы сохранения локации
    dp.message.register(reply_get_loc_name, F.location, StepsForm_three.get_loc)    # при получении геолокации от пользователя
    dp.message.register(save_loc_in_db, F.text, StepsForm_three.get_loc_name)       # при получении имени локации от пользователя

    

    dp.message.register(echo, F.text)                                               # отвечает на все остальные сообщение эмоджи "🤷🏽‍♀️"


    # bot start:
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(Main())