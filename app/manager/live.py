from time import sleep, time_ns
from app.util.session import session
from app.util.json import json_parse, json_stringify
from app.model.user_model import AccessModel
from app.util.date import date_time

from app.lib.sql import sql 

class User:
    def __init__(this, client = None, key = None, name = None):
        this.client = client
        this.key = key
        this.name = name
        

clients = set()

def live_app(client):
 

    msg = client.receive()
    
    if msg is None: return 
    
    data = json_parse(msg)
    if not data:
        return 
    
    if not 'id' in data:
        return         
    
    token = data['id']

    # we only allow one browser to use the socket as posible
    # first layer security
    resp = {
        'type': '',
        'msg': ''
    }

    for x in clients:
        if x.key == token:
            print('Access denied, we only allowed one socket per user')
            resp['msg'] = f'Duplicate auth! were closing your connection! Total Live Con: {len(clients)}'
            client.send(json_stringify(resp))
            return 
    
    # second layer security
    # where check the session
    ses = session(token, True)

    if not ses.get('uid'):
        resp['msg'] = 'You are not authorized!'
        client.send(json_stringify(resp))
        return 
    

    # we add secuirity level to avoid server overloaded!

    user = User(client = client, key = token, name = ses.get('name'))

    clients.add(user)

    

    for x in clients:
        list_user = []
        for y in clients:
            list_user.append(y.name)

        resp['list'] = list_user
        resp['type'] = 'total'
        resp['msg'] = f'{len(clients)} Active Users'
        x.client.send(json_stringify(resp))

    # validate the user information here 
    print(f'New Client Connected! Total Connection: {len(clients)}')
    
    while True:
    
        msg = client.receive()

        if msg is None:
            break
        
        data = json_parse(msg)
        if data:
            if data['type'] == 'all':
                resp['type'] = 'all'
                resp['date'] = date_time()
                resp['user'] = user.name
                resp['msg'] = data['msg']
                for x in clients:
                    x.client.send(json_stringify(resp))

        

    clients.remove(user)

    for x in clients:
        list_user = []
        for y in clients:
            list_user.append(y.name)
            
        resp['list'] = list_user
        resp['type'] = 'total'
        resp['msg'] = f'{len(clients)} Active Users'
        x.client.send(json_stringify(resp))

    print(f'connection closed: Total live connection Left: {len(clients)}')