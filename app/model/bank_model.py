from app.store.bank_store import BankStore, EmpBankStore
from re import match
from app.util.date import date_time

class BankModel:
	def __init__(this, con = None, data: dict = None, uid = None):
		this.con = con
		this.data = data
		this.uid = uid

	def save(this):
		data = this.data
		con = this.con

		if not data:
			return (False, "data is required and data must be a dictionary")
		
		if not "account_number" in data:
			return (False, "account_number is required")
		
		if not "emp_id" in data:
			return (False, "emp_id is required")
		
		if not "bank_code" in data:
			return (False, "bank_code is required")
		
		account_number = data["account_number"]
		emp_id = data["emp_id"]
		bank_code = data["bank_code"]

		uid = this.uid
		
		bank_store = BankStore(con)
		bank_data = bank_store.getBank(bank_code)
		if not bank_data:
			return (False, "Bank Not found")
		
		regex = bank_data[2]
		if not match(regex, str(account_number)):
			return (False, "Invalid account number")


		emp_bank_store = EmpBankStore(con)
		bank = emp_bank_store.exists_v2(bank_code, account_number)
		if bank:
			gemp_id, acc = bank[1], bank[2]

			if str(gemp_id) != str(emp_id):

				emp = con.get("select fname, lname, mname from client where id = ?", (gemp_id, ))
				fname = ""
				if emp:
					fname, lname, mname = emp[0]
					fname = f"{lname}, {fname} {mname}".upper()
				return (False, f"bank already exists: Owner: {fname}")
		
		ins = "New Bank account added"
		try:

			emp_bank_store.add(emp_id, bank_code, account_number, uid, date_time())
		except Exception as er:
			ins = "Bank Account updated!"
			emp_bank_store.update(emp_id, bank_code, account_number, date_time())

		return (True, f"{ins}")

