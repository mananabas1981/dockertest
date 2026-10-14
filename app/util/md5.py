import hashlib
def md5(str):
  return hashlib.md5(str.encode()).hexdigest()
def sha1(str):
	return hashlib.sha1(str.encode()).hexdigest()