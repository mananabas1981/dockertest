from app.store.user_store import UserStore
from re import match
from app.util.md5 import md5

class UserModel(UserStore):
  def __init__(this):
    this.re_user = r"^[0-9a-zA-Z\.\-\(\)\s\!\@\#\$\%\^\&\*\_\+\=\:\;\<\>\,]+$"
  
  def isValidAuthentication(this, username, password) -> bool:
    if not match(this.re_user, username):
      return False
    
    if not match(this.re_user, password):
      return False

    return True

  def authenticate(this, username, password) -> dict:
    return this._getUser(username, md5(password))
  

class AccessModel:
  def __init__(this, con = None):
    this.con = con

    # Remember: key of the access is strictly not advisable to remove or edit
    #           since it required refactoring code from the comment at the right side of the value

    this.access = [
        {
            "key": "em",
            'value': 'Employee Management',
            'tree': [
               {'key': 'em-0', 'value': 'Create Employee'}, # client_handler.py
               {'key': 'em-1', 'value': 'Update Employee'}, # client_handler.py
               {'key': 'em-2', 'value': 'Delete Employee'}, # employee.py
               {'key': 'em-3', 'value': 'View/Search Employee'}, # client_handler.py
               {'key': 'em-4', 'value': 'Rate Management'}, # employee.py
               {'key': 'em-5', 'value': 'Position Management'}, #employee.py
               {'key': 'em-6', 'value': 'Department Management'}, #employee.py
               {'key': 'em-7', 'value': 'Bank Account Management'} #bank.py
            ]
        },
        {
            "key": "pm",
            'value': 'Payroll Management',
            "tree": [
                {'key': 'pm-a-r', 'value': 'Allow auto add all to the payroll (Regular Only)'}, # payroll py

                {'key': 'pm-l-j', 'value': 'Allow Approved the Payroll Job Order'}, # payroll.py
                {'key': 'pm-l-c', 'value': 'Allow Approved the Payroll Contract Of Service'}, # payroll.py
                {'key': 'pm-l-r', 'value': 'Allow Approved the Payroll Regular'}, 

                {"key": "pm-1-j", 'value': 'Create Payroll (Job Order)'}, # payroll.py
                {'key': 'pm-1-c', 'value': 'Create Payroll (Contract Of Service)'}, # payroll.py
                {'key': 'pm-1-r', 'value': 'Create Payroll (Regular(Permanent, Temporary, etc...))'}, # payroll.py
                
                {'key': 'pm-v-j', 'value': 'View Payroll Job Order'}, # payroll.py
                {'key': 'pm-v-c', 'value': 'View Payroll Contract of Service'}, # payroll.py
                {'key': 'pm-v-r', 'value': 'View Payroll Regular'},  # payroll.py
                
                {'key': 'pm-2-j', 'value': 'Delete Payroll (JO)'}, # payroll.py
                {'key': 'pm-2-c', 'value': 'Delete Payroll (COS)'}, # payroll.py
                {'key': 'pm-2-r', 'value': 'Delete Payroll (Regular)'}, # payroll.py
                
                {'key': 'pm-3-v-a', 'value': 'View Payroll Items (All)'},
                {'key': 'pm-3-j','value': 'Add Payroll Item (JO)'}, #payroll.py
                {'key': 'pm-3-c', 'value': 'Add Payroll Item (COS)'}, # payroll.py
                {'key': 'pm-3-r', 'value': 'Add Payroll Item (Regular)'}, # payroll.py

                {'key': 'pm-3-j-u','value': 'Update Payroll Item (JO)'}, #payroll.py
                {'key': 'pm-3-c-u', 'value': 'Update Payroll Item (COS)'}, # payroll.py
                {'key': 'pm-3-r-u', 'value': 'Update Payroll Item (Regular)'}, # payroll.py

                {'key': 'pm-4-j', 'value': 'Remove Payroll Item (JO)'}, # payroll.py
                {'key': 'pm-4-c', 'value': 'Remove Payroll Item (COS)'}, # payroll.py
                {'key': 'pm-4-r', 'value': 'Remove Payroll Item (Regualr)'}, # payroll.py

                {'key': 'r-0', 'value': 'REOPEN PAYROLL (admin)!'},
                {'key': 'r-1', 'value': 'CLOSING PAYROLL REVIEW & DIGITAL SIGNATURE!'},
                {'key': 'r-3', 'value': 'CAN OPEN FOR READY DOWNLOAD A.D.A OR PAYROLL FILE!'},
                {'key': 'f-0', 'value': 'CLOSE FINAL PAYROLL AND PAY (ADMIN OR ADA MAKER)! PAYROLL MUST NOT REVERSE'},
                {'key': 'a-j-1', 'value': 'Can reprint already approved payroll ( this role restrictly for choosen person and for security reason )'}, # payroll 

                {'key': 'pm-6-0', 'value': 'Update Ada Number'}, # payrol.py
                {'key': 'pm-6', 'value': 'Print Payroll'}, #payroll.py
                {'key': 'pm-7', 'value': 'Print ADA'}, # payroll
                {'key': 'pm-7-1', 'value': 'Approve ADA'}, # payroll.py
                {'key': 'pm-8', 'value': 'Edit|Add Costume Payroll signatory'}, # payroll.py
                {'key': 'pm-8-1', 'value': 'Edit|Remove Payroll Header| Deduction & Contribution'}, # payroll.py
                {'key': 'pm-9', 'value': 'View Obligation Requests'}, # payroll.py
                {'key': 'pm-9-u', 'value': 'Update Obligation Requests'}, # payroll.py
                {'key': 'pm-9-c', 'value': 'Close Obligation Requests'}, #payroll.py
                {'key': 'mp-1-a', 'value': 'Print Obligation Requests (For Already Approved Payroll) (retrictly not allow for security reason)'},#payroll
                {'key': 'pm-y-y', 'value': 'Update Bank Account Number in payroll item'}, #payroll.py
                {'key': 'pm-y-y-c', 'value': 'Grant for switching different ATM in payroll(must be only 1 user or admin)'},
                {'key': 'pm-y-y-r', 'value': 'Recompute Payroll Avisable only 1 access!'},
                {'key': 'pm-c-c-c', 'value': 'Copy Payroll (Regular)'}
            ]
        },
        {
            "key": "ss",
            'value': "System Setting",
            'tree': [
                {'key': 'ss-a', 'value': 'Manage User Roles and access roles: Strictly not applicable for many users!'}, # 
                {'key': 'ss-b', 'value': 'Create User'}, # user.py
                {'key': 'ss-c', 'value': 'Update Users'}, # user.py
                {'key': 'ss-d', 'value': 'Can View Users List'},
                {'key': 'ss-e', 'value': 'Can Remove Users'},
                {'key': 'ss-0', 'value': 'Block User Login!, (Once the user is block then the user is no longer access to the system)'},
                {'key': 'ss-1', 'value': 'Department Management[ Add, Update, Remove]'}, # department.py
                {'key': 'ss-f', 'value': 'View Deparment'}, #department.py
                {'key': 'ss-2', 'value': 'Signatory Management, [Add, Update, Delete]'}, #signatory.py
                {'key': 'ss-i', 'value': 'View Signatory List'}, #signatory
                {'key': 'ss-3', 'value': 'Contribution/Deduction Managetment[Add, Delete, Update]'}, # deduction.py
                {'key': 'ss-6', 'value': 'View Contribution / Deduction List'}, # deduction.py
                {'key': 'ss-4', 'value': 'Update Company name'}, # setting.py
                {'key': 'ss-5', 'value': 'Update Company bank information'} # setting.py, bank.py
            ]
        },
        {
           'key': 'us',
           'value': 'User Manager',
           'tree': [
              {'key': 'us-1', 'value': 'User login no need approval'}, #user_session.py
              {'key': 'us-2', 'value': 'Can approve login user!'}, #user_session.py
              {'key': 'us-3', 'value': 'View List of request Login'},
              {'key': 'di-0', 'value': 'Upload Digital Signatories'} #user_session.py
           ]
        },
        {
           'key': 'hs',
           'value': 'API: Human Resource System Connector',
           'tree': [
              {'key': 'hs-1', 'value': 'Access DTR| QRCode'},
              {'key': 'hs-2', 'value': 'Access Employee'},
              {'key': 'hs-3', 'value': 'Sync Individual Employee'},
              {'key': 'hs-4', 'value': 'Sync all HR System employee id'},
              {'key': 'hs-5', 'value': 'Scan DTR (for leave credit deduction)'},
              {'key': 'hs-r', 'value': 'DTR Regular (Reports)'}
           ]
        }
    ]
  
  def getDefaultAccess(this):
    return this.access
  
  def getAccess(this, emp_id):
    ac = AccessModel() # access model class
    userStore = UserStore(this.con) # user store
    userRoles = userStore.getRoles(emp_id)

    default_roles = ac.getDefaultAccess()
    for x in default_roles:
        trees = x['tree']
        for tree in trees:
            tree['check'] = False
            for y in userRoles:
                if tree['key'] == y:
                    tree['check'] = True
                    break
                
    return default_roles
  
  def errorAccess(this):
    return 'You dont have right to access this feature!'

  def hasAccess(this, emp_id, access_list: list = []) -> bool:
    # this method is use to check the user access if it has access to specific data
    # from the databases
      
    default_roles = this.getAccess(emp_id)
    for x in default_roles:
      trees = x['tree']
      for tree in trees:
          for y in access_list:
              if tree['key'] == y and tree['check']:
                  return True              
    return False