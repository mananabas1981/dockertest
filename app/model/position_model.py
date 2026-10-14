from app.store.client_store import PositionStore
from app.util.date import date_time

class PositionModel:
    def __init__(self, con, uid = None):
        self.con = con
        self.uid = uid
        
    def create_position(self, emp_id, pos_title, status):
    
        pos_store = PositionStore(self.con)
        
        last_pos = pos_store.get_last_position(emp_id)
        
        if last_pos:
            last_title = last_pos[0]
            if not (last_title == pos_title):
                pos_store.create_position(emp_id, pos_title, status, date_time(), self.uid)  
        else:
            pos_store.create_position(emp_id, pos_title, status, date_time(), self.uid)

