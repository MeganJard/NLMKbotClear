import json
import re
import pandas as pd
import yadisk
import requests
from authlib.integrations.requests_client import OAuth2Session

BUFFER_EXCEL_PATH = 'C:/Users/byari.GEKTOR-PC/OneDrive/NLMK_data/BUFFER.xlsx'


def get_user_info(user_id):
    for i in config:
        for j in config[i]['sklads']['sklads_dict'].keys():
            for k in config[i]['sklads']['sklads_dict'][j]['users'].keys():
                if k == user_id:
                    return config[i]['sklads']['sklads_dict'][j]['users'][k]


def check_user(user_id):
    for i in config:
        for j in config[i]['sklads']['sklads_dict'].keys():
            for k in config[i]['sklads']['sklads_dict'][j]['users'].keys():
                if k == user_id:
                    return True
    return False


def get_sklad(user_id):
    for i in config:
        for j in config[i]['sklads']['sklads_dict'].keys():
            for k in config[i]['sklads']['sklads_dict'][j]['users'].keys():
                if k == user_id:
                    return j


def get_client(user_id):
    for i in config:
        for j in config[i]['sklads']['sklads_dict'].keys():
            for k in config[i]['sklads']['sklads_dict'][j]['users'].keys():
                if k == user_id:
                    return i


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


def excel_write(data):
    y = yadisk.YaDisk(token=str(config[data['client']]['sklads']['ya_disk_token']))
    name = 'prin' if data['action'] == 'prinat' else 'otpus'
    download_path = config[data['client']]['sklads']['sklads_dict'][data['sklad']]['ya_disk_config'][
        'otpusk_path' if name == 'otpus' else 'prihod_path']
    print(download_path)
    y.download(download_path, BUFFER_EXCEL_PATH)
    book = pd.ExcelFile(BUFFER_EXCEL_PATH).parse('Sheet1')

    client_id = config[data['client']]['nlmk_connect']['client_id']
    client_secret = config[data['client']]['nlmk_connect']['client_secret']
    Username = config[data['client']]['nlmk_connect']['Username']
    password = config[data['client']]['nlmk_connect']['password']
    print(client_id, client_secret, Username, password)
    client = OAuth2Session(client_id, client_secret)
    token = client.fetch_token("https://nlmk.shop/authorizationserver/oauth/token", username=Username,
                               password=password)

    for i in range(len(data['url'])):
        line = []
        print(data['url'][i])
        answ = json.loads(
            str(requests.get(f'https://connect.nlmk.shop/api/v1/certificates/product/{data["url"][i].split("=")[1]}',
                             headers={"Authorization": f'Bearer {token["access_token"]}'}).text))[0]

        cleaned_answ = {}
        for j in answ.keys():
            if j == 'additional':
                for k in answ['additional']:
                    cleaned_answ[k] = answ['additional'][k]
            else:
                cleaned_answ[j] = answ[j]

        args_for_nlmk_api = config[data['client']]['sklads']['sklads_dict'][data['sklad']]['excel_config'][1]
        args_for_nlmk_api = args_for_nlmk_api if name == 'prin' else args_for_nlmk_api + ['number']
        print('data - ', data, 'nlmk_args - ', args_for_nlmk_api, 'nlmk_answ - ', cleaned_answ)
        for j in args_for_nlmk_api:
            if j in cleaned_answ:
                data[j] = cleaned_answ[j]
        for j in args_for_nlmk_api:
            if j == 'Qrref':
                line.append(data['url'][i])
            elif j == 'number':
                line.append(data['number'][i])
            elif j == 'code_cert':
                line.append(f'https://doc.nlmk.shop/api/v1/views/certificates/{data["code_cert"]}/scans')
            else:
                line.append(data[j])
        book = book.append(pd.DataFrame([line], columns=args_for_nlmk_api))
    book.to_excel(BUFFER_EXCEL_PATH, index=False)

    y.upload(BUFFER_EXCEL_PATH, download_path, overwrite=True)
    print('ended')


with open("config.json", encoding="utf-8") as json_file:  # Подгрузка данных о складах
    global config
    config = json.load(json_file)
    json_file.close()
