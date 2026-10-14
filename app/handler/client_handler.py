from app.lib.bottle import Bottle, response as res, request as req
from app.lib.sql import sql

from app.model.client_model import ClientModel, ClientEntity
from app.util.auth import Auth
from app.model.user_model import AccessModel

client_handler = Bottle()

@client_handler.route("/save", method = ["POST"])
def save():


  con = None
  clientModel = ClientModel()
  is_okay = False
  try:
    auth_obj = Auth(req)
    auth = auth_obj.getAuthModel()
    if not auth:
      return auth_obj.send({
        "ok": 2,
        "msg": "you are not logged in"  
      })
    
    data = auth.data
    
    # client Entity
    client = ClientEntity()
    client.id = data["id"]
    client.uid = auth.uid
    client.pref_name = data["pref_name"].strip()
    client.fname = data["fname"].strip()
    client.mname = data["mname"].strip()
    client.lname = data["lname"].strip()
    client.ename = data["ename"].strip()
    client.suf_name = data["suf_name"].strip()
    client.gender = data["gender"].strip()
    client.dob = data["dob"].strip()
    client.addr = data["addr"].strip()
    client.hr_id = data["hr_id"].strip()
    
    is_valid, msg = clientModel.isValid(client = client)

    if not is_valid:
      return auth_obj.send({
        "ok": 0,
        "msg": f"{msg}"  
      })
    con = sql() 

    ac = AccessModel(con)

  
    clientModel._setConnection(con)
    if not client.id:
      if ac.hasAccess(auth_obj.ses.get('uid'), ['em-0']):
        is_okay = clientModel.addClient(client = client)
    else:
      if ac.hasAccess(auth_obj.ses.get('uid'), ['em-1']):
        is_okay = clientModel.updateClient(client = client)
    if is_okay:
      con.go()

  except Exception as er:
    if con:
      con.close()
    print(er)
  finally:
    if con:
      con.close()
  if is_okay:
    return auth_obj.send({
      "ok": 1,
      "msg": "Transaction Completed!"  
    })
  else:
    return auth_obj.send({
      "ok": 0,
      "msg": "Transaction Failed!"  
    })

@client_handler.route("/list", method = ["POST"])
def client_list():
  con = None
  auth_obj = None
  r = {
    "ok": 0,
    "data": {
      "total": 0.0,
      "data": []
    },
    'msg': None
  }
  data = []
  result = []
  try:
    auth_obj = Auth(req)
    auth = auth_obj.getAuthModel()
    
    if not auth.auth:
      raise ValueError(0)
  
    data = auth.data
    if not "search" in data:
      raise ValueError("no search")

    search = data["search"].replace(" ", "").replace(",", "")

    clientModel = ClientModel()
    # if not clientModel.is_search_valid(search = search):
    #   raise ValueError("invalid search")
    
    # dept_id = data["dept_id"] if "dept_id" in data else ""
    dept_id = ""
    if "dept_id" in data:
      dept_id = data["dept_id"]

    emp_status = ""
    if "emp_status" in data:
      emp_status = data["emp_status"]
    
    active = data.get('active')

    if active:
      if not active in ('y', 'n'): # this insure that that input are valid and avoid bad sql injection
        r['ok'] = 0
        r['msg'] = 'Something went wrong!'
        raise ValueError('Error active value')

    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth_obj.ses.get('uid'), ['em-3']):
      r['ok'] = 0
      r['msg'] = ac.errorAccess()
      raise ValueError('you dont have access in search and viewing of the employee')

    clientModel._setConnection(con)
    r["data"]["total"] = clientModel._getClientsCount(search = search, dept_id = dept_id, emp_status = emp_status, is_active = active)

    result = clientModel.getClients(search = search, dept_id = dept_id, emp_status = emp_status, active = active)

    r["data"]["data"] = result

    r["ok"] = 1
  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()
      del con
  # if (r["ok"] == 1):
  #   data = []
  #   for x in result:
  #     data.append({
  #       "pref_name": x[0],
  #       "fname":     x[1],
  #       "mname":     x[2],
  #       "lname":     x[3],
  #       "ename":     x[4],
  #       "suf_name":  x[5],
  #       "status":    x[6],
  #       "address":   x[7],
  #       "gender":    x[8],
  #       "id":        x[9],
  #       "dob":       x[10],
  #       "hr_id":     x[11]
  #     })
  #   r["data"]["data"] = data
  return auth_obj.send(r)