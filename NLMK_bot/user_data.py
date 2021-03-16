import json
import re
import pandas as pd
import yadisk
from syncer import sync

BUFFER_EXCEL_PATH = 'C:/Users/byari.GEKTOR-PC/OneDrive/NLMK_data/BUFFER.xlsx'


with open("sklads.json", encoding="utf-8") as json_file:  # Подгрузка данных о складах
    sklads_data = json.load(json_file)
    json_file.close()

with open("users.json", encoding="utf-8") as json_file:  # Подгрузка данных о юзерах
    users_data = json.load(json_file)
    json_file.close()

def user_status_get(user_id):
    with open('users_data.json') as json_path:
        json_file = json.load(json_path)
        json_path.close()
        if user_id in json_file.keys():

            return json_file[user_id]
        else:
            return -1


def user_data_write(user_id, data):
    with open('users_data.json', 'r') as f:
        json_data = json.load(f)
        if type(data) == list or type(data) == dict:
            json_data[user_id] = data
        else:
            json_data[user_id] = [data]

    with open('users_data.json', 'w') as f:
        f.write(json.dumps(json_data))


def url_valid(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url)

@sync
async def excel_write(data):
    y = yadisk.YaDisk(token="AgAAAAAqfZcQAAb5jHPPtbkCwkkDjCsGM6Dc4so")
    name = 'prin' if data['action'] == 'prinat' else 'otpu'
    y.download(f"/{data['sklad']}/{name}.xlsx", BUFFER_EXCEL_PATH)
    book = pd.ExcelFile(BUFFER_EXCEL_PATH).parse('Sheet1')

    for i in data['url']:
        if 'number' in data.keys():
            book = book.append(pd.DataFrame([[data['sklad'], data['TS'], i, data['time'], data['number']]]))
        else:
            book = book.append(pd.DataFrame([[data['sklad'], data['TS'], i, data['time']]]))

    book.to_excel(BUFFER_EXCEL_PATH, index=False)

    y.upload(BUFFER_EXCEL_PATH, f"/{data['sklad']}/{name}.xlsx", overwrite=True)


