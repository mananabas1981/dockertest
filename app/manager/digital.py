from app.util.auth import Auth
from app.lib.sql import sql_signature, sql
from app.store.digital_store import DigitalStore
from app.model.user_model import AccessModel


def signature_save(req, res):
  auth, con, msg = (None, None, {'ok': False, 'msg': ''})
  con2 = None
  try:
    auth = Auth(req)
    is_auth, payload = auth.isAuth, auth.data
    if not is_auth: raise ValueError('You are not authorized!')

    if not 'id' in payload: raise ValueError('id is required!')

    if not 'name' in payload:
      raise ValueError('name is required!')

    if not 'pos_title' in payload:
      raise ValueError('pos_title is required!')

    if not 'data' in payload:
      raise ValueError('data is required!')

    con2 = sql()
    ac = AccessModel(con2)
    if not ac.hasAccess(auth.ses.get('uid'), ['di-0']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())
    con2.close()

    name, pos_title, data = payload['name'], payload['pos_title'], payload['data']

    con = sql_signature()
    ds = DigitalStore(con)

    if not payload['data']: raise ValueError('image data is required!')

    if not payload['id']: 
      ds.save(name, pos_title, data)
    else:
      ds.update(payload['id'], name, pos_title, data)

    con.go()

    msg['ok'] = True
    msg['msg'] = 'Transaction Completed!'

  except Exception as er:
    print(er)
  finally:
    if con: con.close()
    if con2: con2.close()

  if auth: return auth.send(msg)

def signature_list(req, res):
  auth, con, msg = None, None, {'ok': False, 'msg': '', 'data': None}

  try:
    auth = Auth(req)
    is_auth, _ = auth.isAuth, auth.data

    if not is_auth: raise ValueError('You are not authorized')

    con = sql_signature()
    ds = DigitalStore(con)
    data = ds.get()

    msg['data'] = data
    msg['ok'] = True
    msg['msg'] = 'Transaction Completed!'

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)