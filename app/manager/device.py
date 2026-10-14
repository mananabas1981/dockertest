from app.util.auth import Auth

# tommorrow project verify if the device is logged in or not

def verify(req, res):
  auth = None
  
  msg = {
    "ok": 0,
    "msg": ""  
  }

  try:
    auth = Auth(req)

    if auth.status == -1:
      msg['ok'] = 2
      msg["msg"] = "Not Logged In!"      
    elif auth.status == 1:
      msg["ok"] = 1
      msg["msg"] = "Logged In!"
    else:
      msg['ok'] == 0
      msg["msg"] = "Not Logged In!" 



         
  except Exception as er:
    print(er)
  finally:
    pass

  return msg

def sign_out(req, res):
  auth = None
  msg = {
    "ok": 0,
    "msg": ""  
  }

  try:

    auth = Auth(req)
    auth.ses.destroy()
    
    msg["ok"] = 1
    msg["msg"] = "Signed Out!"
    
  except Exception as er:
    print(er)
  
  if auth:
    return auth.send(msg)