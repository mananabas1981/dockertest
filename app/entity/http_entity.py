from app.lib.sql import sql
from app.util.auth import Auth
class ProcessEntity:
    def __init__(this):
        this.con: sql = None
        this.msg: dict = {
            "ok": False,
            "msg": "",
            "data": None
        }
        this.auth: Auth = None

    def createAuth(this, req) -> Auth:
        this.auth = Auth(req)
        return this.auth

    def openConnection(this) -> sql:
        this.con = sql()
        return this.con

    def send(this):
        if this.auth:
            return this.auth.send(this.msg)
        return None

    def close(this):
        if this.con:
            this.con.close()

