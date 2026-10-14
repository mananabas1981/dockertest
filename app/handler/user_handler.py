from app.lib.bottle import Bottle, request as req, response as res
from app.util.auth import Auth
from app.util.text import Text
from app.util.json import json_parse
from app.lib.sql import sql 
from app.model.user_model import UserModel
from app.util.session import session
from app.manager import user
from app.model.user_model import AccessModel
from app.store.user_session import UserSessionStoreService, UserSessionStore
from app.util.date import date_time


user_app = Bottle()

@user_app.route("/login", method = ["POST"])
def login():
  con = None
  userModel = None 
  auth_obj = None
  txt = None
  try:
    auth_obj = Auth(req)
    default_key = auth_obj.default_key
      
    data_bin = req.body.read(2048) # maximum of 2kb
    if not data_bin:
      return
    
    txt = Text(default_key) 
    data = txt.decrypt(data_bin) 
    data = json_parse(data)  

    header = req.headers
  

    user_agent = header.get("User-Agent")
    origin = header.get("Origin")

    if not origin:
      return txt.encrypt({
        "ok": 0,
        "msg": "Invalid Device"
      })
    
    if not user_agent:
      return txt.encrypt({
        "ok": 0,
        "msg": "Invalid Device"
      })
    
    # if not "firefox" or "chrome" in user_agent:
    #   return txt.encrypt({
    #     "ok": 0,
    #     "msg": "Please Use Firefox or Chrome!"
    #   })

    if not data:
      return
    
    if not "username" in data:
      return
    
    if not "password" in data:
      return
    
    if auth_obj.getAuthModel().auth:
      return txt.encrypt({
        "ok": 2,
        "msg": "This device already logged in!"
      })
    
    # checking if it is on the block listed
    uname = data["username"]
    
    # end checking of blocked listed
    
    userModel = UserModel()
    is_valid = userModel.isValidAuthentication(data["username"], data["password"])
    
    r = {
      "ok": 0,
      "msg": "Invalid Information"
    }

    if not is_valid:
      return txt.encrypt(r)
    con = sql()
    userModel._setConnection(con)
    user_data = userModel.authenticate(data["username"], data["password"])
    
    if not user_data:
      return txt.encrypt(r)

    ids = user_data["id"]

    ac = AccessModel(con)
    if ac.hasAccess(ids, ['ss-0']): # this is a block logined
      con.close()
      r['msg'] = 'You dont have access to the system!'
      return txt.encrypt(r)


    fkey = Text.gen_key().decode()


    ses = session()
    ses.set("uid", user_data["id"])
    ses.set("role", user_data["role"])
    ses.set("username", user_data["username"])
    ses.set("name", user_data["name"])
    ses.set("roles", user_data["roles"])
    ses.set("fkey", fkey)
    ses.set("device", f"{origin}{user_agent}")

    status = -1
    if int(user_data["role"]) == 1:
      status = 1
      # if user is admin then no need approval
    else:
      # for normal user
      if ac.hasAccess(ids, ['us-1']):
        status = 1
    

    ses.set('status', status)

    user_ses = UserSessionStoreService(con)

    user_ses.createSession(UserSessionStore(
      key = ses.key, 
      date = date_time(), 
      uid = user_data['id'], 
      status = status
    ))
    con.go()    

    

    r["name"] = user_data["name"]
    r["uname"] = user_data["username"]
    r["ok"] = 1
    r["msg"] = "Access Granted!"
    r["token"] = ses.key
    r["fkey"] = fkey
    r['status'] = status

    return txt.encrypt(r)
  
  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()
      del con
    if userModel:
      del userModel   
    if auth_obj:
      del auth_obj
    if txt:
      del txt

@user_app.route('/save', method = ['pOST'])
def user_save():
    return user.save(req, res)

# start of user here
@user_app.route('/list', method = ['POST'])
def user_list():
  return user.user_list(req, res)
# end of the user here

@user_app.route('/default/access', method = ['POST'])
def default_access():
  return user.access_list(req, res)

@user_app.route('/access/state', method = ['POST'])
def access_state():
  return user.access_state(req, res)
