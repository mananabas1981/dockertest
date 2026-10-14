from app.util.auth import Auth
from app.store.signatory_store import SignInfo, SignatoryStore
from app.lib.sql import sql
from app.util.json import json_stringify
from re import match

from app.model.user_model import AccessModel


def GetSignatory(req, res):
    
    con = None
    auth = None
    res = {
        "ok": False,
        "msg": None,
        "data": None
    }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("You are not authorized!")
        
        con = sql()
        
        ac = AccessModel(con)

        if not ac.hasAccess(auth.ses.get('uid'), ['ss-i']):
            res['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())
        
        signStore = SignatoryStore(con)
        signData = signStore.GetSignatory()
        res["data"] = signData
        res["msg"] = "Transaction Completed!"
        res["ok"] = True

    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(res)


def save(req, res):
    auth = None
    con = None
    
    msg = {
        "ok": False,
        "msg": None
    }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("you are not authorized!")
        
        data = auth.data
        
        if not "certify" in data:
            raise ValueError("certify required")
        
        if not "name" in data:
            raise ValueError("name is required")

        if not "pos_title" in data:
            raise ValueError("pos_title is required")
        
        if not "index" in data:
            raise ValueError("index is required")

        if not "is_update" in data:
            raise ValueError("is_update is required")

        if not 'sign_id' in data: raise ValueError('sign_id is required!')


        if not match(r"^[0-9][,][0-9]$", data["index"]):
            msg["msg"] = "index is invalid"
            raise ValueError("index is invalid")
        
        udate = data["datecreated"] if "datecreated" in data else None

        is_update = data["is_update"]
        
        _index     = data["index"].split(",")
        
        index_data = json_stringify([_index[0], _index[1]])     
        
        con = sql()

        ac = AccessModel(con)

        if not ac.hasAccess(auth.ses.get('uid'), ['ss-2']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())

        signStore = SignatoryStore(con)    
        signStore.Save(SignInfo(
                data["certify"], 
                data["name"],
                data["pos_title"],
                index_data,
                "y",
                sign_id = data['sign_id']
            ), auth.ses.get("uid"), is_update, udate)
        
        con.go()
        
        msg["msg"] = "Transaction Completed!"
        msg["ok"]  = True

    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)
    
def active_change(req, res):
    con = None
    auth = None
    res = {
        "ok": False,
        "msg": None
    }

    try:
        
        auth = Auth(req)
        
        if not auth.isAuth:
            raise ValueError("you are not authorized!")
        
        data = auth.data
        
        if not "name" in data:
            raise ValueError("name is required")
        
        if not "certify" in data:
            raise ValueError("certify is required")
        
        if not "check" in data:
            raise ValueError("check is required!")
        
        con = sql()
        
        ac = AccessModel(con)

        if not ac.hasAccess(auth.ses.get('uid'), ['ss-2']):
            res['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())
        
        signStore = SignatoryStore(con)
        signStore.change_active("y" if data["check"] else "n", data["name"], data["certify"])
        con.go()
        
        res["msg"] = "Transaction Completed!"
        res["ok"]  = True

    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(res)

def type_change(req, res):
    con = None
    auth = None
    res = {
        "ok": False,
        "msg": None
    }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("you are no autorized!")
        data = auth.data

        if not "name" in data:
            raise ValueError("name is required")
        if not "certify" in data:
            raise ValueError("certify is required")
        
        if not "type" in data:
            raise ValueError("type is required")
        
        con = sql()
        
        ac = AccessModel(con)

        if not ac.hasAccess(auth.ses.get('uid'), ['ss-2']):
            res['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())

        signStore = SignatoryStore(con)
        signStore.change_type(data["name"], data["certify"], json_stringify(data["type"]))
        
        con.go()

        res["msg"] = "Transaction Completed!"
        res["ok"] = True
        
    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()
    
    if auth:
        return auth.send(res)