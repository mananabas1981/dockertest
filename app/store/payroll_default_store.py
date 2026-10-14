from app.lib.sql import sql
from app.util.date import date_time
from app.util.json import json

class DefaultPayrollSignatoryStore:
    def __init__(self, con: sql, uid = None):
        self.con = con
        self.uid = uid

    def load(self, refid: str, dept_id: str) -> list:
        data = self.con.get('select data from custom_payroll_signatory where refid = ? and dept_id = ?', (
            refid, 
            dept_id,
        ))

        ret = []
        for datum in data:
            ret.append({
                'data': datum[0]
            })

        return ret
    

    
    def save(self, refid: str, dept_id: str, data: list):
        _dr = self.load(refid, dept_id)
        if _dr:
            # update
            self.con.commit('update custom_payroll_signatory set data = ? where refid = ? and dept_id = ?', (
                json.dumps(data),
                refid,
                dept_id,
            ))
        else:
            # insert for not found
            self.con.commit('insert into custom_payroll_signatory(refid, dept_id, data, datecreated, createdby) values(?, ?, ?, ?, ?)', (
                refid,
                dept_id,
                json.dumps(data),
                date_time(),
                self.uid,
            ))