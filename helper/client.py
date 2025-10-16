import requests


# /bakiye - /qr 

api = "http://127.0.0.1:8000/bakiye"

data = {
    'kart_id': "0009242731"
}

respone = requests.post(api, json=data)


print(respone.status_code)
print(respone.json())

