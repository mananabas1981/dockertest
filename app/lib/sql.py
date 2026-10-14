import sqlite3
from os import sep

class sql:
  
  def __init__(this, db_name = "payroll.db"):
    this.db_name = db_name
    this.__con = sqlite3.connect(f"data{sep}db{sep}{db_name}")

  def open(this):
    # for if the database closed can be reopen using the open
    this.__con = sqlite3.connect(f"data{sep}db{sep}{this.db_name}")

  def commit(this, query, param = ()):
    if param:
      this.__con.execute(query, param)
    else:
      this.__con.execute(query)

  def get(this, query, param = ()) -> list:
    cur = this.__con.cursor()
    if param:
      cur.execute(query, param)
    else:
      cur.execute(query)

    result = cur.fetchall()
    cur.close()
    return result
  
  def getone(this, query, param = ()) -> tuple:
    cur = this.__con.cursor()
    if param:
      cur.execute(query, param)
    else:
      cur.execute(query)

    result = cur.fetchone()
    cur.close()
    return result

  def go(this):
    this.__con.commit()

  def close(this):
    this.__con.close()
  

# for sql_dtr
class sql_signature(sql):
  def __init__(self):
    super().__init__(db_name = "signature.db")


# for sql_dtr
class sql_dtr(sql):
  def __init__(self):
    super().__init__(db_name = 'dtr.db')