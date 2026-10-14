
def sys_info(con) -> dict:
    data = con.get("select hr_ip, name, addr from sys_info")

    r = {
        "hr_ip": "http://localhost",
        'name': '',
        'addr': ''
    }
    if data:
        r["hr_ip"] = data[0][0]
        r['name'] = data[0][1]
        r['addr'] = data[0][2]
        
    return r