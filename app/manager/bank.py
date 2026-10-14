from app.util.auth import Auth
from app.lib.sql import sql
from app.store.bank_store import BankStore, EmpBankStore
from re import match
from app.util.date import date_time
from app.model.bank_model import BankModel
from app.model.user_model import AccessModel

def save(req, res):
    con = None
    auth = None
    msg = {
        "ok": 0,
        "msg": ""
    }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("Not authorized!")
        
        data = auth.data
        if not data:
            raise ValueError("data is not available")
        
        if not "code" in data:
            raise ValueError("code is required")
        
        if not "name" in data:
            raise ValueError("name is required")

        if not "regex" in data:
            raise ValueError("regex is required")
        
        if not "branch_head" in data:
            raise ValueError("branch_head is required")

        code = data["code"]
        name = data["name"]
        regex = data["regex"]
        branch_head = data["branch_head"]

        if not match(r"^[a-zA-Z0-9\-\_]+$", code):
            msg["msg"] = "Invalid Code"
            raise ValueError("Invalid code")
        
        if not match(r"^[a-zA-Z0-9\-\_\(\)\[\] ]+$", name):
            msg["msg"] = "Invalid Name"
            raise ValueError("Invalid name")
        
        name_reg = r"^[A-Z0-9\Ñ\,\. ]+[;]{1}[A-Z0-9\Ñ\. ]+[;]{1}[A-Z0-9\Ñ\. ]+[;]{1}[A-Z0-9\Ñ\. ]+[;]{1}[A-Z0-9\Ñ\,\. ]+$"
        
        if branch_head:
            if not match(name_reg, branch_head):
                msg["msg"] = "Invalid Branch Head Name"
                raise ValueError("Invalid Branch Head Name")

        con = sql()

        ac = AccessModel(con)

        if not ac.hasAccess(auth.ses.get('uid'), ['ss-5']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())

        bank_store = BankStore(con)
        _bank = bank_store.getBank(code)
        if _bank:
            msg["msg"] = "Bank already added"
            raise ValueError("Bank Already added")
        else:
            bank_store.add(code, name, regex, date_time(), auth.ses.get("uid"), branch_head)
        con.go()
        msg["msg"] = "Transaction Completed!"
        msg["ok"] = 1
    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)
    
def get_all_bank(req, res):
    con = None
    auth = None
    msg = {
        "ok": 0,
        "msg": "",
        "data": []
    }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("You are not authorized")
        
        con = sql()
        bank_store = BankStore(con)
        data = bank_store.getAllBank()
        
        msg["data"] = data
        msg["msg"] = "Transaction Completed!"
        msg["ok"] = 1
    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()
    if auth:
        return auth.send(msg)
    
def remove_bank(req, res):
    con = None
    auth = None
    msg = {
        "ok": 0,
        "msg": ""
    }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("You are not authorized!")
        
        data = auth.data
        if not data:
            raise ValueError("data is required")
        
        if not "code" in data:
            raise ValueError("code is required")
        
        code = data["code"]
        if not match(r"^[a-zA-Z0-9\-\_]+$", code):
            raise ValueError("code is invalid")
        
        con = sql()
        
        ac = AccessModel(con)

        if not ac.hasAccess(auth.ses.get('uid'), ['ss-5']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())

        bank_store = BankStore(con)
        bank_store.removeBank(code, auth.ses.get("uid"))
        con.go()
        msg["msg"] = "Transaction Completed!"
        msg["ok"] = 1
        
    except Exception as er:
        print(er)

    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)
    
def emp_save_bank(req, res):
    con = None
    auth = None
    msg = {
        "ok": 0,
        "msg": ""
    }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("You are not authorized!")
        data = auth.data
        
        con = sql()
        
        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['em-7']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())
        
        bank_model = BankModel(con, data, auth.ses.get("uid"))

        ok, res = bank_model.save()
        if ok:
            con.go()

        msg["msg"] = res
        msg["ok"] = 1 if ok else 0

    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()
    if auth:
        return auth.send(msg)
    
def emp_bank_list(req, res):
    con = None
    auth = None
    msg = {
        "ok": 0,
        "msg": "",
        "data": []
    }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("You are not authorized!")
        
        data = auth.data

        if not data:
            raise ValueError("data is invalid")
        
        if not "emp_id" in data:
            raise ValueError("emp_id is required")
        
        emp_id = data["emp_id"]

        if not match(r"^[0-9]+$", str(emp_id)):
            raise ValueError("emp_id is invalid")
        

        con = sql()
        
        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['em-7']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())

        emp_bank_store = EmpBankStore(con)

        bank_data = emp_bank_store.getAccount(emp_id)

        msg["ok"] = 1
        msg["msg"] = "Transaction Completed!"
        msg["data"] = bank_data

    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)
    
def emp_remove_bank(req, res):
    con = None
    auth = None
    msg = {
        "ok": 0,
        "msg": ""
    }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("You are not authorized!")
        data = auth.data
        
        if not data:
            raise ValueError("data is invalid")
        
        if not "code" in data:
            raise ValueError("code is required")
        
        if not "account_number" in data:
            raise ValueError("account_number is required")
        
        if not "emp_id" in data:
            raise ValueError("emp_id is required")
        
        code = data["code"]
        account_number = data["account_number"]
        emp_id = data["emp_id"]
        
        con = sql()

        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['em-7']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())

        ebank = EmpBankStore(con)
        ebank.remove_bank(emp_id, code, account_number, auth.ses.get("uid"))
        con.go()

        msg["msg"] = "Transaction Completed!"
        msg["ok"] = 1
    except Exception as er:
        print(er)
        
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)