from app.lib.sql import sql
from app.store.client_store import PositionStore
from dataclasses import dataclass

@dataclass
class DefaultDEductionEntity:
  code: str
  name: str
  emp_id: str
  value: float = 0.0
  type_ded: str = None
  end_term: str = None

  createdby: str = None
  datecreated: str = None


class DefaultDeduction:
  def __init__(self, con):
    self.con: sql = con

  def __insert(self, ded: DefaultDEductionEntity):
    self.con.commit('''
      insert into default_emp_ded(
        code, name, emp_id, value, datecreated, createdby, type_ded, end_term
      ) values(?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
      ded.code, ded.name, ded.emp_id, ded.value, ded.datecreated, ded.createdby, ded.type_ded, ded.end_term
    ))

  def save(self, ded: DefaultDEductionEntity):
    self.__insert(ded) # directly insert 

  def remove_default(self, en: DefaultDEductionEntity):
    self.con.commit('delete from default_emp_ded where code = ? and name = ? and emp_id = ? and datecreated = ?', (
      en.code,
      en.name,
      en.emp_id,
      en.datecreated,
    ))

  def get_default_by_emp_id(self, emp_id):
    data = self.con.get(f'''select code, name, emp_id, value, type_ded, end_term, datecreated from default_emp_ded where emp_id = ? order by datecreated desc''', (
      emp_id,
    ))
    ret = []
    
    for item in data:
      ret.append({
        'code': item[0],
        'name': item[1],
        'emp_id': item[2],
        'value': item[3],
        'type_ded': item[4],
        'end_term': item[5],
        'datecreated': item[6]
      })

    return ret


  def get_default(self, en: DefaultDEductionEntity, limit = None):
    
    data = self.con.get(f'''select code, name, emp_id, value, type_ded, end_term, datecreated from default_emp_ded 
                        where code = ? and name = ? and emp_id = ? order by datecreated desc {'limit ' + str(limit) if limit else ''}''', (
      en.code,
      en.name,
      en.emp_id,
    ))
  

    ret = []
    
    for item in data:
      ret.append({
        'code': item[0],
        'name': item[1],
        'emp_id': item[2],
        'value': item[3],
        'type_ded': item[4],
        'end_term': item[5],
        'datecreated': item[6]
      })

    return ret

  def get_employee(self, code, name, search = ""):
    
    search = search.replace(" ", "").replace(",", "")
    search = f"%{search}%"
    
    data = self.con.get('''
      select 
            c.id,
            c.pref_name,
            c.fname,
            c.mname,
            c.lname,
            c.ename,
            c.suf_name,
            c.gender,
            c.dob
      from 
          client as c 
      where status = 1 and replace((c.lname||c.fname||c.mname||c.ename), " ", "") like ?
      order by c.lname, c.fname, c.mname, c.ename, c.dob limit 50
    ''', (
      search,
    ))

    pos_store = PositionStore(self.con)
    ret = []

    for item in data:
      last_pos = pos_store.get_last_position(item[0])
      title, _, emp_status = last_pos if last_pos else (None, None, None) # _ = datecreated
      
      de = self.get_default(DefaultDEductionEntity(code = code, name = name, emp_id = item[0]))
      value = de[0]['value'] if de else None

      ret.append({
        'id': item[0],
        'pref_name': item[1],
        'fname': item[2],
        'mname': item[3],
        'lname': item[4],
        'ename': item[5],
        'suf_name': item[6],
        'gender': item[7],
        'dob': item[8],
        'pos_title': title,
        'emp_status': emp_status,
        'value': value
      })

    return ret