from app.util.date import date_time
from app.store.global_store import create_history
from app.util.json import json

class DeductionStore:
    def __init__(this, con = None):
        this.__con = con

    def save(this, code = None, name = None, floor = None, \
            ceil = None, deduction_value = None, view_only = None,\
            active = None, creator_uid = None, type = None
            ):
        
        this.__con.commit('''
            insert into deduction (
                code, name, floor, ceil, deduction_value,
                view_only,
                active,
                createdby,
                datecreated,
                type, payroll_design
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "[]")
        ''', (
            code,
            name, 
            floor,
            ceil,
            deduction_value,
            view_only,
            active,
            creator_uid,
            date_time(),
            type,
        ))
    
    def update(this, code = None, name = None, floor = None, ceil = None, deduction_value = None, view_only = None, bracket = None, active = None, types = None):
        this.__con.commit('''
            update deduction set floor = ?, ceil = ?, deduction_value = ?, view_only = ?, bracket = ?, active = ?, type = ?
                          where code = ? and name = ?
        ''', (
            floor,
            ceil,
            deduction_value,
            view_only,
            bracket,
            active,
            types, 
            code,
            name,
        ))

    def getDeduction(this, code = None, name = None, status = None):
        
    
        tup = ()

        qw = ""

        if code and name:
           
            tup = (code, name, )
           
            qw += ' where code = ? and name = ? '

        q = f'''select  
            code, name, floor, ceil, deduction_value,
            view_only, active, createdby, datecreated, type, payroll_design, bracket                       
        from deduction {qw} order by code, name asc'''

        items = this.__con.get(q, tup)
        
        
        res = []

        for item in items:
            
            dic = {
                'code': item[0],
                'name': item[1],
                'floor': item[2],
                'ceil': item[3],
                'value': item[4],
                'view_only': item[5],
                'active': item[6],
                'createdby': item[7],
                'datecreated': item[8],
                "type": item[9],
                "payroll_design": item[10],
                "bracket": item[11]
            }
            
            pd = json.loads(dic['payroll_design'])
            
            # the status has only r and c,, c is casual so we need to convert the j as c if j is present
            
            if status == 'j': status = 'c' # conversion if status is j

            if status:
                if status in pd:
                    res.append(dic)
            else:
                res.append(dic)


        return res  

    def change_state(this, code = None, name = None, state = None):
        this.__con.commit("update deduction set active = ? where code = ? and name = ?", (
            state,
            code,
            name,
        ))

    def remove_deduction(this, code = None, name = None, uid = None):
        # this.__commit('dele')
        
        res = this.getDeduction(code, name)
        
        if not res:
            return
        
        data = res[0]
        
        this.__con.commit('delete from deduction where code = ? and name = ?', (code, name,))
        
        create_history(this.__con, uid, 'deduction', data, 'd')

    def emp_change(this, code = None, name = None, emp_status = "[]"):
        this.__con.commit("update deduction set payroll_design = ? where code = ? and name = ?", (
            emp_status,
            code,
            name,
        ))


'''
CREATE TABLE "deduction" (
	"code"	TEXT,
	"name"	TEXT,
	"floor"	TEXT,
	"ceil"	TEXT,
	"deduction_value"	TEXT,
	"view_only"	TEXT,
	"active"	TEXT,
	"createdby"	TEXT,
	"datecreated"	TEXT,
	PRIMARY KEY("code","name")
)
'''