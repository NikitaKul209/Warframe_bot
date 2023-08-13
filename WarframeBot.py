import re
import os
import requests
import telebot
from telebot import types
import datetime
from datetime import datetime
import pytz
import schedule
import time
from threading import Thread
import json

class WarframeBot:

    def __init__(self):

        with open('token.txt') as file:
            token = file.read()
        self.bot = telebot.TeleBot(token, threaded=False)

        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            self.start(message)

        # Декоратор для обработки текстовых сообщений
        @self.bot.message_handler(content_types=['text'])
        def handle_text_messages(message):
            self.get_text_messages(message)

        if os.path.isfile('subscribers.json'):
            with open("subscribers.json", "r") as file:
                self.subscribers = json.load(file)
                self.start_all_schedule_notification()
                print(f'Загружен файл: {self.subscribers}')
        else:
            with open("subscribers.json", "w") as file:
                print("Создан новый файл с подписчиками")
                self.subscribers = {}
                json.dump(self.subscribers, file)

    def get_events(self):
        event_info = ""
        self.events = []
        url = "https://api.warframestat.us/pc/events"
        params = {'language': 'ru', }
        response = requests.get(url,params=params)
        response.headers.get("Content-Type")
        data = response.json()
        for event in data:
            self.events.append(event)
        for i in range(len(self.events)):
            end_date = (self.events[i]['expiry'])
            end_time = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            current_time = datetime.now(pytz.timezone("Europe/Moscow"))
            time_left = end_time - current_time
            remaining_days = time_left.days
            remaining_hours, remainder = divmod(time_left.seconds, 3600)
            remaining_minutes, _ = divmod(remainder, 60)
            remaining_time = (f"*До конца ивента осталось*:\nДней: {remaining_days} | Часов: {remaining_hours} | Минут: {remaining_minutes}")
            event_info+=((f"{'-'*70}\n*{self.events[i]['description']}*\n*Локация: *{self.events[i]['node']}\n*Награда: *{self.events[i]['rewards'][0]['asString']}\n{remaining_time}\n"))
        return event_info

    def get_warframe_description(self, data):
        warframe_info = f"*Имя Warframe:* {data['name']}\n*Описание:* {data['description']}\n{'-' * 70}"
        ability_counter = 1

        for ability in data['abilities']:
            ability['description'] = re.sub(r'<[^>]+>', '', ability['description'])
            warframe_info += f"\n*Способность* {ability_counter}: {ability['name']}\n*Описание способности*: {ability['description']}\n"
            ability_counter += 1

        return warframe_info

    def print_data(self,data, indent=0):
        output = ""

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
                    output += self.print_data(value, indent + 2)  # Добавляем результат рекурсивного вызова в переменную output
                else:
                    output += " " * indent + key.capitalize() + ": " + str(value) + "\n"
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    output += self.print_data(item, indent)  # Добавляем результат рекурсивного вызова в переменную output
        return output  # Возвращаем результат вместо вывода на экран


    def get_item(self,message):
        msg = message
        name = message.text
        if name.lower() == 'назад':
            self.get_text_messages(message)
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        url = f"https://api.warframestat.us/items/{name}"
        params = {'only':["name,description,attacks,type,abilities"],'language':'ru',}
        # params = {'language':'ru',}
        response = requests.get(url,params=params)
        response.headers.get("Content-Type")
        data = response.json()

        print(data)

        if 'error' in data:
            items = "Предмет не найден или возникла ошибка"

        elif data['type'] == 'Warframe':

            items = self.get_warframe_description(data)
            print(items)
        else:
            items = self.print_data(data)

        self.bot.send_message(msg.from_user.id, items, reply_markup=markup,parse_mode="Markdown" )
        self.bot.register_next_step_handler(message, self.get_item)
        return items


    def get_voidTrader(self):
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


    def get_arbitration(self):
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


    def get_worldstate_data(self):
        cycle =''
        cycle +=self.get_vallisCycle()
        cycle +=self.get_cambionCycle()
        cycle += self.get_cetusCycle()
        return cycle

    def get_vallisCycle(self):
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

    def get_cetusCycle(self):
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


    def get_cambionCycle(self):
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

    def get_steel_path__reward(self):
        url = "https://api.warframestat.us/pc/ru/steelPath"
        response = requests.get(url)
        response.headers.get("Content-Type")
        data = response.json()
        steel_path_reward = (f"*{data['currentReward']['name']}*\n*Стоимость*: {data['currentReward']['cost']} стали\n")
        return steel_path_reward


    def get_dat(self,mode):
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


    def start(self,message):
        btn1 = types.KeyboardButton("Разрывы бездны")
        btn2 = types.KeyboardButton("🌑 Циклы мира 🌞")
        btn3 = types.KeyboardButton("Текущая награда стального пути")
        btn4 = types.KeyboardButton("Товары Баро Китира")
        btn5 = types.KeyboardButton("Найти предмет")
        btn6 = types.KeyboardButton("Текущие ивенты")
        btn7 = types.KeyboardButton("Арбитраж")
        if str(message.chat.id) in self.subscribers:
            btn8 = types.KeyboardButton("Отписаться от уведомлений")
        else:
            btn8 = types.KeyboardButton("Подписаться на уведомления")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        markup.add(btn1,btn2,btn3,btn4,btn5,btn6,btn7,btn8)
        self.bot.send_message(message.from_user.id, "Привет,я бот-помощник для игры Warframe", reply_markup=markup)


    def get_text_messages(self,message):

        if message.text == "🌑 Циклы мира 🌞":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Назад")
            markup.add(btn1)
            data = self.get_worldstate_data()
            self.bot.send_message(message.from_user.id,data , reply_markup=markup,parse_mode="Markdown")

        if message.text =="Разрывы бездны":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn2 = types.KeyboardButton("Cтальной путь")
            btn3 = types.KeyboardButton("Обычный режим")
            markup.add(btn2,btn3)
            self.bot.send_message(message.from_user.id, "Выберите режим", reply_markup=markup)

        if message.text == "Cтальной путь":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn4 = types.KeyboardButton("Назад")
            markup.add(btn4)
            data = self.get_dat(message.text)
            self.bot.send_message(message.from_user.id, data,reply_markup=markup,parse_mode="Markdown")

        if message.text == "Обычный режим":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn4 = types.KeyboardButton("Назад")
            markup.add(btn4)
            data = self.get_dat(message.text)
            self.bot.send_message(message.from_user.id, data,reply_markup=markup,parse_mode="Markdown")

        if message.text =="Текущая награда стального пути":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Назад")
            markup.add(btn1)
            data = self.get_steel_path__reward()
            self.bot.send_message(message.from_user.id, data, reply_markup=markup,parse_mode="Markdown")


        if message.text == "Назад":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
            btn1 = types.KeyboardButton("🌑 Циклы мира 🌞")
            btn2 = types.KeyboardButton("Разрывы бездны")
            btn3 = types.KeyboardButton("Текущая награда стального пути")
            btn4 = types.KeyboardButton("Товары Баро Китира")
            btn5 = types.KeyboardButton("Найти предмет")
            btn6 = types.KeyboardButton("Текущие ивенты")
            btn7 = types.KeyboardButton("Арбитраж")
            if str(message.chat.id) in self.subscribers:
                btn8 = types.KeyboardButton("Отписаться от уведомлений")
            else:
                btn8 = types.KeyboardButton("Подписаться на уведомления")
            markup.add(btn1,btn2, btn3,btn4,btn5,btn6,btn7,btn8)
            self.bot.send_message(message.from_user.id, "Выберите режим", reply_markup=markup)

        if message.text == "Товары Баро Китира":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Назад")
            markup.add(btn1)
            data = self.get_voidTrader()
            self.bot.send_message(message.from_user.id, data, reply_markup=markup,parse_mode="Markdown")

        if message.text == "Найти предмет":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Назад")
            markup.add(btn1)
            self.bot.send_message(message.from_user.id, "Введите название предмета", reply_markup=markup, parse_mode="Markdown")
            self.bot.register_next_step_handler(message,self.get_item)

        if message.text == "Текущие ивенты":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Назад")
            markup.add(btn1)
            data = self.get_events()
            self.bot.send_message(message.from_user.id, data, reply_markup=markup, parse_mode="Markdown")

        if message.text == "Арбитраж":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Назад")
            markup.add(btn1)
            data = self.get_arbitration()
            self.bot.send_message(message.from_user.id, data, reply_markup=markup, parse_mode="Markdown")

        if message.text == "Подписаться на уведомления":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Назад")
            markup.add(btn1)
            self.bot.send_message(message.from_user.id,'Вы подписываетесь на уведомления о разрывах бездны стального пути.\n\nВведите интервал уведомлений в минутах' , reply_markup=markup,parse_mode="Markdown")
            self.bot.register_next_step_handler(message, self.set_notification_interval)

        if message.text == "Отписаться от уведомлений":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Назад")
            markup.add(btn1)
            self.bot.send_message(message.chat.id, "Вы отписались от уведомлений.", reply_markup=markup)
            if str(message.chat.id) in self.subscribers:
                schedule.clear(tag=message.chat.id)
                del self.subscribers[str(message.chat.id)]
                with open("subscribers.json", "w") as file:
                    json.dump(self.subscribers, file)
                    # print(f'Подписчик удалён: {subscribers}')

    def set_notification_interval(self,message):
        chat_id = message.chat.id
        if message.text.lower() == 'назад':
            self.get_text_messages(message)
            return
        try:
            minutes = int(message.text)
            if minutes <= 0 or minutes>  720:
                self.bot.send_message(chat_id, "Интервал должен быть положительным числом не более 720 минут.Пожалуйста, попробуйте снова.")
                self.bot.register_next_step_handler(message, self.set_notification_interval)
                return
            self.subscribers[str(message.chat.id)] = True, minutes
            with open("subscribers.json", "w") as file:
                json.dump(self.subscribers, file)
            # print(f'Новый подписчик: {subscribers}')

            self.bot.send_message(chat_id, f"Интервал для уведомлений успешно установлен на {minutes} минут.")
            schedule.clear(tag=chat_id)
            self.schedule_notification(chat_id, minutes)
        except ValueError:
            self.bot.send_message(chat_id, "Пожалуйста, введите целое число минут. Пожалуйста, попробуйте снова.")
            self.bot.register_next_step_handler(message, self.set_notification_interval)


    def schedule_notification(self,chat_id, minutes):
        schedule.every(minutes).minutes.do(self.send_notification, chat_id).tag(chat_id)

    def start_all_schedule_notification(self):
        if len(self.subscribers) == 0:
            return
        else:
            for i in self.subscribers:
                schedule.every(self.subscribers[i][1]).minutes.do(self.send_notification, i).tag(i)


    def send_notification(self,chat_id):
        if str(chat_id) in self.subscribers:
            data = self.get_dat("Cтальной путь")
            notification_text = "*Текущие разрывы бездны стального пути!*\n"
            self.bot.send_message(chat_id,notification_text+data, parse_mode="Markdown")

    def run_schedule(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    while 1:
        try:
            bot = WarframeBot()
            schedule_thread = Thread(target=bot.run_schedule).start()
            bot.bot.infinity_polling()
        except Exception:
            time.sleep(5)


