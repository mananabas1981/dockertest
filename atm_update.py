import os
import csv
from app.lib.sql import sql
from app.store.bank_store import EmpBankStore
from app.model.bank_model import BankModel
import re

def hold():
  input('Enter any key to exit!') # hold the input

def check_bank(code) -> str:
  con = sql()

  res = con.get('select regex from bank where code = ?', (code, ))

  con.close()

  if len(res) > 0: return res[0][0]

  return None


def check_old_atm(atm, regex) -> bool:

  return True if re.match(regex, atm) else False


def check_new_atm(atm, regex) -> bool:

  return True if re.match(regex, atm) else False


def print_error(title, errors: list):
  print(f"""********{title}********""".upper())
  for old_acc, new_acc, name in errors:
    print(old_acc, new_acc, name, sep = ",")
  print(f"\n******** end {title} ********\n".upper())


def check_error(csvs, from_regex, to_regex):
  
  old_error = []
  new_error = []

  for csv in csvs:
    old_account = csv[0]
    new_account = csv[1]
    name        = csv[2]
    
    if check_old_atm(atm = old_account, regex = from_regex) == False:
      old_error.append((old_account, new_account, name))

    if check_new_atm(atm = new_account, regex = to_regex) == False:
      new_error.append((old_account, new_account, name))

  
  print_error(title = "OLD ACCOUNT ERROR", errors = old_error)
  print_error(title = "NEW ACCOUNT ERROR", errors = new_error)


  return (old_error, new_error, len(old_error) == 0 and len(new_error) == 0)
    
def check_match_atm(csvs, atm):
  con = None

  error = []
  print("\n\n")
  print("******** PRINTING MATCH ***************\n\n")
  try:
    con = sql()
    bank = EmpBankStore(con = con)

    errs = []
    for csv in csvs:
      old_account = csv[0]
      new_account = csv[1]
      name        = csv[2]  
      res = bank.account_info(bank_code = atm, account = old_account)      
      prt = f'[{"+" if res else "-"}] {old_account}<->{new_account}:{name} ---> {res["name"] if res else "No Record"}'
      
      errs.append(prt)
    for err in errs:
      print(err)
    

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  print("\n\n************* END PRINTING MATCH ****************\n\n")


def import_account(csvs, old_atm, new_atm):
  con = None

  is_ok = False
  
  try:
    con = sql()
    bank = EmpBankStore(con = con)
    
    for csv in csvs:
      old_account = csv[0]
      new_account = csv[1]
      name        = csv[2]  
      res = bank.account_info(bank_code = old_atm, account = old_account)      
      
      if not res: continue
      emp_id = res["emp_id"]

      bank_model = BankModel(con = con, data = {
        "account_number": new_account,
        "emp_id": emp_id,
        "bank_code": new_atm
      })

      ok, msg = bank_model.save()
      if not ok: 
        raise ValueError(f"{new_account} " + msg)
      
      is_ok = True

      con.go()

  except Exception as er:
    print(er)
    is_ok = False
  finally:
    if con: con.close()

  return is_ok

def validate_csv(csvs: list):
  for csv in csvs:
    csv[0] = str(csv[0])
    csv[1] = str(csv[1])
    csv[2] = str(csv[2]).upper()

    old_account = csv[0]
    new_account = csv[1]
    name        = csv[2]

    #print(old_account, new_account, name)




def load_csv(path: str) -> list:
  fp_csv = open(path, 'r')
  csvreader = csv.reader(fp_csv)

  rows = []
  for row in csvreader:
    rows.append(row)
  return rows

def main():
  
  path = ''

  while True:
    n = str(input('Please select csv file: '))
    path = 'atm' + os.sep + n

    if not os.path.exists(path):
      print(f'{path} is not found! please comply the path and file for migration of atm')
      continue
    break
      
  from_regex = ""
  from_atm = ''
  while True:
    from_atm = str(input('Input the old ATM Code: '))
    res = check_bank(code = from_atm)
    if not res: continue  
    from_regex = res
    break

  to_regex = ""
  to_atm = ''
  while True:
    to_atm   = str(input('Input the New ATM Code for new Copy: '))
    res = check_bank(code = to_atm)
    if not res: continue
    to_regex = res
    break
  


  # load the csv
  
  csv = load_csv(path = path) # return list of row
  
  r = validate_csv(csv)

  _,_,ok = check_error(csvs = csv, from_regex = from_regex, to_regex = to_regex)

  if not ok:
    input("There is an error cant be procceed!")
    raise ValueError("There is an error can be proceed!")
  
  check = check_match_atm(csvs = csv, atm = from_atm)


  
  yn = str(input("Are you sure to continue? (y/n): ")).lower()
  if yn != "y":
    raise ValueError("canceled")
  
  print("Importing Account.... Please wait...")
  is_ok = import_account(csvs = csv, old_atm = from_atm, new_atm = to_atm)
  
  if is_ok:
    print("SUCCESSFULLY IMPORTED!")
  else:
    print("FAILED TO IMPORT, SOME ERROR FOUND!")


  

main()
hold()