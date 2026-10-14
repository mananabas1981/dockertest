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



class PayrollPrintV3:
	def __init__(self, con, refid, dept_id, uid, payroll_type):
		self._con = con
		self._refid = refid
		self._dept_id = dept_id
		self._uid = uid
		self.payroll_type = payroll_type
		
		self.init()
	def init(self):
		# initial of the json generation
		ret = {
			# including the qrcode in the header field
			'header': {

			},
			'body': {
					
			},
			# including the signatories
			'footer': {

			}
		}

		refid = self._refid
		dept_id = self._dept_id

		con = self._con
		pstore = PayrollStore(con)
    
		payroll_info = pstore.info(refid)

		if not payroll_info:
			return False, 'Payroll Not Found'

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
		

		ded_list = json_parse(payroll_info["deduction_list"])
    


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
		sign_key = user_store.sign_key(self._uid)
		for s_item in sign_list:
			if 'sign_key' in s_item:
				if sign_key == s_item['sign_key']:
					self._action.append({
						'sign_key': s_item['sign_key'],
						'sign_val': s_item['sign_val'],
						'sign_date': s_item['sign_date'],
						'action': s_item['c'],
						'name': s_item['n'],
						'pos': s_item['p']
					})
		# end sign key checking

		user_data = user_store.list_user(self._uid)
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
		if self.payroll_type == 'print':
			payroll_no = f'''{dept_code}-{ payroll_info['refid']}'''
			pqrcode = qr.toHtmlTag()

			if not str(dept_id).strip():
				return (False, 'Printing of Payroll is per group/department')


		print(ret)

	def output(): # this is a json output
			pass
    