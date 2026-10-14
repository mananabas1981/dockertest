from app.lib.sql import sql
from app.store.client_store import client_deactivate
from app.util.date import date_time

class ActiveStatus:

    def __init__(self, con: sql = None):
        self.con: sql = con


    def get(self, emp_id = None, frm = None):
        return self.con.get('''select emp_id, frm, tto, remark, type, datecreated, createdby from active_status where emp_id = ? and frm = ?
        ''', (
            emp_id, frm,
        ))

    def insert(self, emp_id = None, frm = None, remark = None, uid = None):
        res = self.get(emp_id, frm)

        if not res:
            self.con.commit('''
                insert into active_status(emp_id, frm, remark, type, datecreated, createdby) values(?, ?, ?, ?, ?, ?)
            ''', (
                emp_id,
                frm,
                remark,
                'd',
                date_time(),
                uid,
            ))
            client_deactivate(con = self.con, emp_id = emp_id)