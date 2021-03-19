import requests
from authlib.integrations.requests_client import OAuth2Session
import json
client_id = "Brok_1000002844"
client_secret = "HybApi#1vH!76"
Username = "bogdanov_of@hotmail.com"
password = "D2*IYgQIWx"
client = OAuth2Session(client_id, client_secret)
token = client.fetch_token("https://nlmk.shop/authorizationserver/oauth/token", username=Username, password=password)
print(token)
answ = requests.get(f'https://connect.nlmk.shop/api/v1/certificates/product/15j0Gg5fq6NZjg5', headers={"Authorization":f'Bearer {token["access_token"]}'})

answ = json.loads(str(answ.text))
print(answ[0].items())
