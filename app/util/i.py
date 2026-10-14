import mysql.connector as conn
import json


class i:
  _con = None
  def open(self):
    self.con = conn.connect (
      host = 'localhost',
      port = 3306,
      user = 'root',
      password = '',
      database = 'payroll_db'
    )
    #i._con = self.con

  def __init__(self, db = "", is_open = True):
    '''
      This is a testing class dont used it for production
    '''
    # here's the configuration of the database
    # for the future development it is use in
    # databasing
    self.db = ''
    if db:
      self.db = db
    self.is_open = is_open
    # if not i._con:
    #   print("mysql connnection started")
    # else:
    #   self.con = i._con
    if self.is_open:
      self.open()
    #self.con.ping(True) # this is not advisable for connection lost
    self.q = self.con.cursor(dictionary = True)

  def __del__(self):
    # closing the connection after it is used
    self.q.close()
    self.con.close()

  def close(self):
    self.con.close()
    
  def commit_r(self, sqltxt, tup = ()):
    # working with a update, delete, insert
    if len(tup) > 0:
      self.q.execute(sqltxt, tup)
    else:
      self.q.execute(sqltxt)
  
  def go(self):
    # Final commit
    self.con.commit()
  
  def commit(self, sqltxt, tup = ()):
    # working with a update, delete, insert
    if len(tup) > 0:
      self.q.execute(sqltxt, tup)
    else:
      self.q.execute(sqltxt)
    self.con.commit()

  def get(self, sqltxt, tup = ()):
    # workign with get data in mysql
    if len(tup) > 0:
      self.q.execute(sqltxt, tup)
    else:
      self.q.execute(sqltxt)
    return self.q.fetchall()
  
  def getone(self, sqltxt, tup = ()):
    # workign with get data in mysql
    if len(tup) > 0:
      self.q.execute(sqltxt, tup)
    else:
      self.q.execute(sqltxt)
    return self.q.fetchone()
    # it return to dictionary format data
    # self.con.rollback() # future dev for sql security    
    
  def json(self, sqltxt, tup = ()):
    if len(tup) > 0:
      self.q.execute(sqltxt, tup)
    else:
      self.q.execute(sqltxt)
    return json.dumps(self.q.fetchall(), default = str) 
    # return to json string