from app.util.date import date_time
from app.util.md5 import md5

class DigitalStore:
  def __init__(self, scon = None):
    # this is a signature.db or the sql_signature
    self.con = scon


  def hash_code(self, name, pos_title):
    return md5(f'{name}{pos_title}'.lower()).upper()

  def save(self, name, pos_title, data, uid = None):
    self.con.commit('insert into sign(id, name, pos_title, data, datestarted, createdby, status) values(?, ?, ?, ?, ?, ?, "y")', (
      self.hash_code(name, pos_title), name, pos_title, data, date_time(), uid,
    ))

  def update(self, ids, name, pos_title, data, uid = None):
    self.con.commit('update sign set name = ?, pos_title = ?, data = ? where id = ?', (
      name, pos_title, data, ids,
    ))

  def get(self, ids = None):
    data = self.con.get('select id, name, pos_title from sign order by name asc') 
    ret = []
    for ids, name, pos_title in data:
      ret.append({
        'id': ids,
        'name': name,
        'pos_title': pos_title
      })
    return ret

  def get_byte(self, ids):
    data = self.con.get('select data from sign where id = ?', (ids, ))
    if not data: return None
    return data[0][0]