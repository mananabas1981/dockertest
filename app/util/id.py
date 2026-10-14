from lib.md5 import md5
from random import randint

def genId(code: str) -> str:
  return md5(code + str(randint(1000000, 9999999)))
  