from app.lib.sql import sql 
from app.util.json import json_parse, json_stringify
from app.util.auth import Auth

from app.store.user_store import UserStore
from app.model.user_model import AccessModel

from re import match

from app.util.md5 import md5


def user_change_password(req, res):
    auth, con, msg = None, None, { "ok": False, "msg": "Invalid Requests" }

    try:
        
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("You are not authorized!")
        data = auth.data

        uid = auth.ses.get("uid")

        if not "old_pass" in data:
            raise ValueError("Old Pass is required!")
        
        if not "new_pass" in data:
            raise ValueError("New Pass is required!")
        
        if not "con_pass" in data:
            raise ValueError("Old Pass is required!");

        old_pass = data["old_pass"]
        new_pass = data["new_pass"]
        con_pass = data["con_pass"]
        # checking the old password is required!

        con = sql()
        res = con.get("select id from user where id = ? and password = ?", (
            uid,
            md5(old_pass)
        ))

        if len(res) == 0: 
            msg["msg"] = "Old Password don't Match!"
            raise ValueError("Invalid Password")

        if (old_pass == new_pass):
            msg["msg"] = "This is your current Password"
            raise ValueError("current password cant be your new password")
        

        if len(new_pass) < 6:
            msg["msg"] = "New Password must be atleast 6 characters"
            raise ValueError("must be a 6 digit password")
        
        if new_pass != con_pass:
            msg["msg"] = "Your new password dont match with the confirm password!"
            raise ValueError("new and con dont match")

        # update the password now 

        con.commit("update user set password = ? where id = ?", (
            md5(new_pass),
            uid
        ))

        msg["msg"] = "Successfully updated!"
        msg["ok"] = True
        con.go()

        
    except Exception as er:
        print(er)

    finally:
        if con: con.close()

    return auth.send(msg) if auth else None

def user_list(req, res):
    auth = None
    con = None
    msg = {
        "ok": False,
        "data": None
    }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("You are not authorized!")
        con = sql()
        
        ac = AccessModel(con)

        role = int(auth.ses.get('role'))
        if not ( role == 1 ):
            if not ac.hasAccess(auth.ses.get('uid'), ['ss-a']):
                msg['msg'] = ac.errorAccess()
                raise ValueError(ac.errorAccess())

        user_store = UserStore(con)
        msg['data'] = user_store.list_user()
        msg['ok'] = True
        
    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)
    

def access_list(req, res):
    auth = None
    msg = {
        'ok': False,
        'data': [],
        'msg': None
    }
    con = None

    try:
        
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError('You are not authorized!')
        
        data = auth.data # get the request data
        
        if not 'emp_id' in data:
            raise ValueError('emp_id is required')
        
        
        con = sql() # connections
        ac = AccessModel(con)

        msg['data'] = ac.getAccess(data['emp_id'])
        msg['ok'] = True
        msg['msg'] = 'Transaction Completed!'

    except Exception as er:
        
        print(er)

    finally:
        if con:
            con.close()

    
    if auth:
        return auth.send(msg)
    
def access_state(req, res):
    auth = None
    msg = {
        'ok': False,
        'msg': None
    }
    con = None

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("you are not authorized!")
        
        data = auth.data
        if not 'code' in data:
            raise ValueError('code is required')
        
        if not 'is_check' in data:
            raise ValueError('is_check is required!')
        
        if not 'emp_id' in data:
            raise ValueError('emp_id is required!')
        
        con = sql()
        
        ac = AccessModel(con)

        role = int(auth.ses.get('role'))
        if not ( role == 1 ):
            if not ac.hasAccess(auth.ses.get('uid'), ['ss-a']):
                msg['msg'] = ac.errorAccess()
                raise ValueError(ac.errorAccess())

        userStore = UserStore(con)
        userStore.updateState(data['emp_id'], data['code'], data['is_check'])
        con.go()
        
        msg['ok'] = True
        msg['msg'] = 'Transaction Completed!'
        

    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)

def save(req, res):
    con = None
    msg = {
        'ok': False,
        'msg': None
    }
    auth = None

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError('You are not authorize!')
        data = auth.data
        
        if not 'name' in data:
            raise ValueError('name is required!')
        
        if not 'gender' in data:
            raise ValueError('gender is required!')
        
        if not 'dob' in data:
            raise ValueError('dob is required')
        
        if not 'username' in data:
            raise ValueError('username is required!')
        
        if not 'password' in data:
            raise ValueError('password is required!')
        
        if not 'type' in data:
            raise ValueError('type is required!')
        
        if not 'uid' in data:
            raise ValueError('uid is required!')
        
        if not 'pos_title' in data:
            raise ValueError('pos_title is required!')
        
        if not 'sign_id' in data:
            raise ValueError('sign id is required!')

        if not match(r'^[0-9a-zA-Z\_\.\-]+$', data['username']):
            msg['msg'] = 'Invalid username it only accept: 0-9 a-z A-Z _ - . characters'
            raise ValueError('Invalid Username')
        
        if len(data['name']) < 4:
            msg['msg'] = 'name is not valid'
            raise ValueError('name is not acceptable')

        if len(data['password']) < 4:
            msg['msg'] = 'password must atleast 4 characters'
            raise ValueError('password must atleast 4 characters')

        con = sql()
        
        ac = AccessModel(con)

        uid = auth.ses.get('uid')

        if not data['sign_id']: data['sign_id'] = None

        if data['type'] == 'insert':
            if not ac.hasAccess(uid, ['ss-b']):
                msg['msg'] = ac.errorAccess()
                raise ValueError(ac.errorAccess())
            
            user_store = UserStore(con)
            ok, m = user_store.createUser(data['name'], 
                                  data['username'], 
                                  data['password'], 
                                  data['gender'], 
                                  data['dob'],
                                  data['pos_title'], data['sign_id'])
            con.go()
            msg['ok'] = ok
            msg['msg'] = m

        elif data['type'] == 'update':
            if not ac.hasAccess(uid, ['ss-c']):
                msg['msg'] = ac.errorAccess()
                raise ValueError(ac.errorAccess())
            
            user_store = UserStore(con)
            ok, m = user_store.updateUser(
                data['uid'],
                data['name'], 
                data['username'], 
                data['password'], 
                data['gender'], 
                data['dob'], 
                data['pos_title'], 
                data['sign_id'])
            
            con.go()

            msg['ok'] = ok
            msg['msg'] =  m


    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)
