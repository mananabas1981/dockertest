from app.store.client_store import DeptInfoStore
from app.util.date import date_time


class DeptModel:
    def __init__(self, con, uid = None):
        self.con = con
        self.uid = uid

    
    def get_dept_by_code(self, code):
        return self.con.get("""select id from department where lower(code) = ?""", (code.lower(), ))

    def get_dept_by_id(self, ids):
        return self.con.get("""select id from department where id = ?""", (ids, ))


    def update_dept(self, emp_id, ids) -> bool:
        dept_id = ""

        # get the department by code
        dept_data = self.get_dept_by_id(ids)
    
        if not dept_data:
            return False
        
        dept_id = dept_data[0][0] # get the deparment
    
        dept_info = DeptInfoStore(self.con)

        last_dept = dept_info.get_last_dept(emp_id)


        if last_dept:
            last_dept_id = str(last_dept[1])
            if not (str(dept_id) == last_dept_id):
                dept_info.create_dept(emp_id, dept_id, date_time(), self.uid)  
        else:
            dept_info.create_dept(emp_id, dept_id, date_time(), self.uid)

        return True

    def update_dept2(self, emp_id, ids) -> bool:
        dept_id = ""

        # get the department by code
        dept_data = self.get_dept_by_code(ids)
    
        if not dept_data:
            return False
        
        dept_id = dept_data[0][0] # get the deparment
    
        dept_info = DeptInfoStore(self.con)

        last_dept = dept_info.get_last_dept(emp_id)


        if last_dept:
            last_dept_id = str(last_dept[1])
            if not (str(dept_id) == last_dept_id):
                dept_info.create_dept(emp_id, dept_id, date_time(), self.uid)  
        else:
            dept_info.create_dept(emp_id, dept_id, date_time(), self.uid)

        return True