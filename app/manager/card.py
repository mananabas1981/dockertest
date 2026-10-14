from app.lib.sql import sql
from app.store.card_store import CardStore
from app.util.auth import Auth

def load(req, res):
  auth, con, msg = None, None, {"ok": False, "msg": "", "data": ""}
  try:
    auth = Auth(req = req)
    payload, is_auth = auth.data, auth.isAuth
    if not is_auth: raise ValueError("You are not authorized!")

    if not "emp_id" in payload: raise ValueError("emp_id is required!")
    if not "code" in payload: raise ValueError("code is require!")

    emp_id, code = payload["emp_id"], payload["code"]
    con = sql()
    card_store = CardStore(con)
    res = card_store.get(code, emp_id)
    if res:
      msg["msg"] = "Transaction Completed!"
      msg["ok"] = True
      msg["data"] = res[0]
  
  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)

def update(req, res):
  auth, con, msg = (None, None, {"ok": False, "msg": ""})
  try:
    auth = Auth(req = req)
    payload, is_auth = (auth.data, auth.isAuth)
    if not is_auth:
      raise ValueError("Not Authorized!")
    
    if not "emp_id" in payload: raise ValueError("emp_id is required!")
    if not "code" in payload: raise ValueError("code is required!")
    if not "value" in payload: raise ValueError("value is required!")

    emp_id, code, value = payload["emp_id"], payload["code"], payload["value"]
    con = sql()
    
    card_store = CardStore(con)
    card_store.save(code, emp_id, value, auth.ses.get("uid"))
    con.go()

    msg["msg"] = "Transaction Completed!"
    msg["ok"] = True

  except Exception as er:
    print(er)
  finally: 
    if con: con.close()

  if auth: return auth.send(msg)

  