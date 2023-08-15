#******************************************************************************************
# API_TOKEN
import logging
from aiogram import Bot, Dispatcher
from keys import API_TOKEN

# Настройки подключения по логину 
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспатчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
    

#******************************************************************************************
# Конструкции для обработки и отправки сообщений пользователю
from aiogram import types
import emoji

# запоминает последний выбор вывода погоды для пользователя, используется при отправки им местоположения 
users_list = {}

# обрабатывается при получении /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply('Hi my dear human friend ^_^', reply_markup=keyboard)    

# обрабатывается при получении 'Weather now'
@dp.message_handler(text='Weather now')
async def reply_message(message: types.Message):
    await message.reply('Ok, just send my your location', reply_markup=keyboard_send_location)
    q = message['from']['first_name']
    users_list[q] = 'now'

# обрабатывается при получении 'Weather for five days'
@dp.message_handler(text='Weather for five days')
async def reply_message(message: types.Message):
    await message.reply('Ok, just send my your location', reply_markup=keyboard_send_location)
    q = message['from']['first_name']
    users_list[q] = 'five days'

# обрабатывается при получении 'test'
@dp.message_handler(text='test')
async def reply_message(message: types.Message):
    from keys import appid
    waether_five_days = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?lat=50.408991&lon=30.635077&appid={appid}')
    data_raw = re.sub(r'"*;*"*', "", waether_five_days.text) 
    data = re.sub(',', '/', data_raw)
    # вернуть готовое сообщение
    compile_message_form_data.weather_for_five_days(data)

# обрабатывается при получении остального текста
@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

# обрабатывается при получении геолокации от юзера
@dp.message_handler(content_types=[types.ContentType.LOCATION])
async def handle_location(message: types.Message):
    try:
        # получить широту
        global latitude
        latitude = message.location.latitude
        # получить долготу
        global longitude
        longitude = message.location.longitude
        # отправить сообщение с готовым описанием погода на сейчас
        q = message['from']['first_name']
        if users_list[q] == 'now':
            await message.reply(get_weather_data.now(latitude, longitude), reply_markup=keyboard)
        elif users_list[q] == 'five days':
            await message.reply(get_weather_data.five_days_every_three_hours(latitude, longitude), reply_markup=keyboard)
    except:
        await message.reply('Nope, try again)', reply_markup=keyboard)


#******************************************************************************************
# Кнопки
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add('Weather now').add('Weather for five days')

keyboard_send_location = types.ReplyKeyboardMarkup(resize_keyboard=True)
button = types.KeyboardButton(text="Send location", request_location=True)
keyboard_send_location.add(button)


#******************************************************************************************
# Получение данных из сторонних API
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


#******************************************************************************************
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
        humidyty = Search_in_data.find_humidyty(data)
        wind_speed = Search_in_data.find_wind_speed(data)
        deg = Search_in_data.find_wind_degree(data)
        deg_word = Degree_to_side_of_the_world.wind(deg)
        sunrise = Search_in_data.find_sunrise(data)
        sunset = Search_in_data.find_sunset(data)
        visibility = Search_in_data.find_visibility(data)

        return f'📍Location: {city_name} {country_name}\n\nWeather now: {weather_now}{weather_emoji}\nDescription: {weather_description}{description_emoji}{clouds_or_rain}\n\nTemperature: {temp_feels}°\nHumidyty: {humidyty}%\n\nWind:  {wind_speed}m/s\nAngel: {deg_word}\n\nSunrise: 🌝 {sunrise}\nSunset:  🌚 {sunset}\n\nVisibility: {visibility}m'

    # (Погода на 5 дней с каждые 3 часа)
    def weather_for_five_days(data_for_five_days):
        from datetime import timedelta
        class data_class:
            def __init__(self, time_emoji, time, temp, weather, weather_emoji, weather_description, wind):
                self.time_emoji = time_emoji
                self.time = time
                self.temp = temp
                self.weather = weather
                self.weather_emoji = weather_emoji
                self.weather_description = weather_description
                self.wind = wind

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

            obj = data_class(time_emoji, time, temp, weather, weather_emoji, waether_description, wind_speed)
            data_objects.append(obj)            
        
        # хуйня что собирает из объекта класса нормальную строку с погодой на отрезок в 3 часа
        func_str = lambda i: f'{i.time_emoji}{i.time} - {i.temp}° ({i.weather}{i.weather_emoji}) Wind {i.wind}m/s'
        
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
        mr_return = f'📍{location} {country_name}\n\nToday:{next(create_day)}\n\nTomorrow:{next(create_day)}\n\n{plus_days(2).strftime("%d.%m")}:{next(create_day)}\n\n{plus_days(3).strftime("%d.%m")}:{next(create_day)}\n\n{plus_days(4).strftime("%d.%m")}:{next(create_day)}'
        return mr_return


#******************************************************************************************
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
            weather_emoji = '🌧'
        else:
            weather_emoji = '🫧'

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


#******************************************************************************************
# Для старта бота
from aiogram import executor

if __name__ == '__main__':
    executor.start_polling(dp)#, skip_updates=True