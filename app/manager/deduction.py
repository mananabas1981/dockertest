from app.util.auth import Auth
from re import match
from app.store.deduction_store import DeductionStore
from app.lib.sql import sql
from app.util.json import json_parse, json_stringify

from app.model.user_model import AccessModel
from app.store.default_ded import DefaultDeduction, DefaultDEductionEntity

from app.util.date import date_time

def add_deduction(req, res):
    con = None
    auth = None
    
    msg = {
        'ok': False,
        'msg': ''
    }
    
    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError('You are not authorized!')
        
        data = auth.data

        if not 'code' in data:
            raise ValueError('code is required!')
        
        if not 'title' in data:
            raise ValueError('title is required')
        
        if not 'floor' in data:
            raise ValueError('floor is required')
        
        if not 'ceil' in data:
            raise ValueError('ceil is required')
        
        if not 'value' in data:
            raise ValueError('value is required')

        if not 'view' in data:
            raise ValueError('view is required!')
        
        if not 'active' in data:
            raise ValueError('active is required!')
        
        if not "type" in data:
            raise ValueError("type is required")
        
        if not 't_type' in data:
            raise ValueError('t_type is required!')
        
        if not 't_bracket' in data:
            raise ValueError('t_bracket is required!')
        
        num_pattern = r'^[0-9]+([.][0-9]+)?$'
        yn_pattern = r'^[y]|[n]$'

        if not match(num_pattern, data['floor']):
            msg['msg'] = 'floor value is not valid'
            raise ValueError('floor value is invalid')

        if not match(num_pattern, data['ceil']):
            msg['msg'] = 'ceil value is invalid'
            raise ValueError('ceil value is invalid')
        
        if not match(num_pattern, data['value']):
            msg['msg'] = 'value is invalid'
            raise ValueError('valid is invalid')

        if not match(yn_pattern, data['view']):
            msg['msg'] = 'Something went wrong! value of view is invalid'
            raise ValueError('Error view got wrong choices')

        if not match(yn_pattern, data['active']):
            msg['msg'] = 'Something went wrong'
            raise ValueError('Error active is wrong choices')
        
        if not match(r"^[l]|[c]|[a]$", data["type"]):
            msg["msg"] = "Invalid type"
            raise ValueError("Invalid type: type must l or c")
        
        
        con = sql()

        ac = AccessModel(con)

        if not ac.hasAccess(auth.ses.get('uid'), ['ss-3']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())

        ded_store = DeductionStore(con)

        if data['t_type'] == 'insert':
        
            ded_store.save(
                data['code'],
                data['title'],
                data['floor'],
                data['ceil'],
                data['value'],
                data['view'],
                data['active'],
                auth.ses.get('uid'),
                data["type"]
            )

        elif data['t_type'] == 'update':

            ded_store.update(
                code = data['code'],
                name = data['title'],
                floor = data['floor'],
                ceil = data['ceil'],
                deduction_value = data['value'],
                view_only = data['view'],
                bracket = json_stringify(data['t_bracket']),
                active = data['active'],
                types = data['type']
            )

        
        con.go()

        msg['msg'] = 'Transaction Completed!'
        msg['ok'] = True

    except Exception as er:
    
        print(er)
    

    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)
    

def default_contrib_emp_list(req, res):
    auth, con, msg = (None, None, {'ok': False, 'msg': '', 'data': None})
    try:
        auth = Auth(req)
        is_auth, payload = (auth.isAuth, auth.data)
        if not is_auth: raise ValueError('Not Authorized!')
        code, name, search = (payload.get('code', None), payload.get('name', None), payload.get("search", ""))
        
        con = sql()
        emp_list = DefaultDeduction(con).get_employee(code, name, search)
        msg['data'] = emp_list

        msg['ok'] = True
        msg['msg'] = 'Transaction Completed!'
        
    except Exception as er:
        print(er)
    finally:
        if con: con.close()

    if auth: return auth.send(msg)


def default_contrib_submit(req, res):
    auth, con, msg = (None, None, {'ok': False, 'msg': ''})

    try:
        auth = Auth(req)
        is_auth, payload = (auth.isAuth, auth.data)
        
        if not is_auth: raise ValueError('Not Authorized!')
        
        card_no = payload.get('card_no')

        ded_data = DefaultDEductionEntity(
            code = payload.get('code'),
            name = payload.get('name'),
            emp_id = payload.get('emp_id'),
            value = float(payload.get('value')),
            type_ded = payload.get('type_ded'),
            end_term = payload.get('end_term') if payload.get('end_term') else None,
            createdby = auth.ses.get('uid'),
            datecreated = date_time()
        )
        con = sql()

        ded = DefaultDeduction(con)
        ded.save(ded = ded_data)
        
        con.go()

        msg['ok'] = True
        msg['msg'] = 'Transaction Completed!'

    except Exception as er:
        print(er)

    finally:
        if con: con.close

    if auth: return auth.send(msg)

def default_contrib_list(req, res):
    auth, con, msg = (None, None, {'ok': False, 'msg': '', 'data': None})
    
    try:
        auth = Auth(req)
        is_auth, payload = (auth.isAuth, auth.data)
        if not is_auth: raise ValueError('Not Authorized!')
        con = sql()

        top = req.query.get('top')

        en = DefaultDEductionEntity(code = payload.get('code'), emp_id = payload.get('id'), name = payload.get('name'))
        ded = DefaultDeduction(con)
        items = ded.get_default(en, limit = 1 if top else None)

        msg['data'] = items
        msg['msg'] = 'Transaction Completed!'
        msg['ok'] = True

    except Exception as er:
        print(er)
    finally:
        if con: con.close()

    if auth: return auth.send(msg)

def default_contrib_remove(req, res):
    auth, con, msg = (None, None, {'ok': False, 'msg': ''})

    try:
        auth = Auth(req)
        is_auth, payload = (auth.isAuth, auth.data)
        if not is_auth: raise ValueError('Authorization required!')

        con = sql()
        
        en = DefaultDEductionEntity(code = payload.get('code'), name = payload.get('name'), emp_id = payload.get('emp_id'), datecreated = payload.get('datecreated'))
        ded = DefaultDeduction(con)

        ded.remove_default(en)
        con.go()

        msg['ok'] = True
        msg['msg'] = 'Transaction Completed!'
        
    except Exception as er:
        print(er)
    finally:
        if con: con.close()

    if auth: return auth.send(msg)
    
def list_deduction(req, res):
    auth = None
    con = None
    msg = {
        'ok': 0,
        'msg': '',
        'data': []
    }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError('You are not authorized!')
        
        con = sql()

        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['ss-6']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())

        status = req.query.get('status')

        ded_store = DeductionStore(con)
        
        data = ded_store.getDeduction(status = status)
        msg['ok'] = 1
        msg['data'] = data

    except Exception as er:
        print(er)
    
    finally:
        if con:
            con.close

    if auth:
        return auth.send(msg)

def remove_deduction(req, res):
    
    auth = None
    con = None
    msg = {
        'ok': 0,
        'msg': None,
    }
    
    try:
        
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError('Your are not authorized!')
        
        data = auth.data
        if not 'code' in data:
            raise ValueError('code is required!')
        
        if not 'name' in data:
            raise ValueError('name is required!')
        
        valid_char_pattern = r'^[.0-9a-zA-Z\-\(\)\-\_ ]+$'
        if not match(valid_char_pattern, data['code']):
            msg['msg'] = 'Invalid code'
            raise ValueError('Invalid code')

        if not match(valid_char_pattern, data['name']):
            msg['msg'] = 'Invalid name'
            raise ValueError('Invalid name')
        
        con = sql()

        ac = AccessModel(con)

        if not ac.hasAccess(auth.ses.get('uid'), ['ss-3']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())

        ded_store = DeductionStore(con)

        ded_store.remove_deduction(
            data['code'], 
            data['name'],
            auth.ses.get('uid')
        )

        con.go()

        msg['ok']  = 1
        msg['msg'] = 'Removed successfully'

    except Exception as er:
        print(er)

    finally:
        if con:
            con.close()
    
    if auth:
        return auth.send(msg)

def change_state(req, res):
    
    auth = None
    con = None
    msg = {
        "ok": False,
        "msg": ""
    }

    try:
        
        auth = Auth(req)
        
        if not auth.isAuth:
            raise ValueError("You are not authorized!")
        
        data = auth.data

        if not "code" in data:
            raise ValueError("code is required")
        
        if not "name" in data:
            raise ValueError("name is required")
        
        if not "state" in data:
            raise ValueError("state is required")
 
        con = sql()

        ac = AccessModel(con)

        if not ac.hasAccess(auth.ses.get('uid'), ['ss-3']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())

        deduction_store  = DeductionStore(con)

        deduction_store.change_state(data["code"], data["name"], "y" if data["state"] else "n")        
        con.go()
        
        msg["ok"] = True
        
        if data["state"]:
            msg["msg"] = "Actvated!"
        else:
            msg["msg"] = "Deactivated!"

    except Exception as er:
    
        print(er)
    
    finally:

        if con:
            
            con.close()

    if auth:
        return auth.send(msg)
    
def emp_status_change(req, res):
    
    con = None
    
    auth = None
    
    msg = {
        "ok": False,
        "msg": ""
    }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("not authorized!")
        
        data = auth.data
        
        if not "name" in data:
            raise ValueError("name is required")
        
        if not "code" in data:
            raise ValueError("code is required")
        
        if not "status" in data:
            raise ValueError("status is required")
        
        status = json_parse(data["status"])
        if not status:
            data["status"] = "[]"

        con = sql()
        ac = AccessModel(con)

        if not ac.hasAccess(auth.ses.get('uid'), ['ss-3']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())
        
        ded_store = DeductionStore(con)

        ded_store.emp_change(data["code"], data["name"], data["status"])

        con.go()

        msg["msg"] = "Changed successfully!"
        msg["ok"]  = True

    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)
    
    