import { AppHttp2 } from "../classes/lib.js";
import { Panel, Select3 } from "../plugin/mcontrol.js";

class DepartmentSelect extends Select3 {
  constructor(title = "", change = null) {

    super(null, change);




    super.prepend(new Panel().text(title).style({
      "font-weight": "bold"
    }));

    (async () => {
      await this.load(); 
      
    })();
  }

  async load() {
    const res = await JSON.parse(await AppHttp2("/department/list", {})).data;

    super.addItem("", "[ All Department ]");
    for (const item of res) {
      super.addItem(item[0], `(${item[1]}) - ${item[2]}`);
    }
  }
}

class EmployeeSelect extends Select3 {
  constructor(title = "", emp_status = "", change = null) {
    super(async(search) => {

      const res = JSON.parse(await AppHttp2("/client/list", {"search": search, emp_status: emp_status}));

      const data = res.data.data;

      const ret = []; 

      for (const item of data) {
        const name = `${ item.lname }, ${ item.fname } ${ item.mname } ${item.ename}`.toUpperCase();
        // console.log(item);
        ret.push([
          item.id,
          name,
          new Panel([
            new Panel().text(name).style( { fontWeight: "bold" }),
            new Panel().text(item.pos_title)
          ])
        ]);
      }

      return ret;
    
    }, change);

    super.prepend(new Panel().text(title).style({
      "font-weight": "bold"
    }));
  }
}


export {
  DepartmentSelect,
  EmployeeSelect
};