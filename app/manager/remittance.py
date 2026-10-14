from app.util.auth import Auth
from app.lib.sql import sql
from app.model.remittance_model import RemittanceDownloadModel
from app.store.remittance_store import RemittanceStore
from app.model.remittance.remittance_file import download_remittance




def gen_remittance(req, res):
  con, auth, msg = None, None, { "ok": False, "msg": "Invalid Requests!", "data": None }
  try:
    auth = Auth(req)
    if not auth.isAuth:
      msg["msg"] = "You Are not Autoraised"
      return auth.send(msg)
    
    payload = auth.data
    
    print(payload)

    msg["msg"] = "Transaction Completed!"
    msg["ok"]  = True
    
  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  return auth.send(msg) if auth else None

# below function are not used

def download(req, res):
  con, auth, msg = None, None, {'ok': False, 'msg': '', 'data': None, 'file_name': '' }
  try:
    auth = Auth(req)
    is_auth, payload = auth.isAuth, auth.data
    if not is_auth:
      msg['msg'] = 'You are not authorized!'
      raise ValueError('You are not authorized!')

    if not 'job_status' in payload:
      msg['msg'] = 'Please Specify Job Status like; Job Order, Contract Of Service, Regular(Permanent, Temporary, etc...)'
      raise ValueError('job_status is required!')

    con = sql()

    rd = RemittanceDownloadModel(con, job_status = payload['job_status'])

    msg = rd.output()
    
  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)

def get_info(req, res):

  con, auth, msg = None, None, { 'ok': False, 'msg': None, 'data': None }

  try:
    
    auth = Auth(req)
    is_auth, payload = auth.isAuth, auth.data

    if not is_auth:
      msg['msg'] = 'You are not authorized!'
      raise ValueError('You are not authorized!')

    if not 'id' in payload: raise ValueError('id is required!')

    con = sql()
    rem_store = RemittanceStore(con)

    data = rem_store.lists( ids = payload['id'])

    if data:
      msg['data'] = data[0]

    msg['msg'] = 'Transaction Completed!'
    msg['ok'] = True

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  return auth.send(msg) if auth else None

def base_gen(req, res):
  con, auth, msg = None, None, {'ok': False, 'msg': ''}

  try:
    auth = Auth(req)
    is_auth, payload = auth.isAuth, auth.data

    if not is_auth:
      msg['msg'] = 'You are not authorized!'
      raise ValueError('You are not authorized!')

    if not 'id' in payload: raise ValueError('id is required!')

    con = sql()

    rem_store = RemittanceStore(con = con, uid = auth.ses.get('uid'))

    rem_store.generate_model(ids = payload['id'])

    con.go() # final commit

    msg['msg'] = 'Transaction Completed!'
    msg['ok'] = True

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  return auth.send(msg) if auth else None

def base_download(req, res):
  con, auth, msg = None, None, { 'ok': False, 'msg': '', 'data': '', 'filename': ''}

  try:
    auth = Auth(req)
    is_auth, payload = auth.isAuth, auth.data

    if not 'id' in payload: raise ValueError('id is required!')
    ids = payload['id']

    if not ids.strip(): raise ValueError('id must have a value')

    con = sql()

    dwn = download_remittance(con, ids)

    msg['ok'] = True
    msg['msg'] = 'Transaction Completed!'
    msg['data'] = dwn['data']
    msg['filename'] = dwn['name']
    

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  return auth.send(msg) if auth else None

def get_base(req, res):
  con, auth, msg = None, None, {'ok': False, 'msg': '', 'data': None}
  
  try:
    auth = Auth(req)
    
    is_auth, payload = auth.isAuth, auth.data

    if not is_auth: 
      msg['msg'] = 'You are not authorized!'
      raise ValueError('You are not authorized!')

    con = sql()

    rem_store = RemittanceStore(con)
    
    data = rem_store.lists()

    msg['msg'] = 'Transaction Completed!'
    msg['ok'] = True
    msg['data'] = data

  except Exception as er:
    print(er)
  finally: 
    if con: con.close()

  if auth: return auth.send(msg)

def create_base(req, res):
  con, auth, msg = None, None, { 'ok': False, 'msg': '' }

  try:
    auth = Auth(req)
    is_auth, payload = auth.isAuth, auth.data

    if not is_auth:
      msg['msg'] = 'You are not authorized!'
      raise ValueError('You are not authorized to create base remittance')

    if not 'code' in payload: raise ValueError('code is required!')
    if not 'name' in payload: raise ValueError('name is required!')
    if not 'from' in payload: raise ValueError('from is required')
    if not 'to' in payload: raise ValueError('to is required!')
    if not 'refid' in payload: raise ValueError('refid is required!')

    code, name, from_, to_, refids = payload['code'], payload['name'], payload['from'], payload['to'], payload['refid']

    if not refids: 
      msg['msg'] = 'Please select atleast one Payroll'
      raise ValueError('Please select atlease one Payroll')

    if not name.strip():
      msg['msg'] = 'Please input valid name'
      raise ValueError('Please Input valid name')

    if not from_.strip():
      msg['msg'] = 'Please input valid range date'
      raise ValueError('Please input valid range date')

    if not to_.strip():
      msg['msg'] = 'Please input valid range date'
      raise ValueError('Please input valid range date')

    con = sql()
    rem_store = RemittanceStore(con, uid = auth.ses.get('uid'))

    rem_store.create_base(code = code, name = name, from_ = from_, to_ = to_, refids = refids)
    con.go()
    msg['msg'] = 'Successfully created!'
    msg['ok'] = True
  except Exception as er:
    print(er)

  finally: 
    if con: con.close()

  if auth: return auth.send(msg)