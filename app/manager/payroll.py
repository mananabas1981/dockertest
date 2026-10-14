import os
from typing import List
from time import time_ns

from openpyxl.workbook.protection import WorkbookProtection
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment, Border, Side, Font 

from app.store.bank_store import EmpBankStore
from app.store.default_ded import DefaultDEductionEntity, DefaultDeduction
from app.store.payroll_default_store import DefaultPayrollSignatoryStore
from app.util.auth import Auth
from re import match
from app.util.date import cdate_last_date_r, date_time
from app.store.payroll_store import BankAda, PayrollStore
from app.lib.sql import sql
from app.util.reg import re_date
from re import match
from app.util.date import date_time, date_normal, date_time_normal

from app.store.client_store import client_info
from app.util.json import json_stringify, json_parse
#from app.store.client_store import RateStore, PositionStore, DeptInfoStore
from app.store.department_store import Department

from app.util.payroll_calulator import payslip
from app.util.date import month_name
from app.util.qrcode import Qr
from app.util.payroll_calulator import CalBasic, SaveNCalulate, recalculate_tax
# Entity class
#from app.entity.deduction_entity import DeductionEntity, PayrollEntity
from app.entity.http_entity import ProcessEntity
# end entity class
from app.util.n2word import  int_to_word

# models
from app.model.payroll_model import PayrollModel, PayrollItemInterface
from app.util.age import ago_simple

from app.model.bank_model import BankModel

from app.model.user_model import AccessModel

from app.model.payroll_print_design.print_1 import PayrollPrintHandler
from app.model.user_model import UserModel


from app.model.remittance_model import RemittanceModel

from app.model.print.remittance.standard import RemittanceStandardPrint


from app.store.card_store import Card, CardModel
from app.store.payroll_store import ind_payslip
from app.store.system_store import sys_info

from app.store.obr import ObEntity, Ob_R

from base64 import b64encode

from io import BytesIO
import pyminizip
from app.lib.sql import sql_signature
from app.store.digital_store import DigitalStore
from app.store.user_store import UserStore
from copy import deepcopy
from app.store.client_store import RateStore, PositionStore
import datetime



def _check_month(from_t, to_t):
  _from, _to = (from_t, to_t)
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

  return type_month

def payroll_copy(req, res):
  con, auth, msg = None, None, {
    'ok': False, 
    'msg': '',
  }

  try:
    auth = Auth(req)
    if not auth.isAuth:
      msg["msg"] = "You are not authorized!"
      raise ValueError("You are not authorized!")
    
    data = auth.data

    name  = data["name"]
    refid = data["refid"]
    frm   = data["from"]
    to    = data["to"]

    # print(data)
    con = sql()
    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-c-c-c']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())
    
    pstore = PayrollStore(con)
    payroll_info = pstore.info(refid)
    
    #print(payroll_info["cutoff"])
    #print(payroll_info["type"])
    #print(payroll_info["deduction_list"])
    #print(payroll_info["signatory_list"])
    #print(payroll_info["bank_info"])
    #print(payroll_info["atm_info"])

    old_items = pstore.get_item(refid)

    # checking if half, whole month

    type_month = _check_month(payroll_info["from"], payroll_info["to"])
  
    cur_type_month = _check_month(frm, to)
  
    # end checking 
    

    newrefid = pstore.generate_refid()
    con.commit("insert into payroll(refid, range_from, range_to, type, datecreated, createdby, deduction_list, signatory_list, name, bank_info, atm_info)\
                      values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                        newrefid, 
                        frm,
                        to,
                        payroll_info["type"],
                        date_time(),
                        auth.ses.get("uid"),
                        payroll_info["deduction_list"],
                        payroll_info["signatory_list"],
                        name,
                        payroll_info["bank_info"],
                        payroll_info["atm_info"],
                      ))

    for item in old_items:

      ded_list = json_parse(item["deduction"])
      for jitem in ded_list:
        if type_month == 0 and (cur_type_month in (1, 2)):
          jitem["value"] = float(jitem["value"]) / 2

      res = pstore.add_item(
        newrefid, 
        item["emp_id"],
        item["emp_info"],
        frm,
        to,
        item["compensation"],
        json_stringify(ded_list),
        item["dept_id"],
        item["dept_info"],
        auth.ses.get("uid"),
        date_time(),
        item["other_info"],
        frm,
        to
      )

      if not res["ok"]:
        msg["msg"] = res["msg"]
        raise ValueError("Error")
    con.go()

    msg["msg"] = "Transaction Completed!"
    msg["ok"]  = True

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  return auth.send(msg) if auth else None

def load_action(req, res):
  con, auth, msg = None, None, {
    'ok': False, 
    'msg': '',
    'data': []
  }


  try:
    auth = Auth(req)
    data, isAuth = auth.data, auth.isAuth
    con = sql()

    uid = auth.ses.get('uid') 
    ustore = UserStore(con)

    my_sign_key = ustore.sign_key(uid)
    # if no  sign key
    if my_sign_key == None: 
      msg['ok'] = True
      msg['msg'] = 'No Sign Key'
      raise ValueError('No Sign Key')
    # get the sign_key

    payroll_store: PayrollStore = PayrollStore(con)
    data: list = payroll_store.list_payroll()

    ret = []

    for item in data:
      # sign reparse
      sign_data = json_parse(item['signatory_list'])
      
      last_need_sign = None
      for sign_item in sign_data:
        sign_item['i'] = json_parse(sign_item['i'])
        sign_item['t'] = json_parse(sign_item['t'])

        if 'sign_val' in sign_item:
          if last_need_sign == None:
            if sign_item['sign_val'] == None or sign_item['sign_val'].strip() == '':
              last_need_sign = sign_item
        # get the last_sign_in
      # end sign reparse

      if item["status"] == None: continue # this common happen to the newly created payroll
    
      status_data = json_parse(item['status'])

      # we must to filter the data 
      # we only get the data with the need of signatory
      if len(status_data) == 0: continue # dont include the status 0 length

      last_status = status_data[len(status_data) - 1]
      step = last_status['step']

      if step != 6: continue # only the step 6, where it is payroll signatory in review
      
      if last_need_sign == None: continue # ensuring that the last sign must not None
      
      # print(last_need_sign)
      if last_need_sign['sign_key'] != my_sign_key: continue # ensuring that the sign key must the same
    
      ret.append({
        'refid': item['refid'],
        'from': item['from'],
        'to': item['to'],
        'title': item['name'],
        'sign_data': sign_data,
        'status_data': status_data,
        'last_need_action': last_need_sign,
        "total_item": item["total_item"]
      })

      # print(item['status'])

    msg['ok']   = True
    msg['msg']  = 'Transaction Completed!'
    msg['data'] = ret

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)

def payslip_print(req, res):

  con, msg, auth = (None, {
    'ok': False,
    'msg': 'Something went wrong!',
    'data': ''
  }, None)
  
  try:
    auth = Auth(req)
    data, isAuth = (auth.data, auth.isAuth)

    if not isAuth: raise ValueError('Not authorized!')

    if not 'id' in data: raise ValueError('id is required!')
    if not 'from' in data: raise ValueError('from is required!')
    if not 'to' in data: raise ValueError('to is required!')
    if not 'refid' in data: raise ValueError('refid id not found')

    id_, from_, to_, refid = (data['id'], data['from'], data['to'], data['refid'])
    
    con = sql()

    sys = sys_info(con)    
    com_name, place = (sys['name'], sys['addr'])

    pstore = PayrollStore(con)
    payroll_info = pstore.info(refid)
    ded_list = json_parse(payroll_info["deduction_list"])
    items = pstore.get_item(refid, {
      "dept_id": "",
      "is_order": False
    })

    slip = None
    for item in items:
      if item['start'] == from_ and item['end'] == to_ and str(id_) == str(item['emp_id']):
        slip = payslip(item, deduction_base = ded_list, payroll_info = payroll_info)
        break
    
    if not slip: raise ValueError('Payslip not found')
    serial = slip['serial_no']
    com = slip['com'] # dictionary
    name = slip['name']
    position = slip['position']
    salary = slip['salary']
    no_work_day = slip['no_work_day']
    absent = slip['absent']
    late = slip['late']
    undertime = slip['undertime']
    gross = slip['gross']
    dept_info = slip['dept_info'] # dictionary

    deduction = slip['deduction'] # Array
    total_ded = slip['total_ded']
    net = slip['net']
    account = slip['account']
    account_type = slip['account_type']

    sal_type = {
      'd': 'Daily',
      'h': 'Hourly',
      'm': 'Monthly',
      'a': 'Annually'
    }

    _net_str_arr = str(net).split('.')
    net_whole, net_dec = (int(_net_str_arr[0]), int(_net_str_arr[1]))

    ded_html = ''

    for item in deduction:
      ded_html += f'''
        <tr>
          <td>{item['code']}|{item['name']}</td>
          <td>P {item['value']:,.2f}</td>
        </tr>
      '''

    html = f'''
    <style>
    .tttt01 {{
      border-collapse: collapse;
        width: 100%;
      }}

      .tttt01 tr th, .tttt01 tr td {{
        text-align: left;
        padding: 4px;
        border:1px dashed;
        font-size: 11px;
      }}

      .tttt01 tr:nth-child(even) {{
        background-color: #D6EEEE;
      }}
    
    </style>
    <div style="">
      <center><h5 style="letter-spacing: 2px;">Pay Slip</h5></center>
      <center><div style="font-size: 20px; font-weight: bold;letter-spacing: 10px;">{com_name.upper()}</div></center>
      <center><div style="letter-spacing: 2px;">{place.upper()}</div></center>
      <center><div style="">ref no.: <span style="color: green;">{refid}</span></div></center>
      <hr style="border-style: dotted;" />
      <div style="font-size: 11px;">
        <div style="width: 50%; float: left;">Name: <b style="letter-spacing: 1px;"> {name.upper()}</b></div>
        <div style="width: 50%; float: left;">Pay Period: <b style="letter-spacing: 2px;"> {date_normal(from_)} to {date_normal(to_)}</b></div>
        <br />
        
        <div style="width: 50%; float: left;">Worked days: <b style="letter-spacing: 2px;"> {no_work_day}</b></div>
        <div style="width: 50%; float: left;">Office: <b style="letter-spacing: 2px;">{dept_info.get('n', '')}</b></div>
        <br />
        <div style="width: 50%; float: left;">Account({account_type})#: <b style="letter-spacing: 2px;"> {account[-3:]:*>10}</b> <b></b></div>
        <div style="width: 50%; float: left;">Designation: <b style="letter-spacing: 2px;"> {position}</b></div>
        <br />
        <br />
        <div style="width: 50%; float: left;">Date Printed: {date_time_normal(date_time())}</div>
      <div/>
      <br /> <br />   
      <div style="width: 50%; float: left;">
        <table class="tttt01">
          <tr>
            <td>Earnings</td>
            <td>Amount</td>
          </tr>
          <tr>
            <td>Basic</td>
            <td>P {com['r']:,.2f} {sal_type.get(com['t'], '')}</td>
          </tr>
          <tr>
            <td>Salary for the period</td>
            <td>P {slip["salary_period"]:,.2f}</td>
          </tr>
          <tr style="color: red;">
            <td>Absent</td>
            <td>({com['a']} day{'s' if float(com['a']) > 1 else ''}) P{absent:,.2f}</td>
          </tr>
          <tr style="color: red;">
            <td>Late</td>
            <td>({com['l']} minute{'s' if float(com['l']) > 1 else ''}) P{late:,.2f}</td>
          </tr>
          <tr style="color: green;">
            <td>Undertime</td>
            <td>({com['u']} minute{'s' if float(com['u']) > 1 else ''}) P{undertime:,.2f}</td>
          </tr>
          <tr>
            <td><span style="color: red;">Deduction</span></td>
            <td><b style="color: red;">P {(slip["late"] + slip["undertime"] + slip["absent"]):,.2f}</b></td>
          </tr>
          <tr>
            <td>Gross</td>
            <td>P {gross:,.2f}</td>
          </tr>
        </table>
      </div>
      <div style="width: 50%; float: left;">
        <table class="tttt01">
          <tr>
            <td>Deductions</td>
            <td>Amount</td>
          </tr>
          {ded_html}
          <tr style="color: red; font-weight: bold; letter-spacing: 2px;">
            <td>Total Deductions</td>
            <td> P {total_ded:,.2f}</td>
          </tr>
          <tr style="font-weight: bolder; letter-spacing: 2px; border: none;">
            <td style="border: none;text-align: right;">Net Pay: </td>
            <td style="border: none;"> P {net:,.2f}</td>
          </tr>
        </table>
      </div>
      <br />
      <br />
      <br />
      <center>
        <div style="font-size: 25px; letter-spacing: 2px; font-weight: bold;">P {net:,.2f}</div>
        <hr style="border-style: dotted;" />
        <div>{int_to_word(net_whole)} {'and ' + int_to_word(net_dec) if net_dec > 0 else ''}</div>
      </center>
      <br /> <br />
      <div></div>

      <center><div style="width: 150px; border-top: 1px solid grey; padding-top: 20px; margin-bottom: 20px;">Employee Signature</div></center>
      <center><p>------------------- This is system generated payslip -------------------</p></center>
    </div>
    '''

    msg['ok'] = True
    msg['msg'] = 'Transaction Completed!'
    msg['data'] = html
  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)
  


def payslip_list(req, res):
  con = None
  msg = {
    'ok': False,
    'msg': '',
    'data': None
  }
  auth = None

  try:
    auth = Auth(req)
    
    if not auth.isAuth:
      raise ValueError('You are not authorized!')
    
    data = auth.data

    if not 'id' in data:
      raise ValueError('emp_id is required!')
    
    con = sql()

    res = ind_payslip(con = con, emp_id = data['id'])
    msg['ok'] = True
    msg['msg'] = 'Transaction completed!'
    msg['data'] = res

  except Exception as er:
    print(er)
  finally:
    if con: 
      con.close()

  if auth:
    return auth.send(msg)

def card_id(req, res):
  con = None
  msg = {
    "ok": False,
    "msg": ""
  }
  auth = None

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("You are not authorized!")
    
    data = auth.data

    if not "type" in data:
      raise ValueError("type is required!")
    
    if not "value" in data:
      raise ValueError("value is required!")
    
    type_t: str = data["type"]
    value: str = data["value"]

    con: sql = sql()


    crd = CardModel(con)
    data: List[Card] = crd.lists(Card(card_type = type_t, card_value = value))

    
    print(data)
    
  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()
  if auth:
    return auth.send(msg)

def generate_remittance(req, res):
    # printing of the remittances
    auth = None
    con = None
    msg = {
      'ok': False,
      'msg': '',
      'data': ''
    }
    try:
      auth = Auth(req)
      if not auth.isAuth:
        raise ValueError('You are not authorized!')
      
      data = auth.data

      if not 'key' in data:
        raise ValueError('key is required')
      
      if not 'refid' in data:
        raise ValueError('refid is required!')
      
      if not "file" in data:
        raise ValueError("file is required!")
    

      key = data['key']
      refid = data['refid']
      
      con = sql() # open the connection

      remModel = RemittanceModel(con)
      
      lists = remModel.generate(refid = refid, key = key)

      print_html = RemittanceStandardPrint(data = lists, file_type = data["file"])
      
      if not print_html.init():
        msg['msg'] = f"""{data["file"]} is not yet available"""
        
        raise ValueError(f"""{data["file"]} is not yet available""")

      msg['data'] = print_html.output()
      msg["file_name"] = f"{key}_{refid}"
      msg['ok'] = True
      msg['msg'] = 'Complated!'
      # print_html.output()

  
    except Exception as er:
      print(er)
    finally:
      if con:
        con.close()

    if auth:
      return auth.send(msg)

def bank_update(req, res):
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
        if not "acc_no" in data:
            raise ValueError("acc_no is required!")

        if not "head_info" in data:
            raise ValueError("head_info is required")

        if not "refid" in data:
            raise ValueError("refid is required")

        if not "sign_info" in data:
            raise ValueError("sign_info is required")
        
        refid = data["refid"]
        # get the ref data to be updated in the system
        # dont ovewrite everything in the database
        con = sql()
        pstore = PayrollStore(con)
        payroll_info = pstore.info(refid)
        
        bank_info = json_parse(payroll_info["bank_info"])
        if not bank_info:
            raise ValueError("payroll not found")

        bank_info["acc_no"] = data["acc_no"]
        head_info = data["head_info"]

        head = bank_info["branch"]["head"]

        if "p" in head_info:
            head["p"] = head_info["p"]
        if "f" in head_info:
            head["f"] = head_info["f"]
        
        if "m" in head_info:
            head["m"] = head_info["m"]

        if "l" in head_info:
            head["l"] = head_info["l"]

        if "s" in head_info:
            head["s"] = head_info["s"]

        if "g" in head_info:
            head["g"] = head_info["g"]

        if "lh" in head_info:
            head["lh"] = head_info["lh"]

        sign_info = data["sign_info"]
        
        new_sign = []

        for item in sign_info:
            if "name" in item and "pos" in item:
                new_sign.append({
                    "name": item["name"],
                    "pos": item["pos"]
                })
        #print(data["head_info"])
        
        bank_info["ada_sign"] = new_sign
        
        pstore.update_bank_info_full(refid, bank_info)
        con.go()

        msg["msg"] = "Transaction Completed!"
        msg["ok"] = True
        
    except Exception as er:
        print(er)

    if auth:
        return auth.send(msg)

def ada_sign_list(req, res):
    auth = None
    con = None
    msg = {
            "ok": False,
            "msg": None,
            "data": {
                "branch": None,
                "ada_sign": None
            }
        }

    try:
        auth = Auth(req)
        if not auth.isAuth:
            raise ValueError("You are not authorized to access the system")

        data = auth.data
        
        if not "refid" in data:
            raise ValueError("refid is required")
        
        con = sql()
        pstore = PayrollStore(con)

        info = pstore.info(data["refid"])
        bank_info = json_parse(info["bank_info"])
        
        branch = {}
        ada_sign = []
        acc_no = ""

        if "branch" in bank_info:    
            branch = bank_info["branch"]
        
        if "acc_no" in bank_info:
            acc_no = bank_info["acc_no"]

        if "ada_sign" in bank_info:
            ada_sign = bank_info["ada_sign"]
        
        msg["data"]["branch"] = branch
        msg["data"]["ada_sign"] = ada_sign
        msg["data"]["acc_no"] = acc_no

        msg["ok"] = True
        msg["msg"] = "Transaction Completed!"

    except Exception as er:
        print(er)
    finally:
        if con:
            con.close()
    if auth:
        return auth.send(msg)

def create_payroll(req, res):

  auth = None
  con = None

  msg = {
    "ok": 0,
    "msg": ""  
  }
  
  try:
    
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("Not Authorized!")
    data = auth.data

    range_from = data["from"]
    range_to   = data["to"]
    status     = data["status"]
    name       = data["name"]
    bank       = data["bank"]

    if not match(re_date, range_from):
      msg["msg"] = "Range from is invalid"
    
    if not match(re_date, range_to):
      msg["msg"] = "Range to is invalid"

    if bank == None or bank.strip() == "":
      msg["msg"] = "Bank is Required!"
      raise ValueError("Bank is required!")
  
    payroll_store = PayrollStore()
    ref_id = payroll_store.generate_refid()
  
    con = sql()

    if status == 'j':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-1-j']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    elif status == 'c':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-1-c']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    elif status == 'r':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-1-r']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    else:
      msg['msg'] = 'Something went wrong!'
      raise ValueError('payroll type is invalid')
    
     # total_con = 0.0
    _from, _to = (range_from, range_to)
    
    _d_f = _from.split('-')[2] # get the first day of from range
    _t_l = _to.split('-')[2] # get the last day of to range

    _, _, _last = cdate_last_date_r(_from)

    if status == 'r':
      # if not (_d_f == '01' and _t_l == _last):
      #   msg['msg'] = 'Payroll of Regular must be whole month'
      #   raise ValueError('Payroll of Regular Employee must be whole month')
      pass
    else:
      is_valid = False
      if _d_f == '01' and _t_l == _last:
        is_valid = True # whole month
      elif _d_f == '01' and _t_l == '15':
        is_valid = True # first half month
      elif _d_f == '16' and _t_l == _last:
        is_valid = True # 2nd half month  
      if not is_valid:
        msg['msg'] = '<span style="color: red; font-size: 15px;">Warning</span>: <span style="font-size: 15px;">Date range must be half month or whole month!</span>'
        raise ValueError('Please check the date range, it must be half or whole month')

    payroll_store.setConnection(con)
    payroll_store.create_payroll(ref_id, range_from, range_to, status, auth.ses.get("uid"), date_time(), name = name, bank = bank)
    con.go()

    msg["ok"] = 1
    msg["msg"] = "Transaction Successfully!"

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)

def list_payroll(req, res):
  con = None
  msg = {
    "ok": 0,
    "msg": "",
    "data": None,
    'date': None
  }

  try:
    auth: Auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("Not Authorized!")
    data: dict = auth.data

    if not "date" in data:
      raise ValueError("date is required!")

    if not "type" in data:
      raise ValueError("type is required!")

    con: sql = sql()

    status = data['type']

    if status == 'j':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-v-j']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    elif status == 'c':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-v-c']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    elif status == 'r':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-v-r']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    elif status == '':
      pass
    else:
      msg['msg'] = 'Something went wrong!'
      raise ValueError('type of payroll is invalid')

    payroll_store: PayrollStore = PayrollStore(con)
    data: list = payroll_store.list_payroll(date = data["date"], stype = data["type"])
    con.close()

    for x in data:
      x["ago"] = ago_simple(x["datecreated"])

    msg["data"] = data
    msg["ok"] = 1
    msg["msg"] = "Transaction Completed!"
    msg['date'] = date_time()
    
  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()
  
  if auth:
    return auth.send(msg)
  
def removePayroll(req, res):
  auth = None
  msg = {
    'ok': False,
    'msg': None,
  }
  con = None

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError('You are not authorized!')
    data = auth.data
    
    if not 'refid' in data:
      raise ValueError('refid is required!')

    refid = data['refid']
    
    con = sql()

    payroll_store = PayrollStore(con)
    info = payroll_store.info(refid)
    if not info:
      msg['Payroll not found']
      raise ValueError('Delete Payroll: payroll not found!')

    info_status = info['status']
    
    if info_status:
      info_status = json_parse(info_status)
      if info_status[len(info_status) - 1]['step'] != 0:
        msg['msg'] = 'The Payroll already closed!'
        raise ValueError('Already locked the payroll')

    status = info['type']

    if status == 'j':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-2-j']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())  
    elif status == 'c':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-2-c']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    elif status == 'r':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-2-r']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())    
    else:
      msg['msg'] = 'Something went wrong !'
      raise ValueError('Something went wrong!')
    
    p_store = PayrollStore(con)

    if info_status == None and status == "r":
      p_store.remove_all_item(refid = refid) # if it is a regular employee
      
    items = p_store.get_item(refid = refid)
    if items:
      msg['msg'] = 'You cant delete this payroll, please remove the payroll item first!'
      raise ValueError('You cant delete this payroll, please remove the payroll item first!')
    
    p_store.removePayroll( refid = refid, uid = auth.ses.get('uid'), payroll_info = info )
    
    con.go() # commit all changes

    # ac = AccessModel(con)
    # if not ac.hasAccess(auth.ses.get('uid'), ['']):
    msg['msg'] = 'Removed Completed!'
    msg['ok']  = True

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)

# this is the tax calculation
def tax_calculate(req, res):
  pro = ProcessEntity()
  try:
    pro.createAuth(req)
    if not pro.auth.isAuth:
      raise ValueError("You are not authorized!")
    
    rdata = pro.auth.data

    if not "refid" in rdata:
      raise ValueError("refid is required")
    
    if not "emp_id" in rdata:
      raise ValueError("emp_id is required")
    
    refid = rdata["refid"]
    emp_id = rdata["emp_id"]

    pro.openConnection()
    pstore = PayrollStore(pro.con)
    p_data = pstore.info_r(refid)
    
    info = pstore.info(refid)
    info_status = info['status']
    
    if info_status:
      pro.msg['msg'] = 'The Payroll already closed!'
      raise ValueError('Already locked the payroll')
          
    tax = recalculate_tax(pro.con, p_data, emp_id, pro.auth.ses.get("uid"))
    
    pro.con.go() # commit all changes

    pro.msg["ok"] = True
    pro.msg["data"] = tax
    pro.msg["msg"] = "Transaction Completed!"
    
  except Exception as er:
    print(er)
  
  finally:
    if pro.con:
      pro.con.close()

  if pro.auth:
    return pro.send()

# end the tax calcaulation

def auto_cal(req, res):
  
  con = None
  msg = { "ok": False, "msg": "Invalid Requests" }
  auth = None

  try:
    
    auth = Auth(req)
    if not auth.isAuth:
      msg["msg"] = "You are not authorized!"
      raise ValueError("You are not authorized!")
    
    data = auth.data

    if not "refid" in data:
      msg["msg"] = "Invalid Parameters!"
      raise ValueError("refid is required!")


    
    refid = data["refid"]

    con = sql()

    pstore = PayrollStore(con)
    payroll_info = pstore.info(refid)

    if payroll_info['status']:
      info_status = json_parse(payroll_info['status'])        
      if info_status[len(info_status) - 1]['step'] != 0:
        msg['msg'] = 'The Payroll already closed-!'
        raise ValueError('Already locked the payroll')

    if payroll_info['type'] == 'r':
      ac = AccessModel( con = con )
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-a-r']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())

    else:
      msg['msg'] = 'Process Not Available!'
      raise ValueError('Not available')

    emp_data = client_info(con, emp_status = payroll_info["type"])
    
    for item in emp_data:
      if item['active'] == 'y':
        is_ok, is_msg = SaveNCalulate(con, payroll_info, item["emp_id"], auth.ses.get("uid")) # connection, refid, emp_id
        if is_ok == False:
          msg["msg"] = f"Failed: {is_msg}"
          raise ValueError("error")


    msg["ok"] = True
    msg["msg"] = "Transaction Completed!"

    con.go() ## this is a final commit 

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)


def set_item(req, res):
  con = None
  auth = None

  msg = {
    'ok': 0,
    'msg': ''
  }
  
  try:
    auth: Auth = Auth(req)
    if not auth.isAuth:
      raise ValueError('You are not authorized!')
    data = auth.data
    
    if not 'emp_id' in data:
      raise ValueError('emp_id is required')
    
    if not 'late' in data:
      raise ValueError('late is required')
    
    if not 'work' in data:
      raise ValueError('work is required')
    
    if not 'payroll_refid' in data:
      raise ValueError('payroll_refid is required')
    
    if not 'absent' in data:
      raise ValueError('absent is required')
    
    if not 'undertime' in data:
      raise ValueError('undertime is required')
    
    if not "deduction_value" in data:
      raise ValueError("deduction value is required!")
      
    if not "is_update" in data:
      raise ValueError("is update is required!")
    
    con = sql()
    
    payrollModel = PayrollModel(con)
    info = PayrollStore(con)

    payinfo = info.info(data['payroll_refid'])
  
    info_status = payinfo['status']
    
    if info_status:
      info_status = json_parse(info_status)
      if info_status[len(info_status) - 1]['step'] != 0:
        msg['msg'] = 'The Payroll already closed!'
        raise ValueError('Already locked the payroll')

    status = payinfo['type']
    
    if not data['is_update']:
      # for create 
      if status == 'j':
        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['pm-3-j']):
          msg['msg'] = ac.errorAccess()
          raise ValueError(ac.errorAccess())
      elif status == 'c':
        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['pm-3-c']):
          msg['msg'] = ac.errorAccess()
          raise ValueError(ac.errorAccess())
      elif status == 'r':
        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['pm-3-r']):
          msg['msg'] = ac.errorAccess()
          raise ValueError(ac.errorAccess())
      else:
        msg['msg'] = 'Something went wrong!'
        raise ValueError('Something went wrong!')
    else:
      # for update roles
      if status == 'j':
        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['pm-3-j-u']):
          msg['msg'] = ac.errorAccess()
          raise ValueError(ac.errorAccess())
      elif status == 'c':
        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['pm-3-c-u']):
          msg['msg'] = ac.errorAccess()
          raise ValueError(ac.errorAccess())
      elif status == 'r':
        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['pm-3-r-u']):
          msg['msg'] = ac.errorAccess()
          raise ValueError(ac.errorAccess())
      else:
        msg['msg'] = 'Something went wrong!'
        raise ValueError('Something went wrong!')
      
    if not  payinfo["atm_info"]:
      msg["msg"] = "No default A.T.M account type setup in the payroll, this error cause by new update of the system, Please contact the developer for this message!"
      raise ValueError("No atm setup")
    
    atm_info = json_parse(payinfo["atm_info"])
    
    if atm_info == None: 
      msg["msg"] = "No atm information in payroll"
      raise ValueError("No atm Info")

    code = atm_info["code"]

    eba = EmpBankStore(con)
    if not eba.getAccount(emp_id = data["emp_id"], limit = 1, code = code):
      msg["msg"] = f"No Bank Account set! for {code}"
      raise ValueError("No Bank Account set!")

    from_t, to_t, emp_id = payinfo['from'], payinfo['to'], data['emp_id']

    from_t = datetime.datetime.strptime(from_t, '%Y-%m-%d').date()
    to_t = datetime.datetime.strptime(to_t, '%Y-%m-%d').date()
    delta = (to_t - from_t)
    
    if float(data['work']) > float(delta.days + 1):
      print("here")
      msg['msg'] = f'Number of Work days must not greater than {delta.days + 1}'

      raise ValueError('Work is to much')

    is_ok, rmsg = payrollModel.addItem(PayrollItemInterface(
      emp_id = data["emp_id"],
      late = data["late"],
      work = data["work"],
      payroll_refid = data["payroll_refid"],
      absent = data["absent"],
      undertime = data["undertime"],
      deduction_value = data["deduction_value"],
      is_update = data["is_update"],
      uid = auth.ses.get("uid")
    ))

    if is_ok:
      con.go()
      
    msg["ok"] = is_ok
    msg["msg"] = rmsg

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)


def remove_item(req, res):

  auth = None
  con = None
  msg = { "ok": False, "msg": "Invalid Request!"}
  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("you are not authorized!")

    data = auth.data

    if not "refid" in data:
      raise ValueError("refid is required")
    
    if not "emp_id" in data:
      raise ValueError("emp_id is required")
    # working with the database
    con = sql()
    pstore = PayrollStore(con)

    info = pstore.info(data['refid'])

    info_status = info['status']
    
    if info_status:
      info_status = json_parse(info_status)
      if info_status[len(info_status) - 1]['step'] != 0:
        msg['msg'] = 'The Payroll already closed!'
        raise ValueError('Already locked the payroll')

    status = info['type']
    
    if status == 'j':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-4-j']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    elif status == 'c':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-4-c']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    elif status == 'r':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-4-r']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    else:
      msg['msg'] = 'Something went wrong!'
      raise ValueError('Something went wrong!')

    qres = pstore.remove_item(data["refid"], data["emp_id"], auth.ses.get("uid"))
    if qres["ok"]:
      con.go()
      msg["msg"] = qres["msg"]
      msg["ok"]  = True

  except Exception as er:
    print(er)
  finally:
    if con: 
      con.close()
  
  if auth:
    return auth.send(msg)

def item_bank_update(req, res):

  auth = None
  msg = {
    "ok": False,
    "msg": None
  }

  con = None

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError("You are not authorized!")

    data = auth.data

    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-y-y']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    bank_model = BankModel(con, data, auth.ses.get("uid"))
    ok, res = bank_model.save()
    if ok:
      pstore = PayrollStore(con)
      
      # this part event the payroll is completed then check if is done or not for the ada
      # info = pstore.info(data['refid'])
      # if not info['status']:
      #   msg['msg'] = 'Payroll was already completed!'
      #   raise ValueError('Already process the payrolle')
      info = pstore.info(data["refid"])
      stat = info["status"]
      if stat:
        stat = json_parse(stat)
        last_stat = stat[len(stat) - 1]
        if last_stat["step"] == 5:
          msg["msg"] = "Ada Already approved!"
          raise ValueError("Already approved!")
      

      pstore.update_bank_info(data["refid"], data["emp_id"], data["bank_code"], data["account_number"])
      msg["msg"] = res
      msg["ok"] = True
    else:
      msg["msg"] = res
    con.go()

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()
  if auth:
    return auth.send(msg)


def get_info(req, res):
  auth = None
  con = None
  msg = {
    'ok': False,
    'msg': "Invalid Requests",
    'data': None
  }

  try:
    
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError('You are not signed in')
    data = auth.data

    if not "refid" in data:

      raise ValueError("refid is required!")
    
    refid = data["refid"]

    con = sql()

    pstore = PayrollStore(con)
    payroll_info = pstore.info(refid)

    if payroll_info["atm_info"]:
      payroll_info["atm_info"] = json_parse(payroll_info["atm_info"])

    if payroll_info["bank_info"]:
      payroll_info["bank_info"] = json_parse(payroll_info["bank_info"])

    if payroll_info["deduction_list"]:
      payroll_info["deduction_list"] = json_parse(payroll_info["deduction_list"])

    if payroll_info["signatory_list"]:
      payroll_info["signatory_list"] = json_parse(payroll_info["signatory_list"])

    msg["data"] = payroll_info


  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  return auth.send(msg) if auth else None

def get_item(req, res):
  auth = None
  con = None
  msg = {
    "ok": False,
    "msg": "Invalid Requests",
    "data": None
  }

  try:
    auth = Auth(req)
    if not auth.isAuth:
      msg["msg"] = "You are not sign in"
      raise ValueError("you are not signed in")

    data = auth.data

    if not "refid" in data:
      raise ValueError("refid is required!")
    
    if not "emp_id" in data:
      raise ValueError("emp_id is required!")
    
    con = sql()

    pstore = PayrollStore(con)
    item = pstore.getOneItem(data["refid"], data["emp_id"])

    payroll_info = pstore.info(data["refid"])
    data = payslip(item[0], json_parse(payroll_info["deduction_list"]) , payroll_info)
    msg['data'] = data
    msg["ok"] = True
    msg["msg"] = "Transaction Completed!"

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  return auth.send(msg) if auth else None
  

def get_items(req, res):
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
      raise ValueError('You are not signed in')
    data = auth.data

    if not 'refid' in data:
      raise ValueError('refid is required!')

    search = ""
    dept_id = ""
    # parameters
    if "search" in data:
      search = data["search"]

    if "dept_id" in data:
      dept_id = data["dept_id"]
    # end parameters

    refid = data['refid']

    con = sql()

    ac = AccessModel(con = con)
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-3-v-a']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    pstore = PayrollStore(con)
    items = pstore.get_item(refid, {"search": search, "dept_id": dept_id, "is_order": True})
    

    payroll_info = pstore.info(refid)
    for item in items:
      data = payslip(item, json_parse(payroll_info["deduction_list"]) , payroll_info)
      msg['data'].append(data)
    msg['ok']  = 1
    msg['msg'] = 'Transaction Completed!'
    
  except Exception as er: 
    print(er)

  finally:

    if con:
      con.close()

  if auth:
    return auth.send(msg)

# default signatory in payroll
def default_sign_load(req, res):
  auth, con, msg = (None, None, {'ok': False, 'msg': '', 'data': None})
  try:
    auth = Auth(req)
    
    is_auth, data = (auth.isAuth, auth.data)
    if not is_auth: raise ValueError('You are not authorized!')
    
    if not 'refid' in data: raise ValueError('refid is required!')
    if not 'dept_id' in data: raise ValueError('dept_id is required!')

    refid, dept_id = (data['refid'], data['dept_id'].strip())
    dept_id = dept_id if dept_id else 'all' # default

    con = sql()

    def_sign = DefaultPayrollSignatoryStore(con)  
    rdata = def_sign.load(refid, dept_id)

    # custome payroll signatory is here then use the the custom payroll design
    if rdata:
      msg['data'] = json_parse(rdata[0]['data'])
    else:
      pinfo = PayrollStore(con)
      rinfo = pinfo.info(refid)
      if rinfo:
        msg['data'] = json_parse(rinfo['signatory_list'])

    msg['ok'] = True
    msg['msg'] = 'Transaction Completed!'

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)


def default_sign_submit(req, res):
  auth, con, msg = (None, None, {'ok': False, 'msg': ''})
  try:
    auth = Auth(req)
    
    is_auth, data = (auth.isAuth, auth.data)
    if not is_auth: raise ValueError('You are not authorized!')
    
    if not 'data' in data: raise ValueError('data is required')
    if not 'dept_id' in data: raise ValueError('dept_id is required')
    if not 'refid' in data: raise ValueError('refid is required')

    _data, refid, dept_id = (data['data'], data['refid'], data['dept_id'].strip())

    dept_id = dept_id if dept_id else 'all' # default value to all
    
    con = sql()

    ac = AccessModel(con = con)
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-8']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    pstore = PayrollStore(con)
    pinfo = pstore.info(refid)

    if pinfo['status']:

      stat = json_parse(pinfo['status'])
      if stat[len(stat) - 1]['step'] == 0:
        pass
      else:
        msg['msg'] = 'Payroll already closed'
        raise ValueError('Payroll already closed!')

    if dept_id == 'all':
      con.commit('update payroll set signatory_list = ? where refid = ?', (json_stringify(_data), refid, ))
    else:
      def_sign = DefaultPayrollSignatoryStore(con, uid = auth.ses.get('uid'))  
      def_sign.save(refid, dept_id, _data)
    con.go() # commit all changes

    msg['msg'] = 'Saved'
    msg['ok'] = True

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)

# payroll info

def payroll_info(req, res):
  auth, con, msg = (None, None, {"ok": False, "msg": "", "data": None})
  try:
    auth = Auth(req)
    data, is_auth = (auth.data, auth.isAuth)
    if not is_auth: raise ValueError("you are not authorized!")
    if not "refid" in data: raise ValueError("refid is required!")
    refid = data["refid"]
    
    con = sql()

    ps = PayrollStore(con)
    res = ps.info(refid = refid)
    lst = json_parse(res["deduction_list"])

    msg["data"] = lst
    msg["ok"] = True

  except Exception as er:
    print(er)

  finally:
    if con: con.close()
  if auth: return auth.send(msg)

def get_ded_default(req, res):

  auth, con, msg = (None, None, {"ok": False, "msg": "", "data": None})
  

  try:

    auth = Auth(req)
    if not auth.isAuth:
      msg["msg"] = "You are not sign in"
      raise ValueError("You are not signed in")


    data = auth.data

    if not "refid" in data: 
      raise ValueError("refid is required!")
    
    if not "emp_id" in data:
      raise ValueError("emp_id is required!")
    
    refid = data["refid"]
    emp_id = data["emp_id"]

    con = sql()

    ps = PayrollStore(con)
    pinfo = ps.info(refid = refid)
    ded_list = json_parse(pinfo["deduction_list"])

    deduction_value = []
    

    res = SaveNCalulate(con, pinfo, emp_id, auth.ses.get("uid"), True)

    if res[0]:
      deduction_value = res[1]
    
    msg["data"] = deduction_value
    msg["ok"] = True
    msg["msg"] = "Transaction Completed!"

  except Exception as er:
    print(er)
  finally:
    if con: con.close()
  
  return auth.send(msg) if auth else None

def payroll_info_update(req, res):
  auth, con, msg = (None, None, {"ok": False, "msg": ""})
  try:
    auth = Auth(req)
    payload, is_auth = (auth.data, auth.isAuth)
    if not is_auth: raise ValueError("You are not authorized!")
    if not "refid" in payload: raise ValueError("refid is required!")
    if not "data" in payload: raise ValueError("data is required!")
    refid, data = (payload["refid"], payload["data"])
  
    con = sql()

    ac = AccessModel(con = con)
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-8-1']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    ps = PayrollStore(con)
    ps.update_deduction_payroll_item(refid = refid, deduction_list = data)
    ps.update_deduction_payroll(refid = refid, deduction_list = data) 
    
    con.go()

    msg["msg"] = "Transaction Completed!"
    msg["ok"] = True

  except Exception as er:
    print(er)
  finally:
    if con: con.close()
  if auth: return auth.send(msg)

# end default signatory in payroll

def payroll_print(req, res):
  auth = None
  con = None
  msg = {
    'ok': 0,
    'msg': '',
    'data': '',
    'payroll_info': '',
    'action': []
  }

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError('You are not signed in')
    data = auth.data

    if not 'refid' in data:
      raise ValueError('refid is required!')

    if not "dept_id" in data:
      raise ValueError("dept_id is required")

    dept_id = data["dept_id"]
    refid = data['refid']

    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-6']):
      msg['msg'] = ac.errorAccess()
      msg['data'] = ac.errorAccess()
      msg['ok'] = True
      raise ValueError(ac.errorAccess())

    payroll_type = req.query.get('type')

    print_obj = PayrollPrintHandler(con, uid = auth.ses.get('uid'), payroll_type = payroll_type)
    ok, msg_01 = print_obj.init(refid  = refid, dept_id = dept_id)
    if not ok:
      msg['msg'] = msg_01
      raise ValueError(msg_01)
    


    pstore = PayrollStore(con)
    pinfo = pstore.info(refid)

    if payroll_type == 'print':
      if pinfo['status']:
        __stat = json_parse(pinfo['status'])

        if __stat[len(__stat) - 1]['step'] == 5:
          if not ac.hasAccess(auth.ses.get('uid'), ['a-j-1']):
            msg['msg'] = 'You can only view this printing is not allowed, Transaction already done!'
            raise ValueError('You cant print the payroll it already done,, you can only view it!')

      
    
    pinfo['bank_info'] = json_parse(pinfo['bank_info'])
    pinfo['deduction_list'] = json_parse(pinfo['deduction_list'])
    pinfo['signatory_list'] = json_parse(pinfo['signatory_list'])

    ###########################################################
    # end Generated signatory
    ###########################################################
    
    msg['payroll_info'] = pinfo
    msg['data'] = print_obj.output()
    msg['ok']  = 1
    msg['msg'] = 'Transaction Completed!'
    msg['action'] = print_obj.action()

  except Exception as er: 
    print(er)

  finally:

    if con:
      con.close()

  if auth:
    return auth.send(msg)

# approving the payroll signature by digital
def payroll_digital_sign_apr(req, res):
  auth, con, msg = None, None, {'ok': False, 'msg': ''}
  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError('You are not signed in')
    data = auth.data

    if not 'refid' in data:
      raise ValueError('refid is required!')

    if not "dept_id" in data:
      raise ValueError("dept_id is required")

    if not 'sign_key' in data: raise ValueError('sign_key is required!')

    refid, dept_id, sign_key = data['refid'], data['dept_id'], data['sign_key']

    con = sql()
    payroll = PayrollStore(con)

    pinfo = payroll.info(refid)

    stat = pinfo['status']

    if stat:
      stat = json_parse(stat)
      if stat[len(stat) - 1]['step'] == 6:
        pass
      else:
        msg['msg'] = 'This transaction is not yet active, please wait for other transaction'
        raise ValueError('The Payroll is not available for signature')

    k, m = payroll.digital_approve(refid, dept_id, auth.ses.get('uid'))
    con.go() # uncomment this for debuuging
    
    msg['ok'] = k
    msg['msg'] = m

  except Exception as er:
    print(er)
  finally: 
    if con: con.close()

  if auth: return auth.send(msg)


def view_ada(req, res):
  con = None
  auth = None
  msg = {
    "ok": False,
    "msg": None,
    "data": None
  }
  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError('You are not signed in')
    data = auth.data

    if not 'refid' in data:
      raise ValueError('refid is required!')

    if not "dept_id" in data:
      raise ValueError("dept_id is required")
    
    # if not 'fund' in data: raise ValueError('fund is required!')


    # fund = data['fund']
    dept_id = data["dept_id"]
    refid = data['refid']

    con = sql()
    pstore = PayrollStore(con)
    items = pstore.get_item(refid, {
      "dept_id": dept_id,
      "is_order": True
    })
 
    # ob_data = ob_r.get_ob_by_code_type(refid, fund)

    payroll_info = pstore.info(refid)
    ded_list = json_parse(payroll_info["deduction_list"])
    
    emp_type = payroll_info['type']
    

    ada_list = []

    for item in items:
      slip = payslip(item, ded_list, payroll_info)
      other_info = json_parse(item["other_info"])

      net = slip['net']
      if emp_type == 'r':
        net = slip['net'] / 2.0


      ada_list.append({
        "emp_id": item["emp_id"],
        "name": slip["name"],
        "net": f'{net:,.2f}',
        "acc": other_info.get("acc"),
        "acc_type": other_info.get("acc_type")
      })

    msg["data"] = ada_list
    msg["ok"] = True

  except Exception as er:
    print(er)

  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)


def generate_ada_number():
  year, month, day = date_time().split('-')
  
  return '20234-01-01'

# Obligation Check List

def ob_check_list(req, res):
  con, auth, msg = (None, None, {'ok': False, 'msg': '', 'data': None})
  try:
    auth = Auth(req)
    is_auth, payload = (auth.isAuth, auth.data)
    if not is_auth: raise ValueError('Not Authorized!')
    if not 'refid' in payload: raise ValueError('refid is required!')
    refid = payload['refid']
    con = sql()
    dept = Department(con)
    
    dept_list = dept.lists()
    
    ob = Ob_R(con)

    ret = []

    for item in dept_list:
      ids, code, name = item # unpacked
      ob_data = ob.getOb(payroll_code = refid, dept_id = ids)
      ret.append({
        'dept_id': ids,
        'dept_code': code,
        'dept_name': name,
        'has_ob': True if ob_data['ob_no'] else False
      })
    msg["ok"] = True
    msg["data"] = ret
    
  except Exception as er:
    print(er)
  finally: 
    if con: con.close()
  
  if auth: return auth.send(msg)

# obligation load
def ob_load(req, res):
  con, auth, msg = (None, None, {'ok': False, 'msg': '', 'data': None})
  try:
    auth = Auth(req)
    is_auth, payload = (auth.isAuth, auth.data)
    if not is_auth: raise ValueError('Not Authorized!')

    payroll_code = payload.get('payroll_code', None)
    dept_id = payload.get('dept_id', None)
    type_t = payload.get('type', None)

    con = sql()
    ob = Ob_R(con)
    
    data = ob.getOb(payroll_code = payroll_code, dept_id = dept_id, type_t = type_t)

    msg['data'] = data
    msg['ok'] = True
    msg['msg'] = 'Trnasaction Completed!'

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)


# ada closing

def ada_close(req, res):
  con, auth, msg = None, None, {"ok": False, "msg": ""}
  try:
    auth = Auth(req)
    is_auth, payload = auth.isAuth, auth.data
    if not is_auth: raise ValueError("You are not authorized!")

    if not "username" in payload: raise ValueError("username is required!")
    if not "password" in payload: raise ValueError("password is required!")
    if not "refid" in payload: raise ValueError("refid is required!")
    if not "remark" in payload: raise ValueError("remark is required!")
    
    username, password, refid, remark = payload["username"], payload["password"], payload["refid"], payload["remark"]

    susername = auth.ses.get('username')

    print("pass")

    if not ( username == susername ):
      msg['msg'] = 'username dont match!'
      raise ValueError('user name does not match')
    
    con = sql()

    user_model = UserModel()
    user_model._setConnection(con)

    user = user_model.authenticate(username, password)
    if not user:
      msg['msg'] = 'Username or Password incorrect!'
      raise ValueError('worng username and password')
    
    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get("uid"), ["pm-7-1"]):
      msg["msg"] = "You Are not Authorized!"
      raise ValueError("You are not authorized!")

    pstore = PayrollStore(con)
    info = pstore.info(refid = refid)
    
    if not info:
      msg["msg"] = "Payroll not found"
      raise ValueError("Payroll not found! please refresh the browser")

    if not info["status"]:
      msg["msg"] = "The Payroll Must need to close first!"
      raise ValueError("Invalid ")

    status = json_parse(info["status"])

    last = status[len(status) - 1]

    if last["step"] == 5:
      msg["msg"] = "Already Approved!"
      raise ValueError("Already Approved!")
    
    if last["step"] != 4:
      msg["msg"] = "This process is not allowed! please check the payroll if it is not closed or ob is not closed"
      raise ValueError("This process is not allowed")
    
    pstore.closeAda(refid, auth.ses.get("user"), remark, user["name"], status)

    con.go()

    msg["msg"] = "Transaction Completed!"
    msg["ok"] = True 

  except Exception as er:
    print(er)
  finally:
    if con: con.close()
  
  if auth: return auth.send(msg)

# obligation closing
def ob_close(req, res):
  con, auth, msg = None, None, {"ok": False, "msg": ""}
  try:
    auth = Auth(req)
    is_auth, payload = auth.isAuth, auth.data
    if not is_auth: raise ValueError("You are not authorized!")

    if not "username" in payload: raise ValueError("username is required!")
    if not "password" in payload: raise ValueError("password is required!")
    if not "refid" in payload: raise ValueError("refid is required!")
    if not "remark" in payload: raise ValueError("remark is required!")
    
    username, password, refid, remark = payload["username"], payload["password"], payload["refid"], payload["remark"]

    susername = auth.ses.get('username')

    if not ( username == susername ):
      msg['msg'] = 'username dont match!'
      raise ValueError('user name does not match')
    
    con = sql()

    user_model = UserModel()
    user_model._setConnection(con)

    user = user_model.authenticate(username, password)
    if not user:
      msg['msg'] = 'Username or Password incorrect!'
      raise ValueError('worng username and password')
    
    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get("uid"), ["pm-9-c"]):
      msg["msg"] = "You Are not Authorized!"
      raise ValueError("You are not authorized!")

    pstore = PayrollStore(con)
    info = pstore.info(refid = refid)
    
    if not info:
      msg["msg"] = "Payroll not found"
      raise ValueError("Payroll not found! please refresh the browser")

    if not info["status"]:
      msg["msg"] = "The Payroll Must need to close first!"
      raise ValueError("Invalid ")

    status = json_parse(info["status"])

    last = status[len(status) - 1]

    if last["step"] == 4:
      msg["msg"] = "Obligation Request already close"
      raise ValueError("Obligation already close!")
    
    if last["step"] != 2:
      msg["msg"] = "This process is not allowed! please check the payroll if it is not closed or if the ob is already close"
      raise ValueError("This process is not allowed")
    
    pstore.closeOb(refid, auth.ses.get("user"), remark, user["name"], status)

    con.go()

    msg["msg"] = "Transaction Completed!"
    msg["ok"] = True 

  except Exception as er:
    print(er)
  finally:
    if con: con.close()
  
  if auth: return auth.send(msg)

# Obligation update
def ob_update(req, res):
  con, auth, msg = (None, None, {'ok': False, 'msg': ''})
  try:
    auth = Auth(req)
    is_auth, payload = (auth.isAuth, auth.data)

    
    if not is_auth: raise ValueError('Not Authorized!')
    
    dept_id = payload.get('dept_id', "")

    if not dept_id:
      msg["msg"] = "Please select deparment"
      raise ValueError("Please Select Department")

    ob = ObEntity(
      ob_no = payload.get('ob_no', None),
      fund_code = payload.get('fund', None),
      particular = payload.get('particular', None),
      account_code = payload.get('account_code', None),
      fpp = payload.get('fpp', None),
      payroll_code = payload.get('payroll_code', None),
      dept_id = dept_id,
      head_name = payload.get('head_name'),
      head_pos = payload.get('head_pos'),
      type_t = payload.get('type', None),
      sign_id = payload.get('sign_id', None)
    )
    
    #{'particular': 'JANITORIAL SERVICES', 'account_code': '1071', 'fpp': '101', 'payroll_code': '20240014062107', 'dept_id': '1000'}
    
    con = sql()
    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-9-u']):
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    # pm-9

    pstore = PayrollStore(con)
    info = pstore.info(refid = ob.payroll_code)
    if not info: raise ValueError("Payroll Not found")
    
    if info["status"]:
      status = json_parse(info["status"])
      last = status[len(status) - 1]

      # if last['step'] == 6:
      #   msg["msg"] = "You cant update right now, the payroll is still in review & signatories!"
      #   raise ValueError("You cant update right now, the payroll is still in signaturies and review")


      # if last["step"] != 2:
      #   msg["msg"] = "Not Allowed! Obligation already closed!"
      #   raise ValueError("Numbering is not allowed! or already done")

      if last['step'] == 5:
        msg['msg'] = 'Transaction Failed! Payroll Ada or Payroll file already Approved from bank!'
        raise ValueError('Aad already approved!')
      
      if last["step"] == 0 or last['step'] == 6 or last['step'] == 2:
        pass
      else:
        msg['msg'] = 'Transaction Failed!'
        raise ValueError('FAiled')

    obr = Ob_R(con)
    obr.update(ob)
    con.go()
    
    msg['ok'] = True
    msg['msg'] = 'Transaction Completed!'

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)

def print_ob(req, res):
  con, auth, msg = (None, None, {'ok': False, 'msg': '', 'data': ''})
  try:
    auth = Auth(req)
    is_auth, data = (auth.isAuth, auth.data)
    if not is_auth: raise ValueError('Not Authorized!')
    if not 'refid' in data: raise ValueError('refid is required')
    if not 'dept_id' in data: raise ValueError('dept_id is required')
    refid = data["refid"]
    dept_id = data["dept_id"]
    type_t = data.get('type')

    con = sql()


    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-9']):
      msg['msg'] = ac.errorAccess()
      msg['data'] = ac.errorAccess()
      msg['ok'] = True
      raise ValueError(ac.errorAccess())
    
    v = req.query.get("v")
    if not v: raise ValueError("not query v found!")

     

    pstore = PayrollStore(con)
    payroll_info = pstore.info(refid)
    payroll_type = payroll_info['type']

    if v == "print":
      # when print button is clicked from the clients
      if payroll_info['status']:
        _remark = json_parse(payroll_info['status'])
        if _remark[len(_remark) - 1]['step'] == 5:
          if not ac.hasAccess(auth.ses.get('uid'), ['mp-1-a']):
            msg['msg'] = 'View Only, you cant reprint it it, payroll already done!'
            raise ValueError('Ob View Only cant be reprinted!')

    _from, _to = (payroll_info['from'], payroll_info['to'])
    from_arr, to_arr = (_from.split('-'), _to.split('-'))

    
    pay_info = f'{month_name(int(from_arr[1]) - 1)} {from_arr[2]} - {to_arr[2]}, {to_arr[0]}'


    ded_list = json_parse(payroll_info["deduction_list"])
    
    dept_name = "All Office"

    dept_obj = Department(con)
    dept_info = dept_obj.lists({
      "dept_id": dept_id
    })   

    if dept_info:
      if dept_id:
        dept_name = f"{dept_info[0][1]} - {dept_info[0][2]}"
    
    items = pstore.get_item(refid, {
      "dept_id": dept_id,
      "is_order": False
    })

    total_salary = 0.0

    payee_name = ""
    for item in items:
      
      # payee_name must be retrieved at first
      if not payee_name:
        emp_info = json_parse(item["emp_info"])
        payee_name = f"""{emp_info["p"]} {emp_info["f"]} {emp_info["m"]} {emp_info["l"]} {emp_info["e"]} {emp_info["p"]} ET.AL""".upper()

      slip = payslip(item, ded_list, payroll_info)
      total_salary += slip['gross']

      if payroll_info["type"] == "r":
        # for payroll regular employee
        total_salary += slip["gov_share"]



    # if payroll_type == 'r': total_salary /= 2 # if it is regular then divided it to 2

    ob = Ob_R(con)
    ob_info = ob.getOb(refid, dept_id, type_t)

    account_code = ''
    fpp = ''
    head_name, head_pos = ('', '')
    ob_no = ''
    particular = ''
    sign_id = ''

    if ob_info:
      account_code = ob_info['account_code']
      fpp          = ob_info['fpp']
      head_name    = ob_info['head_name'].upper()
      head_pos     = ob_info['head_pos'].upper()
      ob_no        = ob_info['ob_no']
      particular   = ob_info['particular']
      sign_id      = ob_info['sign_id']

    head_sign = None
    budget_sign = None

    if sign_id:
      con2 = None
      try:
        con2 = sql_signature()
        
        ds = DigitalStore(con2)
        head_sign = ds.get_byte(sign_id)
        budget_sign = ds.get_byte('8073E2ADE9F4F81B0A99D564BB19EF55') # now we just make a default for signatory
      except Exception as er:
        print(er)
      finally:
        if con2: con2.close()

      #load the signatory

    head_sign_img = ''
    if head_sign:
      head_sign_img = f'''<img src="{head_sign}" style="position: absolute; width: 150px; height: 75px; object-fit: cover; top: -50px; left: 25px;" />'''

    budget_img = ''
    if budget_sign:
      budget_img = f'''<img src="{budget_sign}" style="position: absolute; width: 150px; height: 75px; object-fit: cover; top: -50px; left: 70px;" />'''

    html = f'''
      <style>
      .tbl01 {{
        border-collapse: collapse;
          width: 100%;
        }}

        .tbl01 tr th, .tbl01 tr td {{
          text-align: left;
          padding: 4px;
          border:1px solid grey;
          font-size: 11px;
        }}

        .tbl01 tr:nth-child(even) {{
          background-color: #D6EEEE;
        }}
        
      </style>
      <center><div>Republic of the Philippines</div></center>
      <center><div>Province of Bohol</div></center>
      <center><div>Municipality of Test</div></center>

     
      <table class="tbl01">
        <tr>
          <td><center><b style="letter-spacing: 3px;">OBLIGATION REQUEST</b></center></td>
          <td style="width: 150px;">No. <b>{ ob_no }</b></td>
        </tr>
      </table>
      <table class="tbl01">
        <tr>
          <td style="width: 100px;">Payee/Office</td>
          <td>{payee_name}</td>
        </tr>
        <tr>
          <td style="width: 100px;">Office</td>
          <td>{dept_name}</td>
        </tr>
        <tr>
          <td style="width: 100px;">Address</td>
          <td>test municipal</td>
        </tr>
        <tr>
          <td style="width: 100px;">Payee/Office</td>
          <td></td>
        </tr>
      </table>
      <table class="tbl01">
        <tr>
          <td style="width: 100px;">Responsibility Center</td>
          <td style="width: 200px;"><center><b>Particulars</b></center></td>
          <td>F.P.P</td>
          <td>Account Code</td>
          <td>Amount</td>
        </tr>
        <tr>
          <td style="width: 100px; height: 200px;">{account_code}</td>
          <td style="width: 200px;">
            <center><b>{particular}</b></center>
            <center><b>{pay_info}</b></center>
          </td>
          <td>{fpp}</td>
          <td>{account_code}</td>
          <td style="font-size: 20px; font-weight: bold;"><center>P {total_salary:,.2f}</center></td>
        </tr>
      </table>
      <table class="tbl01">
        <tr>
          <td style="width: 309px;">
             <div>A. Certified</div> 
             <div>           Charges to appropriation/allotment necessary, lawful</div>
             <div>           Supporting documents valid, proper and legal</div>
          </td>
          <td>
            <div>B. Certified</div>
            <div>          Existence of available appropriation</div>
          </td>
        </tr>
      </table>

      <table class="tbl01">
        <tr>
          <td style="width: 100px;">Signatory</td>
          <td style="width: 200px;"></td>
          <td>Signatory</td>
          <td></td
        </tr>

        <tr>
          <td style="width: 100px;">Name</td>
          <td style="width: 200px;">
            <div style="position: relative; width: 200px;">
              <center>{head_sign_img}</center>
              <center><b>{head_name}</b></center></center>
            </div>
          </td>
          <td>Name</td>
          <td style="width: 300px;">
            <div style="position: relative; width: 300px;">
              <center>{budget_img}</center>
              <center><b>Rodney Rasonabe</b></center>
            </div>
          </td>
        </tr>
        <tr>
          <td style="width: 100px;">Position</td>
          <td style="width: 200px;"><center>{head_pos}<br />Head/Requesting Office/Authorized Representative</center></td>
          <td>Position</td>
          <td><center>Municipal Budget Officer<br />Head, Budget Unit/Authorized Representative</center></td>
        </tr>
        <tr>
          <td style="width: 100px;">Date</td>
          <td style="width: 200px;"></td>
          <td>Date</td>
          <td></td
        </tr>
      </table>
    
    '''

    msg['ok'] = True
    msg['msg'] = 'Transaction Completed!'
    msg['data'] = html
  except Exception as er:
    print(er)
  finally:
    if con: con.close()
  
  if auth: return auth.send(msg)



# get ada number

def ada_get_number(req, res):
  auth, con, msg = None, None, {"ok": False, "msg": "", "data": ""}
  try:
    auth = Auth(req)
    isAuth, payload = auth.isAuth, auth.data
    if not isAuth: 
      raise ValueError("You are not authorized!")
    
    if not "refid" in payload: raise ValueError("refid is required!")
    if not "fund" in payload: raise ValueError("fund is required!")

    refid, fund = payload["refid"], payload["fund"]

    con = sql()

    bank = BankAda(con).get(refid, fund)
    if bank:
      msg["data"] = bank[0][0]

    msg["ok"] = True
    msg["msg"] = "Transaction Completed!"    
    
  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)

# update the ada no

def ada_update_no(req, res):
  auth, con, msg = None, None, {"ok": False, "msg": ""}
  try:
    auth = Auth(req)
    isAuth, payload = auth.isAuth, auth.data
    if not isAuth: 
      raise ValueError("You are not authorized!")
    
    if not "refid" in payload: raise ValueError("refid is required!")
    if not "ada_no" in payload: raise ValueError("ada_no is required!")
    if not "fund" in payload: raise ValueError("fund is required!") 

    dept_id = "" # this is per department not yet supported!
    
    refid, ada_no, fund = payload["refid"], payload["ada_no"], payload["fund"]
    con = sql()

    ac = AccessModel( con )
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-6-0']):
      msg['ok'] = False
      msg['msg'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    ob_r = Ob_R(con)

    ob_data = ob_r.get_ob_by_code_type(refid, fund)

    pstore = PayrollStore(con)
    payroll_info = pstore.info(refid)
    if not payroll_info:
      msg["msg"] = "Payroll not found!"
      raise ValueError("payroll not found!")
    
    stat = payroll_info["status"]

    if not stat:
      msg["msg"] = "Payroll is still processing"
      raise ValueError("Sorry you cant add number of ada while the payroll is still processing!")
    
    stat = json_parse(stat)

    last_stat = stat[len(stat) - 1]
    if not (last_stat["step"] == 4):
      msg["msg"] = "Error. Maybe the obligation request is not yet close"
      raise ValueError("You cant still add ada number. maybe the obligation request is not close yet")
    
    items = pstore.get_item(refid, {
      "dept_id": dept_id,
      "is_order": False
    })

    ded_list = json_parse(payroll_info["deduction_list"])

    res = []
    for item in items:
      slip = payslip(item, ded_list, payroll_info)
      other_info = json_parse(item["other_info"])
      ref = ""
      if "acc" in other_info:
        ref = other_info["acc"]

      # filter out all the only with the obR
      if _is_ada_exists(ob_data = ob_data, dept_id = item['dept_id']):
        res.append({
          "ref": ref,
          "name": slip["name"],
          "net": slip["net"]
        })
    
    bank = BankAda(con = con)
    try:
      ok = bank.save(refid, fund, ada_no, res, auth.ses.get("uid"))
    except Exception as er:
      msg["msg"] = "Ada Number already used!"
      raise ValueError(er)
    
    con.go()
    msg["msg"] = ok
    msg["ok"] = True

  except Exception as er:
    print(er)

  finally:
    if con: con.close()
  
  if auth: return auth.send(msg)

def _is_ada_exists(ob_data, dept_id) -> bool:
  for item in ob_data:
    if item['dept_id'] == dept_id: return True
  return False  



def payroll_file_download(req, res):

  bank_account_no = {
      '01': ('0708-03976A-030', "GENERAL_FUND"), # general fund,
      '02': ('0708-03976R-030', "SEF_FUND"), #
      '03': ('0708-03976C-030', "TRUSH_FUND") # trust fund
  }

  auth, con, msg = None, None,  {
    "ok": False,
    "msg": "",
    "data": "",
    "file": ""
  }

  try:
    auth = Auth(req)

    if not auth.isAuth: raise ValueError("You are not authorized!")

    data = auth.data
    
    if not "refid" in data: raise ValueError("refid is required")

    if not "dept_id" in data: raise ValueError("dept_id is required")

    if not 'fund' in data: raise ValueError('fund is not found')
    

    refid = data["refid"]
    dept_id = data["dept_id"]
    fund = data['fund']

    if not fund in bank_account_no:
      msg["msg"] = "Invalid Fund, Select A Valid fund"
      raise ValueError("Invalid Fund")

    if str(dept_id).strip():
      msg["msg"] = "Not yet supported!"
      raise ValueError("Not supported yet") 
    # retrieve the data based on the fundings

    con = sql()
    

    ac = AccessModel( con )
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-7']):
      msg['ok'] = False
      msg['msg'] = ac.errorAccess()
      msg['data'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())
    
     # render the obr 
    # since the ada is based on the budget from the ob-r or obligation requests
    ob_r = Ob_R(con)

    ob_data = ob_r.get_ob_by_code_type(refid, fund)

    

    pstore = PayrollStore(con)
    
    payroll_info = pstore.info(refid)

    payroll_type = payroll_info['type']    
    info_status = []
    if payroll_info['status']:
      info_status = json_parse(payroll_info['status'])

      last_status = info_status[len(info_status) - 1]
      if last_status['step'] == 5:
        msg['msg'] = 'Already closed, you cant redownload the payroll file!'
        raise ValueError('Already closed, you cant redownload the payroll file')
        
      # if last_status['step'] != 4:
      #   msg['msg'] = 'Not Ready for payroll file obligation requests must be close or approved'
      #   raise ValueError('Not ready for payroll file or obligation requests')

      if last_status['step'] == 7:
        pass
      else:
        msg['msg'] = 'Not ready for download! please click on proceed to download button to lock the editing and update of the payroll'
        raise ValueError('Not ready for download!')

    else:
      msg['msg'] = 'Not Ready for payroll file obligation requests must be close or approved'
      raise ValueError('Not ready for payroll file')

    # if not info_status:
    #   msg['ok'] = True
    #   msg['msg'] = 'The Payroll already closed!'
    #   msg['data'] = 'You cant print the ada if the payroll is ongoing'
    #   raise ValueError('Already locked the payroll')

    bank_info = json_parse(payroll_info["bank_info"])

    head_info = bank_info["branch"]["head"]

    ada_sign = bank_info["ada_sign"]


    if not payroll_info:
      msg["msg"] = "Payroll not found!"
      raise ValueError("Payroll not found")
    
    _from = payroll_info["from"].split("-")
    _to   = payroll_info["to"].split("-")

    items = pstore.get_item(refid, {
      "dept_id": dept_id,
      "is_order": False
    })

    qr = Qr(str(refid) + "." + str(dept_id))
    ded_list = json_parse(payroll_info["deduction_list"])

    res = []

    total_net = 0.0

    for item in items:
      slip = payslip(item, ded_list, payroll_info)
      other_info = json_parse(item["other_info"])
      ref = ""
      if "acc" in other_info:
        ref = other_info["acc"]

      # filter out all the only with the obR
      if _is_ada_exists(ob_data = ob_data, dept_id = item['dept_id']):
        emp_info = json_parse(item["emp_info"])
        res.append({
          "ref": ref,
          "name": slip["name"],
          "net": slip["net"],
          "fname": emp_info
        })
        total_net += float(slip["net"])

      #print(slip)

    #--> 001 if payroll_type == 'r': total_net /= 2
    
    over_all = total_net

    total_net = '{:.2f}'.format(float(over_all))

    net = total_net.split(".")
    
    peso = int(net[0])
    cent = int(net[1])

    nword = int_to_word(peso) 
    nword = nword.strip().strip(",") + " pesos"
    if cent > 0:
      nword += " & " + int_to_word(cent) + " centavos"

    nword += ' only'

    com_name = 'Test'
    period = f'{month_name(int(_from[1]) - 1)} {_from[2]}-{_to[2]}, {_from[0]}' # date period


    tahod = ""
    if head_info["g"] == "m":
      tahod = "SIR"

    elif head_info["g"] == "f":
      tahod = "MA'AM"


    emp_type = payroll_info['type']

    print_t = req.query.get('print', '0') # if print equal to 0 then it is a view only, if it is 1 then i generate the ada number
    
    ada_no = 'Draft Mode|Not Accepted'
    
    abank = BankAda(con).get(refid = refid, fund = fund)

    # early close the connection for better performance
    con.close()
    con = None
    
    ada_no = abank[0][0] if abank else "Please add ada number" # generate the ada number here every time print is trigger

    ada_date = abank[0][1] if abank else "" # date

    file_name = f"""PAYROLL-FILE-{ "Regular" if payroll_type == "r" else "Casual" }-{period}"""

    file_name =  file_name.replace(',', '-').replace(' ', '').upper()
    # implementation for DBP ADA
    g_items = [

    ]

    for item in res:
      net = item['net']
      #--> 001 if emp_type == 'r': net = item['net'] / 2.0 # if  regular then divide the ada to two
      
      iref, iname, inet, fname = item["ref"], item["name"], f"{net:.2f}", item["fname"]

      g_items.append({
        'ref': iref,
        'name': iname.replace('  ', ' ').replace('   ', ' ').replace('     ', ' ').upper(),
        'amount': inet,
        "fname": fname
      })

    # sorting ascending base on the name
    g_items.sort(key = lambda x: x['name'])

    # create a prn
    _, fund_name = bank_account_no[fund]
    prn_path = f'data{os.sep}tmp{os.sep}{fund_name}-{refid}-{file_name}.prn'
    txt_path = f'data{os.sep}tmp{os.sep}{fund_name}-{refid}-{file_name}.txt'
    excel_path = f'data{os.sep}tmp{os.sep}{fund_name}-{refid}-{file_name}.xlsx'

    fp = open(prn_path, 'w')
    fp2 = open(txt_path, 'w')

    try:
      for item in g_items:
        ref, name, net = str(item['ref']), item['name'], str(item['amount'])

        prn_line = f'{ref[:10]: <10}{name[:50]: <50}{float(net[:11]): <11}'
        txt_line = f'{ref[:13]: <13}{name[:50]: <50}{float(net[:11]): <11}'

        fp.write(prn_line + '\n')
        fp2.write(txt_line + '\n')
    except Exception as er:
      print(er)

    fp.close()
    fp2.close()

    # creating the DBP raw excel for the automation of the ada excel
    # dbp excel row file with 7 column
    wb = Workbook()
    
    w1 = wb.worksheets[0]
    w1["A1"] = "Employee's First Name"
    w1["B1"] = "Employee's Middle Name"
    w1["C1"] = "Employee's Last Name"
    w1["D1"] = "Account Number"
    w1["E1"] = "Amount"
    w1["F1"] = "Mobile Number"
    w1["G1"] = "Email Address"

    index = 2
    for item in g_items:
      fname, mname, lname, ename = item["fname"]["f"], item["fname"]["m"], item["fname"]["l"], item["fname"]["e"]
      
      ref, _, net = str(item['ref']), item['name'], item['amount']

      w1[f"A{index}"] = f"{fname} {ename}".upper().strip()
      w1[f"B{index}"] = mname.upper().strip()
      w1[f"C{index}"] = lname.upper().strip()
      w1[f"D{index}"] = ref
      w1[f"E{index}"] = net
      w1[f"F{index}"] = "09636382382"
      w1[f"G{index}"] = "testmunicipality@gmail.com"

      index += 1    

    wb.save(excel_path)
    wb.close()
    

    # end dbp excel row with 7 column

    # end of the creation of the excel file, or ada file 

    # zip with password
    zip_password = refid
    prn_zip_path = f"{prn_path}.zip".replace('.prn', '')
    try:      
      pyminizip.compress_multiple([prn_path, txt_path, excel_path], ["", "", ""], prn_zip_path, zip_password, 9)
      # end zip with password
    except Exception as er:
      print(er)

    if os.path.exists(prn_path):
      os.remove(prn_path)
    if os.path.exists(txt_path):
      os.remove(txt_path)
    
    if os.path.exists(excel_path):
      os.remove(excel_path)


    if not os.path.exists(prn_zip_path): raise ValueError('No file found')

    data = b''
    fpp = None
    try:
      fpp = open(prn_zip_path, 'rb')
      data = fpp.read()
    except Exception as er:
      print(er)
    finally:
      if fpp: fpp.close()
      os.remove(prn_zip_path)
    if not data:
      raise ValueError('Error no data')

    msg['msg'] = 'Transaction Completed!'
    msg['ok'] = True
    msg['file'] = file_name
    msg['data'] = b64encode(data).decode()

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)

def payroll_print_file(req, res): 


  # this variable can be cofigurable in the future update
  # 
  bank_account_no = {
      '01': '0708-03976A-030', # general fund,
      '02': '0708-03976R-030', #trust fund
      '03': '0708-03976C-030' # trust fund
  }





  auth, con, msg = None, None,  {
    "ok": False,
    "msg": "",
    "data": "",
    "file": ""
  }


  try:

    auth = Auth(req)

    if not auth.isAuth: raise ValueError("You are not authorized!")

    data = auth.data
    
    if not "refid" in data: raise ValueError("refid is required")

    if not "dept_id" in data: raise ValueError("dept_id is required")

    if not 'fund' in data: raise ValueError('fund is not found')
    

    refid = data["refid"]
    dept_id = data["dept_id"]
    fund = data['fund']

    if str(dept_id).strip():
      msg["msg"] = "Not yet supported!"
      raise ValueError("Not supported yet") 
    # retrieve the data based on the fundings

    con = sql()
    

    ac = AccessModel( con )
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-7']):
      msg['ok'] = False
      msg['msg'] = ac.errorAccess()
      msg['data'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())
    
     # render the obr 
    # since the ada is based on the budget from the ob-r or obligation requests
    ob_r = Ob_R(con)

    ob_data = ob_r.get_ob_by_code_type(refid, fund)

    

    pstore = PayrollStore(con)
    
    payroll_info = pstore.info(refid)

    payroll_type = payroll_info['type']    
    info_status = []
    if payroll_info['status']:
      info_status = json_parse(payroll_info['status'])

      last_status = info_status[len(info_status) - 1]
      if last_status['step'] == 5:
        msg['msg'] = 'Already closed, you cant redownload the payroll file!'
        raise ValueError('Already closed, you cant redownload the payroll file')
        
      # if last_status['step'] != 4:
      #   msg['msg'] = 'Not Ready for payroll file obligation requests must be close or approved'
      #   raise ValueError('Not ready for payroll file or obligation requests')

      if last_status['step'] == 7:
        pass
      else:
        msg['msg'] = 'Not ready for download! please click on proceed to download button to lock the editing and update of the payroll'
        raise ValueError('Not ready for download!')

    else:
      msg['msg'] = 'Not Ready for payroll file obligation requests must be close or approved'
      raise ValueError('Not ready for payroll file')

    # if not info_status:
    #   msg['ok'] = True
    #   msg['msg'] = 'The Payroll already closed!'
    #   msg['data'] = 'You cant print the ada if the payroll is ongoing'
    #   raise ValueError('Already locked the payroll')

    bank_info = json_parse(payroll_info["bank_info"])

    head_info = bank_info["branch"]["head"]

    ada_sign = bank_info["ada_sign"]


    if not payroll_info:
      msg["msg"] = "Payroll not found!"
      raise ValueError("Payroll not found")
    
    _from = payroll_info["from"].split("-")
    _to   = payroll_info["to"].split("-")

    items = pstore.get_item(refid, {
      "dept_id": dept_id,
      "is_order": False
    })

    qr = Qr(str(refid) + "." + str(dept_id))
    ded_list = json_parse(payroll_info["deduction_list"])

    res = []

    total_net = 0.0

    for item in items:
      slip = payslip(item, ded_list, payroll_info)
      other_info = json_parse(item["other_info"])
      ref = ""
      if "acc" in other_info:
        ref = other_info["acc"]

      # filter out all the only with the obR
      if _is_ada_exists(ob_data = ob_data, dept_id = item['dept_id']):
        res.append({
          "ref": ref,
          "name": slip["name"],
          "net": slip["net"]
        })
        total_net += float(slip["net"])

      #print(slip)

    # 001--> if payroll_type == 'r': total_net /= 2
    
    over_all = total_net

    total_net = '{:.2f}'.format(float(over_all))

    net = total_net.split(".")
    
    peso = int(net[0])
    cent = int(net[1])

    nword = int_to_word(peso) 
    nword = nword.strip().strip(",") + " pesos"
    if cent > 0:
      nword += " & " + int_to_word(cent) + " centavos"

    nword += ' only'

    com_name = 'Test'
    period = f'{month_name(int(_from[1]) - 1)} {_from[2]}-{_to[2]}, {_from[0]}' # date period


    tahod = ""
    if head_info["g"] == "m":
      tahod = "SIR"

    elif head_info["g"] == "f":
      tahod = "MA'AM"


    emp_type = payroll_info['type']

    print_t = req.query.get('print', '0') # if print equal to 0 then it is a view only, if it is 1 then i generate the ada number
    
    ada_no = 'Draft Mode|Not Accepted'
    
    abank = BankAda(con).get(refid = refid, fund = fund)
    
    ada_no = abank[0][0] if abank else "Please add ada number" # generate the ada number here every time print is trigger

    ada_date = abank[0][1] if abank else "" # date

    file_name = f"""{ "Regular" if payroll_type == "r" else "Casual" }-{period}-excel-ada-no-{ada_no}"""
    # opening the execel
    excel_ada_template = f'data{os.sep}template{os.sep}ada.xlsx'
    workbook = load_workbook(filename = excel_ada_template)

    # Select the active worksheet
    w1 = workbook.worksheets[0]


    # plotting the header
    w1["C6"] = f"ADA No.: {ada_no}"
    
    w1["C7"] = f"              Date: {date_normal(str(ada_date).split(' ')[0]) if ada_date else ''}"


    pd = f"Please debit the agency Account No. {bank_account_no[fund]} the amount of {nword} (P {float(over_all):,.2f})."
    # Eighty Nine Thousand, Five Hundred pesos & Forty Five centavos only (P 1,589,500.45). 
    
    t1 = pd
    t2 = ""
    if len(pd) > 95:
      t1 = pd[: 95]
      t2 = pd[95: ]

    w1["A11"] = t1
    w1["A12"] = t2


    ptype = "regular employees" if payroll_type == "r" else "casual employees"

    w1["A15"] = f"Please credit the accounts of the listed {ptype} to cover payment of Salaries  "

    w1["A16"] = f"and Wages covering {period}"
    # end plotting the header


    border = Border(
                    left = Side(style = 'thin', color = '000000'),  # red double line
                    right = Side(style = 'thin', color = '000000'),  # green thick line
                    top = Side(style = 'thin', color = '000000'),  # blue dashed line
                    bottom = Side(style = 'thin', color = '000000')
                  )
    
    bold = Font(bold = True, size = 12)
    
    inc = 18
    for item in res:

      net = item['net']
      # --> 001 if emp_type == 'r': net = item['net'] / 2.0 # if  regular then divide the ada to two
      
      iref, iname, inet = item["ref"], item["name"], f"{net:,.2f}"
      # plotting the data
      w1[f"A{inc}"] = iref
      w1[f"B{inc}"] = iname
      w1[f"C{inc}"] = inet

      w1[f"A{inc}"].border = border
      w1[f"B{inc}"].border = border
      w1[f"C{inc}"].border = border
      # w1[f"A{inc}"] = Alignment()
      # end plotting the data
      inc += 1

    w1[f"A{inc}"] = "Total"
    w1[f"C{inc}"] = f"{float(total_net):,.2f}"
    w1[f"A{inc}"].border = border
    w1[f"A{inc}"].font = bold
    
    w1[f"B{inc}"].border = border
    w1[f"C{inc}"].border = border
    w1[f"C{inc}"].font = bold
    

    inc += 1
    w1[f"A{inc}"] = ""
    w1[f"B{inc}"] = ""
    w1[f"C{inc}"] = ""
    w1[f"A{inc}"].border = border
    w1[f"B{inc}"].border = border
    w1[f"C{inc}"].border = border
    inc += 1 # skip 1 line
    
    w1[f"A{inc}"] = "ELIZABETH  B. PABELLAN, CPA"
    w1[f"c{inc}"] = "HON. CONSTANTINO H. REYES"

    center_t = Alignment(horizontal = "center", wrap_text = True)
    
    w1[f"A{inc}"].alignment = center_t
    w1[f"C{inc}"].alignment = center_t
    w1[f"A{inc}"].font = bold
    w1[f"C{inc}"].font = bold
    

    inc += 1 # skip 1 line
    
    w1[f"A{inc}"] = "Municipal Treasurer"
    w1[f"c{inc}"] = "Municipal Mayor"
    w1[f"A{inc}"].alignment = center_t
    w1[f"C{inc}"].alignment = center_t
    
    # signatory = [
    #   [
    #     {"action": "Prepared By:", "name": }
    #   ]
    # ]

    w1.protection.sheet = True
    w1.protection.password = '1996'
    w1.protection.enable()

    buf = BytesIO()
    workbook.save(buf)
    bytes_data = buf.getvalue()    
    buf.close()

    msg["ok"] = True
    msg["file"] = file_name
    msg["msg"] = "Transaction Completed!"
    msg["data"] = b64encode(bytes_data).decode()

  except Exception as er:
    print(er)
  
  finally:
    if con: con.close()

  if auth: return auth.send(msg)
  
  

def payroll_print_ada(req, res):
  auth = None
  con = None
  msg = {
    "ok": False, 
    "msg": "",
    "data": ""
  }

  try:
    auth = Auth(req)

    if not auth.isAuth: raise ValueError("You are not authorized!")

    data = auth.data
    
    if not "refid" in data: raise ValueError("refid is required")

    if not "dept_id" in data: raise ValueError("dept_id is required")

    if not 'fund' in data: raise ValueError('fund is not found')
    

    refid = data["refid"]
    dept_id = data["dept_id"]
    fund = data['fund']

    if str(dept_id).strip():
      msg["msg"] = "Not yet supported!"
      raise ValueError("Not supported yet") 
    # retrieve the data based on the fundings

    con = sql()
    

    ac = AccessModel( con )
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-7']):
      msg['ok'] = True
      msg['msg'] = ac.errorAccess()
      msg['data'] = ac.errorAccess()
      raise ValueError(ac.errorAccess())

    # render the obr 
    # since the ada is based on the budget from the ob-r or obligation requests
    ob_r = Ob_R(con)

    ob_data = ob_r.get_ob_by_code_type(refid, fund)

    

    pstore = PayrollStore(con)
    
    payroll_info = pstore.info(refid)

    payroll_type = payroll_info['type']    
    info_status = payroll_info['status']
    
    # if not info_status:
    #   msg['ok'] = True
    #   msg['msg'] = 'The Payroll already closed!'
    #   msg['data'] = 'You cant print the ada if the payroll is ongoing'
    #   raise ValueError('Already locked the payroll')

    bank_info = json_parse(payroll_info["bank_info"])

    head_info = bank_info["branch"]["head"]

    ada_sign = bank_info["ada_sign"]


    if not payroll_info:
      msg["msg"] = "Payroll not found!"
      raise ValueError("Payroll not found")
    
    _from = payroll_info["from"].split("-")
    _to   = payroll_info["to"].split("-")

    items = pstore.get_item(refid, {
      "dept_id": dept_id,
      "is_order": False
    })

    qr = Qr(str(refid) + "." + str(dept_id))
    ded_list = json_parse(payroll_info["deduction_list"])

    res = []

    total_net = 0.0

    for item in items:
      slip = payslip(item, ded_list, payroll_info)
      other_info = json_parse(item["other_info"])
      ref = ""
      if "acc" in other_info:
        ref = other_info["acc"]

      # filter out all the only with the obR
      if _is_ada_exists(ob_data = ob_data, dept_id = item['dept_id']):
        res.append({
          "ref": ref,
          "name": slip["name"],
          "net": slip["net"]
        })
        total_net += float(slip["net"])

      #print(slip)

    if payroll_type == 'r': total_net /= 2
    
    over_all = total_net

    total_net = '{:.2f}'.format(float(over_all))

    net = total_net.split(".")
    
    peso = int(net[0])
    cent = int(net[1])

    nword = int_to_word(peso) 
    nword = nword.strip().strip(",") + " pesos"
    if cent > 0:
      nword += " & " + int_to_word(cent) + " centavos"

    nword += ' only'

    com_name = 'Test'
    period = f'{month_name(int(_from[1]) - 1)} {_from[2]}-{_to[2]}, {_from[0]}' # date period


    tahod = ""
    if head_info["g"] == "m":
      tahod = "SIR"

    elif head_info["g"] == "f":
      tahod = "MA'AM"


    emp_type = payroll_info['type']

    print_t = req.query.get('print', '0') # if print equal to 0 then it is a view only, if it is 1 then i generate the ada number
    
    ada_no = 'Draft Mode|Not Accepted'
    
    abank = BankAda(con).get(refid = refid, fund = fund)

    if print_t == '1':
      ada_no = abank[0][0] if abank else "Please add ada number" # generate the ada number here every time print is trigger

    t = f'''
      <style>
        table {{
          width: 100%;
        }}
        table, th, td {{
          border: 1px solid black;
          border-collapse: collapse;
        }}
      </style>
      <div style="font-weight: bold; text-align: center;">Municipality of {com_name}</div>
      <h3 style="text-align: center;">AUTHORITY TO DEBIT ACCOUNT (ADA)</h3>

      <div style="position: relative; width: 100%;">
        <div style="float: left; width: 50%;">
          <div>
            {head_info["p"]} {head_info["f"]} {head_info["m"]} {head_info["l"]} {head_info["s"]}
          </div>
        </div>
        <div style="float: right: width: 50%;text-align: right;">ADA No.: <b>{ada_no if info_status else "Not yet Valid(View Mode)"}</b></div>    
      </div>
      <div style="text-indent: 30px;">
        {head_info["lh"]}
      </div>

      <div style="margin-top: 30px;">
        {tahod} {head_info["l"].upper()}:
      </div>
      <div>
        <p style="text-indent: 30px; text-align: justify;">
          Please debit the agency Account No. <b><u>{bank_info["acc_no"]}</b></u> the amount of <span style="text-decoration: underline;">{nword}</span> (<b><u>P {float(total_net):,.2f}</u></b>).
        </p>

        <p style="text-indent: 30px; text-align: justify;">
          Please credit the accounts of the listed creditors to cover payment of the LGU salaries and wages
          of M.O. casual employees for the period of {period}.
        </p>
      </div>
    '''

    t += f'''
      <table>
        <tr>
          <th style="width: 30%;">REFERENCE/ACCOUNT NUMBER<br /></th>
          <th style="width: 50%;">NAME</th>
          <th style="width: 20%;">AMOUNT</th>
        </tr>
    '''
    # data
    for item in res:

      net = item['net']

      #-->001 if emp_type == 'r': net = item['net'] / 2.0 # if  regular then divide the ada to two

      t += f'''
        <tr>
          <td style="text-align: center;">{item["ref"]}</td>
          <td>{item["name"]}</td>
          <td style="text-align: right;">{net:,.2f}</td>
        </tr>
      '''
    # end data
    t += f'</table>'
    t += '<div style="text-align: center;font-weight: bold;">AGENCY AUTHORIZED SIGNATORIES</div>'
    t += '<div style="width: 100%;position: relative; margin-top: 40px;">'

    ada_len = len(ada_sign)
    
    ad = 0.0
    if ada_sign:
      ad = 100.0 / ada_len

    for x in ada_sign:
      t += f'''
            <div style="width: {ad - 1}%;float: left; text-align: center;">
              {x["name"].upper()}
              <div></div>
              <b> {x["pos"].upper()} </b>
            </div>
        '''

    t += '</div>'

    msg["data"] = t
    msg["ok"] = True

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(msg)

def payroll_pre_cal(req, res):
  auth = None
  con = None
  res = {
    "ok": False,
    "msg": None,
    "data": {}
  }

  try:
    
    auth = Auth(req)
    if not auth.isAuth: raise ValueError("You are not authorized!")
    
    data = auth.data

    if not "rate" in data: raise ValueError("rate is required!")
    
    if not "rate_type" in data: raise ValueError("rate_type is required!")
    
    if not "payroll_refid" in data: raise ValueError("payroll_refid is required!")
    
    if not "late" in data: raise ValueError("late is required")

    if not "work_day" in data: raise ValueError("work_day is required")
    
    if not "undertime" in data: raise ValueError("undertime is required!")
    
    if not "total_absent" in data: raise ValueError("total_absent is required")

    if not "ded_data" in data: raise ValueError("ded_data is required!")

    if not 'emp_id' in data: raise ValueError('emp_id is required!')

    emp_id, is_new = (data['emp_id'], False) # true if it is not exists in the database
    
    con = sql()
    payroll_store = PayrollStore(con)
    payroll_info  = payroll_store.info(data["payroll_refid"])

    pitem = payroll_store.get_payroll_item(refid = data["payroll_refid"], emp_id = emp_id)
    
    nwpd = 5
    job_type = ''
    if pitem:
      # retrieve the current position information 
      com = json_parse(pitem[0]['com'])
      job_type = com['s']

      if 'n' in com and com['n']:
        nwpd = com['n']

    else:
      # retrieve the current info for intial computation
      rate_obj = RateStore(con = con)
      rate = rate_obj.get_rate_dict(emp_id = emp_id)
      if rate:
        rate = rate[0]
        if 'nwpd' in rate and rate['nwpd']: nwpd = int(rate['nwpd'])

      pos_obj = PositionStore(con = con)
      pos = pos_obj.get_position_dict(emp_id = emp_id)
      if pos: job_type = pos[0]['status'] 

    if not job_type:
      raise ValueError('job_type must have a value')
    
    con.close()
    con = None

    cal_basic = CalBasic(
      float(data["rate"]),
      data["rate_type"],
      float(data["work_day"]),
      float(data["late"]),
      float(data["undertime"]),
      float(data["total_absent"]),
      json_parse(payroll_info["deduction_list"]),
      data["ded_data"],
      payroll_info,
      nwpd = nwpd,
      job_type = job_type
    )

    cal_basic.calculate()
    result = cal_basic.output

    res["ok"] = True
    res["msg"] = "Transaction Completed!"
    res["data"] = {
      "absent_amount": result.absent_amount,
      "gross_amount": result.gross_amount,
      "late_amount": result.late_amount,
      "undertime_amount": result.undertime_amount,
      "net_amount": result.net_amount,
      "total_deduction": result.total_deduction
    }

  except Exception as er:
    print(er)
  finally:
    if con:
      con.close()

  if auth:
    return auth.send(res)


def status_state_change(req, res):
  con, auth, msg = None, None, {'ok': False, 'msg': 'Invalid Input'}

  try:
    auth = Auth(req)
    is_auth, payload = auth.isAuth, auth.data

    if not is_auth:
      msg['msg'] = 'You are not authorized!'
      raise ValueError('You are not authorized!')

    if not 'refid' in payload: raise ValueError('refid is required!')
    if not 'type' in payload: raise ValueError('type is required!')
    if not 'username' in payload: raise ValueError('username is required!')
    if not 'password' in payload: raise ValueError('password is required')
    if not 'remark' in payload: raise ValueError('remark is required!')
    if not 'dept_id' in payload: raise ValueError('dept_id is required!')

    refid, type_t, username, password, remark, dept_id = payload['refid'], payload['type'], payload['username'], payload['password'], payload['remark'], payload['dept_id']

    # checking if the username is the same as input
    susername = auth.ses.get('username')
    if not ( username == susername ):
      msg['msg'] = 'username dont match!'
      raise ValueError('user name does not match')
    

    con = sql()

    user_model = UserModel()
    user_model._setConnection(con)

    # validating the user if he input the correct password
    user = user_model.authenticate(username, password)
    if not user:
      msg['msg'] = 'Username or Password incorrect!'
      raise ValueError('worng username and password')

    # getting the information of the payroll
    pstore = PayrollStore(con)
    pinfo = pstore.info(refid = refid)
    # checking if payroll exists

    if not pinfo:
      msg['msg'] = 'Payroll not found!'
      raise ValueError('Payroll not found!')


    # get the type
    job_status = pinfo['type']
    # end get the type

    sql_remark = pinfo['status']


    if sql_remark:
      _sq = json_parse(sql_remark)
      last_step = _sq[len(_sq) - 1]['step']
      if last_step == 5: # 5 is the ending of the payroll
        msg['msg'] = 'The salaries and wages of this payroll already approved from Bank'
        raise ValueError('The payroll is payroll file already closed')

    

    if type_t == 'close_payroll':
      #######################################################################################################
      ######################### CLOSING PROCESS FOR PAYROLL #################################################
      #######################################################################################################

      if job_status == 'j':
        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['pm-l-j']):
          msg['msg'] = ac.errorAccess()
          raise ValueError(ac.errorAccess())
      elif job_status == 'c':
        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['pm-l-c']):
          msg['msg'] = ac.errorAccess()
          raise ValueError(ac.errorAccess())
      elif job_status == 'r':
        ac = AccessModel(con)
        if not ac.hasAccess(auth.ses.get('uid'), ['pm-l-r']):
          msg['msg'] = ac.errorAccess()
          raise ValueError(ac.errorAccess())
      else:
        msg['msg'] = 'Something went wrong!'
        raise ValueError('Something went wrong!')


      if sql_remark:

        sql_remark = json_parse(sql_remark)
        if sql_remark[len(sql_remark) - 1]['step'] == 1:
          msg['msg'] = 'Transaction already completed!'
          raise ValueError('Already closed!')
        elif sql_remark[len(sql_remark) - 1]['step'] == 0:
          pass
        else:
          msg['msg'] = 'This process is invalid'
          raise ValueError('You are not allowed!')
      else:
        sql_remark = []

      error = []
      # checking all the payroll if it has zero or negative payroll
      items = pstore.get_item(refid, {
        "dept_id": dept_id,
        "is_order": False
      })
      ded_list = json_parse(pinfo["deduction_list"])
      for item in items:
        slip = payslip(item, ded_list, pinfo)
        if slip["gross"] <= 0.0:
          # if found get the employee information
          emp_info = json_parse(item["emp_info"])          
          error.append(f'Zero or negative gross found: {emp_info["l"].upper()} {emp_info["f"].upper()}')      

      if len(error) > 0:
        msg["msg"] = "Zero gross found in this payroll: please recheck the payroll!"
        raise ValueError("Zero gross found in this payroll: please recheck the payroll!")
      # end checking the payroll -> it check the gross

      pstore.approvePayroll(refid, auth.ses.get('uid'), remark, user['name'], status = sql_remark)
      con.go()
      msg['msg'] = 'Succesfully closed!'
      msg['ok'] = True
      #######################################################################################################
      ######################### END CLOSING FOR PAYROLL     #################################################
      #######################################################################################################
    
    elif type_t == 'check':
      msg['msg'] = 'Okay'
      msg['ok'] = True
    elif type_t == 'open_payroll':
      #######################  REOPENING THE PAYROLL ##########################################

      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['r-0']):
          msg['msg'] = ac.errorAccess()
          raise ValueError(ac.errorAccess())

      if not sql_remark:
        msg['msg'] = 'Cant be reopen, it was already open'
        raise ValueError('cant be reopen,, it was already opened')

      sql_remark = json_parse(sql_remark)
      last_step = sql_remark[len(sql_remark) - 1]['step']
      if last_step == 0: # get the last status
        msg['msg'] = 'Already open already open'
        raise ValueError('cant be reopen,, it was already opened')

      if len(remark.strip()) < 5:
        msg['msg'] = 'Remark or msg is to short, please specify!'
        raise ValueError('Remark or msg is to short, please specify!')

      if last_step == 7:
        msg['msg'] = 'Cant be reopen, because the payroll is ready for download file'
        raise ValueError('Cant be reopen, because the payroll is ready for download payroll file')
        

      sign_list = json_parse(pinfo['signatory_list'])

      pstore.reopenPayroll(refid = refid, uid = auth.ses.get('uid'), msg = remark, status = sql_remark, name = user['name'], sign_list = sign_list)
      con.go()

      msg['msg'] = 'Transaction Completed!'
      msg['ok'] = True
      ####################### END REOPENING THE PAYROLL #######################################

    elif type_t == 'close_review':
      ####################### Close Review and ready for the obligation requests #####################
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['r-1']):
          msg['msg'] = ac.errorAccess()
          raise ValueError(ac.errorAccess())

      sql_remark = json_parse(sql_remark)
      last_step = sql_remark[len(sql_remark) - 1]['step']
      if last_step == 2: # get the last status
        msg['msg'] = 'Closing the Review is already closed!'
        raise ValueError('cant be reopen,, it was already opened')

      pstore.closeReview(refid = refid, uid = auth.ses.get('uid'), msg = remark, status = sql_remark, name = user['name'])
      con.go()
      msg['ok'] = True
      msg['msg'] = 'Transaction Completed!'
      ####################### end close Review and ready for the obligation requests #################

    elif type_t == 'close_ob':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get("uid"), ["pm-9-c"]):
        msg["msg"] = "You Are not Authorized!"
        raise ValueError("You are not authorized!")

      sql_remark = json_parse(sql_remark)
      last_step = sql_remark[len(sql_remark) - 1]['step']
      if last_step == 4: # get the last status
        msg['msg'] = 'OB R already closed!'
        raise ValueError('cant be reopen,, it was already opened')

      pstore.closeOb(refid = refid, uid = auth.ses.get('uid'), msg = remark, status = sql_remark, name = user['name'])
      
      con.go() # commit change
      msg['ok'] = True
      msg['msg'] = 'Transaction Completed!'
    elif type_t == 'ready_download':

      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get("uid"), ["r-3"]):
        msg["msg"] = "You Are not Authorized!"
        raise ValueError("You are not authorized!")


      sql_remark = json_parse(sql_remark)
      last_step = sql_remark[len(sql_remark) - 1]['step']
      if last_step == 7: # get the last status
        msg['msg'] = 'Transaction cant be duplicate!'
        raise ValueError('cant be reopen,, it was already opened')

      pstore.readyForDownloadPayrollFile(refid = refid, uid = auth.ses.get('uid'), msg = remark, status = sql_remark, name = user['name'])
      con.go()
      msg['msg'] = 'You can now download the payroll file'
      msg['ok'] = True

    elif type_t == 'final_close':

      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get("uid"), ["f-0"]):
        msg["msg"] = "You Are not Authorized!"
        raise ValueError("You are not authorized!")

      sql_remark = json_parse(sql_remark)
      pstore.closeAda(refid = refid, uid = auth.ses.get('uid'), msg = remark, status = sql_remark, name = user['name'])
      con.go()
      msg['ok'] = True
      msg['msg'] = 'Transaction Completed!'
    else:
      msg['msg'] = 'Invalid Type'
      raise ValueError('Invalid Type of')


  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)


def payroll_approve(req, res):
  con = None
  msg = {
    'msg': None,
    'ok': False
  }
  auth = None

  try:
    auth = Auth(req)
    if not auth.isAuth:
      raise ValueError('You are not authorized!')
    
    data = auth.data

    if not 'username' in  data:
      raise ValueError('username is required!')
    
    if not 'password' in data:
      raise ValueError('password is required!')
    
    if not 'remark' in data:
      raise ValueError('remark is required!')
    
    if not 'refid' in data:
      raise ValueError('refid is required!')
      

    username = data['username']
    password = data['password']
    remark   = data['remark']
    refid    = data['refid']

    susername = auth.ses.get('username')

    if not ( username == susername ):
      msg['msg'] = 'username dont match!'
      raise ValueError('user name does not match')
    
    con = sql()

    user_model = UserModel()
    user_model._setConnection(con)

    user = user_model.authenticate(username, password)
    if not user:
      msg['msg'] = 'Username or Password incorrect!'
      raise ValueError('worng username and password')
    
    

    pstore = PayrollStore(con)
    pinfo = pstore.info(refid = refid)

    if pinfo['status']:
      msg['msg'] = 'Payroll Already approved!'
      raise ValueError('Payroll Already Approved!')

    if not pinfo:
      msg['msg'] = 'Payroll not found!'
      raise ValueError('Payroll not found!')

    status = pinfo['type']

    if status == 'j':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-l-j']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    elif status == 'c':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-l-c']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    elif status == 'r':
      ac = AccessModel(con)
      if not ac.hasAccess(auth.ses.get('uid'), ['pm-l-r']):
        msg['msg'] = ac.errorAccess()
        raise ValueError(ac.errorAccess())
    else:
      msg['msg'] = 'Something went wrong!'
      raise ValueError('Something went wrong!')

    pstore.approvePayroll(refid, auth.ses.get('uid'), remark, user['name'])

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

# spliting the charges
def split_by_fund(req, res):
  con, auth = None, None
  msg = { "ok": False, "msg": "Invalid Transaction", "data": None }

  try:
    auth = Auth(req)
    if not auth.isAuth:
      msg["msg"] = "You are not authorized!"
      raise ValueError("You are not authorized!")
    
    data = auth.data

    if not "refid" in data:
      raise ValueError("refid is required!")

    general = []  
    sef     = []
    trust   = []

    con = sql()
    ob = Ob_R()
    
    ob.setConnection(con)
    rpt = ob.getReports(data["refid"])
    con.close()

    dept_info = rpt["dept_info"]

    
    for item in dept_info:

      fund_charge = item["fund_charge"] 
      
      if fund_charge == "01":
        general.append(item)

      elif fund_charge == "02":
        sef.append(item)
      
      elif fund_charge == "03":
        trust.append(item)

    gen_html = "<table>"
    for item in general:
      dept_id, dept_name = item["dept_id"][0], item["dept_id"][1]
      gross              = item["gross"]
      gen_html += f"""
        <tr>
          <td>{ dept_name }</td>
          <td style="text-align: right; font-weight: bold; width: 100px;">P { gross:,.2f}</td>
        </tr>
      """
    gen_html += "</table>"



    sef_html = "<table>"
    for item in sef:
      dept_id, dept_name = item["dept_id"][0], item["dept_id"][1]
      gross              = item["gross"]
      sef_html += f"""
        <tr>
          <td>{ dept_name }</td>
          <td style="text-align: right; font-weight: bold;width: 100px;">P { gross:,.2f}</td>
        </tr>
      """
    sef_html += "</table>"
    

    trust_html = "<table>"
    for item in trust:
      dept_id, dept_name = item["dept_id"][0], item["dept_id"][1]
      gross              = item["gross"]
      trust_html += f"""
        <tr>
          <td>{ dept_name }</td>
          <td style="text-align: right; font-weight: bold; width: 100px;">P { gross:,.2f}</td>
        </tr>
      """
    trust_html += "</table>"

    html = ""
    # create html report here
    html = f"""
        <style>
          html, body {{
            margin: 0;
            padding: 0;
          }}
          .col {{
            float: left;
            width: 31%;
            min-height: 50px;
            position: relative;
            border: 1px solid grey;
            padding: 5px;
          }}

          table {{
            font-family: arial, sans-serif;
            border-collapse: collapse;
            width: 100%;
          }}

          td, th {{
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
          }}

          tr:nth-child(even) {{
            background-color: #dddddd;
          }}
        </style>

        <center>Payroll Reports</center>
        <center><div>{ rpt["payroll"]["name"] }</div></center>
        <i><center><div>({rpt["payroll"]["range"][0]} - {rpt["payroll"]["range"][1]})</div></center></i>
        <center><div>REF NO.: <b style="letter-spacing: 3px;">{ rpt["payroll"]["id"] }</b></div></div>
        <h3>Total: <span style="color: red;">{rpt["total_gross"]:,.2f}</span></h3>
        <div class="col">
          <center><b>General Funds</b></center>
          { gen_html }
          <center><h3>P {rpt["fund_gross"]["01"]:,.2f}</h3></center>
        </div>

        <div class="col">
          <center><b>SEF Funds</b></center>
          { sef_html }
          <center><h3>P {rpt["fund_gross"]["02"]:,.2f}</h3></center>
        </div>

        <div class="col">
          <center><b>Trust Funds</b></center>
          { trust_html }
          <center><h3>P {rpt["fund_gross"]["03"]:,.2f}</h3></center>
        </div>  
        <hr />
    """

    # end html report here

    msg["data"] = html
    msg["msg"] = "Transaction Completed!"
    msg["ok"] = True

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)


def ob_fund_reports(req, res):
  con, msg = None, {
    "ok": False,
    "msg": "Invalid Requests",
    "data": ""
  }

  try:
    auth = Auth(req)
    if not auth.isAuth:
      msg["msg"] = "You are not authorized!"
      raise ValueError("You are not authorized!")
    
    data = auth.data

    if not "refid" in data:
      raise ValueError("refid is required!")
    
    con = sql()
    ob = Ob_R()
    
    ob.setConnection(con)
    rpt = ob.getReports(data["refid"], inc_payee = True, inc_deduction = True, inc_ada = True)
    con.close()

    dept_info = rpt["dept_info"]
    payroll   = rpt["payroll"]

    general = []
    sef     = []
    trust   = []

    # create header for the html
    base_header  = rpt["ded_header"]
    
    # ada number
    ada_number = rpt["ada_number"]

    for item in dept_info:

      # print(item["dept_id"][1], item["total_deduction"])
      fund_charge = item["fund_charge"] 
      
      if fund_charge == "01":
        general.append(item)

      elif fund_charge == "02":
        sef.append(item)
      
      elif fund_charge == "03":
        trust.append(item)
    
    ghtml = f"""
      <style>

      @media print {{
        @page {{
          size: landscape;
        }}
        
      }}
      .break{{
        break-before: page;
      }}



        html, body {{
          margin: 0;
          padding: 0;
        }}
      
        table, td, th {{  
          border: 1px solid #ddd;
          text-align: left;
        }}

        table {{
          border-collapse: collapse;
          width: 100%;
        }}

        th, td {{
          padding: 2px;
        }}
      </style>
    """ # global html


    footer   = deepcopy(base_header)
    main_h = ""
    sub_h = ""
    hcnt = 0
    for mh in base_header:
      main_h += f'<th colspan="{len(base_header[mh])}"><center>{mh}</center></th>'

      for sh in base_header[mh]:
        sub_h += f'<th><center>{sh}</center></th>'
        hcnt += 1
  
    # create header
    # general
    genhtml = f"""
      <div>ADA NUMBER: <b>{ada_number["01"]}</b></div>
      <div>PERIOD COVER: {payroll["range"][0]} to {payroll["range"][1]} ({payroll["name"]})</div>
      <div>REF#: {payroll["id"]}</div>
    """
    genhtml += '<table>'
    genhtml += f"""
            <tr>
              <th rowspan="2">OFFICES BASED ON OBLIGATION REQUEST</th>
              <th rowspan="2">PAYEE</th>
              <th rowspan="2"><center>GROSS AMOUNT</center></th>
              {main_h}
              <th rowspan="2"><center>NET AMOUNT</center></th>
            </tr>
            <tr>
              {sub_h}
            </tr>
            """
    gross = 0.0
    net   = 0.0    
    for item in general:
      # genere here the data
      gross += item["gross"]
      net   += item["net"]

      dept_name = item["dept_id"][1]
      genhtml += f"""
      <tr> 
        <td>{dept_name.upper()}</td>
        <td>{item["payee"]}</td>
        <td style="text-align: right;">{item["gross"]:,.2f}</td>"""

      for jitem in item["total_deduction"]:
        for v in item["total_deduction"][jitem]:
          genhtml += f"""<td style="text-align: right;">{item["total_deduction"][jitem][v]:,.2f}</td>"""

          # computing the footer
          for f in footer:
            for sf in footer[f]:
              if f == jitem and sf == v:
                footer[f][sf] += item["total_deduction"][jitem][v]

      genhtml += f"""
        <td style="text-align: right;">{item["net"]:,.2f}</td>
      </tr>
      """

    # create footer
    genhtml += f"""<tr style="font-weight: bold;">"""
    genhtml += f"""
              <td></td>
              <td style="text-align: right;">TOTAL: </td>
              <td style="text-align: right;">{gross:,.2f}</td>
    """
    for f in footer:
      for sf in footer[f]:
        genhtml += f'<td style="text-align: right;">{footer[f][sf]:,.2f}</td>'

    genhtml += f'<td style="text-align: right;">{net:,.2f}</td>'
    genhtml += f"</tr>"
    # en
    genhtml += '</table><div class="break"></div>'
    ghtml += genhtml

############################################################################################
# SEF
############################################################################################
    
    footer   = deepcopy(base_header)
    main_h = ""
    sub_h = ""
    hcnt = 0
    for mh in base_header:
      main_h += f'<th colspan="{len(base_header[mh])}"><center>{mh}</center></th>'

      for sh in base_header[mh]:
        sub_h += f'<th><center>{sh}</center></th>'
        hcnt += 1
  
    # create header
    # general
    genhtml = f"""
      <div>ADA NUMBER: <b>{ada_number["02"]}</b></div>
      <div>PERIOD COVER: {payroll["range"][0]} to {payroll["range"][1]} ({payroll["name"]})</div>
      <div>REF#: {payroll["id"]}</div>
    """
    genhtml += '<table>'
    genhtml += f"""
            <tr>
              <th rowspan="2">OFFICES BASED ON OBLIGATION REQUEST</th>
              <th rowspan="2">PAYEE</th>
              <th rowspan="2"><center>GROSS AMOUNT</center></th>
              {main_h}
              <th rowspan="2"><center>NET AMOUNT</center></th>
            </tr>
            <tr>
              {sub_h}
            </tr>
            """
    gross = 0.0
    net   = 0.0    
    for item in sef:
      # genere here the data
      gross += item["gross"]
      net   += item["net"]

      dept_name = item["dept_id"][1]
      genhtml += f"""
      <tr> 
        <td>{dept_name.upper()}</td>
        <td>{item["payee"]}</td>
        <td style="text-align: right;">{item["gross"]:,.2f}</td>"""

      for jitem in item["total_deduction"]:
        for v in item["total_deduction"][jitem]:
          genhtml += f"""<td style="text-align: right;">{item["total_deduction"][jitem][v]:,.2f}</td>"""

          # computing the footer
          for f in footer:
            for sf in footer[f]:
              if f == jitem and sf == v:
                footer[f][sf] += item["total_deduction"][jitem][v]

      genhtml += f"""
        <td style="text-align: right;">{item["net"]:,.2f}</td>
      </tr>
      """

    # create footer
    genhtml += f"""<tr style="font-weight: bold;">"""
    genhtml += f"""
              <td></td>
              <td style="text-align: right;">TOTAL: </td>
              <td style="text-align: right;">{gross:,.2f}</td>
    """
    for f in footer:
      for sf in footer[f]:
        genhtml += f'<td style="text-align: right;">{footer[f][sf]:,.2f}</td>'

    genhtml += f'<td style="text-align: right;">{net:,.2f}</td>'
    genhtml += f"</tr>"
    # en
    genhtml += '</table><div class="break"></div>'
    ghtml += genhtml

############################################################################################
# SEF
############################################################################################
    footer   = deepcopy(base_header)
    main_h = ""
    sub_h = ""
    hcnt = 0
    for mh in base_header:
      main_h += f'<th colspan="{len(base_header[mh])}"><center>{mh}</center></th>'

      for sh in base_header[mh]:
        sub_h += f'<th><center>{sh}</center></th>'
        hcnt += 1
  
    # create header
    # general
    genhtml = f"""
      <div>ADA NUMBER: <b>{ada_number["03"]}</b></div>
      <div>PERIOD COVER: {payroll["range"][0]} to {payroll["range"][1]} ({payroll["name"]})</div>
      <div>REF#: {payroll["id"]}</div>
    """
    genhtml += '<table>'
    genhtml += f"""
            <tr>
              <th rowspan="2">OFFICES BASED ON OBLIGATION REQUEST</th>
              <th rowspan="2">PAYEE</th>
              <th rowspan="2"><center>GROSS AMOUNT</center></th>
              {main_h}
              <th rowspan="2"><center>NET AMOUNT</center></th>
            </tr>
            <tr>
              {sub_h}
            </tr>
            """
    gross = 0.0
    net   = 0.0    
    for item in trust:
      # genere here the data
      gross += item["gross"]
      net   += item["net"]

      dept_name = item["dept_id"][1]
      genhtml += f"""
      <tr> 
        <td>{dept_name.upper()}</td>
        <td>{item["payee"]}</td>
        <td style="text-align: right;">{item["gross"]:,.2f}</td>"""

      for jitem in item["total_deduction"]:
        for v in item["total_deduction"][jitem]:
          genhtml += f"""<td style="text-align: right;">{item["total_deduction"][jitem][v]:,.2f}</td>"""

          # computing the footer
          for f in footer:
            for sf in footer[f]:
              if f == jitem and sf == v:
                footer[f][sf] += item["total_deduction"][jitem][v]

      genhtml += f"""
        <td style="text-align: right;">{item["net"]:,.2f}</td>
      </tr>
      """

    # create footer
    genhtml += f"""<tr style="font-weight: bold;">"""
    genhtml += f"""
              <td></td>
              <td style="text-align: right;">TOTAL: </td>
              <td style="text-align: right;">{gross:,.2f}</td>
    """
    for f in footer:
      for sf in footer[f]:
        genhtml += f'<td style="text-align: right;">{footer[f][sf]:,.2f}</td>'

    genhtml += f'<td style="text-align: right;">{net:,.2f}</td>'
    genhtml += f"</tr>"
    # en
    ghtml += genhtml


    msg["data"] = ghtml
    msg["ok"]   = True
    msg["msg"]  = "Transaction Completed!"
  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  if auth: return auth.send(msg)


def payroll_change_atm(req, res):
  con, auth, msg = None, None, { "ok": False, "msg": "Invalid Requests", "err": [] }
  
  try:
    auth = Auth(req)
    if not auth.isAuth:
      msg["msg"] = "You are not authorized!"
      raise ValueError("You are not authorized!")
    
    data = auth.data

    if not "refid" in data: raise ValueError("refid is required!")
    
    if not "atm" in data: raise ValueError("Invalid payload")
    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-y-y-c']):
      msg['msg'] = ac.errorAccess()
      raise ValueError("You are not authorized to access")

    pstore = PayrollStore(con = con)
    msg = pstore.change_atm(refid = data["refid"], atm = data["atm"])

    if msg["ok"]: con.go() # final commit

  except Exception as er:
    print(er)
  finally:
    if con: con.close()

  return auth.send(msg) if auth else ""


def payroll_recompute_con_loan(req, res):
  con, auth, msg = None, None, { "ok": False, "msg": "Invalid Requests" }

  try:
    auth = Auth(req)
    if not auth.isAuth: 
      msg["msg"] = "You are not authorized!"

    data = auth.data

    if not "refid" in data:
      raise ValueError("Invalid payload")
    
    refid = data["refid"]

    con = sql()

    ac = AccessModel(con)
    if not ac.hasAccess(auth.ses.get('uid'), ['pm-y-y-r']):
      msg['msg'] = ac.errorAccess()
      raise ValueError("You are not authorized to access")

    pstore = PayrollStore(con = con)
    
    o, m = pstore.recompute_payroll(refid = refid)
    msg["ok"]  = o
    msg["msg"] = m

    con.go()# 

    
  

  except Exception as er:
    print(er)
  finally:
    if con: con.close()


  return auth.send(msg) if auth else ""