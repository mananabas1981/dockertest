def validate(key: list, fdata: dict) -> tuple:
  for x in key:
    if not x in fdata:
      return (False, x)
  return (True, "")

def input_validate(key: list, fdata: dict) -> bool:
  for x in key:
    if not x in fdata:
      return False
  return True