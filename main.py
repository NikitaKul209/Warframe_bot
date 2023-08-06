
import requests
import telebot
from telebot import types
bot = telebot.TeleBot('6451388653:AAFL6iG9PqR8-nbLSvDEhMqU5p51IC1XQPQ')
steel_path_missions= []
common_missions = []
mission = []
all_missions = []
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
                f"Стальной путь\n{mission[i]['missionType']}\n{mission[i]['tier']}\n{mission[i]['eta']}\n{mission[i]['node']}\n{mission[i]['enemyKey']}")
            steel_path_missions.append(mission_info)
        else:
            mission_info = (
                f"Обычный режим\n{mission[i]['missionType']}\n{mission[i]['tier']}\n{mission[i]['eta']}\n{mission[i]['node']}\n{mission[i]['enemyKey']}")
            common_missions.append(mission_info)

    if mode == "Cтальной путь":
        return  steel_path_missions
    else:
        return common_missions

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Список разрывов бездны")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Привет", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
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
            bot.send_message(message.from_user.id, data[i],reply_markup=markup)

    if message.text == "Обычный режим":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn4 = types.KeyboardButton("Назад")
        markup.add(btn4)
        data = get_dat(message.text)
        for i in range(len(data)):
            bot.send_message(message.from_user.id, data[i],reply_markup=markup)

    if message.text == "Назад":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn2 = types.KeyboardButton("Cтальной путь")
        btn3 = types.KeyboardButton("Обычный режим")
        markup.add(btn2, btn3)
        bot.send_message(message.from_user.id, "Выберите режим", reply_markup=markup)


if __name__ == '__main__':
    bot.infinity_polling()


