from app.lib.sql import sql
from app.store.client_store import RateStore
from app.util.date import date_time


class RateModel:
    def __init__(self, con: sql, emp_id):
        self.con = con
        self.emp_id = emp_id

    def create_rate(self, rate, rate_type, nwpd = None):
        rate_store = RateStore(self.con)
        last_rate = rate_store.get_last_rate(self.emp_id)

        if last_rate:
            rate2 = last_rate[1]
            rate_type2 = last_rate[2]
            nwpd2 = last_rate[3]
            if not (rate2 == rate and rate_type2 == rate_type and nwpd == nwpd2):
                rate_store.create_rate(self.emp_id, rate, rate_type, date_time(), nwpd = nwpd)
        else:
        # if there are no last rate
            rate_store.create_rate(self.emp_id, rate, rate_type, date_time(), nwpd = nwpd)