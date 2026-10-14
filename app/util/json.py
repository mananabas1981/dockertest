# in the future we can implement the ujson or orgjson for faster encoding and decoding the 
# json data and json object
# replace this json son for fast 
import json
def json_stringify(obj):
  return json.dumps(obj, default = str)

def json_parse(str_bytes):
  try:
    return json.loads(str_bytes)
  except json.decoder.JSONDecodeError:
    return None