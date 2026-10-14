from app.store.payroll_store import PayrollStore

class Department:
  def __init__(this, con):
    this.__con = con

  def save(this, ids, code, title):
    if not this.exists_on_save(ids, code):
      this.__con.commit("insert into department(id, code, title) values(?, ?, ?)", (
        ids, 
        code, 
        title,  
      ))
    else:
      this.__con.commit("update department set code = ?, title = ? where id = ?", (
        code,
        title,
        ids,  
      ))

  def exists_on_save(this, id, code):
    return this.__con.getone("select id from department where id = ? or code = ?", (
      id,
      code,  
    ))

  def exists_on_update(this, code):
    pass

  def lists(this, param: dict = { "dept_id": "" }, refid = None) -> list:
    # default param
    dept_id = ""
    if "dept_id" in param:
      dept_id = param["dept_id"]

    dept_id = dept_id if dept_id else "%%"
    # end default param

    res = this.__con.get(f"""
      select id, code, title 
      from department where id like ? order by title
    """, (
      dept_id,
    ))
        
    if refid != None:
      n = []

      pstore = PayrollStore(con = this.__con)

      
      for item in res:
        # item[0] -> department code
        c = pstore.getItemCount(refid = refid, dept_id = item[0])
        
        item = list(item) # convert the
        item.append(c)
        
        if c > 0: n.append(item)

      return n
    
    return res