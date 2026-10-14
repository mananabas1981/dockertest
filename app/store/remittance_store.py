from app.util.date import date_time
from app.util.json import json_parse, json_stringify
from app.store.payroll_store import PayrollStore
from app.store.client_store import ClientStore
from app.store.card_store import CardStore
from app.store.deduction_store import DeductionStore
from datetime import datetime

from pprint import pprint

class RemittanceStore:
  def __init__(self, con, uid = None):
    self.con = con
    self.uid = uid


  def get_last_id(self, code):
    yr = date_time().split('-')[0]
    data = self.con.get('SELECT id FROM remittance_base WHERE code = ? and datecreated like ? ORDER BY datecreated DESC LIMIT 1', (code, f'%{yr}%', ))

    ids = ''
    if data:
      last_id = data[0][0].split('-')
      code, yr, second, first = last_id

      second = int(second)
      first = int(first) + 1
      if first > 999:
        first = 1
        second = second + 1

      ids = f'{code}-{yr}-{second:0>3}-{first:0>3}'
    else:
      ids = f'''{code.upper().replace('-', '').replace(' ', '').replace('.', '')}-{yr}-000-001'''  

    return ids



  def create_base(self, code: str, name: str, refids: list, from_: str, to_: str):
    last_id = self.get_last_id(code)
    self.con.commit('INSERT INTO remittance_base(id, code, name, refids, createdby, datecreated, from_, to_) VALUES(?, ?, ?, ?, ?, ?, ?, ?)', (
      last_id, code, name, json_stringify(refids), self.uid, date_time(), from_, to_, 
    ))

  def item_count(self, ids = None) -> int:
    data = self.con.get('select count(remittance_id) as total from remittance_item where remittance_id = ?', ( ids, ))
    ret = 0
    if data:
      ret = data[0][0]

    return int(ret)

  def lists(self, ids = None, code = None, year = None, month = None) -> list:

    where = ''
    tup = ()

    if ids:
      where = 'WHERE id = ?'
      tup = (ids, )

    data = self.con.get(f'SELECT id, code, name, from_, to_, refids, datecreated, status FROM remittance_base {where} ORDER BY datecreated DESC', tup)
    
    ret = [] # return value

    for ids, code, name, from_, to_, refids, datecreated, status in data:

      refids = json_parse(refids)
      ret.append({
        'ids': ids,
        'code': code,
        'name': name,
        'from': from_,
        'to': to_,
        'refids': refids,
        'datecreated': datecreated,
        'status': status,
        'total_item': self.item_count(ids = ids)
      })

    return ret
    
  def get_other_base(self, remittance_id: str, from_: str, to_: str, code: str):
    # get other base for example for checking if already added or already to remittance
    data = self.con.get('select id, name, from_, to_ from remittance_base where from_ <= ? and to_ >= ? and not id = ? and code = ?', (
      to_,
      from_,
      remittance_id,
      code, 
    ))

    ret = []
    
    for item in data:
      ids, name, from_, to_ = item
      ret.append({
        'id': ids,
        'name': name,
        'from_': from_,
        'to_': to_
      })

    return ret


  def get_item(self, remittance_id: str, emp_id: str = None):

    emp_id_q = ''
    
    tup = (remittance_id, )

    if emp_id:
      emp_id_q = ' and emp_id = ? '
      tup = ( remittance_id, emp_id, )

    data = self.con.get(f'select data, emp_id from remittance_item where remittance_id = ?{emp_id_q}', tup)  

    ret = []

    for item in data:
      _data, _emp_id = item
      ret.append({
        'data': json_parse(_data),
        'emp_id': _emp_id
      })

    return ret


  def create_item(self, remittance_id: str, emp_id: str, data: dict):
    self.con.commit('INSERT INTO remittance_item (remittance_id, emp_id, data, addedby, createdby) values(?, ?, ?, ?, ?)', (
      remittance_id, emp_id, json_stringify(data), self.uid, date_time(),
    ))

  # generation of the remittances
  def generate_model(self, ids: str) -> bool:

    info = self.lists(ids = ids)

    if not info: return False

    # base deduction
    _ds = DeductionStore(self.con)
    base_ded = _ds.getDeduction()
    # end base deduction
    
    refids, code, from_, to_ = info[0]['refids'], info[0]['code'], info[0]['from'], info[0]['to']

    if not refids: return False



    pstore = PayrollStore(self.con)
    cs = ClientStore(self.con)

    collected = {

    }

    # collecting the data from the list of payroll
    for refid in refids:
      info = pstore.info(refid)
      if info['status']:
        stat = json_parse(info['status']) 
        if stat[len(stat) - 1]['step'] == 5:
          items = pstore.get_item(refid = refid)
          

          for item in items:
            
            emp_data = {
              'emp_id': item['emp_id'],
              'range': [],
              'value': [],
              'card': {
                'id': ''
              }
            }

            tmp_value = []
            has_value = False

            ded_info = json_parse(item['deduction']) 
            emp_info = cs.info_by_id(item['emp_id']) # retrieving the latest information of the employee

            # retrieving the card information such as pag-ibig number ,sss number and other information
            card = CardStore(self.con)
            card_data = card.get_by_code_emp_id(emp_id = item['emp_id'], code = code)
            if card_data:
              # fill-up all the card information or the custom information of card example 
              emp_data['card']['id'] = card_data[0]['card_no']
            # emp_data['card'] base on the code  
            # end of the card retrieved

            emp_data['info'] = {
              'p': emp_info['p'],
              'f': emp_info['f'],
              'm': emp_info['m'],
              'l': emp_info['l'],
              'e': emp_info['e'],
              's': emp_info['s'],
              'b': emp_info['b'],
              'g': emp_info['g'],
              'h': emp_info['h']
            }

            for ded_item in ded_info:
              if ded_item['code'] == code:
                # name
                # print(ded_item['value'])
                # checking the type of the deduction
                hh_type = 'c'
                for hh in base_ded:
                  if hh['code'] == code and ded_item['name'] == hh['name']:
                    hh_type = hh['type']
                    break # break the loop

                # end checking the type of the deduction
                tmp_value.append((
                  ded_item['name'],
                  ded_item['value'],
                  hh_type
                ))
                # ensuring that the none zero is not included
                if ded_item['value'] != 0.0:
                  has_value = True

            if has_value:
              emp_data['value'].append(tmp_value)

              if item['emp_id'] in collected:
                prev_data = collected[item['emp_id']]
                collected[item['emp_id']]['value'].append(tmp_value)
                collected[item['emp_id']]['range'].append((item['start'], item['end']))
              else: 
                collected[item['emp_id']] = emp_data
                collected[item['emp_id']]['range'].append((item['start'], item['end']))
                



    # logic for the creation of the deduction

    # format of the data
    # {
    #   'card_no': '',
    #   'value': '' 
    # }

    # other base checking to avoid duplication of the data
    other_base = self.get_other_base(remittance_id = ids, from_ = from_, to_ = to_, code = code) # checking the other bases if there are data that is already added
    other_items = []
    for other in other_base:
        # other['id']
        other_item = self.get_item(remittance_id = other['id'])
        for y in other_item:
          other_items.append(y['data'])
    # end other base checking avoid duplication of the data inserted

    for emp_id in collected:
      item = collected[emp_id] # data


      # before adding checking if they are already added in other places
      has_other_item = False
      for aa in other_items:
        if aa['emp_id'] == item['emp_id']:
          aa_range = aa['range']
          item_range = item['range']

          for item_r in item_range:
            from_1, to_1 = item_r

            from_1 = datetime.strptime(from_1, '%Y-%m-%d')
            to_1 = datetime.strptime(to_1, '%Y-%m-%d')

            for aa_r in aa_range:
              from_2, to_2 = aa_r

              from_2 = datetime.strptime(from_2, '%Y-%m-%d')
              to_2 = datetime.strptime(to_2, '%Y-%m-%d')

              if from_1 <= to_2 and to_1 >= from_2:
                has_other_item = True
      # end checking duplicate

      if has_other_item: continue

      has_data = self.get_item(remittance_id = ids, emp_id = emp_id) 
      if has_data: continue

      self.create_item(remittance_id = ids, emp_id = emp_id, data = item)

    # # #  has_data = self.get_item(remittance_id = ids, emp_id = item['emp_id'])
    #   self.create_item(remittance_id = ids, emp_id = item['emp_id'], from_ = item['range'][0], to_ = item['range'][1], data = {})
      

    # end collecting the data from the list of payroll


    return True

