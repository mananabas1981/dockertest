from bottle import Bottle, request as req, response as res, redirect
from app.lib.sql import sql

from app.handler.static_handler import static_app
from app.handler.client_handler import client_handler
from app.handler.user_handler import user_app
from app.manager import  (card, live, setting, department, employee, device, payroll, bank, deduction, signatory, api, dashboard, user_session, remittance, digital, dtr, user)
from bottle.ext.websocket import websocket

app = Bottle()

app.mount("/app", static_app)
app.mount("/client", client_handler)
app.mount("/user", user_app)

@app.error(404)
def error404(error):
    res.status = 404
    return """
      Page not found! <a href="/app/payroll/web/portal">
        Click Here
      </a>
    """

@app.route("/")
def index(): redirect("/app/payroll/web/portal")

@app.route('/dashboard/data', method = ['POST'])
def dash_data(): return dashboard.dash_data(req, res)

@app.route('/setting/setup/save', method = ['POST'])
def setting_save(): return setting.save_setup(req, res)

# setting
@app.route('/setting/setup/get', method = ['POST'])
def setting_get(): return setting.get_info(req, res)

@app.route('/setting/bank/save', method = ['POST'])
def setting_bank_save(): return setting.bank_save(req, res)

@app.route('/setting/bank/list', method = ['POST'])
def setting_bank_list(): return setting.bank_list(req, res)

@app.route('/setting/bank/remove', method = ['POST'])
def setting_bank_remove(): return setting.bank_remove(req, res)

@app.route("/update/password", method = ["POST"])
def update_password(): return user.user_change_password(req, res)


@app.route("/department/save", method = ["POST"])
def dept_save(): return department.save(req, res)

@app.route("/department/list", method = ["POST"])
def dept_list(): return department.lists(req, res)

@app.route("/department/remove", method = ["POST"])
def dept_remove(): return department.dept_remove(req, res)

# employee remove
@app.route("/employee/remove", method = ["POST"])
def emp_remove(): return employee.employee_remove(req, res)

# employee rate save
@app.route("/employee/rate/save", method = ["POST"])
def rate_save(): return employee.save_rate(req, res)

@app.route("/employee/rate/list", method = ["POST"])
def rate_list(): return employee.get_rate(req, res)

@app.route("/employee/rate/remove", method = ["POST"])
def rate_remove(): return employee.remove_rate(req, res)

@app.route("/employee/position/save", method = ["POST"])
def emp_pos_save(): return employee.save_position(req, res)

@app.route("/employee/position/list", method = ["POST"])
def emp_pos_list(): return employee.get_position(req, res)

@app.route("/employee/position/remove", method = ["POST"])
def emp_pos_remove(): return employee.remove_position(req, res)

@app.route("/employee/dept/save", method = ["POST"])
def emp_dept_save(): return employee.dept_save(req, res)

@app.route("/employee/dept/list", method = ["POST"])
def emp_dept_list(): return employee.dept_list(req, res)

@app.route("/employee/dept/remove", method = ["POST"])
def emp_dept_remove(): return employee.dept_remove(req, res)


# Bank
@app.route("/bank/save", method = ["POST"])
def bank_save(): return bank.save(req, res)

@app.route("/bank/list", method = ["POST"])
def bank_list(): return bank.get_all_bank(req, res)

@app.route("/bank/remove", method = ["POST"])
def bank_remove(): return bank.remove_bank(req, res)

@app.route("/employee/bank/save", method = ["POST"])
def emp_bank_save(): return bank.emp_save_bank(req, res)

@app.route("/employee/bank/list", method = ["POST"])
def emp_bank_list(): return bank.emp_bank_list(req, res)

@app.route("/employee/bank/remove", method = ["POST"])
def emp_bank_remove(): return bank.emp_remove_bank(req, res)
# End Bank

@app.route('/employee/information', method = ['POST'])
def emp_information(): return employee.get_all_info(req, res)

# user verify device it is logged in or not
@app.route("/verify", method = "POST")
def verify(): return device.verify(req, res)

# user signout
@app.route("/sign-out", method = ["POST"])
def sign_out(): return device.sign_out(req, res)

# Create payroll
@app.route("/payroll/create", method = ["POST"])
def payroll_create(): return payroll.create_payroll(req, res)

@app.route("/payroll/list", method = ["POST"])
def payroll_list(): return payroll.list_payroll(req, res)

@app.route('/payroll/remove', method = ['POST'])
def payroll_main_remove(): return payroll.removePayroll(req, res)

@app.route("/payroll/bank/update", method = ["POST"])
def payroll_bank_update(): return payroll.bank_update(req, res)
# All about the payroll item
# signatory default
@app.route('/payroll/signatory/default/load', ['POST'])
def payroll_default_load(): return payroll.default_sign_load(req, res)

@app.route('/payroll/signatory/default/submit', ['POST'])
def payroll_default_submit(): return payroll.default_sign_submit(req, res)
# signatory end default

@app.route('/payroll/add/item', method = ['POST'])
def payroll_add_item(): return payroll.set_item(req, res)

@app.route('/payroll/get/items', method = ['POST'])
def payroll_get_item(): return payroll.get_items(req, res)

@app.route("/payroll/get/item", method = ["POST"])
def payroll_get_item(): return payroll.get_item(req, res)

@app.route("/payroll/get/info", method = ["POST"])
def payroll_get_info(): return payroll.get_info(req, res)

@app.route("/payroll/copy", method = ["POST"])
def payroll_copy(): return payroll.payroll_copy(req, res)


@app.route("/payroll/remove/item", method = ["POST"])
def payroll_remove_item(): return payroll.remove_item(req, res)

@app.route('/print/payroll', method = ['POST'])
def print_payroll(): return payroll.payroll_print(req, res)

@app.route("/payroll/change/atm", method = [ "POST" ])
def payroll_change_atm(): return payroll.payroll_change_atm(req, res)

@app.route("/payroll/recompute/con/loan/t", method = ["POST"])
def payroll_recompute_con_loan(): return payroll.payroll_recompute_con_loan(req, res)

# @app.route('/payroll/approve', method = ['POST'])
# def payroll_approve(): return payroll.payroll_approve(req, res)

@app.route('/status/state/change', ['POST'])
def status_state_change(): return payroll.status_state_change(req, res)

@app.route('/payroll/digital/signature/approve', ['POST'])
def payroll_digital_sign_approve(): return payroll.payroll_digital_sign_apr(req, res)


@app.route("/ada/sign/list", method = ['POST'])
def ada_sign_list(): return payroll.ada_sign_list(req, res)

@app.route("/print/ada", method = ["POST"])
def print_ada(): return payroll.payroll_print_ada(req, res)

@app.route("/print/ada/file/excel", ["POST"])
def print_ada_excel(): return payroll.payroll_print_file(req, res)

@app.route('/payroll/file/download', ['POST'])
def payroll_file_download(): return payroll.payroll_file_download(req, res)

@app.route("/ada/update/no", ["POST"])
def ada_update_no(): return payroll.ada_update_no(req, res)

@app.route("/ada/get_number", ["POST"])
def ada_get_number(): return payroll.ada_get_number(req, res)

# @app.route("/ada/close", ["POST"])
# def ada_closing(): return payroll.ada_close(req, res)

@app.route('/print/ob', ['POST'])
def print_ob(): return payroll.print_ob(req, res)

@app.route('/ob/update', ['POST'])
def ob_update(): return payroll.ob_update(req, res)

@app.route('/ob/load', ['POST'])
def ob_load(): return payroll.ob_load(req, res)

@app.route('/ob/check_list', ['POST'])
def ob_check_list(): return payroll.ob_check_list(req, res)

@app.route("/ob/close", ["POST"])
def ob_close(): return payroll.ob_close(req, res)

@app.route("/view/ada", method = ["POST"])
def view_ada(): return payroll.view_ada(req, res)

@app.route("/payroll/emp_ded/default", method = ["POST"])
def payroll_emp_default(): return payroll.get_ded_default(req, res)

@app.route("/payroll/info", ["POST"])
def payroll_info_t(): return payroll.payroll_info(req, res)

@app.route("/payroll/info/update", ["POST"])
def payroll_info_update(): return payroll.payroll_info_update(req, res)

@app.route("/payroll/auto/calculate", method = ["POST"])
def payroll_auto_cal(): return payroll.auto_cal(req, res)

@app.route("/payroll/calculate/tax", method = ["POST"])
def payroll_tax_cal(): return payroll.tax_calculate(req, res)

# update the payroll_item bank information and the bank information

@app.route("/payroll/item/bank/update", method = ["POST"])
def paytoll_item_bank_update(): return payroll.item_bank_update(req, res)

# Notification
@app.route('/load/action', ['POST'])
def load_action(): return payroll.load_action(req, res)
# notes
# remove the table emp_bank_history
# added the emp_bank_account

# end notes

# default contribution
@app.route('/employee/contrib', ['POST'])
def emp_contrib(): return deduction.default_contrib_emp_list(req, res)

@app.route('/default/contrib/submit', ['POST'])
def default_contrib_submit(): return deduction.default_contrib_submit(req, res)

@app.route('/default/contrib/load', ['POST'])
def default_contrib_load(): return deduction.default_contrib_list(req, res)

@app.route('/default/contrib/remove', ['POST'])
def default_contrib_remove(): return deduction.default_contrib_remove(req, res)
# end default contribution

# submitting all the number 
@app.route("/card/update", ["POST"])
def card_update(): return card.update(req, res)
@app.route("/card/load", ["POST"])
def card_load(): return card.load(req, res)
# end submmiting the card number

# deduction setter
@app.route('/setting/deduction/save', method = ['POST'])
def s_ded_save(): return deduction.add_deduction(req, res)

@app.route('/setting/deduction/list', method = ['POST'])
def s_ded_list(): return deduction.list_deduction(req, res)

@app.route('/settings/deduction/remove', method = ['POST'])
def s_ded_remove(): return deduction.remove_deduction(req, res)

@app.route("/settings/deduction/state", method = ["POST"])
def s_ded_state(): return deduction.change_state(req, res)

@app.route("/settings/deduction/status_change", method = ["POST"])
def s_status_state_change(): return deduction.emp_status_change(req, res)

@app.route("/setting/sign/save", method = ["POST"])
def set_sign_save(): return signatory.save(req, res)

@app.route("/settings/sign/list", method = ["POST"])
def set_sign_list(): return signatory.GetSignatory(req, res)


@app.route("/settings/sign/active/change", method = ["POST"])
def set_sign_active_change(): return signatory.active_change(req, res)

@app.route("/settings/sign/type/change", method = ["POST"])
def set_sign_type_change(): return signatory.type_change(req, res)

@app.route("/payroll/pre/calculate", method = ["POST"])
def payroll_pre_cal(): return payroll.payroll_pre_cal(req, res)
# api access request
@app.route("/api/hrms/dtr", method = ["POST"])
def api_hrms_dtr(): return api.api_hrms_dtr(req, res)

@app.route('/api/hrms/dtr/info', ['POST'])
def api_hrms_dtr_info(): return api.api_hrms_dtr_general_info(req, res)

@app.route("/api/hrms/employee", method = ["post"])
def api_hrms_emp(): return api.api_hrms_employee(req, res)

@app.route("/api/hrms/save", method = ["post"])
def api_hrms_save(): return api.api_hrms_save(req, res)

@app.route('/api/hrms/sync_all_id', method = [ 'POST' ])
def api_sync_all(): return api.sync_all_id(req, res)

@app.route('/session/list', method = ['POST'])
def user_session_list(): return user_session.session_list(req, res)

@app.route('/session/approve', method = ['POST'])
def session_approve(): return user_session.session_approve(req, res)

#-- card id like gsis unique number
@app.route("/employee/card/id", method = ["POST"])
def emp_card_id(): return payroll.card_id(req, res)
#-- bir unique id

@app.route('/employee/status/change', ['POST'])
def emp_status_change(): return employee.active_change(req, res)

#-- payslip

@app.route('/payslip/list', method = ['POST']) 
def payslip_list(): return payroll.payslip_list(req, res)

@app.route('/PaySlip/Print', method = ['POST'])
def payslip_print(): return payroll.payslip_print(req, res)

# download template remittance
# @app.route('/remittance/template/download',['POST'])
# def remittance_temp_dwn(): return remittance.download(req, res)

# # create remittance base
# @app.route('/remittance/create/base', ['POST'])
# def remittance_create_base(): return remittance.create_base(req, res)

# @app.route('/remittance/lists/base', ['POST'])
# def remittance_lists_base(): return remittance.get_base(req, res)

# @app.route('/remittance/base/info', ['POST'])
# def remittance_base_info(): return remittance.get_info(req, res)

# @app.route('/remittance/base/regenerate', ['POST'])
# def remittance_base_regen(): return remittance.base_gen(req, res)

# @app.route('/remittance/base/download', ['POST'])
# def remittance_base_download(): return remittance.base_download(req, res)

@app.route("/remittance/generate", ["POST"])
def remittance_generate(): return remittance.gen_remittance(req, res)

#-- remittance
@app.route('/payroll/generate/remittance', method = ['POST'])
def payroll_gen_rem(): return payroll.generate_remittance(req, res)
#-- end remittance

# start of digital
@app.route('/digital/signature/save', ['POST'])
def digital_signature_save(): return digital.signature_save(req, res)

@app.route('/digital/signature/list', ['POST'])
def digital_signature_get(): return digital.signature_list(req, res)

# end start of digital


# Deduction of the leave credits of the employee
@app.route('/dtr/create/transaction/code', ['POST'])
def dtr_create_trans_code(): return dtr.create_code(req, res)

@app.route("/dtr/regular/reports", [ "POST" ])
def dtr_regular_reports(): return dtr.dtr_regular_reports(req, res)

@app.route('/dtr/list', ['POST'])
def dtr_list(): return dtr.list_code(req, res)


@app.route('/dtr/approve', ['POST']) 
def dtr_approve(): return dtr.update_leave_credit(req, res)


# ObR information
@app.route("/payroll/total/fund", [ "POST" ])
def split_by_fund(): return payroll.split_by_fund(req, res)

@app.route("/payroll/ob/reports", [ "POST" ])
def payroll_ob_reports(): return payroll.ob_fund_reports(req, res)

# live-server for chatbox
@app.route('/live-app', apply = [websocket])
def handle_ws(ws):
  try:
    live.live_app(ws)
  except Exception as er:
    # print(er) for debugging
    pass

