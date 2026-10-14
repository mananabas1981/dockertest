from app.lib.fernet.fernet import Fernet
from app.util.json import json_stringify

class Text:
  def __init__(this, key):
    this.__fernet = Fernet(key)
  
  @staticmethod
  def gen_key():
    return Fernet.generate_key()

  def encrypt(this, data):
    #data = pad(data, 16)
    # ensuring that the data is bytes
    data = json_stringify(data) if isinstance(data, dict) else data
    data = data if isinstance(data, bytes) else data.encode()
    return this.__fernet.encrypt(data)


  def decrypt(this, data):
    #data = unpad(data, 16)
    # Ensuring that the data is a byte
    try:
      data = data if isinstance(data, bytes) else data.encode()
      return this.__fernet.decrypt(data)
    except Exception as er:
      return b""