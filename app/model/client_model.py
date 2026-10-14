from re import match
from app.store.client_store import ClientStore
from app.util.date import dt 

class ClientEntity:
  def __init_(this):
    this.id        = ""
    this.pref_name = ""
    this.fname     = ""
    this.mname     = ""
    this.lname     = ""
    this.ename     = ""
    this.suf_name  = ""
    this.gender    = ""
    this.dob       = ""
    this.addr      = ""
    this.uid       = ""
    this.hr_id     = ""


class ClientModel(ClientStore):
  
  def __init__(this):
    this.re_name = r"^[a-zA-ZÑñ\.\-\, ]+$"
    this.re_name2 = r"^[0-9a-zA-ZÑñ\.\-\(\)\!\@\#\$\%\^\&\*\_\+\=\:\;\<\>\, ]+$"

  def isValid(this, client: ClientEntity) -> tuple:

    if client.id:
      if not match(r"^[0-9]+$", str(client.id)):
        return (False, "Invalid Id")
      
    if client.pref_name:
      if not match(this.re_name, client.pref_name):
        return (False, "Invalid pref_name")
    
    if not match(this.re_name, client.fname):
      return (False, "Invalid fname")
    
    if client.mname:
      if not match(this.re_name, client.mname):
        return (False, "Invalid mname")
    
    if not match(this.re_name, client.lname):
      return (False, "Invalid lname")
    
    if client.ename:
      if not match(this.re_name, client.ename):
        return (False, "Invalid ename")
    
    if client.suf_name:
      if not match(this.re_name, client.suf_name):
        return (False, "Invalid suf_name")

    if not match(r"^[mfMF]$", client.gender):
      return (False, "Invalid gender")

    if client.dob:
      if not match(r"^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$", client.dob):
        return (False, "Invalid dob")
      
    if client.addr:
      if not match(this.re_name2, client.addr):
        return (False, "Invalid Address")

    return (True, None)

  def isClientExists(this, client: ClientEntity) -> bool:
    middle = ""
    if client.mname:
      middle = client.mname[0].lower()

    data = this._iExists(fname = client.fname.lower(), mname = middle, lname = client.lname.lower(), ename = client.ename.lower())
    if data:
      return True
    return False
  
  def isClientExistsOnUpdate(this, client: ClientEntity) -> bool:
    middle = ""
    if client.mname:
      middle = client.mname[0].lower()

    data = this._uExists(ids = client.id, fname = client.fname.lower(), mname = middle, lname = client.lname.lower(), ename = client.ename.lower())
    if data:
      return True
    return False
  
   
  def updateClient(this, client: ClientEntity) -> bool:
    if this.isClientExistsOnUpdate(client):
      return False
    
    this._clientUpdate(client)
    return True

  def addClient(this, client: ClientEntity = None) -> bool:
    if not this.isClientExists(client):
      this._insert( 
        pref_name = client.pref_name,
        fname = client.fname,
        mname = client.mname,
        lname = client.lname,
        ename = client.ename,
        suf_name = client.suf_name,
        gender = client.gender,
        addr = client.addr,
        dob = client.dob,
        date = dt(),
        uid = client.uid,
        hr_id = client.hr_id
      )
      return True
    else:
      return False

  def is_search_valid(this, search = "") -> bool:
    if search:
      if not match(r"^[0-9a-zA-Z\-\_\.]+$", search):
        return False
    return True
      
  def getClients(this, search = "", dept_id = "", emp_status = "", active = None) -> list:
    data = this._getClients(search = search, dept_id = dept_id, emp_status = emp_status, is_active = active)

    return data