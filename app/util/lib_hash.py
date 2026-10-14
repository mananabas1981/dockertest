import os, sys, hashlib
class board:
    def get(self, serial):
      s = lib_hash()
      return s.sha3_512(serial) + s.md5(serial) + s.sha256(serial) + s.sha512(serial) + s.sha1(serial) + s.sha224(serial) + s.sha384(serial) + s.blake2b(serial) + s.blake2s(serial) + s.sha3_224(serial) 
class lib_hash():
  def __init__(self):
    self.hash_salt = "cajoconmarjon1996"
  def serial_get(self):
    os_type = sys.platform.lower()
    if "win" in os_type:
      command = "wmic baseboard get serialnumber"
    elif "linux" in os_type:
      command = "hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid"
    elif "darwin" in os_type:
      command = "ioreg -l | grep IOPlatformSerialNumber"
    return os.popen(command).read().replace("\n","").replace("  ","").replace(" ","").replace("SerialNumber", "").replace("\n","").replace("\r", "")
  def md5(self,s): 
    return hashlib.md5(s.encode()).hexdigest() + hashlib.sha256(self.hash_salt.encode()).hexdigest()
  def sha256(self,s): 
    return hashlib.sha256(s.encode()).hexdigest() + hashlib.md5(self.hash_salt.encode()).hexdigest()
  def sha512(self,s): 
    return hashlib.sha512(s.encode()).hexdigest() + hashlib.sha256(self.hash_salt.encode()).hexdigest()
  def sha1(self,s): 
    return hashlib.sha1(s.encode()).hexdigest() + hashlib.sha256(self.hash_salt.encode()).hexdigest()
  def sha224(self,s): 
    return hashlib.sha224(s.encode()).hexdigest() + hashlib.sha224(self.hash_salt.encode()).hexdigest()
  def sha384(self,s): 
    return hashlib.sha384(s.encode()).hexdigest() + hashlib.sha384(self.hash_salt.encode()).hexdigest()
  def blake2b(self,s): 
    return hashlib.blake2b(s.encode()).hexdigest() + hashlib.blake2b(self.hash_salt.encode()).hexdigest()
  def blake2s(self,s): 
    return hashlib.blake2s(s.encode()).hexdigest() + hashlib.blake2s(self.hash_salt.encode()).hexdigest()
  def sha3_224(self,s): 
    return hashlib.sha3_224(s.encode()).hexdigest() + hashlib.sha3_224(self.hash_salt.encode()).hexdigest()
  def sha3_256(self,s): 
    return hashlib.sha3_256(s.encode()).hexdigest() + hashlib.sha3_256(self.hash_salt.encode()).hexdigest()
  def sha3_384(self,s): 
    return hashlib.sha3_384(s.encode()).hexdigest() + hashlib.sha3_384(self.hash_salt.encode()).hexdigest()
  def sha3_512(self,s): 
    return hashlib.sha3_512(s.encode()).hexdigest() + hashlib.sha3_512(self.hash_salt.encode()).hexdigest()
  def shake_128(self,s): 
    return hashlib.shake_128(s.encode()).hexdigest() + hashlib.shake_128(self.hash_salt.encode()).hexdigest()
  def shake_256(self,s): 
    return hashlib.shake_256(s.encode()).hexdigest() + hashlib.shake_256(self.hash_salt.encode()).hexdigest()
  def board_mine(self):
    b = board()
    s = lib_hash()
    ss = b.get(s.serial_get())
    return ss

  