import time
import logging
import requests
import telebot
from telebot import types
import datetime
from datetime import datetime
import pytz
import googletrans
from googletrans import Translator
from deep_translator import (GoogleTranslator,
                             PonsTranslator,
                             LingueeTranslator,
                             MyMemoryTranslator,
                             YandexTranslator,
                             DeeplTranslator,
                             QcriTranslator,
                             single_detection,
                             batch_detection)
bot = telebot.TeleBot('6451388653:AAFL6iG9PqR8-nbLSvDEhMqU5p51IC1XQPQ')
steel_path_missions= []
common_missions = []
mission = []
all_missions = []
cycle = []
events = []
event_info = []
def get_events():
    event_info = []
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
        remaining_time = (f"До конца ивента осталось:\nДней: {remaining_days}\nЧасов: {remaining_hours}\nМинут: {remaining_minutes}")





        event_info.append((f"\n{events[i]['description']}\nЛокация: {events[i]['node']}\nНаграда: {events[i]['rewards'][0]['asString']}\n{remaining_time}\n"))
    return event_info
def get_mods(name):

    url = f"https://api.warframestat.us/items/search/{name}"
    params = {'language': 'ru', }
    response = requests.get(url,params=params)
    response.headers.get("Content-Type")
    data = response.json()
    print(data)



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


def get_item(name):
    msg = name
    name = name.text

    url = f"https://api.warframestat.us/items/{name}"
    params = {'only':["name,description,attacks,type"],'language':'ru',}
    response = requests.get(url,params=params)
    response.headers.get("Content-Type")
    data = response.json()
    items = print_data(data)

    bot.send_message(msg.from_user.id, items)



    print(items)
    return items

    # item = (f"Наименование:*{data['name']}\n*{data['description']}\n\nХарактеристики\n:"
    #         f"\nШанс крита: {data['attacks'][0]['crit_chance']}"
    #         f"\nКрит урон: {data['attacks'][0]['crit_mult']}"
    #         f"\nШанс статуса: {data['attacks'][0]['status_chance']}"
    #         f"\nУдар: {data['attacks'][0]['damage']['impact']}"
    #         f"\nРазрез: {data['attacks'][0]['damage']['slash']}"
    #         f"\nПронзание: {data['attacks'][0]['damage']['puncture']}"
    #         )

    # print(item)

    # return  item


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
    if data['active'] == True:
        voidTrader = (f"Локация: *{data['location']}\n*{data['inventory']}")

    else:
        voidTrader = (f"Баро Китир прибудет через: *{data['startString']}*\nЛокация: *{data['location']}*")
    return voidTrader


def get_worldstate_data():
    cycle =[]
    cycle.append(get_vallisCycle())
    cycle.append(get_cetusCycle())
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
    vallis_cycle = (f"Долина сфер: *{data['state']}*\nОсталось: *{data['timeLeft']}*")
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
    cetus_cycle = ( f"Цетус: *{data['state']}*\nОсталось: *{data['timeLeft']}*")

    return cetus_cycle

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
    steel_path_missions = []
    common_missions = []
    for item in data:
        mission.append((item))
    len_mission = len(mission)

    for i in range(len_mission):
        if mission[i]['isHard'] == True:
            mission_info = (
                f"*{mission[i]['missionType']}*\n{mission[i]['tier']}\n{mission[i]['eta']}\n{mission[i]['node']}\n{mission[i]['enemyKey']}")
            steel_path_missions.append(mission_info)
        else:
            mission_info = (
                f"*{mission[i]['missionType']}*\n{mission[i]['tier']}\n{mission[i]['eta']}\n{mission[i]['node']}\n{mission[i]['enemyKey']}")
            common_missions.append(mission_info)

    if mode == "Cтальной путь":
        return  steel_path_missions
    else:
        return common_missions

@bot.message_handler(commands=['start'])
def start(message):

    btn1 = types.KeyboardButton("Список разрывов бездны")
    btn2 = types.KeyboardButton("Циклы мира")
    btn3 = types.KeyboardButton("Текущая награда стального пути")
    btn4 = types.KeyboardButton("Узнать товары Баро Китира")
    btn5 = types.KeyboardButton("Найти предмет")
    btn6 = types.KeyboardButton("Текущие ивенты")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    markup.add(btn1,btn2,btn3,btn4,btn5,btn6)
    bot.send_message(message.from_user.id, "Привет,я бот-помощник для игры Warframe", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == "Циклы мира":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        data = get_worldstate_data()
        for i in range(len(data)):
            bot.send_message(message.from_user.id,data[i] , reply_markup=markup,parse_mode="Markdown")

    if message.text =="Список разрывов бездны":
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
        for i in range(len(data)):
            bot.send_message(message.from_user.id, data[i],reply_markup=markup,parse_mode="Markdown")

    if message.text == "Обычный режим":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn4 = types.KeyboardButton("Назад")
        markup.add(btn4)
        data = get_dat(message.text)
        for i in range(len(data)):
            bot.send_message(message.from_user.id, data[i],reply_markup=markup,parse_mode="Markdown")


    if message.text =="Текущая награда стального пути":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        data = get_steel_path__reward()
        bot.send_message(message.from_user.id, data, reply_markup=markup,parse_mode="Markdown")


    if message.text == "Назад":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
        btn1 = types.KeyboardButton("Циклы мира")
        btn2 = types.KeyboardButton("Список разрывов бездны")
        btn3 = types.KeyboardButton("Текущая награда стального пути")
        btn4 = types.KeyboardButton("Узнать товары Баро Китира")
        btn5 = types.KeyboardButton("Найти предмет")
        btn6 = types.KeyboardButton("Текущие ивенты")
        markup.add(btn1,btn2, btn3,btn4,btn5,btn6)
        bot.send_message(message.from_user.id, "Выберите режим", reply_markup=markup)

    if message.text == "Узнать товары Баро Китира":
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
        for i in range(len(data)):
            bot.send_message(message.from_user.id, data[i], reply_markup=markup, parse_mode="Markdown")


if __name__ == '__main__':
    while 1:
        try:
            bot.infinity_polling(non_stop = True)
        except Exception as e:
            logging.error(e)
            time.sleep(15)



