from app.lib.sql import sql


class DefaultHead:
    
    def __init__(self, con):
        self.con: sql = con

    def get_head(self, dept_id = None, type_t = None) -> list:
        '''
            return: list<tuple>
                    tuple: (name, pos_title, dept_id, type)
        '''
        res = []
        if dept_id and type_t:
            res = self.con.get('select name, pos_title, dept_id, type from default_head_office where dept_id = ? and type = ?', (
                dept_id, type_t, 
            ))
        else:
            res = self.con.get('select name, pos_title, dept_id, type from default_head_office')

        return res


    def update_head(self, name = None, pos_title = None, dept_id = None, type_t = None):
        if self.get_head(dept_id = dept_id, type_t = type_t):
            self.con.commit('update default_head_office set name = ?, pos_title = ? where dept_id = ? and type = ?', (name, pos_title, dept_id, type_t, ))
        else:
            self.con.commit('insert into default_head_office(name, pos_title, dept_id, type) values(?, ?, ?, ?)', ( name, pos_title, dept_id, type_t ))


