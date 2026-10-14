from app.store.remittance_store import RemittanceStore
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment, Border, Side, Font 

from os import sep
from io import BytesIO
from base64 import b64encode

# custom design for remittances
from app.model.remittance.rpag_ibig import PagIbig 
from app.model.remittance.rsss import SSS
# end custom design for remittances

from app.util.date import month_name

class RemittanceAdapter:
  def __init__(self, con, ids):
    self.con = con
    self.ids = ids

    self.code = ''

    self.data = {}
    self.items = []

    self.rs = RemittanceStore(self.con)
    self.collect = []

    self.load_item()
    self.init_base()
  

  def load_item(self):
    self.items = self.rs.get_item(remittance_id = self.ids)

  def init_base(self):
    info = self.rs.lists(ids = self.ids)
    if not info: raise ValueError('Payroll Not Found!')
    
    info = info[0]

    self.code = info['code']

    self.data = {
      'id': self.ids,
      'code': info['code'],
      'name': info['name'],
      'from': info['from'],
      'to': info['to']
    }

    yy, mm, dd = info['from'].split("-")




  
    for item in self.items:
      data = item['data']
      info = data['info']
      value = data['value']
      range_t = data['range']

      self.collect.append({
        'card_id': item['data']['card']['id'],
        'account_no': '',
        'mem_program': '',
        'lname': info['l'].lower(),
        'fname': info['f'].lower(),
        'ename': info['e'].lower(),
        'mname': info['m'].lower(),
        'dob':  info['b'].lower(),
        'percov': f'{month_name(int(mm) - 1)}, {yy}',
        'value': value,
        'range': range_t
      })

    self.collect.sort(key = lambda x: (x['lname'], x['mname'], x['lname']))

    


  def download(self):
    obj = None
    if self.code == 'PAG-IBIG':

      obj = PagIbig(ids = self.ids, template = f'data{sep}template{sep}pag_ibig2024.xlsx')
      obj.set_data(self.data)
      obj.set_item(self.items)
      obj.set_code(self.code)
      obj.set_id(self.ids)
      obj.set_collect(self.collect)
      
    elif self.code == 'SSS':
      obj = SSS(ids = self.ids, template = f'data{sep}template{sep}sss2024.xlsx')
      obj.set_data(self.data)
      obj.set_item(self.items)
      obj.set_code(self.code)
      obj.set_id(self.ids)
      obj.set_collect(self.collect)
      

    else:
      # default object
      obj = RemittanceDefault()

    return obj.download()


# default if none of the choosen
class RemittanceDefault():

  def download(self):
    pass




# my client code to communicate the adapter class
def download_remittance(con, ids):

  # initialized the code
  
  rem = RemittanceAdapter(con, ids)
  download = rem.download()
  return download