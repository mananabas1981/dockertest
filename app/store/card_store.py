from app.lib.sql import sql
from typing import List

from app.util.date import date_time

class Card:
    def __init__(this, 
        emp_id: str = "",
        card_type: str = "",
        card_name: str = "",
        card_value: str = ""):
        
        this.emp_id     = emp_id
        this.card_type  = card_type
        this.card_name  = card_name
        this.card_value = card_value


class CardModel:
    def __init__(this, con: sql = None):
        this._con: sql = con

    def lists(this, card: Card) -> List[Card]:

        lst = []

        res: List[tuple] = this._con.get("""
            select emp_id, card_type, card_value, card_name from card 
        """)


        return lst
    




class Card:
    def __init__(self, con: sql):
        self.con: sql = con




class CardStore:
    def __init__(self, con: sql):
        self.con = con

    def get(self, code, emp_id):
        return self.con.get("select card_no from card where code = ? and emp_id = ?", (code, emp_id, ))
    
    def get_by_code_emp_id(self, code, emp_id):
        data = self.con.get("select card_no, datecreated, createdby, code from card where code = ? and emp_id = ? order by datecreated desc", (code, emp_id, ))
        ret = []
        for item in data:
            card_no, datecreated, createdby, code = item
            ret.append({
                'card_no': card_no,
                'datecreated': datecreated,
                'createdby': createdby,
                'code': code
            })

        return ret

    def get_by_emp_id(self, emp_id) -> list:
        data = self.con.get('select code, card_no from card where emp_id = ?', (emp_id, ))
        
        ret = []
        for item in data:
            ret.append({
                'code': item[0],
                'card_no': item[1]
            })

        return ret

    def save(self, code, emp_id, card_no, uid = None):
        if (self.get(code, emp_id)):
            self.con.commit("update card set card_no = ? where code = ? and emp_id = ?", (
                card_no, code, emp_id, 
            ))
        else:
            self.con.commit("insert into card(code, emp_id, card_no, datecreated, createdby) values(?, ?, ?, ?, ?)", (
                code, emp_id, card_no, date_time(), uid,
            ))
        