from typing import Union, List
from app.lib.sql import sql
from dataclasses import dataclass

from app.store.default_head import DefaultHead
from app.util.date import date_time
from app.store.payroll_store import PayrollStore
from app.util.payroll_calulator import payslip
from app.util.json import json_parse, json_stringify
from copy import deepcopy

@dataclass
class ObEntity:
  payroll_code: str
  dept_id: str
  ob_no: str
  fund_code: str = None
  particular: str = None
  charge_code: str = None
  charge_name: str = None
  account_code: str = None
  fpp: str = None
  createdby: str = None
  datecreated: str = None
  amount: str = None
  head_name: str = None
  head_pos: str = None
  type_t: str = None # j #c #r
  sign_id: str = None

OB_R_DISPLAY = '''payroll_code, 
                        dept_id, 
                        particular, 
                        charge_code, 
                        charge_name, 
                        account_code, 
                        fpp,
                        head_name,
                        head_pos,
                        fund_code,
                        ob_no,
                        datecreated, sign_id '''

class Ob_R:
  def __init__(self, con: sql = None):
    self.con = con

  def setConnection(self, con: sql) -> None:
    self.con = con

  def is_exists(self, payroll_code: str, dept_id: str) -> bool:

    res = self.con.get('select payroll_code from obr where payroll_code = ? and dept_id = ?', (
      payroll_code,
      dept_id,
    ))

    return True if res else False

  def get_ob_by_code_type(self, payroll_code: str, funds: str) -> list:
    data = self.con.get(f'''select 
                        {OB_R_DISPLAY}
                      from obr where payroll_code = ? and fund_code = ?''', (
      payroll_code,
      funds,
    ))

    ret = []
    if data: 
      for item in data:
        dic = {}
        dic['payroll_code'] = item[0]
        dic['dept_id']      = item[1]
        dic['particular']   = item[2]
        dic['charge_code']  = item[3]
        dic['charge_name']  = item[4]
        dic['account_code'] = item[5]
        dic['fpp']          = item[6]
        
        dic['head_name']    = item[7]
        dic['head_pos']     = item[8]

        dic['fund_code']    = item[9]
        dic['ob_no']        = item[10]
        dic['datecreated']  = item[11]
        dic['sign_id']      = item[12]
        if str(item[10]).strip():
          ret.append(dic)
        
    return ret

  def getOb(self, payroll_code: str, dept_id: str, type_t: str = None) -> dict:
    data = self.con.get(f'''select 
                        {OB_R_DISPLAY}
                      from obr where payroll_code = ? and dept_id = ?''', (
      payroll_code,
      dept_id,
    ))

    ret = {}

    if data:
      ret['payroll_code'] = data[0][0]
      ret['dept_id']      = data[0][1]
      ret['particular']   = data[0][2]
      ret['charge_code']  = data[0][3]
      ret['charge_name']  = data[0][4]
      ret['account_code'] = data[0][5]
      ret['fpp']          = data[0][6]
      
      ret['head_name']    = data[0][7]
      ret['head_pos']     = data[0][8]

      ret['fund_code']    = data[0][9]
      ret['ob_no']        = data[0][10]
      ret['datecreated']  = data[0][11]
      ret['sign_id']      = data[0][12]
    else:
      ret['fpp']          = ''
      ret['account_code'] = ''
      ret['particular']   = ''
      ret['head_name']    = ''
      ret['head_pos']     = ''

      ret['fund_code']    = ''
      ret['ob_no']        = ''
      ret['datecreated']  = ''
      ret['sign_id']      = ''

      d = DefaultHead(self.con)
      de_head = d.get_head(dept_id = dept_id, type_t = type_t)

      if de_head:
        ret['head_name'] = de_head[0][0] # name
        ret['head_pos']  = de_head[0][1] # position


    return ret
    

  def _insert(self, ob: ObEntity):
    ob.datecreated = date_time()
    self.con.commit('''insert into obr(
      payroll_code, dept_id, particular, charge_code, charge_name, account_code, fpp, createdby, datecreated, head_name, head_pos, fund_code, ob_no, sign_id                
    ) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
      ob.payroll_code,
      ob.dept_id,
      ob.particular,
      ob.charge_code,
      ob.charge_name,
      ob.account_code,
      ob.fpp,
      ob.createdby,
      ob.datecreated,
      ob.head_name,
      ob.head_pos,
      ob.fund_code,
      ob.ob_no,
      ob.sign_id,
    ))

  def _update(self, ob: ObEntity):
    self.con.commit('''
      update obr set sign_id = ?, ob_no = ?, fund_code = ?, particular = ?, charge_code = ?, charge_name = ?, account_code = ?, fpp = ?, head_name = ?, head_pos = ? where payroll_code = ? and dept_id = ?
    ''', (
      ob.sign_id,
      ob.ob_no,
      ob.fund_code,
      ob.particular,
      ob.charge_code,
      ob.charge_name,
      ob.account_code,
      ob.fpp,
      ob.head_name,
      ob.head_pos,
      ob.payroll_code,
      ob.dept_id,
    ))
  

  def update(self, ob: ObEntity):
    
    
    if self.is_exists(payroll_code = ob.payroll_code, dept_id = ob.dept_id): 
      self._update(ob)
    else: 
      self._insert(ob)

    d = DefaultHead(self.con)
    
    d.update_head(name = ob.head_name, pos_title = ob.head_pos, dept_id = ob.dept_id, type_t = ob.type_t)


  def get(self, refid):

    items = self.con.get("select ob_no, fund_code, dept_id, fpp, sign_id from obr where payroll_code = ?", (
      refid,
    ))
    
    ret = []
    for item in items:
      ret.append({
        "ob_no":     item[0],
        "fund_code": item[1],
        "dept_id":   item[2],
        "fpp":       item[3],
        "sign_id":   item[4]
      })

    return ret




  def __getPayee(self, emp_info) -> str:
    emp_info = json_parse(emp_info)
    mm = ""
    if isinstance(emp_info["m"], str) and emp_info["m"]: mm = f'{emp_info["m"][0]}.'
    return f"""{emp_info["p"]} {emp_info["f"]} {mm} {emp_info["l"]} {emp_info["e"]} {emp_info["p"]} ET.AL""".upper()

  def __getDeduction(self, con_loan_header, deduction, total = None) -> dict:
    ded = json_parse(deduction)
    
    ret = deepcopy(con_loan_header)
    # ret = {}
    # for k, v in con_loan_header.items():
    #   if not k in ret:
    #     ret[k] = {}
    #     for _v in v:
    #       ret[k][_v] = 0.0
    
    for d in ded:
      for code in ret:
        if d["code"] == code and d["name"] in ret[code]:
          d["value"] = float(d["value"])
          ret[code][d["name"]] = d["value"]

          if total: 
            total[code][d["name"]] += d["value"]

    #print(con_loan_header)
    return ret
          

  def __setConLoanHeader(self, code: Union[bytes, str], name: str, con_loan_header: dict) -> None:
    if not code in con_loan_header:
      con_loan_header[code] = {}
      con_loan_header[code][name] = 0.0
    else:
      con_loan_header[code][name] = 0.0

  def __getDeptName(self, p_item: dict, dept_id: Union[int, bytes, str]) -> str:
    
    n = ""
    if str(p_item["dept_id"]) == str(dept_id):
      dept_info = json_parse(p_item["dept_info"])
      n = dept_info["n"]
    return n
  
  def getAdaNo(self, refid: Union[str, int]) -> List[tuple]:
    return self.con.get("select fund, ada_no from bank_ada where refid = ?", (refid, ))
    

  def getReports(self, refid, inc_payee = False, inc_deduction = False, inc_ada = False): # reusable function
    
    ob_data = self.get(refid = refid)

    pstore = PayrollStore(self.con) # Payroll instances
    payroll_info = pstore.info(refid) # information of the payroll
    ded_list = json_parse(payroll_info["deduction_list"])

    data = {
      "payroll": {
        "range": (payroll_info["from"], payroll_info["to"]),
        "name": payroll_info["name"],
        "id": refid
      },
      "dept_info"   : [],
      "total_gross" : 0.0,
      "fund_gross"  : {},
      "ada_number"  : { "01": None, "02": None, "03": None },
      "ded_header"  : {}
    }

    # Setting Up the ada number of each charges 
    if inc_ada:
      ada_nos = self.getAdaNo(refid)
      for item in ada_nos:
        fund1, ada_no1 = item
        if fund1 == "01":
          data["ada_number"]["01"] = ada_no1
        if fund1 == "02":
          data["ada_number"]["02"] = ada_no1
        if fund1 == "03":
          data["ada_number"]["03"] = ada_no1
      
    # end Ada Number

    total_gross = 0.0
    total_net   = 0.0


    # this is used if @inc_deduction is true
    base_deduction  = [] # collection of all the contribution  and loan and 
    con_loan        = [] # Collection of the contribution and loan
    con_loan_header = {} # collection of the header
    
    if inc_deduction and isinstance(payroll_info["deduction_list"], (str, bytes)):
      
      base_deduction = json_parse(payroll_info["deduction_list"])
      
      for item in base_deduction:

        if isinstance(item["payroll_design"], (str, bytes)):
          item["payroll_design"] = json_parse(item["payroll_design"])

        if isinstance(item["bracket"], (str, bytes)):
          item["bracket"] = json_parse(item["bracket"])

        if item["type"] in ("c", "l"):
          con_loan.append(item)

      # loan and contribution header
      for item in con_loan:
        self.__setConLoanHeader(item["code"], item["name"], con_loan_header)
        
    for item in ob_data:

      dept_name = ""
      dept_id   = item["dept_id"]
      fund_code = item["fund_code"]
      ob_no     = item["ob_no"]
      
      # get the item of the payroll
      payroll_items = pstore.get_item(refid, {
        "dept_id": dept_id,
        "is_order": False
      })
      
      total_gross_per_office = 0.0
      total_net_per_office   = 0.0
      payee_name = ""
      
      total_ded_per_dept = deepcopy(con_loan_header)

      for p_item in payroll_items:

        if inc_payee:
          
          # payee_name must be retrieved at first
          if not payee_name:
            payee_name = self.__getPayee(p_item["emp_info"])
          
        if inc_deduction:
          # we are use like buffer in this situation since we only get the overall total per department
          ded_data = self.__getDeduction(con_loan_header, p_item["deduction"], total_ded_per_dept)

        slip = payslip(p_item, ded_list, payroll_info)
        total_gross_per_office += slip["gross"] + slip["gov_share"]
        total_net_per_office   += slip["net"]

        # get the last name of the dept_id is stored in the payroll_item
        if dept_name == "":
          dept_name = self.__getDeptName(p_item, dept_id)

      # get the total per charged
      if fund_code in data["fund_gross"]:
        data["fund_gross"][fund_code] += total_gross_per_office
      else:
        data["fund_gross"][fund_code] = total_gross_per_office

      # add to total overall gross
      total_gross += total_gross_per_office
      total_net   += total_net_per_office
      
      # information of the department
      data["dept_info"].append({
        "dept_id":         (dept_id, dept_name),
        "gross":           total_gross_per_office,
        "net":             total_net_per_office,
        "fund_charge":     fund_code,
        "ob_no":           ob_no,
        "payee":           payee_name,
        "total_deduction": total_ded_per_dept
      })

    # default if empty
    if not "01" in data["fund_gross"]:
      data["fund_gross"]["01"] = 0.0

    if not "02" in data["fund_gross"]:
      data["fund_gross"]["02"] = 0.0
    
    if not "03" in data["fund_gross"]:
      data["fund_gross"]["03"] = 0.0
    # end default

    data["ded_header"]  = con_loan_header
    data["total_gross"] = total_gross
    data["total_net"]   = total_net

    return data
      



      