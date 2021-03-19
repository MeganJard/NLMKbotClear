import yadisk
import json
import argparse
import pandas as pd



import posixpath
import os
import yadisk


with open("config.json", encoding="utf-8") as json_file:  # Подгрузка данных о складах
    global config
    config = json.load(json_file)
    json_file.close()
parser = argparse.ArgumentParser()
parser.add_argument("client_id", type=str)
args = parser.parse_args()
y = yadisk.YaDisk(token=str(config[args.client_id]['sklads']['ya_disk_token']))
for i in config[args.client_id]['sklads']['sklads_dict'].keys():
    prinat_path = config[args.client_id]['sklads']['sklads_dict'][i]['ya_disk_config']['prihod_path']
    otpus_path = config[args.client_id]['sklads']['sklads_dict'][i]['ya_disk_config']['otpusk_path']
    data = {i: [] for i in config[args.client_id]['sklads']['sklads_dict'][i]['excel_config'][1]}
    excel_file = pd.DataFrame(data)
    excel_file.to_excel('buffer.xlsx', index=False)
    y.upload('buffer.xlsx', prinat_path, overwrite=True)
    data = {i: [] for i in config[args.client_id]['sklads']['sklads_dict'][i]['excel_config'][1] + ['number']}
    excel_file = pd.DataFrame(data)
    excel_file.to_excel('buffer.xlsx', index=False)
    y.upload('buffer.xlsx', otpus_path, overwrite=True)


