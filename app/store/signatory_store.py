from app.util.date import date_time

# Entity
class SignInfo:
    def __init__(this, certify = None, name = None, pos_title = None, index = "[]", is_active = 'y', _type = "[]", sign_id = None):
        this.certify   = certify
        this.name      = name
        this.pos_title = pos_title
        this.index     = index
        this.active    = is_active
        this.type      = _type
        this.sign_id   = sign_id

class SignatoryStore:
    def __init__(this, con = None):
        this.con = con

    def Save(this, info: SignInfo, uid = None, is_update = False, udate = None):
        if not is_update:
            this.con.commit("insert into signatory(name, pos_title, certify, index_t, createdby, datecreated, active, type, sign_id) values(?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                info.name,
                info.pos_title,
                info.certify,
                info.index,
                uid,
                date_time(),
                info.active,
                info.type,
                info.sign_id,
            ))
        else:
            if not udate:
                return
            this.con.commit("update signatory set sign_id = ?, name = ?, pos_title = ?, certify = ?, index_t = ? where datecreated = ?", (
                info.sign_id,
                info.name,
                info.pos_title,
                info.certify,
                info.index,
                udate,
            ))

    def change_active(this, newActive, name, certify):
        this.con.commit("update signatory set active = ? where name = ? and certify = ?", (
            newActive,
            name,
            certify,
        ))

    def change_type(this, name, certify, newType):
        this.con.commit("update signatory set type = ? where name = ? and certify = ?", (
            newType,
            name,
            certify,
        ))

    def GetSignatory(this, info: SignInfo = None) -> list:
        
        res = this.con.get("""select 
                     name, 
                     pos_title,
                     certify,
                     index_t,
                     createdby,
                     datecreated,
                     active,
                     type,
                     sign_id
                    from signatory""")

        data = []

        for name, pos_title, certify, index_t, createdby, datecreated, active, type1, sign_id in res:
            data.append({
                "name": name,
                "pos_title": pos_title,
                "certify": certify,
                "index": index_t,
                "createdby": createdby,
                "datecreated": datecreated,
                "active": active,
                "type": type1,
                'sign_id': sign_id
            })


        # for x in res:
            
        #     data.append({
        #         "name": x[0],
        #         "pos_title": x[1],
        #         "certify": x[2],
        #         "index": x[3],
        #         "createdby": x[4],
        #         "datecreated": x[5],
        #         "active": x[6],
        #         "type": x[7],
        #         'sign_id': x[8]
        #     })
        
        return data