import requests
import asyncio
import datetime
from datetime import datetime
import pytz


def get_voidTrader():
    url = "https://api.warframestat.us/pc/ru/voidTrader"
    response = requests.get(url,verify=False)
    response.headers.get("Content-Type")
    data = response.json()
    items_list = []

    if data['active'] == True:
        items = (f"*Локация:* {data['location']}\n")
        for item_data in data['inventory']:
            item_name = item_data['item']
            ducats_value = item_data['ducats']
            credits_value = item_data['credits']
            items += f"*{'-' * 50}\nПредмет:* {item_name}\n*Дукаты*: {ducats_value}\n*Кредиты*: {credits_value}\n"
            if len(items) > 3800:
                items_list.append(items)
                items = ''
        items_list.append(items)
    else:
        items_list.append((f"Баро Китир прибудет через: *{data['startString']}*\nЛокация: *{data['location']}*"))

    return items_list



def get_steel_path_reward():
    url = "https://api.warframestat.us/pc/ru/steelPath"
    response = requests.get(url,verify=False)
    response.headers.get("Content-Type")
    data = response.json()
    steel_path_reward = (f"*{data['currentReward']['name']}*\n*Стоимость*: {data['currentReward']['cost']} стали\n")
    return steel_path_reward




def get_events():
    event_info = ""
    url = "https://api.warframestat.us/pc/events"
    params = {'language': 'ru', }
    response = requests.get(url,verify=False,params=params)
    response.headers.get("Content-Type")
    data = response.json()

    for event in data:
        if event['active'] == True:
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
                    f"{'-' * 70}\n*{event['description']}*\n*Локация: *{event['node']}\n{remaining_time}\n"))
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
                    f"{'-' * 70}\n*{event['description']}*\n*Локация: *{event['node']}\n*Награда: *{event['rewards'][0]['asString']}\n{remaining_time}\n"))
    return event_info


def get_arbitration():
    url = "https://api.warframestat.us/pc/ru/arbitration"
    response = requests.get(url,verify=False)
    response.headers.get("Content-Type")
    data = response.json()
    if 'expiry' in data:
        end_date = (data['expiry'])
        end_time = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        current_time = datetime.now(pytz.timezone("Europe/Moscow"))
        time_left = end_time - current_time
        remaining_days = time_left.days
        remaining_hours, remainder = divmod(time_left.seconds, 3600)
        remaining_minutes, _ = divmod(remainder, 60)
        remaining_time = (f"*До конца осталось:*\nДней: {remaining_days} | Часов: {remaining_hours} | Минут: {remaining_minutes}")
        arbitration = (f"*{data['type']}*\n{data['node']}\n{data['enemy']}\n{remaining_time}")
    else:
        arbitration = f"Данные обновляются"
    return arbitration


def get_fissures(mode,gamemode):
    print(mode,gamemode)
    url = "https://api.warframestat.us//pc/ru/fissures"
    response = requests.get(url,verify=False)
    response.headers.get("Content-Type")
    data = response.json()
    mission = []
    missions = ""
    for item in data:
        mission.append((item))
    len_mission = len(mission)

    match gamemode:
        case "Обычный режим","Обычный режим":
            for i in range(len_mission):
                if mission[i]['isHard'] == False & mission[i]['isStorm'] == False:
                    missions += f"*{'-' * 30}\n{mission[i]['missionType']}*\n{mission[i]['tier']}\n{mission[i]['eta']}\n{mission[i]['node']}\n{mission[i]['enemyKey']}\n"
                    return missions

        case "Обычный режим","Рейлджек":
            for i in range(len_mission):
                if mission[i]['isHard'] == False & mission[i]['isStorm'] == True:
                    missions += f"*{'-' * 30}\n{mission[i]['missionType']}*\n{mission[i]['tier']}\n{mission[i]['eta']}\n{mission[i]['node']}\n{mission[i]['enemyKey']}\n"
                    return missions

        case "Стальной путь","Обычный режим":
            for i in range(len_mission):
                if mission[i]['isHard'] == True & mission[i]['isStorm']==False:
                    missions += f"*{'-' * 30}\n{mission[i]['missionType']}*\n{mission[i]['tier']}\n{mission[i]['eta']}\n{mission[i]['node']}\n{mission[i]['enemyKey']}\n"
                    return missions

        case "Стальной путь","Рейлджек":
            for i in range(len_mission):
                if mission[i]['isHard'] == True & mission[i]['isStorm'] == True:
                    missions += f"*{'-' * 30}\n{mission[i]['missionType']}*\n{mission[i]['tier']}\n{mission[i]['eta']}\n{mission[i]['node']}\n{mission[i]['enemyKey']}\n"
                    return missions

