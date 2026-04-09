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
from telebot import apihelper
import json

class WarframeBot:

    def __init__(self):
        # apihelper.proxy = {'https':'socks5://127.0.0.1:40000'}
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


    def get_price_from_wfmarket(self):
        url = "https://api.warframe.market/v2/orders/item/ris/"
        params = {'language': 'ru', }
        response = requests.get(url, params=params)

        online_sell_orders = [i for i in response.json()["data"] if i["type"] == "sell" and i["user"]["status"] == "ingame"]
        max_price = max(order["platinum"] for order in online_sell_orders)
        min_price = min(order["platinum"] for order in online_sell_orders)
        avg_price = sum(order["platinum"] for order in online_sell_orders)/len(online_sell_orders)
        print(max_price)
        print(min_price)
        print(avg_price)



        return response

    def get_nighthwave(self):
        nightwave_missions = ""
        url = "https://api.warframestat.us/pc/nightwave"
        params = {'language': 'ru', }
        response = requests.get(url,params=params)
        response.headers.get("Content-Type")
        data = response.json()
        for missions in (data["activeChallenges"]):
            nightwave_missions += f'*Задание:* {missions["title"]}\n*Описание:* {missions["desc"]}\n*Репутация:* {missions["reputation"]}\n*{"-"*50}*\n'
        return nightwave_missions


    def get_events(self):
        event_info = ""
        self.events = []
        url = "https://api.warframestat.us/pc/events"
        params = {'language': 'ru', }
        response = requests.get(url,params=params)
        response.headers.get("Content-Type")
        data = response.json()
        for event in data:

            if len(event['rewards']) == 0:

                end_date = event['expiry']
                end_time = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                current_time = datetime.now(pytz.timezone("Europe/Moscow"))
                time_left = end_time - current_time
                remaining_days = time_left.days
                remaining_hours, remainder = divmod(time_left.seconds, 3600)
                remaining_minutes, _ = divmod(remainder, 60)
                remaining_time = (f"*До конца ивента осталось*:\nДней: {remaining_days} | Часов: {remaining_hours} | Минут: {remaining_minutes}")
                event_info += ((
                    f"{'-' * 70}\n*{event['description']}*\n{remaining_time}\n"))
            else:
                end_date = event['expiry']
                end_time = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                current_time = datetime.now(pytz.timezone("Europe/Moscow"))
                time_left = end_time - current_time
                remaining_days = time_left.days
                remaining_hours, remainder = divmod(time_left.seconds, 3600)
                remaining_minutes, _ = divmod(remainder, 60)
                remaining_time = (f"*До конца ивента осталось*:\nДней: {remaining_days} | Часов: {remaining_hours} | Минут: {remaining_minutes}")
                event_info += ((
                    f"{'-' * 70}\n*{event['description']}*\n*Локация: *{event['node']}\n*Награда: *{event['rewards'][0]['items']}\n{remaining_time}\n"))
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

        translate= {
            'Rifle': 'Винтовка',
            'Shotgun':'Дробовик',
            'Pistol':'Пистолет',
            'puncture': 'Пронзание',
            'impact':'Удар',
            'slash':'Разрез',
            'Radiation':'Радиация',
            'Electricity':'Электричество',
            'Blast':'Взрыв',
            'crit_chance': 'Шанс крита',
            'crit_mult':'Множитель крит урона',
            'status_chance': 'Шанс статуса',
            'Attacks:':f'<strong>{"_"*40}</strong>',
            'Damage':'Урон',
            'Falloff':'Уменьшение урона с расстоянием',
            'Start':'Начальное значение',
            'End':'Конечное значение',
            'Reduction':'Снижение за метр',
            'Incarnon Mode AoE':'Инкарнон режим с уроном по площади',
            'Incarnon Mode':f'<strong>{"_"*40}\nИнкарнон режим</strong>',
            'Normal Attack':'Обычная атака',
            'Shot_type':'Тип выстрела',
            'Hit-Scan':'Мговенное попадание',
            'Mid-Flight Detonation':'',
            'Projectile':'Снаряд',
            'Fully Spooled':'Режим: Полностью автоматический',
            'Shot_Speed':'Скорость полёта снаряда',
            'Speed':'Скорострельность',
            'Viral':'Вирус',
            'Melee':'Ближний бой',
            'Throw':'Режим: метательное',
        }


        if 'name' in data:
            output += f"<strong>{data['name']}</strong>\n\n"
        if 'description' in data:
            output += "<strong>Описание:</strong> " + data['description'] + "\n"
        if 'type' in data:
            output += "Тип: " + data['type'] + "\n"

        if isinstance(data, dict):
            for key, value in data.items():
                if key in ['name', 'description', 'type']:
                    continue  # Пропускаем вывод 'name', 'description' и 'type', так как они уже выведены ранее
                if isinstance(value, (dict, list)):
                    output += f'{" " * indent}{key.capitalize()}:\n'
                    output += self.print_data(value, indent + 2)  # Добавляем результат рекурсивного вызова в переменную output
                else:
                    translate_item = translate.get(str(value), str(value))
                    output += f'{" " * indent}{key.capitalize()}: {translate_item}\n'
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    output += self.print_data(item, indent)  # Добавляем результат рекурсивного вызова в переменную output
        output = self.translate_text_with_case(output,translate)
        return output  # Возвращаем результат вместо вывода на экран

    def translate_text_with_case(self,text, translations):
        translated_text = text
        for original, translation in translations.items():
            pattern = re.compile(re.escape(original), re.IGNORECASE)
            translated_text = pattern.sub(translation, translated_text)
        return translated_text

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
        params = {'only':["name,description,attacks,type,abilities,"],'language':'ru',}
        response = requests.get(url,params=params)
        response.headers.get("Content-Type")
        data = response.json()
        if 'error' in data:
            items = "Предмет не найден или возникла ошибка"
            parse_mode = "HTML"
        elif data['type'] == 'Warframe':
            items = self.get_warframe_description(data)
            parse_mode = "Markdown"
        else:
            items = self.print_data(data)
            parse_mode = "HTML"
        self.bot.send_message(msg.from_user.id, items, reply_markup=markup,parse_mode=parse_mode )
        self.bot.register_next_step_handler(message, self.get_item)
        return items


    def get_voidTrader(self):
        url = "https://api.warframestat.us/pc/ru/voidTrader"
        response = requests.get(url)
        response.headers.get("Content-Type")
        data = response.json()

        time_left = self.make_msk_time(data['activation'])
        items_list = []
        if data['inventory'] == True:
                items = (f"*Локация:* {data['location']}\n")
                for item_data in data['inventory']:
                    item_name = item_data['item']
                    ducats_value = item_data['ducats']
                    credits_value = item_data['credits']
                    items += f"*{'-'*50}\nПредмет:* {item_name}\n*Дукаты*: {ducats_value}\n*Кредиты*: {credits_value}\n"

                    if len(items)> 3800:
                        items_list.append(items)
                        items =''
                items_list.append(items)
        else:
            items_list.append((f"Баро Китир прибудет через: *{time_left}*\nЛокация: *{data['location']}*"))

        return items_list


    def get_arbitration(self):
        # url = "https://api.warframestat.us/pc/ru/arbitration"
        # response = requests.get(url)
        # response.headers.get("Content-Type")
        # data = response.json()
        # print(data)
        # if 'expiry' in data:
        #     end_date = (data['expiry'])
        #     end_time = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        #     current_time = datetime.now(pytz.timezone("Europe/Moscow"))
        #     time_left = end_time - current_time
        #     remaining_days = time_left.days
        #     remaining_hours, remainder = divmod(time_left.seconds, 3600)
        #     remaining_minutes, _ = divmod(remainder, 60)
        #     remaining_time = (f"*До конца осталось:*\nДней: {remaining_days} | Часов: {remaining_hours} | Минут: {remaining_minutes}")
        #     arbitration = (f"*{data['type']}*\n{data['node']}\n{data['enemy']}\n{remaining_time}")
        # else:
        #     arbitration = f"Данные обновляются"
        # return arbitration
        return (f"Эта хуйня, к сожалению, больше не работает(")

    def get_worldstate_data(self):
        cycle =''
        cycle += self.get_cetusCycle()
        cycle += self.get_earthCycle()
        cycle += self.get_vallisCycle()
        cycle += self.get_cambionCycle()

        return cycle

    def get_vallisCycle(self):
        url = "https://api.warframestat.us/pc/ru/vallisCycle"
        response = requests.get(url)
        response.headers.get("Content-Type")
        data = response.json()
        timeLeft =  self.make_msk_time(data['expiry'])


        if data['state'] == "cold":
            vallis_cycle = (f"{'-' * 50}\n*Долина сфер:* Холод\n*Тепло через:* {timeLeft}\n")
        else:
            vallis_cycle = (f"{'-'* 50}\n*Долина сфер:* Тепло\n*Холод через:* {timeLeft}\n")
        return vallis_cycle


    def get_earthCycle(self):
        url ="https://api.warframestat.us/pc/earthCycle/"
        response = requests.get(url)
        response.headers.get("Content-Type")
        data = response.json()
        end_time = datetime.fromisoformat(data['expiry'].replace("Z", "+00:00"))
        current_time = datetime.now(pytz.timezone("Europe/Moscow"))
        time_left = end_time - current_time
        if data['state'] =='night':
            earth_cycle = f"{'-'*50}\n*Земля*: Ночь\n*День через:* {data['timeLeft']}\n"
        else:
            earth_cycle = f"{'-'*50}\n*Земля*: День\n*Ночь через:* {data['timeLeft']}\n"
        return earth_cycle

    def get_cetusCycle(self):
        url = "https://api.warframestat.us/pc/ru/cetusCycle"
        response = requests.get(url)
        response.headers.get("Content-Type")
        data = response.json()

        # end_time = datetime.fromisoformat(data['expiry'].replace("Z", "+00:00"))
        # current_time = datetime.now(pytz.timezone("Europe/Moscow"))
        # time_left = end_time - current_time
        # time_left = self.make_msk_time(data['expiry'])
        if data['state'] == "night":
            cetus_cycle = (f"{'-' * 50}\n*Цетус:* Ночь\n*День через: *{data['timeLeft']}\n")
        else:
            cetus_cycle = ( f"{'-'*50}\n*Цетус:* День\n*Ночь через: *{data['timeLeft']}\n")
        return cetus_cycle


    def get_cambionCycle(self):
        url = "https://api.warframestat.us/pc/ru/cambionCycle"
        response = requests.get(url)
        response.headers.get("Content-Type")
        data = response.json()
        end_time = datetime.fromisoformat(data['expiry'].replace("Z", "+00:00"))
        current_time = datetime.now(pytz.timezone("Europe/Moscow"))
        time_left = end_time - current_time
        if data['state'] == "vome":
            cambion_cycle = (f"{'-' * 50}\n*Камбионский дрейф:* Воум\n*Фэз через:* {data['timeLeft']}\n")
        else:
            cambion_cycle = (f"{'-' * 50}\n*Камбионский дрейф:* Фэз\n*Воум через:* {data['timeLeft']}\n")
        return cambion_cycle

    def get_news(self):
        url ="https://api.warframestat.us/pc/ru/news"
        response = requests.get(url)
        response.headers.get("Content-Type")
        data = response.json()
        game_news=''

        for news in data:
            game_news+=f'\n[{news["message"]}]({news["link"]})\n*{"-"*40}*\n'
        return game_news

    def get_steel_path__reward(self):
        url = "https://api.warframestat.us/pc/ru/steelPath"
        response = requests.get(url)
        response.headers.get("Content-Type")
        data = response.json()
        steel_path_reward = (f"*Награда: {data['currentReward']['name']}*\n*Стоимость: {data['currentReward']['cost']} стали\n*")
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
                end_time = self.make_msk_time(mission[i]['expiry'])
                steel_missions += f"*{'-' * 30}\n{mission[i]['missionType']}*\n{mission[i]['tier']}\n{end_time}\n{mission[i]['node']}\n{mission[i]['enemyKey']}\n"
                steel_iteration += 1
            else:
                end_time = self.make_msk_time(mission[i]['expiry'])
                common_missions += f"*{'-' * 30}\n{mission[i]['missionType']}*\n{mission[i]['tier']}\n{end_time}\n{mission[i]['node']}\n{mission[i]['enemyKey']}\n"
                common_iteration +=1
        if mode == "Cтальной путь":
            return  steel_missions
        else:
            return common_missions


    def start(self,message):
        btn1 = types.KeyboardButton("Разрывы бездны")
        btn2 = types.KeyboardButton("🌑 Циклы мира 🌞")
        btn3 = types.KeyboardButton("Текущая награда СП")
        btn4 = types.KeyboardButton("Товары Баро Китира")
        btn5 = types.KeyboardButton("Найти предмет")
        btn6 = types.KeyboardButton("Текущие ивенты")
        btn7 = types.KeyboardButton("Арбитраж")
        btn8 = types.KeyboardButton("Задания ночной волны")
        btn9 = types.KeyboardButton("Новости")
        btn11 = types.KeyboardButton("Узнать цену на WF Market")

        if str(message.chat.id) in self.subscribers:
            btn10 = types.KeyboardButton("Отписаться от уведомлений")
        else:
            btn10 = types.KeyboardButton("Уведомления СП")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        markup.add(btn1,btn2,btn3,btn4,btn5,btn6,btn7,btn8, btn9,btn10,btn11)
        self.bot.send_message(message.from_user.id, "Привет,я бот-помощник для игры Warframe", reply_markup=markup)


    def get_text_messages(self,message):

        if message.text == "Узнать цену на WF Market":
            data = self.get_price_from_wfmarket()
            print(data)
        if message.text == "🌑 Циклы мира 🌞":
            data = self.get_worldstate_data()
            self.bot.send_message(message.from_user.id,data,parse_mode="Markdown")

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

        if message.text =="Текущая награда СП":
            data = self.get_steel_path__reward()
            self.bot.send_message(message.from_user.id, data,parse_mode="Markdown")


        if message.text == "Назад":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
            btn1 = types.KeyboardButton("🌑 Циклы мира 🌞")
            btn2 = types.KeyboardButton("Разрывы бездны")
            btn3 = types.KeyboardButton("Текущая награда СП")
            btn4 = types.KeyboardButton("Товары Баро Китира")
            btn5 = types.KeyboardButton("Найти предмет")
            btn6 = types.KeyboardButton("Текущие ивенты")
            btn7 = types.KeyboardButton("Арбитраж")
            btn8 = types.KeyboardButton("Задания ночной волны")
            btn9 = types.KeyboardButton("Новости")

            if str(message.chat.id) in self.subscribers:
                btn10 = types.KeyboardButton("Отписаться от уведомлений")
            else:
                btn10 = types.KeyboardButton("Уведомления СП")
            markup.add(btn1,btn2, btn3,btn4,btn5,btn6,btn7,btn8, btn9,btn10)
            self.bot.send_message(message.from_user.id, "Выберите режим", reply_markup=markup)

        if message.text == "Товары Баро Китира":
            data = self.get_voidTrader()
            for i in range (len(data)):
                self.bot.send_message(message.from_user.id, data[i],parse_mode="Markdown")

        if message.text == "Найти предмет":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Назад")
            markup.add(btn1)
            self.bot.send_message(message.from_user.id, "Введите название предмета", reply_markup=markup, parse_mode="Markdown")
            self.bot.register_next_step_handler(message,self.get_item)

        if message.text == "Текущие ивенты":
            data = self.get_events()
            self.bot.send_message(message.from_user.id, data, parse_mode="Markdown")

        if message.text == "Арбитраж":
            data = self.get_arbitration()
            self.bot.send_message(message.from_user.id, data, parse_mode="Markdown")

        if message.text == "Уведомления СП":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Назад")
            markup.add(btn1)
            self.bot.send_message(message.from_user.id,'Вы подписываетесь на уведомления о разрывах бездны стального пути.\n\n'
                                                       'Введите интервал уведомлений в минутах' , reply_markup=markup,parse_mode="Markdown")
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


        if message.text == ("Новости"):
            data = self.get_news()
            self.bot.send_message(message.from_user.id, data, parse_mode="Markdown",disable_web_page_preview=True)



        if message.text == ("Задания ночной волны"):
            data = self.get_nighthwave()
            self.bot.send_message(message.from_user.id, data, parse_mode="Markdown", disable_web_page_preview=True)
    def make_msk_time(self,end_time):
        end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        current_time = datetime.now(pytz.timezone("Europe/Moscow"))
        time_left = end_time - current_time
        remaining_days = time_left.days
        remaining_hours, remainder = divmod(time_left.seconds, 3600)
        remaining_minutes, _ = divmod(remainder, 60)
        remaining_time = (
            f"{remaining_days}d {remaining_hours}h {remaining_minutes}m")
        return remaining_time

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


