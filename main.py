import logging
import requests
import telebot
from telebot import types
import datetime
from datetime import datetime
import pytz
import schedule
import time
from threading import Thread

bot = telebot.TeleBot('6451388653:AAFL6iG9PqR8-nbLSvDEhMqU5p51IC1XQPQ',threaded=False)
steel_path_missions= []
common_missions = []
mission = []
all_missions = []
cycle = []
events = []
event_info = []
subscribers = {}
notification_schedule={}
def get_events():
    event_info = ""
    events = []
    url = "https://api.warframestat.us/pc/events"
    params = {'language': 'ru', }
    response = requests.get(url,params=params)
    response.headers.get("Content-Type")
    data = response.json()
    for event in data:
        events.append(event)
    for i in range(len(events)):
        end_date = (events[i]['expiry'])
        end_time = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        current_time = datetime.now(pytz.timezone("Europe/Moscow"))
        time_left = end_time - current_time
        remaining_days = time_left.days
        remaining_hours, remainder = divmod(time_left.seconds, 3600)
        remaining_minutes, _ = divmod(remainder, 60)
        remaining_time = (f"*До конца ивента осталось*:\nДней: {remaining_days} | Часов: {remaining_hours} | Минут: {remaining_minutes}")
        event_info+=((f"{'-'*70}\n*{events[i]['description']}*\n*Локация: *{events[i]['node']}\n*Награда: *{events[i]['rewards'][0]['asString']}\n{remaining_time}\n"))
    return event_info


def get_mods(name):

    url = f"https://api.warframestat.us/items/search/{name}"
    params = {'language': 'ru', }
    response = requests.get(url,params=params)
    response.headers.get("Content-Type")
    data = response.json()




def print_data(data, indent=0):
    output = ""  # Переменная для сохранения вывода
    # Выводим 'name', 'description' и 'type' сначала


    if 'name' in data:
        output += "Name: " + data['name'] + "\n"
    if 'description' in data:
        output += "Description: " + data['description'] + "\n"
    if 'type' in data:
        output += "Type: " + data['type'] + "\n"

    if isinstance(data, dict):
        for key, value in data.items():
            if key in ['name', 'description', 'type']:
                continue  # Пропускаем вывод 'name', 'description' и 'type', так как они уже выведены ранее
            if isinstance(value, (dict, list)):
                output += " " * indent + key.capitalize() + ":\n"
                output += print_data(value, indent + 2)  # Добавляем результат рекурсивного вызова в переменную output
            else:
                output += " " * indent + key.capitalize() + ": " + str(value) + "\n"
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                output += print_data(item, indent)  # Добавляем результат рекурсивного вызова в переменную output
    return output  # Возвращаем результат вместо вывода на экран


def get_item(message):
    msg = message
    name = message.text
    if name.lower() == 'назад':
        get_text_messages(message)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Назад")
    markup.add(btn1)
    url = f"https://api.warframestat.us/items/{name}"
    params = {'only':["name,description,attacks,type"],'language':'ru',}
    response = requests.get(url,params=params)
    response.headers.get("Content-Type")
    data = response.json()
    items = print_data(data)
    bot.send_message(msg.from_user.id, items, reply_markup=markup )
    bot.register_next_step_handler(message, get_item)
    return items


def get_rivens():
    url = "https://api.warframestat.us/pc/rivens/search/Corvas"
    response = requests.get(url)
    response.headers.get("Content-Type")
    data = response.json()


def get_voidTrader():
    url = "https://api.warframestat.us/pc/ru/voidTrader"
    response = requests.get(url)
    response.headers.get("Content-Type")
    data = response.json()
    items = ''

    if data['active'] == True:
        for item_data in data['inventory']:
            item_name = item_data['item']
            ducats_value = item_data['ducats']
            credits_value = item_data['credits']
            items += f"*{'-'*50}\nПредмет:* {item_name}\n*Дукаты*: {ducats_value}\n*Кредиты*: {credits_value}\n"

        voidTrader = (f"*Локация:* {data['location']}\n\n{items}")
    else:
        voidTrader = (f"Баро Китир прибудет через: *{data['startString']}*\nЛокация: *{data['location']}*")
    return voidTrader


def get_arbitration():
    url = "https://api.warframestat.us/pc/ru/arbitration"
    response = requests.get(url)
    response.headers.get("Content-Type")
    data = response.json()

    end_date = (data['expiry'])
    end_time = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    current_time = datetime.now(pytz.timezone("Europe/Moscow"))
    time_left = end_time - current_time
    remaining_days = time_left.days
    remaining_hours, remainder = divmod(time_left.seconds, 3600)
    remaining_minutes, _ = divmod(remainder, 60)
    remaining_time = (f"*До конца осталось:*\nДней: {remaining_days} | Часов: {remaining_hours} | Минут: {remaining_minutes}")
    arbitration = (f"*{data['type']}*\n{data['node']}\n{data['enemy']}\n{remaining_time}")
    return arbitration


def get_worldstate_data():
    cycle =''
    cycle +=get_vallisCycle()
    cycle +=get_cambionCycle()
    cycle += get_cetusCycle()
    return cycle

def get_vallisCycle():
    url = "https://api.warframestat.us/pc/ru/vallisCycle"
    response = requests.get(url)
    response.headers.get("Content-Type")
    data = response.json()
    if data['state'] == "cold":
        data['state'] = "Холод"
    else:
        data['state'] = "Тепло"
    vallis_cycle = (f"{'-'*50}\n*Долина сфер:* {data['state']}\n*Осталось:* {data['timeLeft']}\n")
    return vallis_cycle

def get_cetusCycle():
    url = "https://api.warframestat.us/pc/ru/cetusCycle"
    response = requests.get(url)
    response.headers.get("Content-Type")
    data = response.json()
    if data['state'] == "night":
        data['state'] = "Ночь"
    else:
        data['state'] = "День"
    cetus_cycle = ( f"{'-'*50}\n*Цетус:* {data['state']}*\nОсталось: *{data['timeLeft']}\n")

    return cetus_cycle


def get_cambionCycle():
    url = "https://api.warframestat.us/pc/ru/cambionCycle"
    response = requests.get(url)
    response.headers.get("Content-Type")
    data = response.json()
    if data['state'] == "vome":
        data['state'] = "Воум"
    else:
        data['state'] = "Фэз"
    cambion_cycle = (f"{'-'*50}\n*Камбионский дрейф:* {data['state']}\n*Осталось:* {data['timeLeft']}\n")

    return cambion_cycle

def get_steel_path__reward():
    url = "https://api.warframestat.us/pc/ru/steelPath"
    response = requests.get(url)
    response.headers.get("Content-Type")
    data = response.json()
    steel_path_reward = (f"*{data['currentReward']['name']}*\n*Стоимость*: {data['currentReward']['cost']} стали\n")
    return steel_path_reward


def get_dat(mode):
    url = "https://api.warframestat.us//pc/ru/fissures"
    response = requests.get(url)
    response.headers.get("Content-Type")
    data = response.json()
    mission = []
    steel_missions = ""
    common_missions = ""
    for item in data:
        mission.append((item))
    len_mission = len(mission)
    steel_iteration = 0
    common_iteration = 0
    for i in range(len_mission):
        if mission[i]['isHard'] == True:
            steel_missions += f"*{'-' * 30}\n{mission[i]['missionType']}*\n{mission[i]['tier']}\n{mission[i]['eta']}\n{mission[i]['node']}\n{mission[i]['enemyKey']}\n"
            steel_iteration += 1
        else:
            common_missions += f"*{'-' * 30}\n{mission[i]['missionType']}*\n{mission[i]['tier']}\n{mission[i]['eta']}\n{mission[i]['node']}\n{mission[i]['enemyKey']}\n"
            common_iteration +=1
    if mode == "Cтальной путь":
        return  steel_missions
    else:
        return common_missions
f'-'
@bot.message_handler(commands=['start'])
def start(message):

    btn1 = types.KeyboardButton("Разрывы бездны")
    btn2 = types.KeyboardButton("🌑 Циклы мира 🌞")
    btn3 = types.KeyboardButton("Текущая награда стального пути")
    btn4 = types.KeyboardButton("Товары Баро Китира")
    btn5 = types.KeyboardButton("Найти предмет")
    btn6 = types.KeyboardButton("Текущие ивенты")
    btn7 = types.KeyboardButton("Арбитраж")
    if message.chat.id in subscribers:
        btn8 = types.KeyboardButton("Отписаться от уведомлений")
    else:
        btn8 = types.KeyboardButton("Подписаться на уведомления")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    markup.add(btn1,btn2,btn3,btn4,btn5,btn6,btn7,btn8)
    bot.send_message(message.from_user.id, "Привет,я бот-помощник для игры Warframe", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == "🌑 Циклы мира 🌞":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        data = get_worldstate_data()
        bot.send_message(message.from_user.id,data , reply_markup=markup,parse_mode="Markdown")

    if message.text =="Разрывы бездны":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn2 = types.KeyboardButton("Cтальной путь")
        btn3 = types.KeyboardButton("Обычный режим")
        markup.add(btn2,btn3)
        bot.send_message(message.from_user.id, "Выберите режим", reply_markup=markup)

    if message.text == "Cтальной путь":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn4 = types.KeyboardButton("Назад")
        markup.add(btn4)
        data = get_dat(message.text)
        bot.send_message(message.from_user.id, data,reply_markup=markup,parse_mode="Markdown")

    if message.text == "Обычный режим":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn4 = types.KeyboardButton("Назад")
        markup.add(btn4)
        data = get_dat(message.text)
        bot.send_message(message.from_user.id, data,reply_markup=markup,parse_mode="Markdown")

    if message.text =="Текущая награда стального пути":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        data = get_steel_path__reward()
        bot.send_message(message.from_user.id, data, reply_markup=markup,parse_mode="Markdown")


    if message.text == "Назад":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        btn1 = types.KeyboardButton("🌑 Циклы мира 🌞")
        btn2 = types.KeyboardButton("Разрывы бездны")
        btn3 = types.KeyboardButton("Текущая награда стального пути")
        btn4 = types.KeyboardButton("Товары Баро Китира")
        btn5 = types.KeyboardButton("Найти предмет")
        btn6 = types.KeyboardButton("Текущие ивенты")
        btn7 = types.KeyboardButton("Арбитраж")
        if message.chat.id in subscribers:
            btn8 = types.KeyboardButton("Отписаться от уведомлений")
        else:
            btn8 = types.KeyboardButton("Подписаться на уведомления")
        markup.add(btn1,btn2, btn3,btn4,btn5,btn6,btn7,btn8)
        bot.send_message(message.from_user.id, "Выберите режим", reply_markup=markup)

    if message.text == "Товары Баро Китира":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        data = get_voidTrader()
        bot.send_message(message.from_user.id, data, reply_markup=markup,parse_mode="Markdown")

    if message.text == "Найти предмет":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        bot.send_message(message.from_user.id, "Введите название предмета", reply_markup=markup, parse_mode="Markdown")
        bot.register_next_step_handler(message,get_item)

    if message.text == "Текущие ивенты":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        data = get_events()
        bot.send_message(message.from_user.id, data, reply_markup=markup, parse_mode="Markdown")

    if message.text == "Арбитраж":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        data = get_arbitration()
        bot.send_message(message.from_user.id, data, reply_markup=markup, parse_mode="Markdown")

    if message.text == "Подписаться на уведомления":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        bot.send_message(message.from_user.id,'Вы подписываетесь на уведомления о разрывах бездны стального пути.\n\nВведите интервал уведомлений в минутах' , reply_markup=markup,parse_mode="Markdown")
        bot.register_next_step_handler(message, set_notification_interval)

    if message.text == "Отписаться от уведомлений":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        bot.send_message(message.chat.id, "Вы отписались от уведомлений.", reply_markup=markup)
        if message.chat.id in subscribers:
            del subscribers[message.chat.id]
            del notification_schedule[message.chat.id]

def set_notification_interval(message):
    chat_id = message.chat.id
    if message.text.lower() == 'назад':
        get_text_messages(message)
        return
    try:
        minutes = int(message.text)
        if minutes <= 0 or minutes>  720:
            bot.send_message(chat_id, "Интервал должен быть положительным числом не более 720 минут.Пожалуйста, попробуйте снова.")
            bot.register_next_step_handler(message, set_notification_interval)
            return
        subscribers[message.chat.id] = True
        notification_schedule[chat_id] = minutes
        bot.send_message(chat_id, f"Интервал для уведомлений успешно установлен на {minutes} минут.")
        schedule.clear(tag=chat_id)
        schedule_notification(chat_id, minutes)
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите целое число минут. Пожалуйста, попробуйте снова.")
        bot.register_next_step_handler(message, set_notification_interval)


def schedule_notification(chat_id, minutes):
    schedule.every(minutes).minutes.do(send_notification, chat_id).tag(chat_id)

def send_notification(chat_id):
    if chat_id in subscribers:
        data = get_dat("Cтальной путь")
        bot.send_message(chat_id, data, parse_mode="Markdown")

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    while 1:
        try:
            schedule_thread = Thread(target=run_schedule)
            schedule_thread.start()
            bot.infinity_polling()
        except Exception:
            logging.basicConfig(level=logging.ERROR, filename="py_log.log", filemode="w")
            time.sleep(5)
            


