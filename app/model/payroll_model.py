from app.store.payroll_store import PayrollStore
from app.util.json import json_stringify, json_parse
from app.store.client_store import ClientStore, RateStore, PositionStore, DeptInfoStore
from app.util.date import date_time, cdate_last_date_r
from app.store.bank_store import EmpBankStore
from app.store.default_ded import DefaultDeduction


class PayrollItemInterface:
    def __init__(this, 
                    emp_id = None,
                    late = None,
                    work = None,
                    payroll_refid = None,
                    absent = None,
                    undertime = None,
                    deduction_value = None,
                    is_update = None,
                    uid = None,
                    from_t = None,
                    to_t  = None
                ):
        this.emp_id = emp_id
        this.late = late
        this.work = work
        this.payroll_refid = payroll_refid
        this.absent = absent
        this.undertime = undertime
        this.deduction_value: list = deduction_value
        this.is_update = is_update
        this.uid = uid
        this.from_t = from_t
        this.to_t  = to_t

# this is a reusable model
class PayrollModel:
    def __init__(this, con = None):
        this.con = con

    def addItem(this, payroll_item: PayrollItemInterface):
        con = this.con

        is_update     = payroll_item.is_update

        emp_id        = payroll_item.emp_id
        late          = payroll_item.late
        work          = payroll_item.work
        payroll_refid = payroll_item.payroll_refid
        absent        = payroll_item.absent
        undertime     = payroll_item.undertime

        # get emp_data
        payroll_store = PayrollStore(con)
        payroll_info = payroll_store.info(payroll_refid)

        if not payroll_info: return (0, 'Payroll is invalid!')   
        
        client = ClientStore()
        client._setConnection(con)
        client_data = client.get(emp_id)

    
        if not client_data: return (0, 'employee not found!')
        
        emp_info = {
            'p': client_data['pref_name'],
            'f': client_data['fname'],
            'm': client_data['mname'],
            'l': client_data['lname'],
            'e': client_data['ename'],
            's': client_data['suf_name']
        }
        
        # get the rate information
        rate_store = RateStore(con)
        rate_data = rate_store.get_rate_dict(emp_id, 1)  

        if not rate_data: return (0, 'The rate is not set, please update the rate information!')
            
        pos_store = PositionStore(con)
        pos_data = pos_store.get_position_dict(emp_id, 1)
        

        if not pos_data: return (0, 'Position need to setup, please update the employee position!')
        
        payroll_type = payroll_info['type']

        if pos_data[0]['status'] != payroll_type: return (0, 'You cant add it here! Transaction Failed!')
            
        compensation = {
            'r': rate_data[0]['rate'],
            't': rate_data[0]['rate_type'],
            'w': work,
            'a': absent,
            'l': late,
            'u': undertime,
            'p': pos_data[0]['title'],
            's': pos_data[0]['status'],
            'n': rate_data[0]['nwpd']
        }

        dept_info_store = DeptInfoStore(con)
        dept_data = dept_info_store.get_dept_dict(emp_id, 1)
        
        if not dept_data: return (0, 'Employee Department must setup first!')
            
            
        dept_info =  {
            'n': dept_data[0]['dept_name']
        }

        
        # deduction
        deduction = payroll_item.deduction_value # list of the deduction in the future
        # sample deduction
        # { 'code': 'ps' }
        atm_info = json_parse(payroll_info["atm_info"]) \
            if payroll_info["atm_info"] != None \
                or payroll_info["atm_info"] != "" else None
        
        _code = None
        if atm_info:
            _code = atm_info["code"]

        emp_bank = EmpBankStore(con)
        bdata = emp_bank.getAccount(emp_id, code = _code)
        other_info = { }
        if bdata:
            other_info["acc_type"] = bdata[0][0]
            other_info["acc"] = bdata[0][1]
        else:
            raise ValueError("Bank account is not found!")
        # acc_no: acc_type
        # load the account number

        q_res = {}


        if not is_update:
            # add item

            # checking if perhalf or second half
            # fyr, fm, fd = payroll_info['from'].split('-')
            # tyr, tm, td = payroll_info['to'].split('-')

            # lyr, lm, ld = cdate_last_date_r(payroll_info['to'])

            # d_type = ''
            # if fd == '16' and td == ld:
            #     #second half
            #     d_type = '2'
            # elif fd == '01' and td == '15':
            #     d_type = '1' # 1st half
            # elif fm == '01' and td == ld:
            #     d_type = '0'
            
            


            # de = DefaultDeduction(con = con)
            # d = de.get_default_by_emp_id(emp_id = emp_id)
            
            # # checking if there is a default deductions
            # for item in deduction:
            #     # setting default value here like sss or other information
            #     #print(item)
            #     for ditem in d:
            #         if item['code'] == ditem['code'] \
            #             and item['name'] == ditem['name']:
            #             #print(ditem)
            #             if d_type == ditem['type_ded']:
            #                 item['value'] = float(ditem['value'])

            
            if not (payroll_item.from_t and payroll_item.to_t):
                payroll_item.from_t = payroll_info["from"]
                payroll_item.to_t =  payroll_info["to"]

                # check the bound of the date

            q_res =  payroll_store.add_item(
                payroll_refid, 
                emp_id, 
                json_stringify(emp_info),
                payroll_item.from_t,
                payroll_item.to_t,
                json_stringify(compensation),
                json_stringify(deduction),
                dept_data[0]['dept_id'],
                json_stringify(dept_info),
                payroll_item.uid,
                date_time(),
                json_stringify(other_info),
                payroll_start = payroll_info["from"],
                payroll_end = payroll_info["to"]
            )
            
        else:
            q_res = payroll_store.update_item(
                payroll_refid, 
                emp_id, 
                json_stringify(emp_info),
                payroll_item.from_t,
                payroll_item.to_t,
                json_stringify(compensation),
                json_stringify(deduction),
                dept_data[0]['dept_id'],
                json_stringify(dept_info),
                payroll_item.uid,
                date_time()
            )
            
        return (q_res["ok"], q_res["msg"])