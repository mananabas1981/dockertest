import requests
from app.util.json import json_stringify
def http(url, data = {}) -> str:
    ret = ""
    try:
        req = requests.post(url, None, json_stringify(data))
        ret = req.text
    except Exception as er:
        print(er)
    return ret


