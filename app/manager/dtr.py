from app.lib.sql import sql_dtr, sql
from app.util.auth import Auth
from app.store.dtr_store import DtrStore
from app.model.user_model import AccessModel
from app.store.department_store import Department
from app.store.client_store import ClientStore
import json



def dtr_regular_reports(req, res):
  con, auth, msg = None, None, { "ok": False, "msg": "", "data": "" }

  try:
    auth = Auth(req)

    if not auth.isAuth:
      msg["msg"] = "You are not authorized!"
      raise ValueError("You are not authorized!")

    data = auth.data
    if not "from" in data or not "to" in data:
      raise ValueError("error payload")

    rcon = sql()
    ac = AccessModel(rcon)
    if not ac.hasAccess(auth.ses.get('uid'), ['hs-r']):
      msg['msg'] = ac.errorAccess()
      rcon.close()
      del rcon
      raise ValueError(ac.errorAccess())
    
    cstore = ClientStore(con = rcon)

    dstore = Department(con = rcon)
    dinfos = dstore.lists()
    

    storage = [

    ]

    # select all employee

    for dinfo in dinfos:
      id_, code_, name_ = dinfo

      
      emp_item = []

      emp_infos = cstore._getClients(dept_id = id_, is_active = 'y', limit = None, emp_status = "r")
      for emp_info in emp_infos:
        emp_item.append({
          "id": emp_info["id"],
          "name1": f''' {emp_info["lname"]}, {emp_info["fname"]} {emp_info["mname"]} {emp_info["ename"]}'''.upper(),
          "pos_title": emp_info["pos_title"],
          "pass": False
        })

      
      storage.append({
        "dept": (id_, code_, name_),
        "item": emp_item
      })

    # print(storage)

    rcon.close() # early close to avoid loading
    del rcon



    con = sql_dtr()

    # retrieve the department

    from_t = data["from"]
    to_t   = data["to"]

    # retrieve all the 
    items = con.get('select emp_id, header from dtr where from_t >= ? and to_t <= ?', (
      from_t,
      to_t,
    ))

    con.close()
    # collecting 
    

    for item in items:
      
      header = json.loads(item[1])
      emp_id = item[0]
      dept_id = header["dept"]["dept_id"]

      for s in storage:
        s_dept_id, s_code, s_name = s["dept"] 
        
        s_emp_items = s["item"]
        for s_emp_item in s_emp_items:
          s_emp_id = s_emp_item["id"]
          if str(s_emp_id) == str(emp_id):
            s_emp_item["pass"] = True


    final_storage = []

    for item in storage:
      if len(item["item"]) > 0:
        final_storage.append(item)




    


    htm = []

    htm.append(f"""
      <center><h4> {from_t} to {to_t} </h4></center>
      <center><h5>CHECK LIST OF DTR (REGULAR EMPLOYEE)</h5></center>
      <hr />
    """)

    for item in final_storage:
      dept_id, code, name = item["dept"] 

      htm.append(f"""
      <div style="text-decoration: underline; font-weight: bold;">{ code }</div>
      """)

      ditems = item["item"]

      for ditem in ditems:
        if ditem["pass"]:
          htm.append(f"""
            <div style="margin-left: 50px; color: black;">{ditem["name1"]} - {ditem["pos_title"]}</div>
          """)
        else:
          htm.append(f"""
            <div style="margin-left: 50px; color: red;">{ditem["name1"]} - {ditem["pos_title"]}</div>
          """)
      
    

    
    msg["data"] = "".join(htm) 
    msg["ok"]   = True
    
  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  return auth.send(msg) if auth else ""



def create_code(req, res):

  con, auth, msg = None, None, {'ok': False, 'msg': '', 'code': None}

  try:
    auth = Auth(req)
    if not auth.isAuth:
      msg['msg'] = 'You are not authorized!'
      raise ValueError('You are not authorized!')


    rcon = sql()
    ac = AccessModel(rcon)
    if not ac.hasAccess(auth.ses.get('uid'), ['hs-5']):
      msg['msg'] = ac.errorAccess()
      rcon.close()
      del rcon
      raise ValueError(ac.errorAccess())
    rcon.close() # early close to avoid loading
    del rcon

    payload = auth.data

    if not 'data' in payload: raise ValueError('data is required')
    if not 'header' in payload: raise ValueError('header is required!')
    if not 'from' in payload: raise ValueError('from is required!')
    if not 'to' in payload: raise ValueError('to is required!')
    if not 'emp_id' in payload: raise ValueError('emp_id is required!')
    if not 'hr_id' in payload: raise ValueError('hr_id is required!')

    data, header, from_, to_, emp_id, hr_id = payload['data'], payload['header'], payload['from'], payload['to'], payload['emp_id'], payload['hr_id'] 

    con = sql_dtr()

    ds = DtrStore(con, auth.ses.get('uid'))
    if not ds.exists(emp_id, from_, to_):
      code = ds.insert(data = data, header = header, from_ = from_, to_ = to_, emp_id = emp_id, hr_id = hr_id)
      con.go() # final commit
      msg['msg'] = 'Transaction completed!'
      msg['ok'] = True
      msg['code'] = code
    else:
      msg['msg'] = 'RANGE DATE ALREADY ADDED!'
      msg['ok'] = False

  except Exception as er:
    print(er)
  finally:
    if con: con.close()


  if auth: return auth.send(msg)

def update_leave_credit(req, res):
  con, auth, msg = None, None, { 'ok': False, 'msg': '' }

  try:
    
    auth = Auth(req)
    
    if not auth.isAuth: 
      msg['msg'] = 'You are not authorized!'
      raise ValueError('You are not authorized!')

    rcon = sql()
    ac = AccessModel(rcon)
    if not ac.hasAccess(auth.ses.get('uid'), ['hs-5']):
      msg['msg'] = ac.errorAccess()
      rcon.close()
      del rcon
      raise ValueError(ac.errorAccess())
    rcon.close() # early close to avoid loading
    del rcon

    payload = auth.data

    if not 'code' in payload: raise ValueError('code is required!')
    if not 'absent' in payload: raise ValueError('absent is required!')
    if not 'late' in payload: raise ValueError('late is required!')
    if not 'ut' in payload: raise ValueError('ut is required!')
    if not 'total_leave' in payload: raise ValueError('total_leave is required!')
    
    con = sql_dtr()

    ds = DtrStore(con, auth.ses.get('uid'))

    if ds.is_approve(payload['code']):
      msg['msg'] = 'Already Approve'
      raise ValueError('Already approved')

    res = ds.getCode(code = payload['code'])
    if not res:
      msg['msg'] = 'Data not found!'
      raise ValueError('Data not found!')

    hr_id = res[0]['hr_id']
    from_t = res[0]['from_t']

    tard_info = {
      'absent': res[0]['total_absent'],
      'late':  res[0]['total_late'],
      'undertime': res[0]['total_undertime']
    }

    ds.update(code = payload['code'], 
      absent = payload['absent'], 
      late = payload['late'],
      undertime = payload['ut'], 
      total_leave = payload['total_leave']
    )
    
    data = ds.update_hrms(code = payload['code'], emp_id = hr_id, credit_minus = payload['total_leave'], from_t = from_t, tard = tard_info)
    
    if data['ok']:
      con.go()

    msg['msg'] = data['msg']
    msg['ok'] = data['ok']

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)


def list_code(req, res):
  con, auth, msg = None, None, { 'ok': False, 'msg': '', 'data': [ ] }

  try:
    auth = Auth(req)
    if not auth.isAuth: 
      msg['msg'] = 'You are not authorized!'
      raise ValueError('You are not authorized!')
    

    con = sql_dtr()
    ds = DtrStore(con)
    data = ds.getCode()

    msg['data'] = data
    msg['ok']  = True
    msg['msg'] = 'Transaction Completed!'


  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)