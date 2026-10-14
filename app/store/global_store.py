from app.util.date import date_time
from app.util.json import json_stringify

def create_history(con, uid, table, data, type):
    """
    * Functions 
        * This function is create a history for the deletion and and update history
        
    * Args
        * con   -> Database connection
        * uid   -> user id
        * table -> database tablename
        * data  -> JSON string, dictionary of deleted data
        * type  
            * d -> for Delete transaction
            * u -> for update Transaction
    * Return -> Boolean value
    """
    datecreated  = date_time()
    f = con.get("select * from up_del_history where tablename = ? and data = ? and type = ?", (
        table,
        json_stringify(data),
        type,
    ))
    if not f:
        con.commit("insert into up_del_history(datecreated, uid, tablename, data, type) values(?, ?, ?, ?, ?)", (
            datecreated,
            uid,
            table,
            json_stringify(data),    
            type,
        ))
    
    