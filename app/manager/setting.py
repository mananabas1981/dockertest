from app.util.auth import Auth
from re import match
from app.lib.sql import sql
from app.store.global_store import create_history

from app.model.user_model import AccessModel

def save_setup(req, res):
  auth = Auth(req)
  if not auth.isAuth:
    return
  
  data = auth.data
  msg = {'ok': 0, 'msg': 'Invalid Request'}
  con = None
  try:
    if not 'name' in data:
      raise ValueError('[!] name is not found')
    
    if not 'addr' in data:
      raise ValueError('[!] addr is not found')
    
    if not 'tin' in data:
      raise ValueError('[!] tin is not found')
    
    name = data['name']
    addr = data['addr']
    tin = data['tin']

    # Validation action

    reg_info = r'^[a-zA-Z\-\_ 0-9\,]+$'
    
    if not match(reg_info, name):
      raise ValueError('[!] name regex not accepted')
    
    if not match(reg_info, addr):
      raise ValueError('[!] addr not accepted')
    
    if not match(r'^[0-9]+$', tin):
      raise ValueError('[!] tin not accepted')
    
    # Database Action
    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess( auth.ses.get('uid'), ['ss-4'] ):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    con.commit('delete from sys_info')
    con.commit('insert into sys_info(name, addr, tin) values(?, ?, ?)', (name, addr, tin, ))
    con.go()
    
    # Success Message
    msg['ok'] = 1
    msg['msg'] = 'Successfully submitted'
  except Exception as er:
    print(er)
    msg['ok'] = 0
    msg['msg'] = 'Something went wrong!'
  finally:
    if con:
      con.close()

  return auth.send(msg)

def bank_save(req, res):

  auth = Auth(req)
  
  msg = {
    'ok': 0,
    'msg': ''  
  }
  
  con = None

  try:

    # check authorization
    if not auth.isAuth:
      raise ValueError('not logged in')
    
    # Data validation
    data = auth.data
    if not 'code' in data:
      raise ValueError('code is not defined')
    
    if not 'name' in data:
      raise ValueError('name is not defined')
    
    if not 'bankno' in data:
      raise ValueError('bankno is not defined')

    code = data['code']
    name = data['name']
    bankno = data['bankno']

    if not match(r'^[A-Z0-9\_\-]+$', code):
      raise ValueError('regex code is not valid')
    
    if not match(r'^[0-9a-zA-Z\ \-\_]+$', name):
      raise ValueError('regex name is not valid')
    
    if not match(r'^[0-9]+$', bankno):
      raise ValueError('bankno is not valid')
    
    # Working with database
    con = sql()

    ac = AccessModel(con)

    if not ac.hasAccess(auth.ses.get('uid'), ['ss-5']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())


    banks = con.getone('select code from com_bank where code = ?', (code, ))
    
    if banks:
      # update
      msg['msg'] = 'Bank code is already added'
      raise ValueError('Bank code is already added')
    else:
      con.commit('insert into com_bank(code, name, bankno) values(?, ?, ?)', (code, name, bankno, ))
      msg['msg'] = 'Successfully added'
    con.go()
    msg['ok'] = 1
    # success message
  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()
  
  return auth.send(msg)
  

def get_info(req, res):
  msg = {'ok': 0, 'data': {'name': '', 'addr': '', 'tin': ''}}
  auth = None
  con = None
  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError()
    
    # Database Action
    con = sql()
    data = con.getone('select name, addr, tin from sys_info')
    if data:
      msg['data']['name'] = data[0]
      msg['data']['addr'] = data[1]
      msg['data']['tin'] = data[2]
    
  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  return auth.send(msg)

def bank_list(req, res):
  con = None
  
  msg = {'ok': 0, 'msg': '', 'data': ()}
  auth = None

  try:
    auth = Auth(req)
    if not auth.isAuth:
      msg['msg'] = 'not logged in'
      raise ValueError('not logged in')
    con = sql()
    banks = con.get('select code, name, bankno from com_bank')
    con.close()
    con = None
    msg['ok'] = 1
    msg['data'] = banks

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)

def bank_remove(req, res):
  con = None
  auth = None
  msg = {'ok': 0, 'msg': ''}
  try:
    auth = Auth(req)

    if not auth.isAuth:
      msg['msg'] = 'not logged in!'
      raise ValueError('not logged in')
    data = auth.data
    if not 'code' in data:
      msg['msg'] = 'Something went wrong!'
      raise ValueError('code is not defined')
    
    code = data['code']
    if not match(r'^[A-Z0-9\_\-]+$', code):
      msg['msg'] = 'code is not valid!'
      raise ValueError('code regex invalid')
    
    con = sql()

    ac = AccessModel(con)

    if not ac.hasAccess(auth.ses.get('uid'), ['ss-5']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())


    bank = con.getone("select code, name, bankno from com_bank where code = ?", (
      code,
    ))
    if bank:
      create_history(con, auth.ses.get("uid"), "com_bank", bank, "d")
      con.commit('delete from com_bank where code = ?', (code, ))
      con.go()
      msg['ok'] = 1
      msg['msg'] = 'remove successfully'
    else:
      msg["msg"] = "bank is not found!"
      
  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()
  
  if auth:
    return auth.send(msg)
