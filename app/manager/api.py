from app.entity.http_entity import ProcessEntity
from app.lib.net import http

from app.model.dept_model import DeptModel
from app.model.position_model import PositionModel
from app.model.rate_model import RateModel
from app.store.bank_store import EmpBankStore
from app.store.default_ded import DefaultDEductionEntity, DefaultDeduction
from app.util.date import cdate_last_date_r
from app.util.json import json_parse

from app.model.payroll_model import PayrollModel, PayrollItemInterface
from app.store.client_store import ClientStore
from app.store.payroll_store import PayrollStore
from app.store.system_store import sys_info
from app.model.client_model import ClientModel, ClientEntity

from app.model.user_model import AccessModel
from app.util.auth import Auth
from app.lib.sql import sql
from app.util.payroll_calulator import SaveNCalulate

from app.store.dtr_store import DtrStore
import json


def api_hrms_dtr_general_info(req, res):
    con, msg = None, { 'ok': False, 'msg': 'HRMS Server Offline!', 'data': [] }

    try:
        auth = Auth(req)
        if not auth.isAuth: 
            msg['msg'] = 'You are not authorezed!'
            raise ValueError('You are not authorized!')
        payload =  auth.data

        if not 'qrcode' in payload: raise ValueError('qrcode is required!')

        qrcode = payload['qrcode']

        if not qrcode: raise ValueError('qrcode is not valid!')

        con = sql()
        ss = sys_info(con)
        con.close() # avoid database lock

        dtr_data = http(f'{ss["hr_ip"]}/api/shared/dtr', { "qrcode": qrcode })
        rdata = json_parse(dtr_data)

        data = rdata["data"]
    
        if len(data) == 0: 
            msg['msg'] = 'no data found in dtr!'
            raise ValueError('no data found in qrcode')


        header = data["header"]

        salary, salary_type = (header["salary"][0], header["salary"][1])
        pay_type, pos_title = (header["pay_type"], header["pos_title"]) # it is c: constr

        if salary_type == 'a':
            salary_type = 'm'
            salary = salary / 12
            header['salary'] = (salary, salary_type)

        hr_id = header["emp_id"]
        _range = header["range"]
        _total_late = header["total_late"]
        _total_undertime = header["total_undertime"]
        _total_work = float(header["total_work"]) / 480.0
        
        con.open()

        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['hs-1']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())
        

        # load the client by using the hr_id
        client_store = ClientStore()
        client_store._setConnection(con)
        c_data = client_store.info(hr_id)

        if not c_data:
            msg["msg"] = "Client not found or id of hr system not register"
            raise ValueError("Not found")

        emp_id = c_data[0][0]

        header['payroll_emp_id'] = emp_id

        # update the salary of the employee
        rate_model = RateModel(con, emp_id)
        rate_model.create_rate(salary, salary_type)

        # update position Information
        pos_model = PositionModel(con, auth.ses.get("uid"))
        pos_model.create_position(emp_id, pos_title, pay_type)

        #update the department history
        
        dept_model = DeptModel(con, auth.ses.get("uid"))
        ok = dept_model.update_dept2(emp_id, header["dept"]["code"])
        if not ok:
            msg["msg"] = f"""No department code: {header["dept"]["code"]}"""
            raise ValueError("No Department in payroll register")
        
        ebs = EmpBankStore(con)

        bank_account = ebs.getAccount(emp_id = emp_id, limit = 1)
        
        if not bank_account:
            msg["msg"] = "No Bank Account set!"
            raise ValueError("No Bank Account set")
        

        lname2, fname2, mname2 = header["name2"]

        has_emp = con.get("select id from client where lower(fname) = ? and lower(lname) = ?", (fname2.lower(), lname2.lower()))
     
        if not has_emp:
            msg["msg"] = "HRMS and Payroll dont have similar data please check the payroll system employee registered!"
            raise ValueError(f"HRMS and Payroll dont have similar data please check the payroll system employee registered!")

        con.go() # final commit

        # creating a transaction of the dtr


        msg['data'] = data
        msg['msg'] = 'Transaction Completed!'
        msg['ok'] = True


    except Exception as er:
        print(er)
    finally:
        if con: con.close()

    if auth: return auth.send(msg)


def api_hrms_dtr(req, res):
    pro = ProcessEntity()
    try:
        pro.createAuth(req)
        if not pro.auth.isAuth:
            raise ValueError("Invalid")
        
        data = pro.auth.data
        if not "qrcode"in data:
            raise ValueError("qrcode is required")
        
        if not "refid" in data:
            raise ValueError("refid is required!")
        
        refid = data["refid"]

        
        
        qrcode = data["qrcode"]
        
        pro.openConnection()    
        ss = sys_info(pro.con)
        pro.con.close() # avoid database lock

        dtr_data = http(f'{ss["hr_ip"]}/api/shared/dtr', {"qrcode": qrcode})

        
        rdata = json_parse(dtr_data)

        data = rdata["data"]
        
        header = data["header"]

        salary, salary_type = (header["salary"][0], header["salary"][1])
        pay_type, pos_title = (header["pay_type"], header["pos_title"]) # it is c: constract, j job order, r for regular
        # update the salary
        

        if salary_type == 'a':
            pro.msg['msg'] = 'YEARLY TYPE OF SALARY IS NOT YET SUPPORTED IN THE PAYROLL SYSTEM'
            raise ValueError('Annual salary is not yet supported in the payroll system!')

        hr_id = header["emp_id"]
        _range = header["range"]
        _total_late = header["total_late"]
        _total_undertime = header["total_undertime"]
        _total_work = float(header["total_work"]) / 480.0
        

        if header["valid"][0] == False:
            pro.msg["msg"] = "Invalid DTR, maybe the contract has changed!, or maybe the employee has not been renew or the renewal is cancelled! please ask the HR department for the reason!"
            raise ValueError("Invalid DTR")
        
        # print()
        # print()
        # print(hr_id)
        # print(_range)
        # print(_total_late)
        # print(_total_undertime)
        # print(_total_work)
        pro.openConnection()
        
        ac = AccessModel(pro.con)
        if not ac.hasAccess(pro.auth.ses.get('uid'), ['hs-1']):
            pro.msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())
        


        # load the client by using the hr_id
        client_store = ClientStore()
        client_store._setConnection(pro.con)
        c_data = client_store.info(hr_id)

        if not c_data:
            pro.msg["msg"] = "Client not found or id of hr system not register"
            raise ValueError("Not found")
        

        emp_id = c_data[0][0]
        # update the salary of the employee
        rate_model = RateModel(pro.con, emp_id)
        rate_model.create_rate(salary, salary_type, nwpd = data['header']['no_work_day'])

        # update position Information
        pos_model = PositionModel(pro.con, pro.auth.ses.get("uid"))
        pos_model.create_position(emp_id, pos_title, pay_type)

        #update the department history
        
        dept_model = DeptModel(pro.con, pro.auth.ses.get("uid"))
        ok = dept_model.update_dept2(emp_id, header["dept"]["code"])
        if not ok:
            pro.msg["msg"] = f"""No department code: {header["dept"]["code"]}"""
            raise ValueError("No Department in payroll register")
        
        proll = PayrollStore(pro.con)

        pinfo = proll.info(refid)

        if not pinfo["atm_info"]:
            pro.msg["msg"] = "No default A.T.M account type setup in the payroll, this error cause by new update of the system, Please contact the developer for this message!"
            raise ValueError("No default A.T.M account type setup in the payroll, this error cause by new update of the system, Please contact the developer for this message!")

        atm_info = json_parse(pinfo["atm_info"])

        if atm_info == None:
            pro.msg["msg"] = f"No ATM Information set in payroll, please update the payroll information or contact the payroll administrator!"
            raise ValueError("Not Atm Information")
        
        ebs = EmpBankStore(pro.con)

        bank_account = ebs.getAccount(emp_id = emp_id, limit = 1, code = atm_info["code"])
        
        if not bank_account:
            pro.msg["msg"] = f"""No Bank Account set! for {atm_info["code"]} - {atm_info["name"]}"""
            raise ValueError("No Bank Account set")
        

        lname2, fname2, _ = header["name2"]

        has_emp = pro.con.get("select id from client where lower(fname) = ? and lower(lname) = ?", (fname2.lower(), lname2.lower()))
     
        if not has_emp:
            pro.msg["msg"] = "HRMS and Payroll dont have similar data please check the payroll system employee registered!"
            raise ValueError(f"HRMS and Payroll dont have similar data please check the payroll system employee registered!")

        

        # frm = pinfo["from"]
        # to = pinfo["to"]

        info_status = pinfo['status']
        if info_status:
          info_status = json_parse(info_status)
          if info_status[len(info_status) - 1]['step'] != 0:
            pro.msg['msg'] = 'The Payroll already closed!'
            raise ValueError('Already locked the payroll')


        # if not (frm == _range[0] and to == _range[1]):
        #     pro.msg["msg"] = "Sorry the dtr you passed dont match the date of the payroll, please reprint the dtr"
        #     raise ValueError(pro.msg)
        
        # added on july 5, 2024
        # total_con = 0.0
        # _from, _to = (frm, to)
        
        # _d_f = _from.split('-')[2] # get the first day of from range
        # _t_l = _to.split('-')[2] # get the last day of to range

        # _, _, _last = cdate_last_date_r(_from)
        
        # type_month = None # 0 for whole month, 1 for first half month, 2 for second half month
        # if _d_f == '01' and _t_l == _last:
        #     type_month = 0 # whole month
        # elif _d_f == '01' and _t_l == '15':
        #     type_month = 1 # first half month
        # elif _d_f == '16' and _t_l == _last:
        #     type_month = 2 # 2nd half month
        # end july 5, 2024


        # ded_list = json_parse(pinfo["deduction_list"])

        deduction_value = []
        



        # dd = DefaultDeduction(pro.con)
        
        # for item in ded_list:
        #     # in the future this will be auto calculated
        #     # Start getting the deduction code #
        #     # this prioritise the default set by the user
        #     # added in july 5, 2024
        #     default_value = 0.0
        #     dd_res = dd.get_default(DefaultDEductionEntity(code = item['code'], name = item['name'], emp_id = emp_id), limit = 1)
        #     if dd_res:
        #         type_d = int(dd_res[0]['type_ded']) # type_d : 1 for first half month, 2 for 2nd half month, 0 for whole month of processing
        #         if type_month != None and type_d == type_month:
        #             default_value = float(dd_res[0]['value'])
        #     # end getting the deduction code   #
        #     # end future
        #     # end july 5, 2024
            
        #     deduction_value.append({
        #         "code": item["code"],
        #         "name": item["name"],
        #         "value": default_value
        #     })

        ok, ded1 = SaveNCalulate(pro.con, pinfo, emp_id, pro.auth.ses.get("uid"), True);

        if not ok:
            pro.msg["msg"] = "Invalid Transaction"
            raise ValueError("Invalid Transaction")
        deduction_value = ded1



        payrollModel = PayrollModel(pro.con)

        is_ok, rmsg = payrollModel.addItem(PayrollItemInterface(
            emp_id = emp_id,
            late = 0,
            work = _total_work,
            payroll_refid = refid,
            absent = 0.0,
            undertime = 0,
            deduction_value = deduction_value,
            is_update = False,
            uid = pro.auth.ses.get("uid"),
            from_t = _range[0], # from dtr
            to_t = _range[1] # to dtr
        ))


            
        # added this on july 5, 2024
        #is_ok, rmsg = SaveNCalulate(con = pro.con, payroll_info = pinfo, emp_id = emp_id, uid = pro.auth.ses.get('uid'), num_day_work = _total_work)
        # end added here on july 5, 2024
        

        # load auto
        pro.msg["ok"] = is_ok
        pro.msg["msg"] = rmsg
        pro.msg["data"] = {
            "emp_id": emp_id,
            "refid": refid,
            "work": _total_work
        }
         
        pro.con.go()
        # end auto
    except Exception as er:
        print(er)
        # pro.msg["msg"] = "Something went wrong"
    finally:
        pro.close()

    return pro.send()




def check_sync_data(pro, emp_data): 
    # this function search everything matches in between payroll and Human reasource management system
    con = pro.con
    
    client_store = ClientStore(con)
    cnt = 0
    cnt2 = 0
    for item in emp_data:
        # checking everything to the database for validation
        fname = item["fname"]
        mname = item["mname"]
        lname = item["lname"]
        ename = item["ename"]
        
        data = client_store.check_a(fname, lname)
        if data:
            found = data[0]
            if found:
                item["found"] = True
        else:
            # not found
            pass

        data2 = client_store.check_b(fname, lname, ename)
        if data2:
            cnt2 += 1

    

def api_hrms_employee(req, res):
    pro = ProcessEntity()
    try:
        pro.createAuth(req)
        if not pro.auth.isAuth:
            raise ValueError("You are not authorized!")
        data = pro.auth.data
        pro.openConnection()    
        ss = sys_info(pro.con)
        pro.con.close() # avoid database lock
        emp_data = ""

        is_no_access = False
        
        if not 'from' in data:
            pro.msg['msg'] = 'range from is required!'
            raise ValueError('from is required')
        
        if not 'to' in data:
            pro.msg['msg'] = 'range to is required!'
            raise ValueError('to is required!')
        
        if not ( data['from'] or data['to'] ):
            pro.msg['msg'] = 'range from and range to must not empty'
            raise ValueError('from and to must not empty')
        

        try:
            emp_data = str(http(f'{ss["hr_ip"]}/api/shared/all/employee', { 
                'from': data['from'],
                'to': data['to']
            }))
            emp_data = json_parse(emp_data)
            
            pro.openConnection()

            ac = AccessModel(pro.con)
            if not ac.hasAccess(pro.auth.ses.get('uid'), ['hs-2']):
                pro.msg['msg'] = ac.errorAccess()
                is_no_access = True
                raise ValueError(ac.errorAccess())

            check_sync_data(pro, emp_data["data"])
            pro.close()

            pro.msg["data"] = emp_data["data"]
            pro.msg["ok"] = True
            pro.msg["msg"] = emp_data["msg"]
        except Exception as er:
            print(er)
            if not is_no_access:
                pro.msg["msg"] = "Sorry! there is a problem connecting to HR System, please check the Internet connection"

    except Exception as er:
        print(er)
        pro.msg["msg"] = "Sorry we cant process your request this time"
    finally:
        if pro.con:
            pro.con.close()

    return pro.send()

def saveClient(con, data: dict, uid) -> bool: # this mehtod must be in the model for now  it is in the controller
    client: ClientEntity = ClientEntity()
    client.pref_name = data["pref_name"]
    client.fname = data["fname"]
    client.mname = data["mname"]
    client.lname = data["lname"]
    client.ename = data["ename"]
    client.suf_name = data["suf_name"]
    client.dob = data["bod"]
    client.gender = data["gender"]
    client.hr_id = data["no"]
    client.uid = uid
    client.id = None
    client.addr = ""
    # {'no': 1620, 'pref_name': None, 'fname': 'MARJON', 'mname': 'MANGINDO', 'lname': 'CAJOCON', 'ename': '', 'suf_name': None, 'gender': 'm', 'bod': '1996-03-31', 'dept_info': '{"id": 1001, "code": "HR", "name": "Human Resource"}', 'code_t': 'f22e0020a86b266ed4097d54e89a3f7f00d20662', 'start_t': '2024-01-01', 'end_t': '2024-12-31', 'contact': '{"email": "marjoncajocon08@gmail.com", "phone": "+639636382382"}', 'item_no': '6', 'pos_title': 'ADMINISTRATIVE AIDE III(UTILITY WORKER II)', 'rate': 158520, 'rate_type': 'a', 'emp_status_id': 8, 'stat_code': 'per', 'stat': 'Permanent', 'work_left': 298, 'work_status': 'active', 'found': True, 'token': 'ses17096259521194820007279359'}
    client_model = ClientModel()
    client_model._setConnection(con)
    return client_model.addClient(client)

def saveRate(data: dict):
    print(data)

def savePosition(data: dict):
    print(data)

def api_hrms_save(req, res):
    pro = ProcessEntity()
    try:
        pro.createAuth(req)
        if not pro.auth.isAuth:
            raise ValueError("You are not autorized")
        data = pro.auth.data
        pro.openConnection()
        ac = AccessModel(pro.con)
        if not ac.hasAccess(pro.auth.ses.get('uid'), ['hs-3']):
            pro.msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())

        ok = saveClient(pro.con, data, pro.auth.ses.get("uid"))
        pro.con.go()
        pro.close()
        if ok:
            pro.msg["ok"] = True
            pro.msg["msg"] = "Transaction Completed!"
        else:
            pro.msg["msg"] = "Transaction Failed! Already exists"

    except Exception as er:
        print(er)
    finally:
        pro.close()

    return pro.send()

def sync_all_id(req, res):
    con = None
    auth = None
    msg = {
        'ok': False,
        'msg': None
    }

    try:

        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError('You are not authorized!')
        
        data = auth.data # this is the data from the hrms
        con = sql()

        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['hs-4']):
            msg['msg'] = ac.errorAccess()
            raise ValueError(ac.errorAccess())
        
        cstore = ClientStore(con)
        total = 0
        for x in data:
            f = cstore.check_c(x['fname'], x['lname']) # update all the same name
            for cc in f:
                client_id = cc[0]
                hr_id = x['emp_id']
                cstore.updateHRId(client_id, hr_id)
                total += 1

        con.go()
        msg['ok'] = True
        msg['msg'] = f'Transaction Completed! {total} no. of employee updated!'

    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()

    if auth:
        return auth.send(msg)