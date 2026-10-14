from app.lib.sql import sql
from app.util.auth import Auth
from re import match
from app.store.department_store import Department
from app.model.user_model import AccessModel

def save(req, res):
  con = None
  auth = None
  
  msg = {
    "ok": 0,
    "msg": ""  
  }

  try:
    auth = Auth(req)
    data = auth.data

    if not auth.isAuth:
      raise ValueError()

    if not "id" in data:
      raise ValueError("id is required")

    if not "code" in data:
      raise ValueError("code is required")
    
    if not "title" in data:
      raise ValueError("title is required")
    
    valid_string = r"^[0-9a-zA-Z\-\_\(\)\#\. ]+$"

    if not match(valid_string, data["title"]):
      msg["msg"] = "Invalid title"
      raise ValueError("Invalid title")
    
    if not match(valid_string, data["code"]):
      msg["msg"] = "Invalid code"
      raise ValueError("Invalid Code")
    
    if not match(r"^[0-9]+$", data["id"]):
      msg["msg"] = "Invalid id"
      raise ValueError("Invalid Id")
    


    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess( auth.ses.get('uid'), ['ss-1'] ):
      msg['msg'] = ac.errorAccess()
      raise ValueError( ac.errorAccess() )

    dept = Department(con)
    dept.save(data["id"], data["code"], data["title"])
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
  
def lists(req, res):
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
      raise ValueError("not authorized!")
    con = sql()

    ac = AccessModel(con)

    if not ac.hasAccess( auth.ses.get('uid'), ['ss-f'] ):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    refid = req.query.get('refid') # query

    dept = Department(con)
    msg["data"] = dept.lists(refid = refid)
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
    data = auth.data
    if not auth.isAuth:
      raise ValueError("not authorized!")
    
    if not "id" in data:
      raise ValueError("id is invalid")
    
    ids = data["id"]

    if not match(r"^[0-9]+$", ids):
      raise ValueError("Invalid ids")

    con = sql()

    ac = AccessModel(con)

    if not ac.hasAccess( auth.ses.get('uid'), ['ss-1'] ):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    con.commit("delete from department where id = ?", (
      ids,  
    ))

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