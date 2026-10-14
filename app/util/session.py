# session managements
# date updated: September 16, 2022
# details: remove the first param in object session http
# focusing localStorage not in the session in a browser
from functools import lru_cache
from datetime import datetime
# from cryptography.fernet import Fernet
# from App.lib.fernet.fernet import Fernet
from app.lib.fernet.fernet import Fernet

import random
import time
import os
#import ujson as json
import json

# using the memory as the storage of the session list
# to avoid repeat open file and boast performance from file decryption

SESSION_CACHE = {}
SESSION_CACHE_MAX_SIZE = 10000

class session:

  def _create_key(this):
    this.key = "ses" + str(time.time_ns()) + str(random.randrange(1000000, 9999999))
    this._joinpath()
    if not this.exists():
      fp = open(this.path, "wb")
      f = this.__fernet.encrypt(json.dumps(this.data).encode())
      fp.write(f)
      fp.close()
  def _update_file(this):
    if this.exists():
      fp = open(this.path, "wb")
      f = this.__fernet.encrypt(json.dumps(this.data).encode())
      fp.write(f)
      fp.close()
  def _file_content(this):
    if this.exists():
      fp = open(this.path, "rb")
      e = this.__fernet.decrypt(fp.read().decode())
      this.data = json.loads(e)
      fp.close()
  def __str__(this):
    return str(this.data)

  def __init__(this, keyA = "", manual = False):

    # fernet key
    this.__key = "ulSTa7sUSKNCBoYRUQPFTki-19RHlJfECNdSvFQTByI="
    this.__fernet = Fernet(this.__key)

    this.key = keyA
    this.data = {}
    this.manual = manual
    t = time.gmtime() # python c style time
    this.data["date"] = str(t.tm_year) + "/" + str(t.tm_mon) + "/" + str(t.tm_mday) + " " + str(t.tm_hour) + ":" + str(t.tm_min) + ":" + str(t.tm_sec)
    if not this.manual:
      # generate a key if the key is empty
      this._create_key() # if key is not found generate new key,,
      # useful in fresh logged in
    else:
      this._joinpath()    
    #print(os.path.abspath("tmp"))

    if len(SESSION_CACHE) > SESSION_CACHE_MAX_SIZE:
      SESSION_CACHE.clear()
      print("SESSION CACHE STORAGE RESET")

    this.__LoadSession()

    # adding the expiration date of the session
    dt_exp = this.get("dt_exp") 
    if not dt_exp:
      dt = datetime.now()
      dt_st = dt.strftime("%Y-%m-%d %H:%M:%S")      
      this.set("dt_exp", dt_st)
    else:
      dt = datetime.strptime(dt_exp, "%Y-%m-%d %H:%M:%S")
      delta = datetime.now() - dt
      age = delta.total_seconds()
      
      half_day_session = 14400.0 # another layer of security where 4hours
      if age > half_day_session:
        this.destroy()


  def __LoadSession(this):
    if this.key in SESSION_CACHE:
      # load the session from the memory
      this.data = SESSION_CACHE[this.key]
    else:
      # load the session from file
      this._file_content()
      this.__update_cache() # update the cache memory

  def __update_cache(this):
    # after loaded the session from file then need to add it to the memory cache
    if this.data:
      SESSION_CACHE[this.key] = this.data
      
  def _joinpath(this):
    this.path = os.path.abspath(os.path.join("data", "tmp", this.key))
  def set(this, key, value):
    this.data[key] = value
    this._update_file()
    this.__update_cache()
  def get(this, key):
    return this.data.get(key)
  def unset(this, key):
    if this.data.get(key):
      del this.data[key]
      this._update_file()
      this.__update_cache()
  def destroy(this):
    if this.key in SESSION_CACHE:
      del SESSION_CACHE[this.key]
    if this.exists():
      os.remove(this.path)
    this.data = {}


  def exists(this):
    # return false if the key is empty, since it is always true if folder exist
    if not this.key:
      return False
    if os.path.exists(this.path):
      return True
    return False
#ses = session(http)