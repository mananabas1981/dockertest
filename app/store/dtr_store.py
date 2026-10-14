from app.util.json import json_stringify, json_parse
from app.util.date import dt, date_time
from app.lib.net import http
from app.store.system_store import sys_info
from app.lib.sql import sql
from app.util.date import month_name, dt

class DtrStore:
  def __init__(self, con, uid = None):  
    self.con = con
    self.uid = uid

  def getCode(self, code = None) -> list:

    where_q = ''
    tup = ()
    if code:
      where_q = 'where code = ?'
      tup = (code, )


    res = self.con.get(f'''select 
      code,
      emp_id, 
      hr_id, 
      from_t, 
      to_t, 
      header, 
      data, 
      total_absent, 
      total_late, 
      total_undertime,
      scannedby,
      credit_deduction,
      status,
      sent_status 
    from dtr {where_q} order by code desc limit 100
  ''', tup)

    ret = []
    for code, emp_id, hr_id, from_t, to_t, header, data, total_absent, total_late, total_undertime, scannedby, credit_deduction, status, sent_status in res:
      ret.append({
        'code': code,
        'emp_id': emp_id,
        'hr_id': hr_id,
        'from_t': from_t,
        'to_t': to_t,
        'header': json_parse(header),
        'data': json_parse(data),
        'total_absent': total_absent,
        'total_late': total_late,
        'total_undertime': total_undertime,
        'scannedby': scannedby,
        'status': status,
        'credit_deduction': credit_deduction,
        'sent_status': sent_status
      })

    return ret

  def last_code(self):
    code = f'001-0001'
    last_q = self.con.get('select code from dtr order by code desc limit 1')

    if last_q:
      tmp = last_q[0][0]

      key, value = tmp.split('-')
      key = int(key)
      value = int(value)

      value += 1

      if value > 9999:
        key += 1
        value = 1


      code = f'{key:0>3}-{value:0>4}'

    return code


  def exists(self, emp_id, from_, to_):
    res = self.con.get('select code from dtr where emp_id = ? and from_t <= ? and to_t >= ?', ( 
      emp_id,
      to_,
      from_,
    ))

    return len(res) > 0

  def insert(self, data, header, from_, to_, emp_id, hr_id):

    code = self.last_code()

    self.con.commit('''
      insert into dtr (code, emp_id, hr_id, from_t, to_t, header, data, scannedby, status, sent_status, scannedby, date_scanned)
      values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
      code, emp_id, hr_id, from_, to_, json_stringify(header), json_stringify(data), self.uid, 0, 0, self.uid, date_time(),
    ))

    return code

  def is_approve(self, code):
    res = self.con.get('select status from dtr where code = ?', (code, ))
    if res:
      status = int(res[0][0])
      if status == 1: return True

    return False

  def is_sent(self, code):
    res = self.con.get('select sent_status from dtr where code = ?', (code, ))
    if res:
      status = int(res[0][0])
      if status == 1: return True

    return False

  def update(self, code, absent, late, undertime, total_leave):
    self.con.commit('''
      update dtr set total_absent = ?,
      total_late = ?,
      total_undertime = ?,
      status = ?,
      credit_deduction = ?, 
      approved_by = ?,
      date_approved = ?,
      sent_by = ?,
      date_sent = ?,
      sent_status = 1
      where status = 0 and code = ?
    ''', (absent, late, undertime, 1, total_leave, self.uid, date_time(), self.uid, date_time(), code, ))
    

  def update_hrms(self, code, emp_id, credit_minus, from_t, tard):
    
    # particular
    # format: July.Late.Undertime.Absent.code
    yr, month, _ = from_t.split('-') # get the dtr information

    particular = f'''{month_name(int(month) - 1)}.Late({tard['late']}).Undertime({tard['undertime']}).Absent({tard['absent']})..{code}'''


    # payload for the hrms
    cpayload = {
        "emp_id": f'{emp_id}', # this also must edited
        "year": f'0', # This is update in the hrmsystem
        "month": f'0', # this is updated in the hrmssystem
        "type": "A",
        "particular": particular, # this also edited
        "vac": f"{credit_minus}", # the late and absent, undertime must be deducted here
        "sick": "",
        "vac_bal": "0.0", # this is proceesed by the server hrms
        "sic_bal": "0.0" # this processed by the server hrms
    } 

    hrms_url = '/api/leave/tardiness/deduction/qywhduysii2232434idkdopsosklmmmksjsjs'
    con = sql()
    ss = sys_info(con)
    con.close() # avoid database lock

    dtr_data = http(f'{ss["hr_ip"]}{hrms_url}', cpayload)
    rdata = json_parse(dtr_data)
    
    return rdata
