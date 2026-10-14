from app.util.json import json_parse
from datetime import datetime
from calendar import monthrange

from app.store.client_store import client_info, RateStore
from app.store.payroll_store import PayrollStore
from app.util.json import json_stringify
from app.util.date import date_time

from app.entity.deduction_entity import PayrollEntity
from app.store.bank_store import EmpBankStore

from app.store.default_ded import DefaultDeduction, DefaultDEductionEntity
from app.util.date import cdate_last_date_r, datetime_implement


class CalOutput:
    def __init__(this):
        
        this.rate_permin      = 0.0
        this.late_amount      = 0.0
        this.undertime_amount = 0.0
        this.absent_amount    = 0.0
        this.total_deduction  = 0.0
        this.gross_amount     = 0.0
        this.net_amount       = 0.0

        this.deduction_com    = 0.0
        this.salary_period    = 0.0
        
        this.deduction_amount = []


def __get_match_bir_table(normal_gross, bracket) -> dict:
    for item in bracket:
        
        if item["to"] < 0.0:
            return item
        
        frm = item["from"]
        to = item["to"]
        
        if normal_gross > frm and  normal_gross <= to:
            return item
        
    return {}

def tax_calculator(salary: float, total_contribution: float, bracket: list, extra_income = 0.0) -> float:

    # convert the to float  

    # computation of the tax is based the bir table


    for x in bracket:
        x['bracket'] = int(x['bracket'])
        x['fix_tax'] = float(x['fix_tax'])
        x['from'] = float(x['from'])
        x['to'] = float(x['to'])
        x['rate_on_excess'] = float(x['rate_on_excess'])

    # ret: float = 0.0

    # normal_gross = (salary) # we must first subtract the gross by the only the contribution not included the loans
    normal_gross = (salary) - (total_contribution * 12)

    bir_table =  __get_match_bir_table(normal_gross, bracket) # the normal gross after it is subtract lookup to the table of the bir to use for the calculation

    percentage = bir_table["rate_on_excess"]

    frm = bir_table["from"]


    fix_tax = bir_table["fix_tax"]

    excess = normal_gross - frm
    
    wtax = (excess * percentage) + fix_tax

    return wtax / 12

def recalculate_tax(con, payroll_info: PayrollEntity, emp_id, uid): # this function use to recalculate
    
    base_ded = payroll_info.deduction_list
    bracket = []
    for x in base_ded:
        if (x["code"].lower() == "tax"):
            bracket = json_parse(x["bracket"])
            break
    
    if not bracket:
        return

    pstore = PayrollStore(con)
    payroll_item = pstore.get_payroll_item(payroll_info.refid, emp_id)
    ded_list = json_parse(payroll_item[0]["ded"])
    
    total_contrib, extra_sal = total_contribution(ded_list, base_ded)

    rate_store = RateStore(con)
    rateinfo = rate_store.get_rate_dict(emp_id = emp_id)

    rate = rateinfo[0]["rate"] * 12

    if rateinfo[0]["rate_type"] != "m":
        return
    
    
            
    wtax = tax_calculator(rate, total_contrib, bracket, extra_sal)
    for x in ded_list:
        if x["code"].lower() == "tax":
            x["value"] = wtax
            break

    # print(total_contrib)
    
    # print(ded_list)
    return {
        "tax": float(f'{wtax:.2f}'),
        "total_contribution": total_contrib
    }
    #pstore.updateDeduction(payroll_info.refid, emp_id, json_stringify(ded_list)) # update the database

    # total_contribution(emp_data)
    # for ded in base_ded:
    #     vcode    = ded["code"].lower()
    #     bracket  = json_parse(ded["bracket"]) if ded["bracket"] else []
        
    #     if vcode == "tax":
    #         if emp_data["rate_type"] == "m": # for supported only for monthly 
    #             wtax = tax_calculator(rate, total_con, bracket)
    #             my_ded_list.append({
    #                 "code": ded["code"],
    #                 "name": ded["name"],
    #                 "value": wtax
    #             })      
    #         break
    # end calculation of the tax
    


def total_contribution(ded, base_ded) -> float:
    total_con = 0.0
    extra_sal = 0.0
    for x in ded:
        if x["code"].lower() == "tax":
            continue
        for b in base_ded:
            if b["code"].lower() == "tax":
                continue
            # this is for not include the government share
            if x["code"] == b["code"] and x["name"] == b["name"] and b["view_only"] == "n" and b["type"] in ("c"):
                total_con += x["value"]
            
            # this include goverment share to be calculated
            # if x["code"] == b["code"] and x["name"] == b["name"] and b["type"] == "c":
            #     total_con += x["value"]
            
            if x["code"] == b["code"] and x["name"] == b["name"] and b["view_only"] == "n" and b["type"] in ("a"):
                extra_sal += x["value"]


    return total_con, extra_sal

def SaveNCalulate(con, payroll_info, emp_id, uid, is_view_only = False) -> tuple: # this is connecto the PayrollStore Class
    base_ded = json_parse(payroll_info["deduction_list"])
    emp_data = client_info(con, emp_id = emp_id) # create the employee id
    
    pstore = PayrollStore(con)
    emp_data = emp_data[0]

    # here the start of auto calculation the deduction
    my_ded_list = []

    # total_con = 0.0
    _from, _to = (payroll_info['from'], payroll_info['to'])
    
    _d_f = _from.split('-')[2] # get the first day of from range
    _t_l = _to.split('-')[2] # get the last day of to range

    _, _, _last = cdate_last_date_r(_from)
    
    type_month = None # 0 for whole month, 1 for first half month, 2 for second half month

    if _d_f == '01' and _t_l == _last:
        type_month = 0 # whole month
    elif _d_f == '01' and _t_l == '15':
        type_month = 1 # first half month
    elif _d_f == '16' and _t_l == _last:
        type_month = 2 # 2nd half month
    


    if payroll_info["atm_info"] == None or payroll_info["atm_info"] == "":
        raise ValueError("Must have a valid atm information")
    
    atm_info = json_parse(payroll_info["atm_info"])

    for ded in base_ded:
        # ded: 'floor': '0', 'ceil': '0', 'value': '0', 'view_only': 'n', 'active': 'y'
        vcode   = ded["code"].lower()
        ded_value = 0.0
        vfloor  = float(ded["floor"])
        vceil   = float(ded["ceil"])
        vvalue  = float(ded["value"])
        vview   = ded["view_only"]
        vactive = ded["active"]

        rate    = emp_data["rate"]

        if emp_data["rate_type"] == "m":
            # applicable for monthly
            if vfloor > 0 and vceil > 0 and vvalue > 0:
                # get the minimum deduction
                min_value = vfloor * vvalue
                max_value = vceil * vvalue
                if rate <= vfloor:
                    ded_value = min_value
                elif rate > vfloor and rate < vceil:
                    ded_value = rate * vvalue
                else:
                    ded_value = max_value

            elif vfloor == 0 and vceil == 0 and vvalue > 0 and vvalue <= 1:
                ded_value = rate * vvalue
            
        # if ded["type"] == "c":
        #     total_con += ded_value
        my_ded_list.append({
            "code": ded["code"],
            "name": ded["name"],
            "value": ded_value
        })

    # calculating the automatic tax
    # for ded in base_ded:
    #     vcode    = ded["code"].lower()
    #     bracket  = json_parse(ded["bracket"]) if ded["bracket"] else []
        
    #     if vcode == "tax":
    #         if emp_data["rate_type"] == "m": # for supported only for monthly 
    #             wtax = tax_calculator(rate, total_con, bracket)
    #             my_ded_list.append({
    #                 "code": ded["code"],
    #                 "name": ded["name"],
    #                 "value": wtax
    #             })      
    #         break
    # end calculation of the tax

    # end here auto calculation of the deduction
    other_info = {}
    emp_bank = EmpBankStore(con)
    bdata = emp_bank.getAccount(emp_id, limit = 1, code = atm_info["code"])
    other_info = { }
    if bdata:
        other_info["acc_type"] = bdata[0][0]
        other_info["acc"] = bdata[0][1]
    else:
        return (False, f"""Error: No Bank Account: {atm_info["code"]} - {emp_data["pref_name"]} {emp_data["fname"]} {emp_data["mname"]} {emp_data["lname"]} {emp_data["ename"]}""")

    # start copy the last value of the payroll
    
    # pStore = PayrollStore(con)

    # last_item = pStore.get_last_item(emp_id, payroll_info["from"], payroll_info["to"])
    
    # last = []
    
    # if last_item:
    #     last = last_item[0]["last_deduction"]

    # for x in my_ded_list:
    #     for y in last:
    #         if x["code"] == y["code"] and x["name"] == y["name"]:
    #             x["value"] = y["value"]
    #             break
    # end  copy the last value of the payroll copy remove since 2024-07-02
    

    # Start getting the deduction code #
    # this prioritise the default set by the user

    # regular half -> 001
    is_half = False
    if payroll_info["type"] == "r" and (type_month == 1 or type_month == 2):
        is_half = True 
        type_month = 0       
    # end regular half -> 001

    dd = DefaultDeduction(con)
    for item in my_ded_list:
        dd_res = dd.get_default(DefaultDEductionEntity(code = item['code'], name = item['name'], emp_id = emp_id))
        
        if dd_res:

            for citem in dd_res:
                type_d = int(citem['type_ded']) # type_d : 1 for first half month, 2 for 2nd half month, 0 for whole month of processing
                if type_month != None:
                    if type_d == type_month:
                        item['value'] = float(citem['value'])
                        break
    # end getting the deduction code   #

    # regular half -> 001
    if payroll_info["type"] == "r" and (is_half):
        for item in my_ded_list:
            item["value"] = item["value"] / 2
    # end regular half -> 001
                    

    if is_view_only == False:
        try:
            pstore.add_item(
                refid = payroll_info["refid"], 
                emp_id = emp_id, 
                emp_info = json_stringify({
                    "p": emp_data["pref_name"], 
                    "f": emp_data["fname"], 
                    "m": emp_data["mname"], 
                    "l": emp_data["lname"], 
                    "e": emp_data["ename"], 
                    "s": emp_data["suf_name"]
                }), 
                start = payroll_info["from"], 
                end = payroll_info["to"],
                compensation = json_stringify({
                    "r": emp_data["rate"], 
                    "t": emp_data["rate_type"], 
                    "w": 0, 
                    "a": 0, 
                    "l": 0, 
                    "u": 0, 
                    "p": emp_data["pos_title"], 
                    "s": emp_data["emp_status"]
                }), 
                deduction = json_stringify(my_ded_list), 
                dept_id = emp_data["dept_id"], 
                dept_info = json_stringify({ "n": emp_data["dept_title"] }), 
                uid = uid, 
                datecreated = date_time(),
                other_info = json_stringify(other_info), payroll_start = payroll_info["from"], payroll_end = payroll_info["to"]
            )
            print(f'Success: {emp_id}')
        except Exception as er:
            print(er)
            print(f'Error: {emp_id} - {emp_data["lname"]},{emp_data["fname"]}')
    
    if is_view_only == True:
        return (True, my_ded_list)

    # deduction [{"code": "PAG-IBIG", "name": "CONTRIBUTION", "value": 100}]
    # compensation
    # {"r": 500, "t": "d", "w": 10, "a": 1, "l": 1, "u": 1, "p": "Office Staff", "s": "j"} 
    # name
    # {"p": "", "f": "Lhia", "m": "", "l": "Reyes", "e": "", "s": ""} # emp_info
    return (True, "No Error")

class CalBasic:
    def __init__(this, rate = 0.0, rate_type = "", no_work_day = 0.0, \
                 late = 0.0, undertime = 0.0, absent = 0.0, ded_base = [], \
                    ded_value = [], payroll_info = {}, is_new = False, \
                        job_type:str = None, nwpd:int = 5):
        
        if not isinstance(nwpd, int): nwpd = int(nwpd)

        # parameters
        this.rate                = rate
        this.rate_type           = rate_type
        this.no_work_day         = no_work_day
        this.late                = late
        this.undertime           = undertime
        this.absent              = absent
        # parameters

        this.deduction_base      = ded_base # list of the deductions from main payroll group
        this.deduction_value     = ded_value
        this.payroll_info        = payroll_info

        this.output              = CalOutput() 

        this.is_new              = is_new
        this.nwpd                = nwpd
        
        if job_type == None: raise ValueError('CalBasic class required ' + 
                                               + 'job_type, job_type is invalid')
        if not job_type in ('r', 'c', 'j'): raise ValueError('Invalid Job type, ' + 
                                                + 'Job type must be r, c, j')

        this.job_type = job_type

        this.constant_day = {
            5: 22, # for 5 days
            6: 26, # for 6 days
            7: 30  # for 7 
        }
        

    def cal_default_deduction(deduction_base):
        # this function is the automatic deduction default,
        # example the deduction of the philhealth and the gsis contribution 
        pass
    
    def _last_month(this, yr, mn):
        return monthrange(yr, mn)[1]

    def calculate(this):
        
        _refid, _from, _to = (this.payroll_info['refid'], this.payroll_info['from'], this.payroll_info['to'])

        if this.rate_type == "d":
           
            # for daily calculation
            if this.rate > 0:
                this.output.rate_permin = (this.rate / 8) / 60

            this.output.late_amount      = round(this.output.rate_permin * this.late, 2) # get the amount of late
            this.output.undertime_amount = round(this.output.rate_permin * this.undertime, 2)
            this.output.absent_amount    = round(this.rate * this.absent)
            

            if datetime_implement('2024-08-07 00:00:00', this.payroll_info['datecreated']):
                __tmp01  = this.output.late_amount + this.output.undertime_amount + this.output.absent_amount
                
                __gross = (this.rate * this.no_work_day)

                this.output.gross_amount     = __gross - __tmp01

                this.output.deduction_com = __tmp01
                this.output.salary_period = __gross

            else:
                this.output.total_deduction  = this.output.late_amount + this.output.undertime_amount + this.output.absent_amount
            
                this.output.gross_amount     = (this.rate * this.no_work_day) - this.output.total_deduction

        elif this.rate_type == "m":
            # checking if the total date
            frm = this.payroll_info["from"].split("-")
            to  = this.payroll_info["to"].split("-")
            last_day = this._last_month(int(frm[0]), int(frm[1]))
            
            gross_rate = 0.0

            daily = this.rate / 22 # basis

            if datetime_implement('2024-11-05 00:00:00', this.payroll_info['datecreated']):
                # print("new implementation")
                # print(this.nwpd)
                if this.nwpd in this.constant_day:
                    daily = this.rate / this.constant_day[this.nwpd]



            if datetime_implement('2024-11-05 00:00:00', \
                                  this.payroll_info['datecreated']) \
                                    and this.job_type == 'j' and this.nwpd > 4:
                # while this is for job order where no work no salary
                gross_rate = daily * this.no_work_day 
            else:
                # this use in regular , and contract of services
                if int(frm[2]) == 1 and int(to[2]) == last_day:
                    # whole month
                    gross_rate = this.rate
                elif ( int(frm[2]) == 1 and int(to[2]) == 15 ) or ( int(frm[2]) == 16 and int(to[2]) == last_day ):
                    #half month
                    gross_rate = this.rate / 2
                else:
                    # other implementation of getting the rate
                    # example if getting the daily rate
                    pass

            # ############# for other the monthly  #####################
            # the next features where
            # if the client is monthly and it is contractual or regular
            # then it should be full pay minus the late + absent + undertime 
            # the scanning of the qrcode if he or she is a contract auto add the undertime and late
            # for automated computation



            this.output.salary_period = gross_rate
            # calculation for montly
            # set the gross to base_rate
            if daily > 0:
                this.output.rate_permin  = (daily / 8.0) / 60.0

            this.output.late_amount      = round(this.output.rate_permin * this.late, 2) # get the amount of late
            this.output.undertime_amount = round(this.output.rate_permin * this.undertime, 2)
            this.output.absent_amount    = round(daily * this.absent, 2) # get the absent           
            if datetime_implement('2024-08-07 00:00:00', this.payroll_info['datecreated']):
                __tmp01  = this.output.late_amount + this.output.undertime_amount + this.output.absent_amount
                this.output.gross_amount     = gross_rate - __tmp01

                this.output.deduction_com = __tmp01
            else:
                this.output.total_deduction  = this.output.late_amount + this.output.undertime_amount + this.output.absent_amount
                this.output.gross_amount     = gross_rate - this.output.total_deduction
            # end calculation for monthly


        
        # get the net
        this.output.net_amount = this.output.gross_amount

        # here is the deduction calculation
        for x in this.deduction_base:
            for y in this.deduction_value:
                
            
                if (x["code"] == y["code"] and x["name"] == y["name"] and x["view_only"] == "n" and x["active"] == "y"):
                    # where x is the base 
                    # and y is the custom value of the x base 
                    

                    if x['type'] == 'a':
                        # this is the additional of the compensation such like the
                        # clothing, pera and aca
                        y_value = float(y["value"])
                        # for gross amount
                        this.output.gross_amount += y_value # example RATA, PERA, OT
                        # for net amount
                        this.output.net_amount += y_value
                        continue
                    # _floor = float(x["floor"])
                    # _ceil  = float(x["ceil"])
                    # x_value = float(x["value"])

                    y_value = float(y["value"])
                    
                    this.output.total_deduction += y_value
                    this.output.net_amount      -= y_value

                    
        # end of the deduction calculation
        
        # checking if payroll exists
        if this.is_new: 
            print('new ')
        # end checking payroll existence

        return this.output

def payslip(data: dict, deduction_base = [], payroll_info = {}) -> dict:
    # this function use to get the payslip
    slip = {

    }
    # calculation basic rate

    # extract the employee information
    emp_info = json_parse(data['emp_info'])
    com = json_parse(data['compensation'])
    deduction = json_parse(data['deduction'])
    dept_info = json_parse(data['dept_info'])
    other = json_parse(data['other_info'])

    # compensation
    # get the rate
    rate = 0.0
    rate_type = '' # d daily, m for monthly, y for yearly h for hourly
    
    work = 0.0 # total day of work
    absent = 0.0 # total absent in day format
    late = 0.0 # total late in minutes
    undertime = 0.0 # total undertime in minute

    # print(payroll_info["deduction_list"], type())
    base_deduction = json_parse(payroll_info["deduction_list"]) if isinstance(payroll_info["deduction_list"], str) else payroll_info["deduction_list"]

    if 'r' in com:
        rate = float(com['r'])
    
    if 't' in com:
        rate_type = com['t']

    if 'w' in com:
        work = float(com['w'])

    if 'l' in com:
        late = float(com['l'])

    if 'a' in com:
        absent = float(com['a'])

    if 'u' in com:
        undertime = float(com['u']) 

    rtype = {
        'm': 'Monthly',
        'd': 'Daily',
        'h': 'Hourly'
    }

    pos_title = com['p'] if 'p' in com else ''
    mname = emp_info["m"][0] + '.' if emp_info["m"] else ''
    suffix = ', ' + emp_info['s'] if emp_info['s'] else ''

    nwpd = 5
    if 'n' in com and com['n']:
        nwpd = int(com['n'])

    job_type = com['s'] # like, j, c, r, means, job order, contract of server, regular

    ###### get the total contribution from the government
    total_gov_share = 0.0
    for ded_item in deduction:
        for base_item in base_deduction:
            if base_item["code"] == ded_item["code"] and base_item["name"] == ded_item["name"]:
                if base_item["type"] == "c" and base_item["view_only"] == "y":
                    total_gov_share += round(float(ded_item["value"]), 2)
    ###### end get the total contribution from the government,, this is included in the ob-r
    # print(total_gov_share)
    # info and compensation
    slip["gov_share"]    = total_gov_share
    slip["com"]          = com
    slip['serial_no']    = ''
    slip["from"]         = data["start"]
    slip["to"]           = data["end"]
    slip['name']         = f'{emp_info["l"]}, {emp_info["p"]} ' + \
        f'{emp_info["f"]} {emp_info["e"]} {mname}{suffix}'.upper()
    slip['position']     = pos_title.upper()
    slip['employee_no']  = data["emp_id"]
    slip['salary']       = f'{rate:,.2f}/{rtype[rate_type]}'
    slip["salary_type"]  = rate_type
    slip['no_work_day']  = work
    slip['absent']       = 0.0
    slip['late']         = 0.0
    slip['undertime']    = 0.0
    slip['gross']        = 0.0
    slip['dept_info']    = dept_info
    
    slip['deduction']    = deduction # list of the deductions
    
    slip["total_ded"]    = 0.0 

    slip['net']          = 0.0  
    
    slip['account']      = '' # bank account number
    slip['account_type'] = ''
    slip['nwpd']         = nwpd
    
    if other: 
        if 'acc' in other: slip['account'] = other['acc']
        if 'acc_type' in other: slip['account_type'] = other['acc_type']
    # if rate_type equal to daily
    calBasic = CalBasic(rate, rate_type, work, late, undertime, absent, \
                        deduction_base, deduction, payroll_info,\
                              nwpd = nwpd, job_type = job_type)
    result = calBasic.calculate()
    # end calBasic

    slip['deduction_com'] = result.deduction_com
    slip['salary_period'] = round(result.salary_period, 2)

    slip['total_ded']    =  result.total_deduction

    slip['late']      = result.late_amount # get the amount of late
    slip['undertime'] = result.undertime_amount # get the amount of undertime
    slip['absent']    = result.absent_amount # get the amount of  absent

    # initial total deduction
    slip["total_ded"] = round(result.total_deduction, 2)
    
    # get the gross earned !
    slip['gross']     = round(result.gross_amount, 2)
    

    slip['net']       = round(result.net_amount, 2) # this is an initial net

        
    




    return slip