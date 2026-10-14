from app.store.global_store import create_history

from app.store.client_store import ClientStore

class BankStore:
    def __init__(this, con):
        this.__con = con

    def getBank(this, code):
        data = this.__con.getone("select code, name, regex, branch_head, datecreated, createdby, status from bank where code = ?", (
            code,
        ))
        return data

    def getAllBank(this):
        data = this.__con.get("select code, name, regex, datecreated from bank")
        return data
    
    def add(this, code, name, regex, datecreated = None, createdby = None, branch_head = None, status = 1):
        this.__con.commit("insert into bank(code, name, regex, datecreated, createdby, status, branch_head) values(?, ?, ?, ?, ?, ?, ?)", (
            code, name, regex, datecreated, createdby, status, branch_head,
        ))

    def removeBank(this, code, uid = None):
        data = this.getBank(code)
        if data:
            create_history(this.__con, uid, "bank", data, "d")
            this.__con.commit("delete from bank where code = ?", (
                code,
            ))


class EmpBankStore:
    def __init__(this, con):
        this.__con = con

    def add(this, emp_id, bank_code, bank_account, createdby = None, datecreated = None):
        this.__con.commit("insert into emp_bank_account(emp_id, bank_code, bank_account, createdby, datecreated) values(?, ?, ?, ?, ?)", (
            emp_id,
            bank_code,
            bank_account,
            createdby,
            datecreated,            
        ))

    def update(this, emp_id, bank_code, bank_account, datecreated):
        this.__con.commit("update emp_bank_account set datecreated = ?, bank_account = ? where emp_id = ? and bank_account = ? and bank_code = ?", (
            datecreated,
            bank_account,
            emp_id,
            bank_account,
            bank_code,
        ));
    
    def account_info(this, bank_code, account):
        info = {}
        name = ""
        
        res = this.__con.get("""
            select bank_account, emp_id from emp_bank_account where bank_account = ? and bank_code = ?
        """, (account, bank_code, ))
        
        if not res: return info
        account, emp_id = res[0]

        emp = ClientStore(con = this.__con)
        
        e = emp.info_by_id(ids = emp_id)
        
        if e: name = f"""{e["l"]}, {e["f"]} {e["m"] + "." if e["m"] else ""} {e["e"]}""".upper()

        info = {
            "account": account,
            "emp_id": emp_id,
            "name": name
        }

        
        return info

    def exists(this, bank_code, bank_account):
        data = this.__con.getone("select bank_code from emp_bank_account where bank_code = ? and bank_account = ?", (
            bank_code, bank_account,
        ))
        return True if data else False
    
    def exists_v2(this, bank_code, bank_account):
        data = this.__con.getone("select bank_code, emp_id, bank_account from emp_bank_account where bank_code = ? and bank_account = ?", (
            bank_code, bank_account,
        ))
        return data
    
    
    
    def getAccount(this, emp_id, limit: int = None, code = None):
        limit_q = ""
        if limit:
            limit_q = f"limit {limit}"
        tup_ = [emp_id]
        code_q = ""
        if code != None:
            code_q = "and bank_code = ?"
            tup_.append(code)

        data = this.__con.get(f"select bank_code, bank_account, datecreated from emp_bank_account where emp_id = ? {code_q} order by datecreated desc {limit_q}", tuple(tup_))
        
        return data

    def get_bank(this, emp_id, code, account_number):
        return this.__con.getone("select bank_code, bank_account, datecreated, createdby from emp_bank_account where bank_code = ? and emp_id = ? and bank_account = ?", (
            code,
            emp_id,
            account_number,
        ))

    def remove_bank(this, emp_id, code, account_number, uid):
        bank = this.get_bank(emp_id, code, account_number)
        if bank:
            this.__con.commit("delete from emp_bank_account where bank_code = ? and emp_id = ? and bank_account = ?", (
                code,
                emp_id,
                account_number
            ))

            create_history(this.__con, uid, "emp_bank_account", bank, "d")