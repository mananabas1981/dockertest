class UserSessionStore:
    def __init__(this, key = None, date = None, uid = None, status = -1, remark = None):
        this.key = key
        this.date = date
        this.uid = uid
        this.status = status # 1 for approved! 0 for disapproved with remark
        this.remark = remark

class UserSessionStoreService:
    def __init__(this, con):
        this.con = con

    def createSession(this, user: UserSessionStore):
        this.con.commit('insert into user_session(key, date, uid, status) values(?, ?, ?, ?)', (
            user.key,
            user.date,
            user.uid,
            user.status,
        ))

    def approve(this, user: UserSessionStore):
        this.con.commit('update user_session set status = ?, remark = ? where key = ?', (
            user.status,
            user.remark,
            user.key,
        ))

    def disapprove(this, user: UserSessionStore):
        pass
    
    def listSession(this, user: UserSessionStore = None) -> list:
        
        _data = this.con.get('''
            select us.key, us.date, us.uid, us.status, us.remark, u.name from user_session as us 
            left join user as u on u.id = us.uid where us.status = '-1'
        ''')

        data = []

        for item in _data:
            data.append({
                'key': item[0],
                'date': item[1],
                'uid': item[2],
                'status': item[3],
                'remark': item[4],
                'name': item[5]
            })

        return data

        

    