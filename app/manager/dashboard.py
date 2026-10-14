from app.util.auth import Auth
from app.lib.sql import sql
from app.store.user_store import UserStore

def dash_data(req, res):
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
            msg['msg'] = 'You are not authorized!'

            raise ValueError('You are not authorized!')
        
        q = req.query.get('q')

        if not q:
            raise ValueError('Invalid Query')

        uid = auth.ses.get('uid')
        con = sql()

        if q == 'profile':
            # load profile information
            # profile information and access
            ustore = UserStore(con)
            udata = ustore.list_user(uid)
            if udata:
                x = udata[0]
                msg['data'] = {
                    'Name': x['name'],
                    'Username': x['username'],
                    'Birth': x['dob'],
                    'Date Registered': x['date']
                }
                
                msg['ok'] = True
        elif q == 'total_register':
            pass

    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)