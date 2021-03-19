import vk_api
from user_data import *
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from threading import *
import datetime


def reload():
    global config
    with open(CONFIG_PATH, encoding="utf-8") as json_file:  # Подгрузка данных
        config = json.load(json_file)
        json_file.close()


VK_BOT_TOKEN = "8a1a10d828bc9726cd6fd6637f3e6142f57fc8af82cdf86f8dd35030606f53a46821de932314f01c10256"
CONFIG_PATH = "config.json"
VK_GROUP_ID = 203228178

vk_session = vk_api.VkApi(token=VK_BOT_TOKEN)
longpoll = VkBotLongPoll(vk_session, VK_GROUP_ID)  # инициализация бота
vk = vk_session.get_api()
Lslongpoll = VkLongPoll(vk_session)
Lsvk = vk_session.get_api()

for event in Lslongpoll.listen():
    reload()
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        vk_id = str(event.user_id)
        if user_status_get(vk_id) == -1:
            if check_user(vk_id):
                user_data_write(vk_id, {"status": 1})
            else:
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message="К сожалению, Вас нет в базе",
                    random_id=get_random_id()
                )
        elif user_status_get(vk_id)["status"] == 1:
            if event.text == "Принять ТС":
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message="Введите номер транспортного средства",
                    random_id=get_random_id())
                user_data_write(vk_id, {"status": 2, "action": "prinat"})
            elif event.text == "Отпустить ТС":
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message="Введите номер транспортного средства",
                    random_id=get_random_id())
                user_data_write(vk_id, {"status": 2, "action": "otpus"})
            else:

                message_data = f'Вот ваше меню, {get_user_info(vk_id)["name"]}'
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button("Принять ТС", color=VkKeyboardColor.POSITIVE)
                keyboard.add_button("Отпустить ТС", color=VkKeyboardColor.POSITIVE)
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message=message_data,
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard())
        elif user_status_get(vk_id)["status"] == 2:
            if event.text == "Да":
                user_data_write(vk_id, {**user_status_get(vk_id), "status": 3})
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button("Закончить погрузку", color=VkKeyboardColor.POSITIVE)
                keyboard.add_button("Изменить название ТС", color=VkKeyboardColor.NEGATIVE)
                keyboard.add_line()
                keyboard.add_button("Добавить рулон", color=VkKeyboardColor.POSITIVE)
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message=f"Меню записи рулонов",
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard())
            elif event.text == "Нет":
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message="Введите номер ТС",
                    random_id=get_random_id())
            else:
                user_data_write(vk_id, {**user_status_get(vk_id), "tsNumber": event.text, "status": 2})
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button("Да", color=VkKeyboardColor.POSITIVE)
                keyboard.add_button("Нет", color=VkKeyboardColor.NEGATIVE)
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message=f"Номер ТС - {event.text.lower()}, подтвердить?",
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard())
        elif user_status_get(vk_id)["status"] == 3:
            if event.text == "Добавить рулон":
                user_data_write(vk_id, {**user_status_get(vk_id), "status": 4})
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message=f"Введите отсканированную ссылку",
                    random_id=get_random_id())
            elif event.text == "Закончить погрузку":
                if not 'url' in user_status_get(vk_id):
                    keyboard = VkKeyboard()
                    keyboard.add_button("Продолжить", color=VkKeyboardColor.POSITIVE)
                    Lsvk.messages.send(
                        user_id=event.user_id,
                        message=f"Нет отсканированных ссылок",
                        random_id=get_random_id(),
                        keyboard=keyboard.get_keyboard())
                    continue
                data = user_status_get(vk_id)
                del data['status']
                keyboard = VkKeyboard()
                keyboard.add_callback_button("Понятно", color=VkKeyboardColor.POSITIVE)
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message=f"Обработка...",
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard())
                thread = Thread(target=excel_write,
                                args=({**user_status_get(vk_id), "operDateTime": str(datetime.datetime.now()),
                                       "sklad": get_sklad(vk_id), "client": get_client(vk_id)},))
                thread.start()
                print(data)
                user_data_write(vk_id, {"status": 1})
                keyboard = VkKeyboard()
                keyboard.add_button("Продолжить", color=VkKeyboardColor.POSITIVE)
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message=f"Офромление ТС закончено",
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard())
            elif event.text == "Изменить название ТС":
                data = user_status_get(vk_id)
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message=f"Введите номер ТС",
                    random_id=get_random_id())
                data['status'] = 2
                user_data_write(vk_id, data)
            else:
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button("Закончить погрузку", color=VkKeyboardColor.POSITIVE)
                keyboard.add_button("Изменить название ТС", color=VkKeyboardColor.NEGATIVE)
                keyboard.add_line()
                keyboard.add_button("Добавить рулон", color=VkKeyboardColor.POSITIVE)
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message=f"Меню записи рулонов",
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard())

        elif user_status_get(vk_id)["status"] == 4:
            if url_valid(event.text):
                if user_status_get(vk_id)['action'] == 'prinat':
                    if "url" in user_status_get(vk_id).keys():
                        datas = user_status_get(vk_id)
                        urls = user_status_get(vk_id)["url"] + [event.text]
                        datas["status"] = 3
                        datas["url"] = urls

                        user_data_write(vk_id, datas)
                    else:
                        user_data_write(vk_id, {**user_status_get(vk_id), "status": 3, "url": [event.text]})
                    keyboard = VkKeyboard()
                    keyboard.add_button("Продолжить", color=VkKeyboardColor.POSITIVE)
                    Lsvk.messages.send(
                        user_id=event.user_id,
                        message=f"Ссылка обработана",
                        random_id=get_random_id(),
                        keyboard=keyboard.get_keyboard())
                elif user_status_get(vk_id)['action'] == 'otpus':
                    if "url" in user_status_get(vk_id).keys():
                        datas = user_status_get(vk_id)
                        urls = user_status_get(vk_id)["url"] + [event.text]
                        datas["status"] = 5
                        datas["url"] = urls
                        user_data_write(vk_id, datas)
                    else:
                        user_data_write(vk_id, {**user_status_get(vk_id), "status": 5, "url": [event.text]})
                    Lsvk.messages.send(
                            user_id=event.user_id,
                            message=f"Введите количество",
                            random_id=get_random_id())
            else:
                user_data_write(vk_id, {**user_status_get(vk_id), "status": 3})
                keyboard = VkKeyboard()
                keyboard.add_button("Продолжить", color=VkKeyboardColor.POSITIVE)
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message="Невалидная ссылка",
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard())
        elif user_status_get(vk_id)['status'] == 5:
            if event.text.isdigit():
                data = user_status_get(vk_id)
                if 'number' in data:
                    numbers = data['number'] + [event.text]
                else:
                    numbers = [event.text]
                user_data_write(vk_id, {**user_status_get(vk_id), "status": 3, 'number': numbers})
                keyboard = VkKeyboard()
                keyboard.add_button("Продолжить", color=VkKeyboardColor.POSITIVE)
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message=f"Ссылка обработана",
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard())
            else:
                Lsvk.messages.send(
                    user_id=event.user_id,
                    message=f"Введите количество",
                    random_id=get_random_id())
