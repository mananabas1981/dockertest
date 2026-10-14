from app.lib.sql import sql 
from app.store.global_store import create_history
from app.util.age import ago_simple


def client_deactivate(con: sql, emp_id = None):
  con.commit('''update client set active = "n" where id = ?''', (emp_id, ))



def client_info(con, emp_id = None, emp_status = None, dept_id = None):
  
  cond = ""
  tup = []
  
  if emp_id:
    cond = " and c.id = ? "
    tup.append(emp_id)

  if emp_status:
    cond = " and ph.status = ? "
    tup.append(emp_status)

  if dept_id:
    cond = " and d.id = ? "
    tup.append(dept_id)
  
  
  q = f"""
    select 
      c.id as emp_id, c.pref_name, c.fname, c.mname, c.lname, c.suf_name,
      ph.title as pos_title, ph.status as emp_status,
      r.rate, r.rate_type,
      dh.dept_id, d.code as dept_code, d.title as dept_title,
      c.ename,
      c.gender,
      c.hr_id,
      c.active
    from position_history as ph 
    inner join client as c 
    on c.id = ph.emp_id and ph.datecreated = (
      select max(ph2.datecreated) from position_history as ph2 where ph2.emp_id = c.id
    )
    inner join rate_history as r on r.client_id = c.id and r.datecreated = (
      select max(r2.datecreated) from rate_history as r2 where r2.client_id = c.id
    )
    inner join department_history as dh on dh.emp_id = c.id and dh.datecreated = (
      select max(dh2.datecreated) from department_history as dh2 where dh2.emp_id = c.id
    )
    inner join department as d on dh.dept_id = d.id
    where c.status = '1' {cond}
  """

  res = con.get(q, tuple(tup)) # convert the list to touple

  ret = []
  for x in res:
    ret.append({
      "emp_id":    x[0],
      "pref_name": x[1],
      "fname": x[2],
      "mname": x[3],
      "lname": x[4],
      "suf_name": x[5],
      "pos_title": x[6],
      "emp_status": x[7],
      "rate": x[8],
      "rate_type": x[9],
      "dept_id": x[10],
      "dept_code": x[11],
      "dept_title": x[12],
      "ename": x[13],
      "gender": x[14],
      "hr_id": x[15],
      'active': x[16]
    })
    #     data.append({
    #       "pref_name": x[0],
    #       "fname":     x[1],
    #       "mname":     x[2],
    #       "lname":     x[3],
    #       "ename":     x[4],
    #       "suf_name":  x[5],
    #       "status":    x[6],
    #       "address":   x[7],
    #       "gender":    x[8],
    #       "id":        x[9],
    #       "dob":       x[10]
    #     })
  return ret

class ClientStore:
  def __init__(this, con = None):
    this.__con = con

  def _setConnection(this, con: sql):
    this.__con = con

  def info(this, hr_id):
    return this.__con.get("select id, fname, mname, lname from client where hr_id = ?", (
      hr_id,
    ))

  def info_by_id(this, ids: str):
    data = this.__con.get("select id, pref_name, fname, mname, lname, ename, suf_name, gender, dob, hr_id from client where id = ?", (
      ids,
    ))
    ret = None
    if data:
      ids, pref_name, fname, mname, lname, ename, suf_name, gender, dob, hr_id = data[0]
      ret = {
        'i': ids,
        'p': pref_name,
        'f': fname,
        'm': mname,
        'l': lname,
        'e': ename,
        's': suf_name,
        'g': gender,
        'b': dob,
        'h': hr_id
      }
      
    return ret


  def check_a(this, fname, lname):  
    fname = fname.lower()
    lname = lname.lower()

    r = this.__con.getone("select id, fname, mname, lname, ename from client where lower(fname) = ? and lower(lname) = ?", (
      fname,
      lname,
    ))
    return r
  
  def check_c(this, fname, lname):
    fname = fname.lower()
    lname = lname.lower()

    r = this.__con.get("select id, fname, mname, lname, ename from client where lower(fname) = ? and lower(lname) = ?", (
      fname,
      lname,
    ))
    return r
  
  def check_b(this, fname, lname, mname):  
    if fname:
      fname = fname.lower()
    if lname:
      lname = lname.lower()
    if mname:
      mname = mname.lower()
    
    r = this.__con.getone("select id, fname, mname, lname, ename from client where lower(fname) = ? and lower(lname) = ? and lower(mname) = ?", (
      fname,
      lname,
      mname,
    ))
    return r
    

  def _iExists(this, fname = "", mname = "", lname = "", ename = ""):
    q = "select * from client where (lower(fname) = ? and lower(lname) = ? and lower(mname) like ? and lower(ename) = ?) and status = 1"
    data = this.__con.getone(q, (
      fname,
      lname,
      f'{mname}%',
      ename,
    ))
    return data
  
  def _uExists(this, fname = "", mname = "", lname = "", ename = "", ids = ""):
    q = "select * from client where (lower(fname) = ? and lower(lname) = ? and lower(mname) like ? and lower(ename) = ? and not id = ?) and status = 1"
    data = this.__con.getone(q, (
      fname,
      lname,
      f'{mname}%',
      ename,
      ids, 
    ))
    return data

  def updateHRId(this, ids, hr_id):
    this.__con.commit('update client set hr_id = ? where id = ?', (
      hr_id,
      ids,
    ))

  def _clientUpdate(this, client):
    q = "update client set hr_id = ?, pref_name = ?, fname = ?, mname = ?, lname = ?, ename = ?, suf_name = ?, gender = ?, addr = ?, dob = ? where id = ? and status = 1"
    this.__con.commit(q, (
      client.hr_id,
      client.pref_name,
      client.fname,
      client.mname,
      client.lname,
      client.ename,
      client.suf_name,
      client.gender,
      client.addr,
      client.dob,
      client.id,      
    ))

  def _getClientsCount(this, search = "", dept_id = "", emp_status = "", is_active = None) -> int:
    c = this._getClients(search, dept_id, emp_status, is_count = True, is_active = is_active)
    if c:
      return int(c[0][0])
    return 0
  
  def _getClients(this, search = "", dept_id = "", emp_status = "", is_count = False, is_active = None, limit: int = 200) -> list:
    '''
      is_active: y or n , y for active and n for inactive
    '''


    dept_query = "dh.dept_id is null or" if not dept_id else ""

    search     = f'%{search.lower()}%'
    search_r   = search[::-1]

    q_pos = '' 
    if emp_status:
      q_pos = 'and ph.datecreated is not null'

    dept_id    = dept_id if dept_id else "%%"
    emp_status = emp_status if emp_status else "%%"
    
    qparam = ""
    qlimit = ""
    # if is_count is active then qparam will count the data

    # is_active = None
    active = ''
    if is_active:
      active = f'and c.active = "{is_active}"'


    if is_count:
      qparam = "count(c.id) as total"
    else:
      qparam = """
        c.pref_name, 
        c.fname, 
        c.mname, 
        c.lname, 
        c.ename, 
        c.suf_name, 
        c.status, 
        c.addr, 
        c.gender, 
        c.id, 
        c.dob,
        c.hr_id,
        ph.emp_id as is_position,
        r.client_id as is_rate,
        dh.dept_id as is_dept,
        eba.emp_id as is_bank,
        c.datecreated,
        r.rate,
        r.rate_type,
        d.code as dept_code,
        c.active,
        ph.status as pos_status,
        ph.title as pos_title
      """
      
      if limit:
        qlimit = f"limit {limit}"

    result = this.__con.get(f"""
                            select 
                              {qparam}
                            from client as c
                        
                        left join position_history as ph 
                        on c.id = ph.emp_id and ph.datecreated = (
                          select max(ph2.datecreated) from position_history as ph2 where ph2.emp_id = c.id
                        )
                        
                        left join rate_history as r on r.client_id = c.id and r.datecreated = (
                          select max(r2.datecreated) from rate_history as r2 where r2.client_id = c.id
                        )
                        left join emp_bank_account as eba on eba.emp_id = c.id and eba.datecreated = (
                          select max(eba2.datecreated) from emp_bank_account as eba2 where eba2.emp_id = c.id
                        )
                        left join department_history as dh on dh.emp_id = c.id and dh.datecreated = (
                          select max(dh2.datecreated) from department_history as dh2 where dh2.emp_id = c.id
                        )
                            
                        left join department as d on dh.dept_id = d.id
                            where 
                              (
                                (
                                  lower(c.fname) || lower(c.lname) like ? or 
                                  lower(c.lname) || lower(c.fname) like ? or 
                                  lower(c.fname) || lower(c.mname) || lower(c.lname) like ? or 
                                  lower(c.lname) || lower(c.fname) || lower(c.mname) like ?
                                ) or (
                                  lower(c.fname) || lower(c.lname) like ? or 
                                  lower(c.lname) || lower(c.fname) like ? or 
                                  lower(c.fname) || lower(c.mname) || lower(c.lname) like ? or 
                                  lower(c.lname) || lower(c.fname) || lower(c.mname) like ?
                                ) 
                              ) and c.status = 1
                              and ({dept_query} dh.dept_id like ? ) 
                              and (ph.status is null or ph.status like ?)
                              {active}
                              {q_pos}

                              order by c.lname, c.fname, c.mname { qlimit }""", (
                              search, 
                              search,
                              search,
                              search,
                              search_r, 
                              search_r,
                              search_r,
                              search_r,
                              dept_id,
                              emp_status,
                            ))
    
    # "pref_name": x[0],
    #   "fname":     x[1],
    #   "mname":     x[2],
    #   "lname":     x[3],
    #   "ename":     x[4],
    #   "suf_name":  x[5],
    #   "status":    x[6],
    #   "address":   x[7],
    #   "gender":    x[8],
    #   "id":        x[9],
    #   "dob":       x[10],
    #   "hr_id":     x[11]
    if not is_count:
      data = []
      rtype = {
        "d": "Daily",
        "m": "Monthly",
        'a': 'Yearly'
      }
      for x in result:
        # error list variable
        error_list = []

        if not x[12]:
          error_list.append({
            "error": True,
            "msg": "Position assigned!"
          })
        else:
          error_list.append({
            "error": False,
            "msg": "Position assigned!"
          })
        
        if not x[13]:
          error_list.append({
            "error": True,
            "msg": "Rate assigned!"
          })
        else:
          error_list.append({
            "error": False,
            "msg": "Rate assigned!"
          })

        if not x[14]:
          error_list.append({
            "error": True,
            "msg": "Department assigned!"
          })
        else:
          error_list.append({
            "error": False,
            "msg": "Department assigned!"
          })


        if not x[15]:
          error_list.append({
            "error": True,
            "msg": "Bank account assigned!"
          })
        else:
          error_list.append({
            "error": False,
            "msg": "Bank account assigned!"
          })
        
        # end of error list
          
        # check pos
        pos_list = []

        if x[17]:
          pos_list.append({
            'key': "Rate",
            'value': str(x[17]) + " / " + rtype[str(x[18])]
          })
        
        if x[19]:
          pos_list.append({
            'key': "Department",
            'value': x[19]
          })

        claim = None
        rs = this.__con.get("select pi.start, pi.end, p.refid from payroll_item as pi inner join payroll as p on p.refid = pi.payroll_refid where pi.emp_id = ? order by pi.start desc limit 1", (x[9], )) # emp_id
        if rs:
          start, end, refid = rs[0]
          claim = (start, end, refid)

        data.append({
          "pref_name": x[0],
          "fname": x[1],
          "mname": x[2],
          "lname": x[3],
          "ename": x[4],
          "suf_name": x[5],
          "status": x[6],
          "address": x[7],
          "gender": x[8],
          "id": x[9],
          "dob": x[10],
          "hr_id": x[11],
          "is_pos": x[12],
          "is_rate": x[13],
          "is_dept": x[14],
          "is_bank": x[15],
          "error":  error_list,
          "created": ago_simple(x[16]), # employee registered in the system
          "pos_info": pos_list,
          'active': x[20],
          "pos_status": x[21],
          "claim": claim,
          "pos_title": x[22]
        })
      result = data

    return result
  
  def get(this, emp_id = None) -> dict:
    res = this.__con.getone('''select 
                                pref_name, 
                                fname, 
                                mname, 
                                lname, 
                                ename, 
                                suf_name, 
                                status, 
                                addr, 
                                gender, 
                                id, 
                                dob,
                                hr_id,
                                active 
                              from client where id = ?
                            ''', (
                              emp_id,
                            ))
    data = {}
    if res:
      data['pref_name'] = res[0]
      data['fname']     = res[1]
      data['mname']     = res[2]
      data['lname']     = res[3]
      data['ename']     = res[4]
      data['suf_name']  = res[5]
      data['status']    = res[6]
      data['addr']      = res[7]
      data['address']   = res[7]
      data['gender']    = res[8]
      data['id']        = res[9]
      data['dob']       = res[10]
      data["hr_id"]     = res[11]
      data['active']    = res[12]

      # "pref_name": x[0],
      #   "fname":     x[1],
      #   "mname":     x[2],
      #   "lname":     x[3],
      #   "ename":     x[4],
      #   "suf_name":  x[5],
      #   "status":    x[6],
      #   "address":   x[7],
      #   "gender":    x[8],
      #   "id":        x[9],
      #   "dob":       x[10],
      #   "hr_id":     x[11]

    return data

  def newid(this) -> int:
    data = this.__con.get("select max(id + 1) as newid from client")
    return data[0][0]


  def _insert(this, pref_name = None, fname = None, mname = None, lname = None, ename = None, suf_name = None, gender = None, addr = None, dob = None, date = None, uid = "", hr_id = ""):
    q = "insert into client(id, pref_name, fname, mname, lname, ename, suf_name, gender, addr, datecreated, status, dob, addedby, hr_id, active) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    this.__con.commit(q, (
      this.newid(),
      pref_name,
      fname,
      mname,
      lname,
      ename,
      suf_name,
      gender,
      addr,
      date,
      1,
      dob,
      uid,
      hr_id,
      'y', # y for yes n for no
    ))

  def remove_employee(this, ids):
    q = "update client set status = ? where id = ?"
    this.__con.commit(q, (
      0, # status 0 means that the data is remove
      ids,  
    ))

class RateStore:
  def __init__(this, con):
    this.__con = con

  def get_last_rate(this, emp_id):
    return this.__con.getone("select client_id, rate, rate_type, nwpd from rate_history where client_id = ? order by datecreated desc", (
      emp_id,
    ))

  def get_rate(this, emp_id, limit = 0) -> list:
    # all rate of individual employee
    q = "select rate, rate_type, datecreated, nwpd from rate_history where client_id = ? order by datecreated desc"
    if limit > 0:
      q += f' limit {limit}'  
    return this.__con.get(q, (
      emp_id,  
    ))
  
  def get_rate_dict(this, emp_id, limit = 0) -> list:
    res = this.get_rate(emp_id, limit)
    data = []
    for x in res:
      data.append({
        'rate': x[0],
        'rate_type': x[1],
        'datecreated': x[2],
        'nwpd': x[3]
      })
        
    return data
  
  def create_rate(this, emp_id, rate, rate_type, datecreated, nwpd = None):
    this.__con.commit("insert into rate_history(client_id, rate, rate_type, datecreated, nwpd) values(?, ?, ?, ?, ?)", (
      emp_id,
      rate,
      rate_type,
      datecreated,  
      nwpd,
    ))

  def get_rate_one(this, emp_id, date):
    return this.__con.getone("select client_id, rate, rate_type, datecreated, createdby from rate_history where client_id = ? and datecreated = ?", (
      emp_id,
      date,
    ))

  def remove_rate(this, emp_id, date, uid):
    rate = this.get_rate_one(emp_id, date)
    if rate:
      create_history(this.__con, uid, "rate_history", rate, "d")
      this.__con.commit("delete from rate_history where client_id = ? and datecreated = ?", (
        emp_id,
        date,
      ))
      
class PositionStore:
  def __init__(this, con):
    this.__con = con

  def create_position(this, emp_id, title, status, datecreated, uid = None):
    this.__con.commit("insert into position_history(emp_id, title, status, datecreated, createdby) values(?, ?, ?, ?, ?)", (
      emp_id,
      title,
      status,
      datecreated,  
      uid,
    ))

  def get_last_position(this, emp_id):
    return this.__con.getone("select title, datecreated, status from position_history where emp_id = ? order by datecreated desc", (
      emp_id,  
    ))
  
  def get_position(this, emp_id, limit: int = 0):
    q = "select title, datecreated, status from position_history where emp_id = ? order by datecreated desc"
    if limit > 0:
      q += f' limit {limit}'

    return this.__con.get(q, (
      emp_id,  
    ))
  
  def get_position_dict(this, emp_id, limit = 0) -> list:
    res = this.get_position(emp_id, limit)  
    data = []
    for x in res:
      data.append({
        'title': x[0],
        'datecreated': x[1],
        'status': x[2]
      })
    return data

  def get_position_one(this, emp_id, date):
    return this.__con.getone("select emp_id, title, status, datecreated, createdby from position_history where emp_id = ? and datecreated = ?", (
      emp_id, 
      date,
    ))

  def remove_position(this, emp_id, date, uid):
    data = this.get_position_one(emp_id, date)
    if data:
      create_history(this.__con, uid, "position_history", data, "d")
      this.__con.commit("delete from position_history where emp_id = ? and datecreated = ?", (
          emp_id,
          date,
      ))



class DeptInfoStore:
  def __init__(this, con):
    this.__con = con

  def create_dept(this, emp_id, dept_id, datecreated, uid = None):
    this.__con.commit("insert into department_history(emp_id, dept_id, datecreated, createdby) values(?, ?, ?, ?)", (
      emp_id,
      dept_id,
      datecreated,  
      uid,
    ))

  def get_last_dept(this, emp_id):
    return this.__con.getone("select emp_id, dept_id from department_history where emp_id = ? order by datecreated desc", (
      emp_id,  
    ))

  def get_dept(this, emp_id, limit:int = 0) -> list:
    
    q = "select dh.emp_id, dh.dept_id, d.title, dh.datecreated \
                          from department_history as dh \
                          left join department as d on d.id = dh.dept_id\
                          where dh.emp_id = ? order by dh.datecreated desc"
    # if limit found
    if limit > 0:
      q += f' limit {limit}'

    return this.__con.get(q, (
      emp_id,  
    ))
  
  def get_dept_dict(this, emp_id, limit = 0) -> list:
    res = this.get_dept(emp_id, limit)
    data = []
    for x in res:
      data.append({
        'emp_id': x[0],
        'dept_id': x[1],
        'dept_name': x[2],
        'datecreated': x[3]
      })

    return data
  
  def get_dept_one(this, emp_id, dept_id, date):
    return this.__con.getone("select dept_id, emp_id, datecreated, createdby from department_history where dept_id = ? and emp_id = ? and datecreated = ?", (
      dept_id,
      emp_id,
      date,
    ))

  def remove_dept(this, emp_id, dept_id, date, uid):
    #this.__con.commit("")
    data = this.get_dept_one(emp_id, dept_id, date)
    if data:
      create_history(this.__con, uid, "department_history", data, "d")
      this.__con.commit("delete from department_history where dept_id = ? and emp_id = ? and datecreated = ?", (
        dept_id,
        emp_id,
        date,
      ))