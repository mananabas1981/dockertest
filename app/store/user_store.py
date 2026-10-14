from app.lib.sql import sql 
from app.util.json import json_stringify, json_parse
from app.util.date import date_time
from app.util.md5 import md5

class UserEntity:
  def __init__(this, ids = None, name = '', pos_title = ''):
    this.ids = ids
    this.name = name
    this.pos_title = pos_title
    

class UserStore:
  def __init__(this, con = None):
    this.__con  = con

  def _setConnection(this, con: sql = None):
    this.__con = con

  def _getUser(this, username = None, password = None) -> dict:
    data = {}
    
    tmp = this.__con.getone("SELECT id, username, name, role, roles FROM user WHERE username = ? and password = ?", (
      username, 
      password,
    ))
    if tmp: 
      data["id"] = tmp[0]
      data["username"] = tmp[1]
      data["name"]     = tmp[2]
      data["role"]     = tmp[3]
      data["roles"]    = tmp[4]

    return data
  
  def isUserExistsOnInsert(this, username) -> bool:
    data = this.__con.get('select id from user where username = ?', (username, ))
    return True if data else False

  def autoid(this):
    data = this.__con.get('select (max(id) + 1) as id from user')
    return data[0][0]

  def createUser( this, name, username, password, gender, dob, pos_title, signature_id, role = 0, roles = [] ) -> tuple:
    if this.isUserExistsOnInsert( username ):
      return (False, 'Username is already exists')
    
    ids = this.autoid()
    
    this.__con.commit('''INSERT INTO user(id, name, username, role, roles, gender, dob, status, datecreated, password, pos_title, signature_id) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                        ids, 
                        name,
                        username,
                        role,
                        json_stringify(roles),
                        gender,
                        dob,
                        '1',
                        date_time(),
                        md5(password),
                        pos_title,
                        signature_id,
                      ))

    return (True, 'New User added!')


  def isUserExistsOnUpdate(this, ids, username):
    
    data = this.__con.get('select id from user where username = ? and not id = ?', (
      username,
      ids,
    ))

    return True if data else False

  def updateUser(this, ids, name, username, password, gender, dob, pos_title, signature_id, role = 0, roles = []):
    if this.isUserExistsOnUpdate( ids, username ):
      return (False, 'username is already exists!')
    
    this.__con.commit('''
      update user set name = ?, username = ?, password = ?, gender = ?, dob = ?, pos_title = ?, signature_id = ? where id = ?
    ''', (
        name,
        username,
        md5(password),
        gender,
        dob,
        pos_title,
        signature_id,
        ids,
    ))

    return (True, 'User updated!')

  def list_user(this, ids = None) -> list:
    con = this.__con

    ids_q = ''
    tup = ()
    if ids:
      ids_q = ' where id = ?'
      tup = (ids, )
    
    data = con.get(f'select id, name, username, role, roles, gender, dob, status, datecreated, pos_title, signature_id from user {ids_q}', tup)

    ret = []

    for x in data:
      ret.append({
        "id":        x[0],
        "name":      x[1],
        "username":  x[2],
        "role":      x[3],
        "roles":     x[4],
        "gender":    x[5],
        'dob':       x[6],
        'status':    x[7],
        'date':      x[8],
        'pos_title': x[9],
        'sign_id':   x[10]
      })

    return ret
  
  def sign_key(this, uid):
    d = this.list_user(uid)
    if d: return d[0]['sign_id']
    return None


  def getState(this, emp_id):
    con = this.__con
    data = con.get('select roles from user where id = ?', (
      emp_id,
    ))
    return data
  
  def getRoles(this, emp_id) -> list:
    data = this.getState(emp_id)
    if data:
      return json_parse(data[0][0])
    return []

  def isRoleExists(this, code, roles) -> bool:
    for x in roles:
      if x == code:
        return True
    return False

  def updateState(this, emp_id, code, is_check):
    data = this.getState(emp_id)
    roles = []
    if data and data[0][0]:
      roles = json_parse(data[0][0])

    if not this.isRoleExists(code, roles):
      if is_check:
        roles.append(code)
    else:
      if not is_check:
        roles.remove(code)

    con = this.__con

    con.commit("update user set roles = ? where id = ?", (
      json_stringify(roles),
      emp_id,
    ))

