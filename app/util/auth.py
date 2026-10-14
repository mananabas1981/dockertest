from app.util.session import session
from app.util.text import Text
from app.util.json import json_parse, json_stringify

class AuthModel:
  def __init__(this):
    this.auth = False
    this.data = None
    this.uid = None

class Auth:
  def __init__(this, req = None, token = None, def_key = "HZRIHcFraxLP-s0HJtHO7vYRvyYSVeFKTZU1OopNY5A="):

    this.default_key = def_key
    this.token = ""
    this.req = req

    if not token:  
      t = this.req.headers.get("Auth")
      if t:
        t = t.split("=")
        if len(t) >= 2:
          this.token = t[1]
    else:
      this.token = token
    
    this.ses = session(this.token, True)  
    this.isAuth = True if this.ses.get("uid") else False

    fkey = this.ses.get("fkey")
    this.txt = Text(def_key)
    if fkey:
      this.txt = Text(fkey)

    this.data = json_parse(this.txt.decrypt(this.req.body.read()))
    if this.isAuth:
      # second layer security for request data
      if this.data and "token" in this.data:
        this.isAuth = this.data["token"] == this.token
    
    this.status = this.ses.get('status')


    if this.status == -1 or this.status == 0:
      this.isAuth = False

    origin = this.req.headers.get("Origin", "")
    user_agent = this.req.headers.get("User-Agent", "")
    
    cur_device = f"{origin}{user_agent}"
    reg_device = this.ses.get("device")
    
    if not (cur_device == reg_device):
      this.isAuth = False
    # if status == -1 or status == 0:
    #   this.isAuth = False

    #print(this.token)
    #print(this.data["token"])    

  def getAuthModel(this):
    authModel = AuthModel()
    if this.isAuth:
      authModel.auth = True
      authModel.uid = this.ses.get('uid')
      authModel.data = this.data
    return authModel

  def get(this):
    if not this.isAuth:
      return {
        "auth": False,
        "data": None
      }
    return {
      "auth": True,
      "data": json_stringify(this.data),
      "uid": this.ses.get("uid")  
    }
  
  def json(this):
    if not this.isAuth:
      return {
        "auth": False,
        "data": None
      }
    return {
      "auth": True,
      "data": this.data,
      "uid": this.ses.get("uid")  
    }
  
  def send(this, data):
    if isinstance(data, str):
      data = data.encode()
    elif isinstance(data, dict):
      data = json_stringify(data)
    elif isinstance(data, list):
      data = json_stringify(data)
    return this.txt.encrypt(data)
