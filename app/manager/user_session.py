from app.util.auth import Auth
from app.store.user_session import UserSessionStoreService, UserSessionStore
from app.lib.sql import sql 
from app.util.date import date_time
from app.util.json import json_stringify
from app.model.user_model import AccessModel

def session_list(req, res):
    con = None
    auth = None
    msg = {
        'ok': False,
        'msg': None,
        'data': None
    }
   
    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError('You are not authorized!')
        
        con = sql()

        ac = AccessModel(con)
        
        if not ac.hasAccess(auth.ses.get('uid'), ['us-3']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())

        user_ses = UserSessionStoreService(con)

        msg['data'] = user_ses.listSession()
        msg['msg'] = 'Completed!'
        msg['ok'] = True

    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)
    
def session_approve(req, res):
    con = None
    auth = None
    msg = {
        'ok': False,
        'msg': None,
    }

    try:
        auth = Auth(req)
        
        if not auth.isAuth:
            raise ValueError('You are not authorized!')
        
        data = auth.data

        if not 'key' in data:
            raise ValueError('key is required!')
        
        con = sql()

        ac = AccessModel(con)

        if not (int(auth.ses.get('role')) == 1):
            if not ac.hasAccess(auth.ses.get('uid'), ['us-2']):
                msg['msg'] = ac.errorAccess()
                raise ValueError(ac.errorAccess())


        key = data['key'] 
        user_auth = Auth(req, key)
        us = UserSessionStoreService(con)
        us.approve(UserSessionStore(status = 1, key = key, remark = json_stringify({
            'date': date_time()
        })))
        con.go()
        user_auth.ses.set('status', 1)
        

        msg['ok'] = True
        msg['msg'] = 'Sign in Approved!'


    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)
    