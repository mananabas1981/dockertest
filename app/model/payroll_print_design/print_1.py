from app.store.payroll_default_store import DefaultPayrollSignatoryStore
from app.store.payroll_store import PayrollStore
from app.util.json import json_parse, json_stringify
from app.store.department_store import Department
from app.util.qrcode import Qr
from app.util.date import month_name
from app.util.payroll_calulator import payslip

from app.store.user_store import UserStore, UserEntity
from app.util.date import cdate_last_date_r, datetime_implement

from app.lib.sql import sql_signature
from app.store.digital_store import DigitalStore
from app.store.user_store import UserStore
from io import StringIO

class Total:
  def __init__(this):
    this.dw        = 0.0
    this.absent    = 0.0
    this.late      = 0.0
    this.undertime = 0.0
    this.gross     = 0.0
    this.total_ded = 0.0
    this.total_net = 0.0
    this.other     = {}

class _PrintHtml:
  def __init__(this, con, refid, dept_id, uid, payroll_type):
    this._con = con
    this._refid = refid
    this._dept_id = dept_id
    this._uid = uid

    this._output = ''
    this.payroll_type = payroll_type
    

  def init(this) -> tuple:
    refid = this._refid
    dept_id = this._dept_id

    con = this._con
    pstore = PayrollStore(con)
    
    payroll_info = pstore.info(refid)

    if not payroll_info:
      return False, 'Payroll Not Found'
    

    prepared_name = ''
    if payroll_info['status']:
      remark_status = json_parse(payroll_info['status'])
      
      for item in remark_status:
        if (item['step'] == 1):
          prepared_name = item['user']['name']

    _from = payroll_info["from"].split("-")
    _to   = payroll_info["to"].split("-")
    

    ded_list = json_parse(payroll_info["deduction_list"])
    
    # load all the signatory

    sign_list = json_parse(payroll_info["signatory_list"])

    # load the custom sign_list

    dd = DefaultPayrollSignatoryStore(con = con)
    c_sign = dd.load(refid, dept_id if dept_id else 'all')
    if c_sign:
      sign_list = json_parse(c_sign[0]['data'])

    user_store = UserStore(con)

    user_data = user_store.list_user(this._uid)
    if not user_data:
      return False, 'User not found!'
    
    user_info = UserEntity( ids = user_data[0]['id'], name = user_data[0]['name'], pos_title = user_data[0]['pos_title'] )

    ded_data = {

    }
    
  
    com_len = 0

    for x in ded_list:
      if (x['type'] == 'a'):
        com_len += 1

      if not x["code"] in ded_data:
        ded_data[x["code"]] = []

      ded_data[x["code"]].append(x)

    ded_len = 0
    # for x in ded_data:
    #   ded_len += 1

    for x in ded_data:
      x_cnt = len(ded_data[x])
      ded_len += x_cnt

    dept_name = "All Office"

    dept_obj = Department(con)
    dept_info = dept_obj.lists({
      "dept_id": dept_id
    })   

    dept_code = ''
    if dept_info:
      if dept_id:
        dept_code = dept_info[0][1]
        dept_name = f"{dept_info[0][1]} - {dept_info[0][2]}"

    items = pstore.get_item(refid, {
      "dept_id": dept_id,
      "is_order": False
    })

    qr = Qr(f"{dept_id}-{ payroll_info['refid'] }")

    g_total = Total()

    payroll_no = ''
    pqrcode = ''
    if this.payroll_type == 'print':
      payroll_no = f'''{dept_code}-{ payroll_info['refid']}'''
      pqrcode = qr.toHtmlTag()

      if not str(dept_id).strip():
        return (False, 'Printing of Payroll is per group/department')
    
    
    t = ''' 
      <style>
      
        @media print {
          header {
           
          }
          
          

          footer {
          }

          

          main {
            padding-top: 50px;

          }

          @page {
            size: landscape;
          }
        }


        .table, .table tr td, .table tr th {  
          border: 1px solid rgba(120, 120, 120);
          text-align: left;
        }

        .table {
          border-collapse: collapse;
          width: 100%;
        }
        .table tr th, .table td {
          text-align: center;
        }
        .table tr th {
          padding: 2px;
          font-size: 8pt;
          color: rgba(120, 120, 120);
        }
        .table td {
          padding-left: 5px;
          padding-right: 5px;
          font-size: 8pt;
        }
        .center {
          text-align: center;
        }
        .left {
          text-align: left;
        }

      </style>
      
    '''   
    
    t += f'''
      <header>
        <div style="position: relative;"> 
          <center><b>PAYROLL</b></center>
          <center>
            For the period: {month_name(int(_from[1]) - 1).upper()} {_from[2]}-{_to[2]}, {_from[0]}
          </center>
          <br />
        </div>
        <div style="width: 100%; position: relative;">

          <div style="position: absolute; left: 5px;">
            Company: Test Municipal
            <br />
            Fund: 
          </div>
          <div style="position: absolute; right: 200px;">
            Payroll No. : <b>{payroll_no}</b> 
            <br />
            Office: { dept_name.upper() }
          </div>
          <img src="{ pqrcode }" width="90" height="90" style="border-radius:5px; border: 1px solid black; position : absolute; right: 0px; top: -60px;" />
        </div>
      </header>
    '''
    ###############################################################
    #  HEADER OF THE TABLE                                        #
    ###############################################################
    
    t += f"""
    <main style="margin-top: 30px;">
    We acknowledge receipt of cash shown opposite our name as full compensation for services rendered for the period covered.
    <table class="table" style="margin-bottom: 5px;">
      <tr>
        <th rowspan="3">No</th>
        <th rowspan="3">Name</th>
        <th rowspan="3">Position</th>
        <th colspan="{6 + com_len}" class="center">Compensation</th>
        <th colspan="{ded_len - com_len}" class="center">Deduction</th>
        <th rowspan="3">Total <br />Deduction</th>
        <th rowspan="3">Net Amount</th>
        <th rowspan="3">Account<br /> Number</th>
      </tr>
    """
    # 6 + ded_len it is the original

    t += """
      <tr>
        <th rowspan="2">Rate</th>
        <th rowspan="2">No.<br/>Of<br/>Days<br/>Work</th>
        <th rowspan="2">Absent</th>
        <th rowspan="2">Late</th>
        <th rowspan="2">Under<br /> Time</th>
        <th rowspan="2">Gross Amount<br/> Earned</th>
    """
    # header group of the deduction like pag-ibig, sss
    for x in ded_data:
      x_cnt = len(ded_data[x])
      t += f"""
        <th colspan="{x_cnt}">{x}</th>
      """

    t += """
      </tr>
    """

    t += "<tr>"
    
    # name of the deduction like contribution , loan, ec etc...
    for x in ded_list:
      t += f"""
        <th>{x["name"]}</th>
      """
    t += "</tr>"

    ###############################################################
    #  END HEADER OF THE TABLE                                    #
    ###############################################################

    ###############################################################
    #  BODY OF THE TABLE                                          #
    ###############################################################
    i = 0

    for item in items:
      i += 1

      slip = payslip(item, ded_list, payroll_info)

      rt = str(slip['no_work_day']).split(".")
      
      no_day = slip['no_work_day']
      if len(rt) > 1:
        if (len(rt[1]) >= 6):
          no_day = f"{float(slip['no_work_day']):,.6f}"
          
      dw = "" if slip["no_work_day"] <= 0 else f"{no_day}"

      page_break = 'style="page-break-after:always;"' if i % 25 == 0 else '';

      # t += f'<tr {page_break}></tr>';

      t += f'<tr>'
      com:dict = slip['com'] # we can get the late, undertime, total absent
      
      # get the total
      g_total.dw += slip["no_work_day"]
      g_total.absent += slip["absent"]
      g_total.late += slip["late"] 
      g_total.undertime += slip["undertime"]
      g_total.gross += slip["gross"]

      # end get the total

      absent_t = f'{com["a"]}d : {slip["absent"]:,.2f}' if slip["absent"] != 0.0 else "-"
      late_t = f'{com["l"]}m : {slip["late"]:,.2f}' if slip["late"] != 0.0 else "-"
      under_time_t = f'{com["u"]}m : {slip["undertime"]:,.2f}' if slip["undertime"] != 0.0 else "-"
      gross_t = f'{slip["gross"]:,.2f}' if slip["gross"] != 0.0 else "-"
      
      # if i they dont want to display the  no of work days
      # dw if slip["salary_type"] == "d" else ""
      
      t += f"""
              <td>{i}</td>
              <td class="left">{slip["name"]}</td>
              <td class="left">{slip["position"]}</td>
              <td class="left">{slip["salary"]}</td>
              <td>{dw}</td>
              <td>{absent_t}</td>
              <td>{late_t}</td>
              <td>{under_time_t}</td>
              <td class="center">{gross_t}</td>
        """
      
      # deduction checker
      # check the check deductio
      # if match then display it
      for m in ded_list:
        ded01 = slip["deduction"]
        for n in ded01:
          value =  f'{float(n["value"]):,.2f}' if float(n["value"]) != 0.0 else "-"
          if m["code"] == n["code"] and m["name"] == n["name"]:
            t += f"""
              <td style="text-align: center;">{ value }</td>
            """
            # get the total
            nkey = m['code'] + m['name']
            if nkey in g_total.other:
              g_total.other[nkey] += float(n['value'])
            else:
              g_total.other[nkey] = float(n['value'])
          # else:
          #   t += f"""
          #   <td></td>
          # """

      # total 
      g_total.total_ded += slip["total_ded"]
      g_total.total_net += slip['net']
      # end total
      # net amount
      t += f"""<td class="left">{slip["total_ded"]:,.2f}</td>"""
      t += f"""<td class="left">{slip["net"]:,.2f}</td>"""
      
      # t += f"""<td class="left">{slip["account"]}</td>"""
      t += f"""<td class="left"></td>"""

      t += "</tr>"

    ###############################################################
    #  BODY OF THE TABLE                                          #
    ###############################################################

    # footer 
    t += '<tr>'
    t += f"""
          <td></td>
          <td class="left"></td>
          <td class="left"></td>
          <td class="left"></td>
          <td></td>
          <td>{float(g_total.absent):,.2f}</td>
          <td>{float(g_total.late):,.2f}</td>
          <td>{float(g_total.undertime):,.2f}</td>
          <td class="center">{g_total.gross:,.2f}</td>
    """
    # for dynamic total
    for key in g_total.other:
      t += f'<td><center>{g_total.other[key]:,.2f}</center></td>'
    
    t += f'<td>{g_total.total_ded:,.2f}</td>'
    t += f'<td>{g_total.total_net:,.2f}</td>'
    t += '<td></td>'

    t += '</tr>'

    # end footer
    t += """
    </table>
    </main>
    """

    ###########################################################
    # Generation of the signatory
    ###########################################################

    
    sign_list.insert(0, {
      'n': prepared_name,
      'c': 'Prepared By: ',
      'p': ''
    })

    # Add the prepared by in the top of the stack #
   
    # r = 0
    # ap = 'A'
    # for x in range(0, 3):
    #   c = 0
    #   for y in range(0, 3):
    #     for z in sign_list:
    #       index = json_parse(z["i"])
    #       if int(index[0]) == c and int(index[1]) == r:
    #         t += """<div style="font-size: 8pt; width: 33.12%; height: 70px; background-color: white; float: left;position: relative;border: 1px solid rgba(0, 0, 0, 0.2);" class="l">"""
    #         t += f"""
    #                   <div style="position: absolute;left: 0px; top: 0px; padding: 5px; height: 20px; width: 100%;">
    #                     {ap}. {z["c"]}
                        
    #                     <div style="text-align: center; margin-top: 20px; font-weight: bold;">
    #                       {z["n"].upper()}
    #                     </div>
    #                     <div style="text-align: center;">Signature Over Printed Name</div>
    #                     <div style="text-align: center;">{z["p"]}</div>
    #                   </div>
    #         """
    #         t += "</div>"
    #         ap = chr(ord(ap) + 1)
    #         break

    #     c += 1
    #   r += 1
    t += '<footer>'

  
    ap = 'A'
    for item in sign_list:
      t += """<div style="font-size: 8pt; width: calc((100% / 3) - 2px); height: 90px; background-color: white; float: left;position: relative; border: 1px solid rgba(0, 0, 0, 0.1);" class="l">"""
      t += f"""
                <div style="position: absolute;left: 0px; top: 0px; padding: 5px; height: 20px; width: 100%;">
                  
                  <div style="text-align: center; margin-top: 24px; font-weight: bold;margin-bottom: 5px;position: relative;">
                    {item["n"].upper()}
                  </div>
                  <div style="text-align: center;">Signature Over Printed Name</div>
                  <div style="text-align: center;">{item["p"]}</div>
                </div>
      """
      t += "</div>"
      ap = chr(ord(ap) + 1)


    
    ######################################## CAFOA NO. ################################################################
    t += """<div style="font-size: 8pt; width: calc((100% / 3) - 2px); height: 90px; background-color: white; float: left;position: relative;border: 1px solid rgba(0, 0, 0, 0.1);" class="l">"""
    t += f"""
              <div style="position: absolute;left: 0px; top: 0px; padding: 5px; height: 20px; width: 100%;">
                
                {ap}.
                <div style="text-align: center; margin-top: 24px; ;margin-bottom: 5px;">
                  CAFOA NO. ______________________
                  <br />
                  <br />
                  Date: _____________________
                </div>
                
              </div>
    """
    t += "</div>"
    ######################################## END CAFOA ################################################################

    
    t += '</footer>';

    this._output = t
    return True, "Ok"
  
  def output(this):
    return this._output


####################################################################################################################


# end 



####################################################################################################################


# demo testing
from app.model.payroll_print_design.print_v3 import PayrollPrintV3

# this class is used to print the payroll in json format

class PrintJSON:
  def __init__(self, con, refid, dept_id, uid):
    self.con     = con
    self.refid   = refid
    self.dept_id = dept_id
    self.uid     = uid

    self.output = {
      'header': {

      },

      'footer': {

      }
    }

    self.init()


  def init(self):
    pass

  

  def print(self):
    
    return self.output




class _PrintHtmlV2:
  # introduce in august 06, 2024
  
  def __init__(this, con, refid, dept_id, uid, payroll_type):
    this._con = con
    this._refid = refid
    this._dept_id = dept_id
    this._uid = uid

    this._output = ''
    this._action = []
    this.payroll_type = payroll_type
    
    # PayrollPrintV3(con, refid, dept_id, uid, payroll_type) # this is a testing


  def filter_display(this, ded_list, _ded_list, items):
    jj = 0
    while jj < len(_ded_list):
      _isfound = False
      if _ded_list[jj]["type"] == "a" or _ded_list[jj]["type"] == "l":
        for jitem in items:
          _deds = json_parse(jitem["deduction"])
          for _ded in _deds:
            if _ded_list[jj]["code"] == _ded["code"] and _ded_list[jj]["name"] == _ded["name"]:
              if _ded["value"] != 0.0:
                # print(ded_list[jj]["code"], ded_list[jj]["name"], _ded["code"], _ded["name"])
                _isfound = True
                break

        
        if _isfound:
          ded_list.append(_ded_list[jj])
      else:
        ded_list.append(_ded_list[jj]) # this is a contribution
      jj += 1


  def init(this) -> tuple:
    refid = this._refid
    dept_id = this._dept_id

    con = this._con
    pstore = PayrollStore(con)
    
    payroll_info = pstore.info(refid)

    if not payroll_info:
      return False, 'Payroll Not Found'
    
    job_title = {
      'j': 'JOB ORDER',
      'c': 'CONTRACT OF SERVICE',
      'r': 'REGULAR'
    }[payroll_info['type']]

    remark_status = payroll_info['status']

    prepared_name = ''
    sign_id = None
    if payroll_info['status']:
      remark_status = json_parse(payroll_info['status'])
      
      for item in remark_status:
        if (item['step'] == 1):
          prepared_name = item['user']['name']
          if 'sign_id' in item:
            sign_id  = item['sign_id']

    sign_data = ''
    if sign_id:
      sql_sign_con = None
      try:
        sql_sign_con = sql_signature()
        dss = DigitalStore(sql_sign_con)
        sign_data = dss.get_byte(sign_id)
      except Exception as er:
        print(er)
      finally:
        if sql_sign_con: sql_sign_con.close()

    _from = payroll_info["from"].split("-")
    _to   = payroll_info["to"].split("-")
    

    items = pstore.get_item(refid, {
      "dept_id": dept_id,
      "is_order": False
    })

    # here is collections where the the uneccessary to display not want to display
    #################################################################################
    # this algorithm is use to filter and onley display the
    ded_list = [] # container
    this.filter_display(ded_list, json_parse(payroll_info["deduction_list"]), items)
    ####################################################################################
    # not display uneccessary
    # ded_list = json_parse(payroll_info["deduction_list"])

    


    gcom_data, gded_data = {}, { }
    for item in ded_list:
      if item['type'] == 'a':
        if not item['code'] in gcom_data:
          gcom_data[item['code']] = []
        gcom_data[item['code']].append(item['name'])

      else:

        if not item['code'] in gded_data:
          gded_data[item['code']] = []
        gded_data[item['code']].append(item['name'])

    #get all the length of the compensation
    gcom_data_len = 0
    for x in gcom_data:
      gcom_data_len += len(gcom_data[x])

    # get all the length of the deducation
    gded_data_len = 0
    for x in gded_data:
      gded_data_len += len(gded_data[x])


    # 

    # load all the signatory

    sign_list = json_parse(payroll_info["signatory_list"])

    # load the custom sign_list

    dd = DefaultPayrollSignatoryStore(con = con)
    c_sign = dd.load(refid, dept_id if dept_id else 'all')
    if c_sign:
      sign_list = json_parse(c_sign[0]['data'])

    user_store = UserStore(con)

    # Sign key checking
    sign_key = user_store.sign_key(this._uid)
    for s_item in sign_list:
      if 'sign_key' in s_item:
        if sign_key == s_item['sign_key']:
          this._action.append({
            'sign_key': s_item['sign_key'],
            'sign_val': s_item['sign_val'],
            'sign_date': s_item['sign_date'],
            'action': s_item['c'],
            'name': s_item['n'],
            'pos': s_item['p']
          })
    # end sign key checking

    user_data = user_store.list_user(this._uid)
    if not user_data:
      return False, 'User not found!'
    
    user_info = UserEntity( ids = user_data[0]['id'], name = user_data[0]['name'], pos_title = user_data[0]['pos_title'] )

    ded_data = {

    }
    
  
    com_len = 0

    for x in ded_list:
      if (x['type'] == 'a'):
        com_len += 1

      if not x["code"] in ded_data:
        ded_data[x["code"]] = []

      ded_data[x["code"]].append(x)

    ded_len = 0
    # for x in ded_data:
    #   ded_len += 1

    for x in ded_data:
      x_cnt = len(ded_data[x])
      ded_len += x_cnt

    dept_name = "All Office"

    dept_obj = Department(con)
    dept_info = dept_obj.lists({
      "dept_id": dept_id
    })   

    dept_code = ''
    if dept_info:
      if dept_id:
        dept_code = dept_info[0][1]
        dept_name = f"{dept_info[0][1]} - {dept_info[0][2]}"

   
    

    qr = Qr(f"{dept_id}-{ payroll_info['refid'] }")

    g_total = Total()

    payroll_no = ''
    pqrcode = ''
    if this.payroll_type == 'print':
      payroll_no = f'''{dept_code}-{ payroll_info['refid']}'''
      pqrcode = qr.toHtmlTag()

      if not str(dept_id).strip():
        return (False, 'Printing of Payroll is per group/department')
    

    this.tio = StringIO()


    this.tio.write(''' 
      <style>

        body {
            opacity: 0; /* Start invisible */
            animation: fadeIn 0.5s forwards; /* Apply fadeIn animation */
        }

        @keyframes fadeIn {
            from {
                opacity: 0; /* Start with opacity 0 */
            }
            to {
                opacity: 1; /* End with opacity 1 */
            }
        }
        
        @media print {
          header {
           
          }
          
          

          footer {
          }

          

          main {
            padding-top: 50px;

          }

          @page {
            size: landscape;
          }
        }


        .table, .table tr td, .table tr th {  
          border: 1px solid rgba(120, 120, 120);
          text-align: left;
        }

        .table {
          border-collapse: collapse;
          width: 100%;
        }
        .table tr th, .table td {
          text-align: center;
        }
        .table tr th {
          padding: 2px;
          font-size: 8pt;
          color: rgba(120, 120, 120);
        }
        .table td {
          padding-left: 5px;
          padding-right: 5px;
          font-size: 8pt;
        }
        .center {
          text-align: center;
        }
        .left {
          text-align: left;
        }

    ''')

    # start of the sticky
    if this.payroll_type != 'print':
      # add a sticky to the browser when viewing the payroll list
      # add sticky position in  header of the document
      this.tio.write('''
          .hhh-01 {
            position: -webkit-sticky;
            position: sticky;
            top: -1px;
          }

          .hhh-02 {
            position: -webkit-sticky;
            position: sticky;
            top: 14px;
          }
          .hhh-03 {
            position: -webkit-sticky;
            position: sticky;
            top: 29px;
          }

          table tr:hover {
            background-color: #ddd;
            cursor: pointer;
          }

      ''')
    # end sticky header 

    this.tio.write('</style>')   
    
    this.tio.write(f'''
      <header>
        <div style="position: relative;"> 
          <center style="letter-spacing: 3px;"><b>PAYROLL OF THE {job_title}</b></center>
          <center>
            For the period: <b>{month_name(int(_from[1]) - 1).upper()} {_from[2]}-{_to[2]}, {_from[0]}</b>
          </center>
          <br />
        </div>
        <div style="width: 100%; position: relative;">

          <div style="position: absolute; left: 5px;">
            Company: Test Municipal
            <br />
            Fund: 
          </div>
          <div style="position: absolute; right: 200px;">
            Payroll No. : <b>{payroll_no}</b> 
            <br />
            Office: { dept_name.upper() }
          </div>
          <img src="{ pqrcode }" width="90" height="90" style="border-radius:5px; position : absolute; right: 0px; top: -60px;" />
        </div>
      </header>
    ''')



    ###############################################################
    #  HEADER OF THE TABLE                                        #
    ###############################################################


    colspan_01 = 8
    if payroll_info['type'] == 'r':
      colspan_01 = 3
    
    this.tio.write(f"""
    <main style="margin-top: 30px;">
    We acknowledge receipt of cash shown opposite our name as full compensation for services rendered for the period covered.
    <table class="table" style="margin-bottom: 5px;">
      <tr class="hhh-01">
        <th rowspan="3" style="color: black; background-color: #dddddd;">No</th>
        <th rowspan="3" style="color: black; background-color: #dddddd;">Name</th>
        <th rowspan="3" style="color: black; background-color: #dddddd;">Position</th>
        <th colspan="{colspan_01 + gcom_data_len}" class="center" style="color: white; background-color: #b6d7a8; font-weight: bold;">COMPENSATIONS</th>
        <th colspan="{gded_data_len}" class="center" style="color: white; background-color: #93c47d; font-weight: bold;">DEDUCTIONS</th>
        <th rowspan="3" style="color: white; background-color: #6aa84f;">Total <br />Deduction</th>
        <th rowspan="3" style="color: black; background-color: #dddddd;">Net Amount</th>
        <th rowspan="3" style="color: black; background-color: #dddddd;">Account<br /> Number</th>
      </tr>
    """)
    # 6 + ded_len it is the original

    if payroll_info['type'] == 'r':
      this.tio.write("""
        <tr class="hhh-02">
          <th rowspan="2" style="color: black; background-color: #dddddd;">Rate</th>
          <th rowspan="2" style="color: black; background-color: #dddddd;">Salary<br/>for<br>the period</th>
      """)
    else:
      this.tio.write("""
        <tr class="hhh-02">
          <th rowspan="2" style="color: black; background-color: #dddddd;">Rate</th>
          <th rowspan="2" style="color: black; background-color: #dddddd;">No.<br/>Of<br/>Days<br/>Work</th>
          <th rowspan="2" style="color: black; background-color: #dddddd;">Salary<br/>for<br>the period</th>
          <th rowspan="2" style="color: black; background-color: #dddddd;">Absent</th>
          <th rowspan="2" style="color: black; background-color: #dddddd;">Late</th>
          <th rowspan="2" style="color: black; background-color: #dddddd;">Under<br /> Time</th>
          <th rowspan="2" style="color: black; background-color: #dddddd;">Total<br/>Deduction</th>
      """)
    # header group of the deduction like pag-ibig, sss
    for x in gcom_data:
      this.tio.write(f'<th colspan="{len(gcom_data[x])}" style="color: black; background-color: #dddddd;">{x}</th>')

    this.tio.write('<th rowspan="2" style="color: black; background-color: #dddddd;">Gross Amount<br/> Earned</th>')
    
    # top under
    for x in gded_data:
      this.tio.write(f'<th colspan="{len(gded_data[x])}" style="background-color: #38761d; color: white;">{x}</th>')

    this.tio.write('</tr>')

    this.tio.write('<tr class="hhh-03">')
    for x in gcom_data:
      for y in gcom_data[x]:
        this.tio.write(f'<td style="color: black; background-color: #dddddd;">{y}</td>')
    
    # under
    for x in gded_data:
      for y in gded_data[x]:
        this.tio.write(f'<td style="background-color: #b6d7a8; color: black;">{y}</td>')

    this.tio.write('</tr>')

    gtotal_gross, gtotal_deduction_com = 0.0, 0.0
    count = 0

    gtotal_com, gtotal_deduction_con_loan = {}, {}

    gtotal_deduction, gtotal_net, g_total_salary_period = 0.0, 0.0, 0.0
    for item in items:
      count += 1

      slip = payslip(item, ded_list, payroll_info)

      gtotal_gross += slip['gross']
      gtotal_deduction_com += slip['deduction_com']

      gtotal_deduction += slip['total_ded']
      gtotal_net += slip['net']

      item_emp_info = json_parse(item['emp_info'])
      item_ded = json_parse(item['deduction'])

      # item_com = json_parse(item['compensation'])
      item_name = f'''{item_emp_info['l']}, {item_emp_info['f']} {item_emp_info['m']} {item_emp_info['e']}'''.upper()
      this.tio.write(f'''<tr class="tr01" rel="{slip['employee_no']}">''')

      __absent, __late, __undertime, __ded_com = '', '', '', ''
      __absent = f"{slip['absent']:,.2f}" if slip['absent'] != 0.0 else '-'
      __late = f"{slip['late']:,.2f}" if slip['late'] != 0.0 else '-'
      __undertime = f"{slip['undertime']:,.2f}" if slip['undertime'] != 0.0 else '-'
      __ded_com = f"{slip['deduction_com']:,.2f}" if slip['deduction_com'] != 0.0 else '-'


      # print(item["start"], item["end"])          
      period_txt = ''


      if datetime_implement('2024-12-23 00:00:00', payroll_info['datecreated']):
        _, _, sday = item["start"].split("-")
        _, _, eday = item["end"].split("-")

        period_txt = f' - <span style="color: red;"> (<b>{sday}-{eday}</b>)</span>'


      

      if payroll_info['type'] == 'r':
        this.tio.write(f'''
                <td>{count}</td>
                <td>{slip['name'].upper()}</td>
                <td>{slip['position']}</td>
                <td style="text-align: right;">{slip['salary']}</td>
                <td style="text-align: right;">{slip['salary_period']:,.2f} {period_txt}</td>
              ''')
      else:

        slip_work_day = f'''{slip['no_work_day']:,.2f}'''
        no_work_day_01 = slip_work_day if slip['salary_type'] != 'm' else '-'
        if datetime_implement('2024-11-05 00:00:00', \
                              payroll_info['datecreated']) \
                                and slip['nwpd'] > 4:
          # Starting in the this month it display the total work day
          if slip['salary_type'] == 'm':
            no_work_day_01 = slip_work_day # 

        this.tio.write(f'''
              <td>{count}</td>
              <td>{slip['name'].upper()}</td>
              <td>{slip['position']}</td>
              <td style="text-align: right;">{slip['salary']}</td>
              <td style="text-align: right;">{ no_work_day_01 }</td>
              <td style="text-align: right;">{slip['salary_period']:,.2f} {period_txt}</td>
              <td style="text-align: right;">{__absent}</td>
              <td style="text-align: right;">{__late}</td>
              <td style="text-align: right;">{__undertime}</td>
              <td style="text-align: right;">{__ded_com}</td>
            ''')

      g_total_salary_period += slip['salary_period']
      
      # compensation
      for x in gcom_data:
        for y in gcom_data[x]:
          for __item in item_ded:
            if y == __item['name'] and x == __item['code']:
              __value = f'{__item["value"]:,.2f}' if __item['value'] != 0.0 else '-'
              this.tio.write(f'''<td style="text-align: right;">{__value}</td>''')

              # get the total like aca , clothing or rata
              __code = f'''{__item['code']}@{__item['name']}'''
              if not __code in gtotal_com:
                gtotal_com[__code] = 0.0
              gtotal_com[__code] += __item['value']

      this.tio.write(f"""<td style="text-align: right;">{slip['gross']:,.2f}</td>""")
    
      # deduction & contribution
      for x in gded_data:
        for y in gded_data[x]:
          for __item in item_ded:
            if y == __item['name'] and x == __item['code']:
              __value = f'{__item["value"]:,.2f}' if __item['value'] != 0.0 else '-'

              # for coloring red
              # this down a bit performance for large datasets
              __red_color = ' style="text-align: right;"';
              for ded_based in ded_list:
                if ded_based['type'] != 'a' and ded_based['view_only'] == 'n' and ded_based['code'] == __item['code'] and ded_based['name'] == __item['name'] and __item['value'] != 0.0:
                  __red_color = ' style="color: red; text-align: right;"'
              # end coloring red

              this.tio.write(f'''<td{__red_color}>{__value}</td>''')


              # get the total contribution or loan
              __code = f'''{__item['code']}@{__item['name']}'''
              if not __code in gtotal_deduction_con_loan:
                gtotal_deduction_con_loan[__code] = 0.0
              gtotal_deduction_con_loan[__code] += __item['value']
      
      # Total Deduction
      ___total_ded = f"{slip['total_ded']:,.2f}" if slip['total_ded'] != 0.0 else '-' 
      this.tio.write(f'''<td style="text-align: right;">{___total_ded}</td>''')
      this.tio.write(f'''<td style="text-align: right; font-weight: bold;">{slip['net']:,.2f}</td>''')
      this.tio.write('<td></td>')


      this.tio.write('</tr>')


    # total footer
    jjj = f'{gtotal_deduction_com:,.2f}' if gtotal_deduction_com != 0.0 else '-'

    if payroll_info['type'] == "r":
      this.tio.write(f'''
        <tr style="font-weight: bold;">
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td style="text-align: right;">{jjj}</td>
      ''')
    else:
      this.tio.write(f'''
        <tr style="font-weight: bold;">
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td style="text-align: right;">{g_total_salary_period:,.2f}</td>
          <td></td>
          <td></td>
          <td></td>
          <td style="text-align: right;">{jjj}</td>
      ''')

    for x in gtotal_com:
      yyy = f'{gtotal_com[x]:,.2f}' if gtotal_com[x] != 0.0 else '-'
      this.tio.write(f'<td style="text-align: right;">{yyy}</td>')

    this.tio.write(f'<td style="text-align: right;">{gtotal_gross:,.2f}</td>')

    for x in gtotal_deduction_con_loan:
      yyy = f'{gtotal_deduction_con_loan[x]:,.2f}' if gtotal_deduction_con_loan[x] != 0.0 else '-'
      this.tio.write(f'<td style="text-align: right;">{yyy}</td>')

    # total deduction and net
    __gtotal_deduction = f'{gtotal_deduction:,.2f}' if gtotal_deduction != 0.0 else '-'
    this.tio.write(f'<td style="text-align: right;">{__gtotal_deduction}</td>')
    this.tio.write(f'<td style="text-align: right;">{gtotal_net:,.2f}</td>')

    this.tio.write('</tr>')
    # end total footer'


    # end footer
    this.tio.write("""
    </table>
    </main>
    """)

    ###########################################################
    # Generation of the signatory
    ###########################################################

    
    sign_list.insert(0, {
      'n': prepared_name,
      'c': 'Prepared By: ',
      'p': '',
      'data': sign_data
    })

    # Add the prepared by in the top of the stack #
   
    # r = 0
    # ap = 'A'
    # for x in range(0, 3):
    #   c = 0
    #   for y in range(0, 3):
    #     for z in sign_list:
    #       index = json_parse(z["i"])
    #       if int(index[0]) == c and int(index[1]) == r:
    #         t += """<div style="font-size: 8pt; width: 33.12%; height: 70px; background-color: white; float: left;position: relative;border: 1px solid rgba(0, 0, 0, 0.2);" class="l">"""
    #         t += f"""
    #                   <div style="position: absolute;left: 0px; top: 0px; padding: 5px; height: 20px; width: 100%;">
    #                     {ap}. {z["c"]}
                        
    #                     <div style="text-align: center; margin-top: 20px; font-weight: bold;">
    #                       {z["n"].upper()}
    #                     </div>
    #                     <div style="text-align: center;">Signature Over Printed Name</div>
    #                     <div style="text-align: center;">{z["p"]}</div>
    #                   </div>
    #         """
    #         t += "</div>"
    #         ap = chr(ord(ap) + 1)
    #         break

    #     c += 1
    #   r += 1
    this.tio.write('<footer>')

    # generating the e signature
    sql_sign_con = None
    try:
      sql_sign_con = sql_signature()
      dss = DigitalStore(sql_sign_con)
      
      for item in sign_list:
        if 'sign_val' in item:
          if item['sign_val']:
            sign_id = item['sign_val']
            sign_data = dss.get_byte(sign_id)
            item['data'] = sign_data
    except Exception as er:
      print(er)
    finally:
      if sql_sign_con: sql_sign_con.close()
    # end generating e signature
    
    ap = 'A'
    for item in sign_list:
      this.tio.write("""<div style="font-size: 8pt; width: calc((100% / 3) - 2px); height: 90px; background-color: white; float: left;position: relative; border: 1px solid rgba(0, 0, 0, 0.1);" class="l">""")

      img = ''
      if 'data' in item:
        if item['data']:
          img = f'<img src="{item["data"]}" style="position: absolute; top: -45px; left: 0px; right: 0px; margin: auto; width: 100px; height: 50px; z-index: 10;" />'


      this.tio.write(f"""
                <div style="position: absolute;left: 0px; top: 0px; padding: 5px; height: 20px; width: 100%;">
                  {ap}. {item["c"]}
                  
                  <div style="text-align: center; margin-top: 24px; font-weight: bold;margin-bottom: 5px;position: relative;">
                    {img}
                    {item["n"].upper()}
                  </div>
                  <div style="text-align: center;">Signature Over Printed Name</div>
                  <div style="text-align: center;">{item["p"]}</div>
                </div>
      """)
      this.tio.write("</div>")
      ap = chr(ord(ap) + 1)


    
    ######################################## CAFOA NO. ################################################################
    this.tio.write("""<div style="font-size: 8pt; width: calc((100% / 3) - 2px); height: 90px; background-color: white; float: left;position: relative;border: 1px solid rgba(0, 0, 0, 0.1);" class="l">""")
    this.tio.write(f"""
              <div style="position: absolute;left: 0px; top: 0px; padding: 5px; height: 20px; width: 100%;">
                
                {ap}.
                <div style="text-align: center; margin-top: 24px; ;margin-bottom: 5px;">
                  CAFOA NO. ______________________
                  <br />
                  <br />
                  Date: _____________________
                </div>
                
              </div>
    """)
    this.tio.write("</div>")
    ######################################## END CAFOA ################################################################

    
    this.tio.write('</footer>')


    # this part the must the payroll editor only
    this.tio.write('''
      <script>
        (async () => {
          const tr = document.getElementsByClassName("tr01");
          const tr_len = tr.length;
          for (let i = 0; i < tr_len; i++) {
            tr[i].addEventListener('click', () => {
              const emp_id = tr[i].attributes.rel.nodeValue;
              localStorage.setItem('frame_emp_id', emp_id);
            });
          }
        })();
      </script>

    ''')
    this._output = this.tio.getvalue()
    this.tio.close()

    return True, "Ok"
  
  def output(this):
    return this._output

  def action(this):
    return this._action



class PayrollPrintHandler():
  def __init__(this, con = None, kind = 'html', uid = None, payroll_type = 'view'):
    this._output = ''
    this._con = con
    this._kind = kind

    this._uid = uid

    this.payroll_type = payroll_type
    this._action = []

  def init(this, refid, dept_id) -> tuple:
    if this._kind == 'html':

      pstore = PayrollStore(this._con) 
      payroll_info = pstore.info(refid)

      if datetime_implement('2024-08-07 00:00:00', payroll_info['datecreated']):
      
        print_obj = _PrintHtmlV2(this._con, refid, dept_id, this._uid, this.payroll_type)
        this._action = print_obj.action()

      else:
        
        print_obj = _PrintHtml(this._con, refid, dept_id, this._uid, this.payroll_type)

      ok, msg = print_obj.init()
      this._output = print_obj.output()
      return (ok, msg)

  def action(this):

    return this._action

  def output(this):
    return this._output
  