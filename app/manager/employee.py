from app.model.dept_model import DeptModel
from app.model.position_model import PositionModel
from app.model.rate_model import RateModel
from app.store.active_status_store import ActiveStatus
from app.util.auth import Auth
from re import match
from app.util.date import date_time
from app.lib.sql import sql 
from app.store.client_store import RateStore, PositionStore, DeptInfoStore, ClientStore
from app.store.payroll_store import PayrollStore
from app.model.user_model import AccessModel


def active_change(req, res):
  con, auth, msg = (None, None, {'ok': False, 'msg': ''})

  try:
    auth = Auth(req)

    payload, is_auth, uid = ( auth.data, auth.isAuth, auth.ses.get('uid') )

    if not is_auth: raise ValueError('Not Authorized!')

    if not 'remark' in payload: raise ValueError('remark is required')
    if not 'from' in payload: raise ValueError('from is required!')
    if not 'emp_id' in payload: raise ValueError('emp_id is required')

    remark, frm, emp_id = (payload['remark'], payload['from'], payload['emp_id'])

    con = sql()

    ac = ActiveStatus(con = con)
    ac.insert(emp_id, frm, remark, uid)
    con.go()

    msg['ok']  = True
    msg['msg'] = 'Transaction Completed!'

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)


def save_rate(req, res):
  con = None
  auth = None
  msg = {
    "ok": 0,
    "msg": ""  
  }
  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("Not Authorized!")
    data = auth.data
    if not data:
      raise ValueError("Invalid Requests")
    
    if not "rate" in data:
      raise ValueError("rate required")
    
    if not "rate_type" in data:
      raise ValueError("rate_type required")
    
    if not "emp_id" in data:
      raise ValueError("emp_id is required")
    
    if not match(r"^[0-9\.]+$", str(data["rate"])):
      raise ValueError("rate invalid")
    

    rate = data["rate"]
    rate_type = data["rate_type"]
    emp_id = data["emp_id"]

    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['em-4']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    # rate_store = RateStore(con)
    # last_rate = rate_store.get_last_rate(emp_id)

    # if last_rate:
    #   rate2 = last_rate[1]
    #   rate_type2 = last_rate[2]
    #   if not (rate2 == rate and rate_type2 == rate_type):
    #     rate_store.create_rate(emp_id, rate, rate_type, date_time())
    # else:
    #   # if there are no last rate
    #   rate_store.create_rate(emp_id, rate, rate_type, date_time())
    rate_model = RateModel(con, emp_id)
    rate_model.create_rate(rate, rate_type)

    con.go()
    msg["ok"] = 1
    msg["msg"] = "Transaction Completed"
  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)

def employee_remove(req, res):
  
  con = None
  auth = None
  msg = {
    "ok": 0,
    "msg": ""  
  }

  try:

    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("You are not authorized!")    
    data = auth.data

    if not data:
      raise ValueError("data is not available")
    
    ids = data["id"]
    if not match(r"^[0-9]+$", str(ids)):
      raise ValueError("id is invalid")

    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['em-2']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())
    
    client_store = ClientStore()
    client_store._setConnection(con)
    client_store.remove_employee(ids)
    con.go()  
    msg["ok"] = 1
    msg["msg"] = "Transaction Completed!"

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)

def get_rate(req, res):
  con = None
  auth = None
  msg = {
    "ok": 0,
    "msg": "",
    "data": []  
  }

  try:

    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("Not Authorized!")
    data = auth.data
    if not data:
      raise ValueError("Invalid Requests")
    
    if not "emp_id" in data:
      raise ValueError("Invalid id")
    
    if not match(r"^[0-9]+$", str(data["emp_id"])):
      raise ValueError("emp_id is invalid")
    
    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['em-4']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    rate_store = RateStore(con)
    msg["ok"] = 1
    msg["msg"] = "Transaction Completed!"
    msg["data"] = rate_store.get_rate(data["emp_id"])

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)

def remove_rate(req, res):
  con = None
  auth = None
  msg = {
    "ok": 0,
    "msg": ""
  }  

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("You are not authorized!")
    data = auth.data
  
    if not data:
      raise ValueError("Data is invalid!")
    
    if not "date" in data:
      raise ValueError("date is required")
    
    if not "emp_id" in data:
      raise ValueError("emp_id is required")

    date = data["date"]
    emp_id = data["emp_id"]

    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['em-4']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    rate_store = RateStore(con)
    rate_store.remove_rate(emp_id, date, auth.ses.get("uid"))

    con.go()
    msg["ok"] = 1
    msg["msg"] = "Transaction Completed!"

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()
  if auth:
    return auth.send(msg)

def save_position(req, res):
  con = None
  auth = None
  msg = {
    "ok": 0,
    "msg": ""  
  }

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("Not Authorized!")
    data = auth.data

    if not data:
      raise ValueError("Invalid Requests")
    
    if not "title" in data:
      raise ValueError("title is not valid")
    
    if not "emp_id" in data:
      raise ValueError("emp_id is not valid")

    if not match(r"^[0-9a-zA-Z\-\(\)\_\#\$\& ]+$", data["title"]):
      raise ValueError("title is not valid")
    
    if not "status" in data:
      raise ValueError("status is not valid")
    
    if not match(r"^[rcj]$", data["status"]):
      raise ValueError("status value is invalid")
    
    status = data["status"]

    emp_id = data["emp_id"]  
    pos_title = data["title"]
    
    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['em-5']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())
    print(pos_title)
    print(emp_id)
    uid = auth.ses.get("uid")
    # pos_store = PositionStore(con)
    # last_pos = pos_store.get_last_position(emp_id)
    
    # if last_pos:
    #   last_title = last_pos[0]
    #   if not (last_title == pos_title):
    #     pos_store.create_position(emp_id, pos_title, status, date_time(), auth.ses.get("uid"))  
    # else:
    #   pos_store.create_position(emp_id, pos_title, status, date_time(), auth.ses.get("uid"))

    pos_model = PositionModel(con, uid)
    pos_model.create_position(emp_id, pos_title, status)


    con.go()
    msg["msg"] = "Transaction Completed!"
    msg["ok"] = 1

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)

def remove_position(req, res):
  con = None
  auth = None
  msg = {
    "ok": 0,
    "msg": ""
  }

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("You are not authorized!")
    data = auth.data
    
    if not data:
      raise ValueError("data is required!")
    
    if not "emp_id" in data:
      raise ValueError("emp_id is required!")
    
    if not "date" in data:
      raise ValueError("date is required!")
    
    emp_id = data["emp_id"]
    date = data["date"]

    con = sql()
    
    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['em-5']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    pos_store = PositionStore(con)
    pos_store.remove_position(emp_id, date, auth.ses.get("uid"))
    con.go()
    msg["msg"] = "Transactiton Completed!"
    msg["ok"] = 1

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)

def get_position(req, res):
  con = None
  auth = None
  msg = {
    "ok": 0,
    "msg": "",
    "data": []  
  }

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("You are not authorized")

    data = auth.data

    if not data:
      raise ValueError("Invalid Requests")
    
    if not "emp_id" in data:
      raise ValueError("Invalid emp_id")
    
    if not match(r"^[0-9]+$", str(data["emp_id"])):
      raise ValueError("emp_id regex invalid")
    
    emp_id = data["emp_id"]
    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['em-5']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    pos_store = PositionStore(con)
    res_data = pos_store.get_position(emp_id)
    msg["ok"] = 1
    msg["msg"] = "Transaction Completed!"
    msg["data"] = res_data

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)

def dept_save(req, res):
  con = None
  auth = None
  msg = {
    "ok": 0,
    "msg": ""  
  }

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("Not Authorized!")

    data = auth.data
    if not data:
      raise ValueError("invalid data")
    
    if not "emp_id" in data:
      raise ValueError("emp_id invalid")
    
    if not "dept_id" in data:
      raise ValueError("dept_id invalid")
    
    if not match(r"^[0-9]+$", str(data["emp_id"])):
      raise ValueError("invalid emp_id")
    
    if not match(r"^[0-9]+$", str(data["dept_id"])):
      raise ValueError("Invalid dept_id")
    
    emp_id = data["emp_id"]
    dept_id = data["dept_id"]

    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['em-6']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    # dept_info = DeptInfoStore(con)

    # last_dept = dept_info.get_last_dept(emp_id)

    # if last_dept:
    #   last_dept_id = str(last_dept[1])
    #   if not (str(dept_id) == last_dept_id):
    #     dept_info.create_dept(emp_id, dept_id, date_time(), auth.ses.get("uid"))  
    # else:
    #   dept_info.create_dept(emp_id, dept_id, date_time(), auth.ses.get("uid"))
    dept_model = DeptModel(con, auth.ses.get("uid"))
    dept_model.update_dept(emp_id, dept_id)
    
    con.go()
    msg["ok"] = 1
    msg["msg"] = "Transaction Completed!"

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)
  

def dept_list(req, res):
  con = None
  msg = {
    "ok": 0,
    "msg": "",
    "data": []  
  }
  auth = None

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("not Authorized!")
    data = auth.data
    if not data:
      raise ValueError("Invalid data")
    
    if not "emp_id" in data:
      raise ValueError("emp_id is required!")
    
    emp_id = data["emp_id"]
    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['em-6']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())


    dept = DeptInfoStore(con)
    dept_data = dept.get_dept(emp_id)

    msg["ok"] = 1
    msg["msg"] = "Transaction Completed!"
    msg["data"] = dept_data

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()
  
  if auth:
    return auth.send(msg)

def dept_remove(req, res):
  con = None
  auth = None
  msg = {
    "ok": 0,
    "msg": ""
  }

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("You are not authorized!")
    data = auth.data
    if not data:
      raise ValueError("data is not valid")
    
    if not "emp_id" in data:
      raise ValueError("emp_id is required")
    
    if not "date" in data:
      raise ValueError("date is required")
    
    if not "dept_id" in data:
      raise ValueError("dept_id is required")
    
    emp_id = data["emp_id"]
    date = data["date"]
    dept_id = data["dept_id"]
    
    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['em-6']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())


    dept = DeptInfoStore(con)
    dept.remove_dept(emp_id, dept_id, date, auth.ses.get("uid"))
    con.go()
    msg["msg"] = "Transaction Completed!"
    msg["ok"] = 1

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()
  
  if auth:
    return auth.send(msg)
  

def get_all_info(req, res):
  auth = None
  con = None
  msg = {
    'ok': 0,
    'msg': '',
    'data': {
      'emp_info': None,
      'dept_info': None,
      'pos_info': None,
      'rate_info': None,
      'last_ded': None
    }
  }

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError('Not Authorized!')
    data = auth.data

    if not 'emp_id' in data:
      raise ValueError('emp_id is required')

    if not "from" in data:
      raise ValueError("from is required")
    
    if not 'to' in data:
      raise ValueError('to is required')
  
    emp_id = data['emp_id']
    
    con = sql()


    cstore = ClientStore(con)
    msg["data"]["emp_info"] = cstore.info_by_id(emp_id)

    client_store = DeptInfoStore(con)

    dept = client_store.get_dept_dict(emp_id = emp_id, limit = 1)

    if len(dept) > 0:
      msg['data']['dept_info'] = dept[0]

    pos_store = PositionStore(con)
    pos_res = pos_store.get_position_dict(emp_id)
    if len(pos_res) > 0:
      msg['data']['pos_info'] = pos_res[0]

    rate_store = RateStore(con)
    rate_data = rate_store.get_rate_dict(emp_id, 1)

    if len(rate_data) > 0:
      msg['data']['rate_info'] = rate_data[0]

    # get the last innformation of the payroll
    
    pstore = PayrollStore(con)

    last_payslip = pstore.get_last_item(emp_id = emp_id, frm = data["from"], to = data["to"])

    if last_payslip:
      msg["data"]["last_ded"] = last_payslip[0]["last_deduction"]
    msg['ok']  = 1
    msg['msg'] = 'Transaction Completed!'

  except Exception as er:
    print(er)

  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)