from app.lib.sql import sql
from app.store.default_ded import DefaultDeduction
from app.util.date import date_time, cdate_last_date_r
from app.util.json import json_stringify, json_parse

from app.store.deduction_store import DeductionStore
from app.store.signatory_store import SignatoryStore
from app.util.date import date_normal
from app.store.global_store import create_history
from app.entity.deduction_entity import PayrollEntity
from typing import List
from app.util.json import json
from app.store.payroll_default_store import DefaultPayrollSignatoryStore
from app.store.user_store import UserStore
from app.store.bank_store import BankStore, EmpBankStore



class Search:
  def __init__(this):
    this.search      = ""
    this.dept_id     = ""
    this.status_type = "" # jo, contract, and regular

class PayrollStore:
  def __init__(this, con: sql = None):
    this.__con: sql = con


  def recompute_payroll(this, refid):
    info = this.info(refid = refid)
    if not info:
      return (False, "Payroll not found!")
    from_t, to_t = (info["from"], info["to"])

    

    # this logic found in PayrollModel->addItem 
    # this message in the future must be dry, for now this is not dry yet

    fyr, fm, fd = from_t.split('-')
    tyr, tm, td = to_t.split('-')

    lyr, lm, ld = cdate_last_date_r(to_t)

    d_type = ''
    if fd == '16' and td == ld:
        #second half
        d_type = '2'
    elif fd == '01' and td == '15':
        d_type = '1' # 1st half
    elif fm == '01' and td == ld:
        d_type = '0'
    # end not dry

    status = json_parse(info["status"]) if info["status"] else None
    if status == None or status[len(status) - 1]["step"] == 0:
      pitems = this.__con.get("select emp_id, deduction from payroll_item where payroll_refid = ?", (refid, ))
      
      for ditem in pitems:
        emp_id = ditem[0]
        deduction = json_parse(ditem[1])

        de = DefaultDeduction(con = this.__con)
        d = de.get_default_by_emp_id(emp_id = emp_id)
        
        # checking if there is a default deductions
        for item in deduction:
          # setting default value here like sss or other information
          #print(item)
          for ditem in d:
            if item['code'] == ditem['code'] \
              and item['name'] == ditem['name']:
              #print(ditem)
              if d_type == ditem['type_ded']:
                item['value'] = float(ditem['value'])


        this.__con.commit('update payroll_item set deduction = ? where payroll_refid = ? and emp_id = ?', (
          json_stringify(deduction), refid, emp_id,
        ))
      
      return (True, "Successfully Recomputed!")
    else:
      return (False, "You Cant recompute this payroll! check the payroll status")

  

  def change_atm(this, refid, atm):
    ret = { "ok": False, "msg": "Invalid ", "err": [] }

    info = this.info(refid = refid)
    if not info:
      return (False, "Payroll not found!")
    
    status = json_parse(info["status"]) if info["status"] else None

    if status == None or status[len(status) - 1]["step"] != 5:
      
      # get the bank informatino
      bank = BankStore(con = this.__con)
      b = bank.getBank(code = atm)
      if not b:
        return (False, "Invalid atm code")
      code, name, regex = b[0], b[1], b[2]
      # format
      atm_info = {"code": code, "name": name, "regex": regex}

      
      # update the payrooll bank
      this.__con.commit("update payroll set atm_info = ? where refid = ?", (
        json_stringify(atm_info), refid,        
      ))
      
      # update the payroll item 
      # format: {"acc_type": "DBP", "acc": "5064397082"}
      pitems = this.__con.get("select emp_id, emp_info from payroll_item where payroll_refid = ?", (refid, ))
      
      # checking all if there is an bank account for the new atm

      emp_bank = EmpBankStore(con = this.__con)
      
      # other_info = { }
      # if bdata:
      #     other_info["acc_type"] = bdata[0][0]
      #     other_info["acc"] = bdata[0][1]

      error = []
      for pitem in pitems:
        emp_id = pitem[0]
        emp_info = json_parse(pitem[1])

        bdata = emp_bank.getAccount(emp_id, code = atm)
        if not bdata:
          error.append(f'NO {atm} ACCOUNT - {emp_info["l"]} {emp_info["f"]} {emp_info["m"]} {emp_info["l"]}'.upper())
        
        if bdata:
          other_info = {}
          other_info["acc_type"] = bdata[0][0]
          other_info["acc"] = bdata[0][1]

          this.__con.commit('''update payroll_item 
                            set other_info = ? 
                            where payroll_refid = ? and emp_id = ?''', ( 
                              json_stringify(other_info), 
                              refid, 
                              emp_id,  
                            ))
      
      if error:

        ret["msg"] = "List of no account!"
        ret["err"] = error
        return ret

      ret["msg"] = "Transaction Completed"
      ret["ok"] = True

      
    return ret


  def digital_approve(this, refid, dept_id, uid = None):
    con = this.__con

    payroll_info = this.info(refid)
    remark_status = payroll_info['status']

    sign_list = json_parse(payroll_info["signatory_list"])

    # load the custom sign_list
    is_default = False
    dd = DefaultPayrollSignatoryStore(con = con)
    c_sign = dd.load(refid, dept_id if dept_id else 'all')
    if c_sign:
      sign_list = json_parse(c_sign[0]['data'])
      is_default = True

    user_store = UserStore(con)

    # Sign key checking
    is_ok = False
    sign_key = user_store.sign_key(uid)
    for s_item in sign_list:
      if 'sign_key' in s_item:
        if sign_key == s_item['sign_key']:
          is_ok = True
          break
          # action.append({
          #   'sign_key': s_item['sign_key'],
          #   'sign_val': s_item['sign_val'],
          #   'sign_date': s_item['sign_date'],
          #   'action': s_item['c'],
          #   'name': s_item['n'],
          #   'pos': s_item['p']
          # })
    # end sign key checking
    if not is_ok: return (False, 'Invalid Transaction')
    
    if not is_default:
      # no custom signatory
      # just update the payroll signlist
      for _sign in sign_list:
        if _sign['sign_key'] == sign_key:
          if _sign['sign_val']:
            return (False, 'Already Approved!')

          _sign['sign_val'] = sign_key
          _sign['sign_date'] = date_time()

      con.commit('update payroll set signatory_list = ? where refid = ?', (
        json_stringify(sign_list),
        refid,
      ))      


    else:
      # for custom signatory
      for _sign in sign_list:
        if _sign['sign_key'] == sign_key:
          if _sign['sign_val']:
            return (False, 'Already Approved!')

          _sign['sign_val'] = sign_key
          _sign['sign_date'] = date_time()

      dept_id = dept_id if dept_id else "all"
      con.commit('update custom_payroll_signatory set data = ? where refid = ? and dept_id = ?', ( json_stringify(sign_list), refid, dept_id,  ))
    
    # checking of the last signatory

    # code started here
  
    final_sign_ok = True
    for n in sign_list:
      if n['sign_val'] == None or n['sign_val'].strip() == '':
        final_sign_ok = False
        break
    
    # if the final_sign is okay
    # or all the signatory is already done, then automatic to close the payroll review
    if final_sign_ok == True:
      pstore = PayrollStore(con)
      pinfo = pstore.info(refid = refid)
      sql_remark = pinfo['status']
      if sql_remark:
        sql_remark = json_parse(sql_remark)
        last_step = sql_remark[len(sql_remark) - 1]['step']
        if last_step == 2: # get the last status
          pass
        else:
          pstore.closeReview(refid = refid, uid = uid, msg = 'Auto Close the Payroll', status = sql_remark, name = 'Admin')
        

        if last_step == 4: # get the last status
          pass
        else:
          pstore.closeOb(refid = refid, uid = uid, msg = "Auto Close Obligation", status = sql_remark, name = "Admin")
    # end code here


    # this means that the signatory is success and need to proceed to the 
    # closing of the payroll review # this happend if the mayor or the final signatory 
    # will close the payroll 
    


    return (True, 'Success')


  def update_deduction_payroll(this, refid, deduction_list: list):

    sorted_ded = sorted(deduction_list, key = lambda x: (x["code"], x["name"]))

    this.__con.commit("update payroll set deduction_list = ? where refid = ? and status is null", (
      json.dumps(sorted_ded, default = str),
      refid,
    ))

  def update_deduction_payroll_item(this, refid, deduction_list: list):
    data = this.get_all_deduction_payroll_item(refid)
    for item in data:
      ded = json.loads(item[0])
      emp_id = item[1]

      new_ded = []
      for base_ded in deduction_list:
        
        # check the value if it has value added already in the system
        value = 0.0
        for my_ded in ded:
          if my_ded["code"] == base_ded["code"] and my_ded["name"] == base_ded["name"]:
            value = my_ded["value"]
            break

        new_ded.append({
          "code": base_ded["code"],
          "name": base_ded["name"],
          "value": value
        })

      sorted_new_ded = sorted(new_ded, key = lambda x: (x["code"], x["name"]))

      this.__con.commit("update payroll_item set deduction = ? where payroll_refid = ? and emp_id = ?", (
        json.dumps(sorted_new_ded, default = str),
        refid, 
        emp_id,))


  def get_all_deduction_payroll_item(this, refid):
    return this.__con.get("""select deduction, emp_id from payroll_item where payroll_refid = ?""", (refid, ))
    


  def setConnection(this, con: sql = None):
    this.__con = con

  def updateDeduction(this, refid, emp_id, data):
    this.__con.commit('update payroll_item set deduction = ? where payroll_refid = ? and emp_id = ?', (
      data,
      refid,
      emp_id,
    ))

  def generate_refid(this):
    
    date_str = date_time()
    date, time = date_str.split(" ")
    
    yr, mon, day = date.split("-")
    hh, mm, ss = time.split(":")

    refid = f"{yr}{ss}{hh}{mon}{day}{mm}"
    
    return refid

  def update_bank_info_full(this, refid, data: dict):
    this.__con.commit("update payroll set bank_info = ? where refid = ?", (json_stringify(data), refid, ))

  def update_bank_info(this, refid, emp_id, acc_type, acc_no):
    data = this.get_payroll_item(refid, emp_id)
    if not data:
      return 

    other_info = json_parse(data[0]["other_info"])

    other_info["acc_type"] = acc_type
    other_info["acc"] = acc_no

    # {"acc_type": "DBP", "acc": "5056797085"}
    this.__con.commit("update payroll_item set other_info = ? where emp_id = ? and payroll_refid = ?", (
      json_stringify(other_info),
      emp_id,
      refid,
    ))

  def init_bank(this):
    con = this.__con

    '''
      @ require value
      bank_info = {
        "agency_acc_no": None,
        "ada": {
          "sign": [], # [ { name: value, pos: value }  ]
          ""
        }
      }
    '''

    bank_info = {
      "acc_no": "",
      "branch": {
        "head": {
          "p": "",
          "l": "",
          "f": "",
          "m": "",
          "s": "",
          "g": "", # gender
          "lh": "" 
        }
      },
      "ada_sign": [
        #{ "name": "", "pos": "" }
      ]
    }

  # sample
  # {"acc_no": "", "branch": {"head": {"p": "", "l": "MALARAN", "f": "MA.SHEILA", "m": "F.", "s": "", "g": "f", "lh": "Branch Head, Development Bank of the Philippines, Ubay Branch"}}}



    return bank_info

  def last_payroll(this, status):
      data = this.__con.get("select signatory_list, deduction_list, bank_info, name from payroll where type = ? order by datecreated desc", (status, ))
      ret = { }

      if data:
        ret["signatory_list"] = data[0][1]
        ret["deduction_list"] = data[0][2]
        ret["bank_info"] = data[0][2]
        ret["name"] = data[0][3]

      return ret

  def create_payroll(this, refid, range_from: str, range_to: str, status: any, uid: str = None, date = None, name = None, bank = None):
    last_payroll = this.last_payroll(status)

    '''
    @bank_info -> is where the storage of the information of bank information including the 
    ada and other information
    '''

    

    if not last_payroll:
        bank_info = this.init_bank()

    else:
        # initial the bank_information
        bank_info = json_parse(last_payroll["bank_info"])
    # end inital the bank_information


    ded_list = []

    ded_store = DeductionStore(this.__con)
    ded_data = ded_store.getDeduction()
    for x in ded_data:
      # only the active deduction is added
      if x["active"] == "y":
        pdata = json_parse(x["payroll_design"])
        for y in pdata:
          if status in ("j", "c") and y == "c":
            ded_list.append(x)
            break
          elif status == "r" and y == "r":
            ded_list.append(x)
            break

    signStore = SignatoryStore(this.__con)

    signData = signStore.GetSignatory()

    sign_list = []

    for x in signData:
      
      __types = json_parse(x["type"])
      __active = x["active"]

      if __active == "y":
        for __type in __types:
          if status in ("c", "j") and __type == "c":
            sign_list.append({
              "n": x["name"],
              "p": x["pos_title"],
              "c": x["certify"],
              "i": x["index"],
              "a": x["active"],
              "t": x["type"],
              'sign_key': x['sign_id'],
              'sign_val': '',
              'sign_date': ''
            })
            break
          
          elif status == "r" and __type == "r":
            sign_list.append({
              "n": x["name"],
              "p": x["pos_title"],
              "c": x["certify"],
              "i": x["index"],
              "a": x["active"],
              "t": x["type"],
              'sign_key': x['sign_id'],
              'sign_val': '',
              'sign_date': ''
            })
            break
    
    b_store = BankStore(this.__con)
    bank_data = b_store.getBank(bank)
    if not bank_data: raise ValueError("No Bank Found!")
    
    _code, _name, regex, _, _, _, _ = bank_data # unpacking the data bank information

    atm_info = {
      "code": _code,
      "name": _name,
      "regex": regex
    }

    this.__con.commit("insert into payroll(refid, range_from, range_to, type, datecreated, createdby, deduction_list, signatory_list, name, bank_info, atm_info)\
                      values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                        refid, 
                        range_from,
                        range_to,
                        status,
                        date,
                        uid,
                        json_stringify(ded_list),
                        json_stringify(sign_list),
                        name,
                        json_stringify(bank_info),
                        json_stringify(atm_info),
                      ))
  
  def list_payroll(this, date = None, stype = None):

    if date:
      date += "%"
    else:
      date = '%%'

    if not stype:
      stype = "%%"

    res: list = this.__con.get("""select 
                          p.refid, 
                          p.range_from, 
                          p.range_to, 
                          p.cutoff, 
                          p.type, 
                          p.datecreated, 
                          p.createdby,
                          p.signatory_list,
                          p.deduction_list,
                          (select count(pi.payroll_refid) from payroll_item as pi where pi.payroll_refid = p.refid) as total_item,
                          p.name,
                          p.status,
                          p.atm_info
                          from payroll as p
                          where (range_from like ? or range_to like ?) and type like ?
                          order by datecreated desc""", (
                            date,
                            date,
                            stype,
                          ))
    data: list = []

    for x in res:
      data.append({
        "refid":          x[0],
        "from":           x[1],
        "to":             x[2],
        "cutoff":         x[3],
        "type":           x[4],
        "datecreated":    x[5],
        "createdby":      x[6],
        "signatory_list": x[7],
        "deduction_list": x[8],
        "total_item":     x[9],
        "name":           x[10],
        'status':         x[11],
        "atm_info":       json_parse(x[12]) if x[12] else None
      })

    return data

  def info(this, refid):
    res = this.__con.getone("""
      select 
        refid, 
        range_from, 
        range_to, 
        cutoff, 
        type, 
        datecreated, 
        createdby, deduction_list, signatory_list, bank_info, status, atm_info, name from payroll 
      where refid = ?
    """, (refid, ))

    data = {}

    if res:
      data['refid']          = res[0]
      data['from']           = res[1]
      data['to']             = res[2]
      data['cutoff']         = res[3]
      data['type']           = res[4]
      data['datecreated']    = res[5]
      data['createdby']      = res[6]
      data["deduction_list"] = res[7]
      data["signatory_list"] = res[8]
      data["bank_info"]      = res[9]
      data['status']         = res[10]
      data["atm_info"]       = res[11]
      data["name"]           = res[12]

    return data

  def info_r(this, refid) -> PayrollEntity:
    data = this.info(refid)
    payroll = PayrollEntity()
    payroll.refid = data["refid"]
    payroll.from_ = data["from"]
    payroll.to = data["to"]
    payroll.cutoff = data["cutoff"]
    payroll.datecreated = data["datecreated"]
    payroll.createdby = data["createdby"]
    payroll.deduction_list = json_parse(data["deduction_list"]) if data["deduction_list"] else []
    payroll.signatory_list = json_parse(data["signatory_list"]) if data["signatory_list"] else []
    return payroll

  def getItemCount(this, refid, dept_id) -> int:
    item = this.__con.get('''select count(payroll_refid) from payroll_item
                            where payroll_refid = ? and dept_id = ?
                           ''', (
                             refid, dept_id,
                           ))
    return item[0][0] if item else 0


  def get_payroll_item(this, refid, emp_id):
    items = this.__con.get("""select 
                        payroll_refid, 
                        emp_id, 
                        emp_info, 
                        start,
                        end, 
                        compensation,
                        deduction,
                        dept_id,
                        dept_info,
                        createdby,
                        datecreated,
                        other_info
                   from payroll_item where payroll_refid = ? and emp_id = ? 
                  """, (
                    refid,
                    emp_id,
                  ))
    data = []
    for item in items:
      data.append({
       "payroll_refid": item[0],
       "emp_id": item[1],
       "emp_info": item[2],
       "start" : item[3],
       "end": item[4],
       "com": item[5],
       "ded": item[6],
       "ded_id": item[7],
       "ded_info": item[8],
       "createdby": item[9],
       "datecreated": item[10],
       "other_info": item[11]
      })

    return data
  
  def remove_all_item(this, refid):
    this.__con.commit('delete from payroll_item where payroll_refid = ?', (
      refid,
    ))
    

  def remove_item(this, refid, emp_id, uid = None):
    
    res = {"ok": True, "msg": None}
    data = this.get_payroll_item(refid, emp_id)
    if data:
      create_history(this.__con, uid, "payroll_item", data, "d")

    this.__con.commit("""delete from payroll_item 
                     where payroll_refid = ? and emp_id = ?
                    """, (
                      refid,
                      emp_id,
                    ))
    res["msg"] = "Successfully removed!"
    
    return res

  def update_item(this, refid = None, emp_id = None, \
               emp_info = None, start = None, end = None,\
               compensation = None, \
               deduction = None, dept_id = None, \
               dept_info = None, uid = None, datecreated = None 
              ):
    
    res = {
      "ok": True,
      "msg": "Successfully updated!"
    }

    d01 = this.get_payroll_item(refid, emp_id)
    if d01:
      create_history(this.__con, uid, "payroll_item", d01, "u")
    
    _, _, sd = d01[0]["start"].split("-")
    _, _, ed = d01[0]["end"].split("-")
  

    com = json_parse(compensation)  
    max_day = int(ed) - int(sd)

    if int(com["w"]) > (max_day + 1):

      res["ok"] = False
      res["msg"] = f"Number of work day must maximum of {max_day + 1} day(s)"
      return res

    



    this.__con.commit("""
      update payroll_item 
          set emp_info = ?,
          compensation = ?,
          deduction = ?,
          dept_id = ?,
          dept_info = ?    
      where payroll_refid = ? and emp_id = ?
    """, (
        emp_info,
        compensation,
        deduction,
        dept_id,
        dept_info,
        refid,
        emp_id,
    ))

    return res

  def _last_month(this, emp_id, frm_day: str, to_day: str) -> list:
    # get the lastmonth
    data = this.__con.get("""
      select deduction, compensation from payroll_item where 
      start like ? and end like ?              
      and emp_id = ? order by datecreated desc
    """, (
      '%' + frm_day,
      '%' + to_day,
      emp_id,
    ))

    return data
  

  def _get_prev_month(this, fy, fm) -> tuple:
    py = int(fy)
    pm = int(fm) - 1

    if pm <= 0:
      pm = 12
      py -= 1

    pm = '0' + str(pm) if pm < 10 else str(pm)

    _, _, last_day = cdate_last_date_r(f'{py}-{pm}')

    return (str(py), pm, last_day)
  


  def get_last_item(this, emp_id, frm, to):
    # to check the last item
    frm_day = frm.split('-')
    to_day = to.split('-')

    fy, fm, fd = frm_day
    ty, tm, td = to_day

    py, pm, pd = this._get_prev_month(fy, fm)

    td1 = td
    if int(td) > 28:
      td1 = pd

    # get the previous month if possible
    data = this._last_month(emp_id, f'{py}-{pm}-{fd}', f'{py}-{pm}-{td1}')

    if not data:
      # alternative for getting data
      pass 

    ret = []
    
    for x in data:
      ret.append({
        "last_deduction": json_parse(x[0])
      })
    
    return ret

  def add_item(this, refid = None, emp_id = None, \
               emp_info = None, start = None, end = None,\
               compensation = None, \
               deduction = None, dept_id = None, \
               dept_info = None, uid = None, datecreated = None, other_info = None, 
               payroll_start = None,
               payroll_end = None
              ):
    
    res = {
      "ok": 1,
      "msg": "Added In Payroll"
    }

   

    yr1, m1, d1 = start.split("-")
    yr2, m2, d2 = payroll_start.split("-")
    yr4, m4, d4 = payroll_end.split("-")
    yr3, m3, d3 = end.split("-")

    if not (m2 == m1 and m2 == m3 and yr1 == yr2):
      res["ok"] = False
      res["msg"] = "Payroll month and the DTR month is not similar!"
      return res
    
    if (int(d3) > int(d4)):
      res["ok"]  = False
      res["msg"] = "The end day of the dtr is greater than the payroll end date"
      return res
      


    

    d = this.__con.get("""
      select payroll_refid from payroll_item where emp_id = ? and 
      start <= ? and end >= ? and status = 1
    """, (
      emp_id,
      end,
      start,
    ))


    d2 = this.__con.get("""
      select payroll_refid from payroll_item where emp_id = ? and status = 1 and payroll_refid = ?
    """, (
      emp_id,
      refid,
    ))

    if d2:
      res["ok"]  = False
      res["msg"] = "This employee is already in here! please check the name"
      return res


    if not d:
      this.__con.commit('''
        insert into payroll_item(
                        payroll_refid, 
                        emp_id, 
                        emp_info, 
                        start,
                        end, 
                        compensation,
                        deduction,
                        dept_id,
                        dept_info,
                        createdby,
                        datecreated,
                        other_info,
                        status
                        ) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
      ''', (
        refid,
        emp_id,
        emp_info,
        start,
        end,
        compensation,
        deduction,
        dept_id,
        dept_info,
        uid, 
        datecreated,
        other_info,
      ))

    else:
      res["ok"] = False
      prefid = d[0][0]
      if str(refid) == str(prefid):
        res["msg"] = "Already added here!"
      else:
        pstore = PayrollStore(this.__con)
        payroll_info = pstore.info(prefid)
        if str(payroll_info["refid"]) == str(prefid):
          res["msg"] = f"""Already added! {payroll_info["name"]} Range:  {date_normal(payroll_info["from"])} - {date_normal(payroll_info["to"])}"""
                
    return res
  
  def get_item(this, refid = None, data = {"search": "", "dept_id": "", "is_order": False}):
    
    # default value
    psearch = ""
    if "search" in data:
      psearch = data["search"]
  
    pdept_id = ""
    if "dept_id" in data:
      pdept_id = data["dept_id"]

    is_order = False
    if "is_order" in data:
      is_order = data["is_order"]
    # end default value

    search = "%" + psearch + "%"

    dept_id = "%%"
    if pdept_id:
      dept_id = pdept_id
    
    order_q = ""

    if is_order and not pdept_id: 
      order_q = "pi.datecreated desc,"
    
    res = this.__con.get(f'''
      select 
          pi.emp_id, 
          pi.emp_info, 
          pi.compensation,
          pi.deduction,
          pi.dept_id,
          pi.dept_info,
          pi.other_info,
          pi.start,
          pi.end  
      from payroll_item as pi 
         left join client as c on c.id = pi.emp_id
      where 
                         
          (pi.payroll_refid = ? and
          ( replace((c.lname||c.fname), " ", "") like ? or
          replace((c.fname||c.lname), " ", "") like ? ) and
          pi.dept_id like ?) order by {order_q}c.lname, c.fname, c.mname asc
    ''', (
      refid,
      search,
      search,
      dept_id,
    ))
    
    data = []

    for x in res:
      data.append({
        'emp_id': x[0],
        'emp_info': x[1],
        'compensation': x[2],
        'deduction': x[3],
        'dept_id': x[4],
        'dept_info': x[5],
        'other_info': x[6],
        'start': x[7],
        'end': x[8]
      })
    
    return data

  def getOneItem(this, refid, emp_id):
    
    res = this.__con.get(f'''
      select 
          pi.emp_id, 
          pi.emp_info, 
          pi.compensation,
          pi.deduction,
          pi.dept_id,
          pi.dept_info,
          pi.other_info,
          pi.start,
          pi.end  
      from payroll_item as pi 
         left join client as c on c.id = pi.emp_id
      where 
                         
          pi.payroll_refid = ? and pi.emp_id = ?
          
    ''', (
      refid,
      emp_id
    ))
    
    data = []

    for x in res:
      data.append({
        'emp_id': x[0],
        'emp_info': x[1],
        'compensation': x[2],
        'deduction': x[3],
        'dept_id': x[4],
        'dept_info': x[5],
        'other_info': x[6],
        'start': x[7],
        'end': x[8]
      })
    
    return data

  def removePayroll( this, refid = None, uid = None, payroll_info = None ):
    
    # payroll_info = None # this reduce the double query or query overloaded

    if not payroll_info:
      payroll_info = this.info(refid)

    this.__con.commit('delete from payroll where refid = ?', (refid, ))
    create_history(this.__con, uid, "payroll", payroll_info, "d")
  
  def create_step(this, step: int, remark: str, user_name: str, user_id: int, user_msg, status: list = [], sign_id = None):
    
    status.append({
      "step": step,
      "remark": remark,
      "date": date_time(),
      "user": {
        "id": user_id,
        "name": user_name,
        "msg": user_msg,
        'sign_id': sign_id
      },
      'sign_id': sign_id
    })



  ##############################################################################
  #                                 PROCESS NUMBER                             
  # 0 -> FOR RECEIVING THE DTR
  # 1 -> FOR CLOSING THE PAYROLL
  # 2 -> FOR READY FOR OBLIGATION REQUESTS
  # 3 -> CLOSED OBLIGATION REQUESTS
  # 4 -> PAYROLL READY FOR ADA
  # 5 -> APPROVED OR CLOSE ADA
  # 6 -> PAYROLL REVIEW & SIGNATURE
  ##############################################################################
  
  def approvePayroll( this, refid = None, uid = None, msg = None, name = None, status = [] ):
    '''
    refid -> payroll refid
    uid -> the one who qd 

    status: { remark: 1, uid: creator_id }
    '''
    # 1 => for approved #
    
    sign_id = None
    us = UserStore(this.__con)
    info = us.list_user(uid)
    if info:
      sign_id = info[0]['sign_id']

    for item in status:
      if item['step'] == 1:
        item['sign_id'] = sign_id

    this.create_step(1, "Payroll Closed!", name, uid, msg, status, sign_id)
    this.create_step(6, 'PAYROLL IN REVIEW & DIGITAL SIGNATORIES', name, uid, msg, status)

    #this.create_step(2, "Ready for Obligation Requests", name, uid, msg, status)
  
    this.__con.commit('update payroll set status = ? where refid = ?', (
      json_stringify(status),
      refid,
    ))

  def closeReview(this, refid = None, uid = None, msg = None, name = None, status = []):
    
    this.create_step(2, "The Payroll review is done & now ready for OBligation Requests", name, uid, msg, status)
    this.__con.commit('update payroll set status = ? where refid = ?', (
      json_stringify(status),
      refid,
    ))


  def reopenPayroll(this, refid = None, uid = None, msg = None, name = None, status = [], sign_list = []):

    for item in status:
      if item['step'] == 1:
        item['sign_id'] = None

    for sitem in sign_list:
      if 'sign_val' in sitem:
        sitem['sign_val'] = None
        sitem['sign_date'] = None

    this.create_step(0, f'The Payroll is reprocess: due to {msg}', name, uid, msg, status)
    this.__con.commit('update payroll set status = ?, signatory_list = ? where refid = ?', (
      json_stringify(status),
      json_stringify(sign_list),
      refid,
    ))
    


  def closeOb(this, refid, uid, msg, name, status = []):
    """status: status of the payroll"""

    this.create_step(3, "Obligation Requests Closed", name, uid, msg, status)
    this.create_step(4, "ADA OR PAYROLL FILE FOR SALARIES", name, uid, msg, status)

    this.__con.commit('update payroll set status = ? where refid = ?', (
      json_stringify(status),
      refid,
    ))

  def closeAda(this, refid, uid, msg, name, status = []):
    """status: status of the payroll"""
    # 5 for ending the payroll file or ada

    this.create_step(5, "THE PAYROLL'S ADA OR PAYROLL FILE ALREADY APPROVED FROM THE BANK!", name, uid, msg, status)

    this.__con.commit('update payroll set status = ? where refid = ?', (
      json_stringify(status),
      refid,
    ))

  def readyForDownloadPayrollFile(this, refid, uid, msg, name, status = []):
    this.create_step(7, "READY TO DOWNLOAD THE PAYROLL FILE!", name, uid, msg, status)
    this.__con.commit('update payroll set status = ? where refid = ?', (
      json_stringify(status),
      refid,
    ))


def ind_payslip(con, emp_id) -> List[tuple]:

  return con.get('''select 
                  pi.start, 
                  pi.end, 
                  pi.emp_info, 
                  pi.compensation, 
                  pi.deduction, 
                  pi.dept_info, 
                  pi.other_info,
                  pi.payroll_refid
                  from payroll_item as pi inner join payroll as p on p.refid = pi.payroll_refid
                 where pi.emp_id = ? and p.status is not null''', (
    emp_id,
  ))





class BankAda:
  def __init__(self, con):
    self.con: sql = con

  def get(self, refid: str, fund: str):
    return self.con.get("select ada_no, datecreated from bank_ada where refid = ? and fund = ?", (refid, fund))
  
  # def isAdaNoExists(self, ada_no: str, refid: str, fund: str):
  #   return self.con.get("select ada_no from bank_ada where ada_no = ? and not (refid = ? and fund = ?)", (
  #     ada_no,
  #   ))
  

  def save(self, refid: str, fund: str, ada_no: str, ada_list: list = [], uid = None) -> bool:
    if self.get(refid, fund):
      self.con.commit("update bank_ada set ada_no = ?, list_ada = ? where refid = ? and fund = ?", (ada_no, json_stringify(ada_list), refid, fund, ))
      return "Ada number updated!"
    
    self.con.commit("insert into bank_ada(ada_no, refid, fund, list_ada, createdby, datecreated) values(?, ?, ?, ?, ?, ?)", (
      ada_no, refid, fund, json_stringify(ada_list), uid, date_time(),
    ))

    return "Ada number added!"

    

    