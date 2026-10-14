import { AppHttp2 } from "../classes/lib.js";
import { ContribLoan } from "../component/ContribLoan.js";
import { messageBox } from "../main.js";
import { AppHttp } from "../plugin/app.js";
import { BasicTab, Button, ComboBox, DropDown, Form, Grid, Label, Modal, ModalV2, Panel, Table, TextBox } from "../plugin/mcontrol.js";
import { search_employee } from "../transaction.js";
import { Alert, Confirm } from "../util/dialog.js";
import { ActiveModal } from "./active.js";


const searchEmployee = async (param) => {

  const promise = new Promise((resolve, reject) => {
    try {
      search_employee(param, (o) => {
        resolve(o);
      }); 
    } catch(er) {
      reject(er);
    }
  });
  return promise;  
}

class DeptComboBox extends ComboBox {
  constructor() {
    super(null, null, null, "home");


    (async () => {
      await this.init();
    })();

  }
  async init() {
    const res = JSON.parse(await AppHttp2("/department/list"));
    const data = res.data;
    const data_len = data.length;
    this.clear();
    this.add("", "All Department");

    for (let i = 0; i < data_len; i++) {
      this.add(data[i][0], data[i][1] + " - " + data[i][2]);
    }
  }
}


////////////////////////////////////////  EmployeeUpdateModal  //////////////////////////////////////////////////////////////
// rate information
class RateInfoModal extends ModalV2 {
  constructor(emp_id) {
    super("Rate Information", "edit");

    this.emp_id = emp_id;
    const form = new Form();
    const rate = new TextBox("Rate", "text");
    const rate_type = new ComboBox([
      ["d", "Daily"],
      ["m", "Monthly"]
    ], "Rate Type");

    form.add([
      [rate, "rate"],
      [rate_type, "rate_type"]
    ]);

    const submit = new Button("Save", "success", "save");
    submit.control.style.marginTop = "5px";

    submit.addEventListener("click", async () => {
      const data = form.getValues();
      data.rate = data.rate.replace(",", "").replace(" ", "").trim();
      if (!/^[0-9\.]+$/.test(data.rate)) {
        alert("Invalid Rate");
        return;
      }

      const rate = parseFloat(data.rate);
      const rate_type = data.rate_type;
      if (rate_type == "d") {
        if (rate >= 800) {
          if (!confirm(rate + " is perday?")) {
            return;
          }
        }
        if (rate <= 50) {
          if (!confirm(rate + " is perday?")) {
            return;
          }
        }
      }

      const o = await AppHttp2("/employee/rate/save", { emp_id: this.emp_id, rate: rate, rate_type: rate_type });
      const res = JSON.parse(o);
      if (res.ok == 1) {
        await Alert(res.msg);
        this.hide(true);
        // reload the table
      } else {
        await Alert(res.msg);
      }


      
    });


    this.add([
      form, submit
    ]);
  }
}

// rate information
class RateInfo extends Panel {
  constructor(emp_id) {
    super();
    this.setStyle({
      border: "1px solid #ddd",
      borderTop: "none",
      width: "100%",
      height: "100%"
    });

    this.emp_id = emp_id;
    
    this.table = new Table(["Date", "Rate", "Type", 'NWPD', "Action"]);

    const newbtn = new Button("Add", "success", "plus-circle").setStyle({
      margin: "2px"
    });

    newbtn.addEventListener("click", async () => {
      const modal = new RateInfoModal(this.emp_id);
      const res = await modal.show();

      if (res != null && res) {
        await this.load();
      }
    });

    this.add([newbtn, this.table]);

    (async () => {
      await this.load();
    })();
  }

  async load() {
    const fdata = JSON.parse(await AppHttp2("/employee/rate/list", {
      emp_id: this.emp_id
    }));
    const data = fdata.data;
    const data_len = data.length;

    this.table.clear();

    for (let i = 0; i < data_len; i++) {
      const remove = new Button(null, "danger", "trash", "Please click to remove the rate!");

      remove.addEventListener("click", async () => {
        if (!await Confirm("Remove Rate?")) {
          return;
        } 

        const o = await AppHttp2("/employee/rate/remove", {
          date: data[i][2],
          emp_id: this.emp_id
        });

        const res = JSON.parse(o);
        if (res.ok == 1) {
          await Alert(res.msg);
          await this.load();
        } else {
          await Alert(res.msg);
        }

      });
    
      const no_type = data[i][3] != null ? data[i][3] : '';
      this.table.add([
        data[i][2], data[i][0], data[i][1] == "m" ? "Monthly" : "Daily", no_type, remove
      ]);
    }

  }
}


class PositionInfoModal extends ModalV2 {
  constructor(emp_id) {
    super("Position Information", "edit");
    this.emp_id = emp_id;

    this.form = new Form();
    
    const title = new TextBox("Position", "text", null);
    const status = new ComboBox(null, "Status", null);
    status.add("j", "Job Order");
    status.add("c", "Contract Of Service");
    status.add("r", "Regular Employee");
    
    this.form.add([
      [title, "title"],
      [status, "status"]
    ]);


    const submit = new Button("Save", "success", "save");
    submit.control.style.marginTop = "5px";

    submit.addEventListener("click", async () => {
      const data = this.form.getValues();
      data["emp_id"] = this.emp_id;
     
      const o = await AppHttp2("/employee/position/save", data);
      const res = JSON.parse(o);
      
      if (res.ok == 1) {
        await Alert(res.msg);
        this.hide(true);
      } else {
        await Alert(res.msg);
      }

    });

    this.add([
      this.form,
      submit
    ]);
  }




}

class PositionInfo extends Panel {
  constructor(emp_id) {
    super();
    this.setStyle({
      border: "1px solid #ddd",
      borderTop: "none",
      width: "100%",
      height: "100%"
    });

    this.emp_id = emp_id;
    
    this.table = new Table(["Title", "Date", "Status", "Action"]);
    const newbtn = new Button("Add", "success", "plus-circle").setStyle({
      margin: "2px"
    });


    newbtn.addEventListener("click", async () => {
      const modal = new PositionInfoModal(this.emp_id);
      const res = await modal.show();
      if (res != null && res) {
        await this.load();
      }
    });

    this.add([
      newbtn,
      this.table
    ]);

    (async() => {
      await this.load();
    })();
    
  }

  async load() {
    const o = await AppHttp2("/employee/position/list", { emp_id: this.emp_id });
    const fdata = JSON.parse(o);
    const data = fdata.data;
    const data_len = data.length;

    this.table.clear();
    for (let i = 0; i < data_len; i++) {
      const title = data[i][0];
      const date = data[i][1];
      const status = data[i][2];
      const remove = new Button(null, "danger", "trash");

      remove.addEventListener("click", async () => {
        if (!await Confirm("Delete this position?")) {
          return 
        }

        const _data = data[i];
        const rdata = {
          emp_id: this.emp_id,
          date: _data[1]
        };

        const o = await AppHttp2("/employee/position/remove", rdata);
        const res = JSON.parse(o);
        if (res.ok == 1) {
          await Alert(res.msg);
          await this.load();
        } else {
          await Alert(res.msg);
        }

      });

      this.table.add([
        title, date, status, remove
      ]);
    }

  }
}


class DepartmentInfoModal extends ModalV2 {

  constructor(emp_id) {
    super("Department Information", "edit");

    this.emp_id = emp_id;

    this.dept_input = new ComboBox(null, "Department", null, null, null, null);
    this.dept_input.add("", "[ Select Department ]")
    
    const submit = new Button("Save", "success", "save", "click to save the employee department");
    submit.control.style.marginTop = "5px";

    submit.addEventListener("click", async () => {
      const o = await AppHttp2("/employee/dept/save", {
        emp_id: this.emp_id,
        dept_id: this.dept_input.getValue()
      });
      const res = JSON.parse(o);
      if (res.ok === 1) {
        await Alert(res.msg);
        this.hide(true);
      } else {
        await  Alert(res.msg);
      }
      
    });

    this.add([
      this.dept_input,
      submit
    ]);

    (async () => {
      await this.load_dept();
    })();

  }

  async load_dept() {

    const o = await AppHttp2("/department/list", {});
    const fdata = JSON.parse(o);
    const data = fdata.data;
    const data_len = data.length;
    for (let i = 0; i < data_len; i++) {
      const name = data[i][2];
      const id = data[i][0];
      this.dept_input.add(id, name);
    }
  }
}

class DepartmentInfo extends Panel {
  constructor(emp_id) {
    super();
    
    this.setStyle({
      border: "1px solid #ddd",
      borderTop: "none",
      width: "100%",
      height: "100%"
    });
    
    this.emp_id = emp_id;
    this.table = new Table(["Date", "Title", "Action"]);

    const nbtn = new Button("Add", "success", "plus-circle").setStyle({
      margin: "2px"
    });


    nbtn.addEventListener("click", async () => {
      const modal = new DepartmentInfoModal(this.emp_id);
      const res = await modal.show();
      if (res != null && res) {
        await this.load(); // reload the table if success 
      }
      
    });


    this.add([
      nbtn,
      this.table
    ]);

    (async () => {
      await this.load();
    })();

  }

  async load() {
    const o = await AppHttp2("/employee/dept/list", { emp_id: this.emp_id });
    const fdata = JSON.parse(o);
    const data = fdata.data;
    const data_len = data.length;
    this.table.clear();

    for (let i = 0; i < data_len; i++) {
      const date = data[i][3];
      const title = data[i][2];
      const remove = new Button(null, "danger", "trash");
      
      remove.addEventListener("click", async () => {
        if (!await Confirm("Remove this?")) return;
        const data1 = data[i];
        const emp_id = this.emp_id;
        const dept_id = data1[1];
        const date = data1[3];

        const rdata = {
          "emp_id": emp_id,
          "dept_id": dept_id,
          "date": date
        };

        const o = await AppHttp2("/employee/dept/remove", rdata);
        const res = JSON.parse(o);

        if (res.ok === 1) {
          await Alert(res.msg);
          await this.load(); // reload the table
        } else {
          await Alert(res.msg);
        }

      });

      this.table.add([
        date, title, remove
      ]);
    }
  }
}

class BankInfoModal extends ModalV2 {
  constructor(emp_id) {
    super("Bank Information", "edit");

    this.bank = [];

    this.emp_id = emp_id;

    this.form = new Form();

    this.type = new ComboBox(null, "Bank In.");
    this.account_number = new TextBox("Account", "text", null);


    this.type.addEventListener("change", () => {
      this.isValid();
    });

    this.account_number.addEventListener("keyup", () => {
      this.isValid();
    });

    this.form.add([
      [this.type, "bank_index"],
      [this.account_number, "account_number"]
    ]);

    const submit = new Button("Save", "success", "save").setStyle({
      marginTop: "5px"
    });

    submit.addEventListener("click", async () => {
      const data = this.form.getValues();
      data["emp_id"] = this.emp_id;
      data["bank_code"] = this.bank[data["bank_index"]][0];

      if (!this.isValid()) {
        await Alert("Invalid Bank Account Number!");
        return;
      }

      const o = await AppHttp2("/employee/bank/save", data);
      const res = JSON.parse(o);
      if (res.ok === 1) {
        await Alert(res.msg);
        this.hide(true);
      } else {
        await Alert(res.msg);
      }

    });

    this.add([
      this.form,
      submit
    ]);

    (async () => {
      await this.loadBank();
    })();
  }

  isValid() {
    const v = this.account_number.getValue();
    const index = this.type.getValue();
    const _regex = this.bank[index][2];
    const pattern = new RegExp(_regex);
    const is_ok = pattern.test(v);

    if (!is_ok) {
      this.account_number.control.style.border = "1px solid red";
    } else {
      this.account_number.control.style.border = "1px solid white";
    }
    return is_ok;
  }

  async loadBank() {
    const o = await AppHttp2("/bank/list", {});
    const dataf = JSON.parse(o);
    const data = dataf.data;
    const data_len = data.length;
    
    this.bank = data;
    
    for (let i = 0; i < data_len; i++) {
      this.type.add(i, data[i][1]);
    }
  }
}

class BankInfo extends Panel {
  constructor(emp_id) {
    super();
    this.setStyle({
      border: "1px solid #ddd",
      borderTop: "none",
      width: "100%",
      height: "100%"
    });

    this.emp_id = emp_id;

    this.table = new Table(["Date", "Bank", "Account Number", "Action"]);

    const nbtn = new Button("Add", "success", "plus-circle").setStyle({
      margin: "2px"
    });

    nbtn.addEventListener("click", async () => {
      const modal = new BankInfoModal(this.emp_id);
      const res = await modal.show();

      if (res != null && res) {
        await this.load();
      }

    });

    this.add([
      nbtn,
      this.table
    ]);

    (async () => {
      await this.load();
    })();

  }

  async load() {
    const o = await AppHttp2("/employee/bank/list", { emp_id: this.emp_id });
    const res = JSON.parse(o);
    const data = res.data;
    const data_len = data.length;

    this.table.clear();

    for (let i = 0; i < data_len; i++) {
      const date = data[i][2];
      const code = data[i][0];
      const account = data[i][1];
      const remove = new Button(null, "danger", "trash");

      remove.addEventListener("click", async () => {
        // reverse the condition to make code cleaner
        if (!await Confirm("Are you sure to delete this bank account?")) {
          return;
        }

        const o = await AppHttp2("/employee/bank/remove", {
          code: code, account_number: account, emp_id: this.emp_id
        });

        const res = JSON.parse(o);
        if (res.ok === 1) {
          await Alert(res.msg);
          await this.load(); // reload the table after the deletion
          // reloading is not effecient way, in the future removing only node of the table
        } else {  
          await Alert(res.msg);
        }



      });

      this.table.add([
        date, code, account, remove
      ]);

    }

  }

  
}

class EmployeeUpdateModal extends ModalV2 {
  constructor(emp_id, name = "") {
    super(`Employee Update - ${name}`, "edit");
    this.emp_id = emp_id;
    this.resolve = true;

    const tab = new BasicTab();
    tab.add("Rate", o => {
      o.add(new RateInfo(this.emp_id));
    }, true);


    tab.add("Position", o => {
      o.add(new PositionInfo(this.emp_id));
    });

    tab.add("Department", o => {
      o.add(new DepartmentInfo(this.emp_id));
    });

    tab.add("Bank Account", o => {
      o.add(new BankInfo(this.emp_id));
    });


    this.add([
      tab
    ]);
  }
}
/////////////////////////    End EmployeeUpdateModal     ///////////////////////////////////////////////////////


//////////////////////// Contribution and Loan Modal //////////////////////



////////////////////// End Contribution and loan Modal ////////////////////


class EmployeeTable extends Panel {
  constructor() {
    super();
    this.addClass("card");
    this.addClass("table-responsive");

    this.table = new Table(["Action", "Profile", "Name", "Position", "Status", 'Active', 'Last Process']);
    this.add(this.table);
    
    (async() => {
      await this.reload();
    })();

    this.search = "";
    this.dept_id = "";
    this.emp_status = "";
    this.active = "";

  }

  async reload(search = "", dept_id = "", emp_status = "", active = "", input = true) {

    if (input) {
      this.search = search;
      this.dept_id = dept_id;
      this.emp_status = emp_status;
      this.active = active;
    }

    this.table.clear();

    const o = await searchEmployee({
      "search": this.search,
      "dept_id": this.dept_id,
      "emp_status": this.emp_status,
      'active': this.active
    });

    const total = o["data"]["total"];
    const data = o["data"]["data"];
    const data_len = data.length;

    for (let i = 0; i < data_len; i++) {
      const error = data[i]["error"];
      const pos_info = data[i]["pos_info"];
      const view = new Button(null, "success", "user").setStyle({ width: '40px' }); 

      const menu = new DropDown(`Action`);

      menu.addItem(`<i class="fa fa-edit"></i> Edit Employee`, async () => {
        const fdata = data[i];
        /// open the modal
        // console.log(emp_form.getValues());
        const modal = new EmployeeModal(fdata);
        const res = await modal.show();  
        if (res != null && res["ok"]) {
          await this.reload(null, null, null, null, false);
        }    

      });

      menu.addItem(`<i class="fa fa-pencil"></i> Update Rate, Position, Department etc...`, async () => {
        const emp_data = data[i];
        // emp_info_modal.show();
        // e_info.name.control.innerHTML = (emp_data.lname + ", " + emp_data.fname).toUpperCase();
        // GLOBAL_DATA["emp_id"] = emp_data.id;

        console.log(emp_data);

        const modal = new EmployeeUpdateModal(emp_data.id, `${emp_data.lname}, ${emp_data.fname} ${emp_data.ename}`.toUpperCase());
        const res = await modal.show();
        if (res != null && res) {
          await this.reload(null, null, null, null, false);
        }

      });

      menu.addItem(`<i class="fa fa-money"></i> Update loan & Contribution`, async () => {
        const { id, fname, lname, mname, ename, pref_name, suf_name, pos_status } = data[i];
        const cl = new ContribLoan(id, pos_status, `${pref_name} ${fname} ${mname} ${lname} ${ename} ${suf_name}`.toUpperCase());
        const res = await cl.show();
      });

      menu.addItem(`<i class="fa fa-flag"></i> Activation or Deactivation`, async () => {
        const info = data[i];
        const ac = new ActiveModal(info.id, `${info.pref_name} ${info.fname} ${info.mname} ${info.lname} ${info.suf_name}`.toUpperCase(), info.active);
        const res = await ac.show();

      });
      // end menu

      
      // position information
      let _p = new Panel();
      const pos_panel = new Panel();
      _p.control.innerHTML = 'Created: ' + data[i].created + " ago";

      pos_panel.add(_p);

      for (var m = 0; m < pos_info.length; m++) {
        _p = new Panel();
        _p.control.innerHTML = pos_info[m].key + " : " + pos_info[m].value;
        pos_panel.add(_p);
      }
      // end position information


      const err_panel = new Panel();
      for (let k = 0; k < error.length; k++) {
        const p1 = new Panel();
        if (error[k].error) {
          p1.control.innerHTML = '<span style="color: black; text-decoration: underline;"><i class="fa fa-close" style="color: red;"></i> ' + error[k].msg + '</span>';
        } else {
          p1.control.innerHTML = '<span style="color: black; text-decoration: underline;"><i class="fa fa-check" style="color: green;"></i> ' + error[k].msg + '</span>';
        }
        err_panel.add(p1);
      }

      const claim = data[i]["claim"];
      let last_refid = '';
      if (claim) {
        last_refid = claim[2]
      }

      this.table.add([
        new Panel().add([menu]),
        '',
        (data[i].lname + ", " + data[i]["fname"] + " " + data[i].mname).toUpperCase(),
        pos_panel,
        err_panel,
        new Panel().add(new Label(data[i].active == 'y' ? 'YES' : 'NO')).setStyle({ color: (data[i].active == 'y' ? 'green' : 'red'), padding: '2px' }),
        new Label(`${last_refid}`)
      ]);
    }
    
  } 
}


class EmployeeModal extends ModalV2 {
  constructor(data = null) {
    console.log(data);

    super("Employee Information", "plus-circle");
    const ids = new TextBox("refid", "text", null);
    ids.setAttr({
      "readonly": ""
    });

    const pref_name = new TextBox("Prefix", "text", null);
    const fname = new TextBox("Firstname", "text", null);
    const mname = new TextBox("Middlename", "text", null);
    const lname = new TextBox("Lastname", "text", null);
    const ename = new TextBox("Ex. name", "text", null);
    const sufname = new TextBox("Suffix", "text", null);
    const dob = new TextBox("Birth", "date", null);
    const gender = new ComboBox([
      ["", ""],
      ["m", "Male"],
      ["f", "Female"]
    ], "Gender", null, null);
    

    const address = new TextBox("Address", "text", null);

    const hr_id = new TextBox("HR System employee Id", "text", null);


    if (data != null) {
      ids.setValue(data.id);
      fname.setValue(data.fname);
      mname.setValue(data.mname);
      lname.setValue(data.lname);
      ename.setValue(data.ename);
      sufname.setValue(data.suf_name);
      dob.setValue(data.dob);
      gender.setValue(data.gender);
      address.setValue(data.address);
      hr_id.setValue(data.hr_id);
    }

    this.form = new Form();

    const submit = new Button("Save", "success", "plus-circle");


    submit.addEventListener("click", async () => {
      console.log(this.form.getValues());

      const data = this.form.getValues();
      // AppHttp("/client/save", data, null, function (o) {
      //   var rdata = JSON.parse(o);
      //   messageBox.show(rdata.msg, function () {
      //     modal.hide();
      //     reload_table();
      //   });
      // });

      const o = await AppHttp2("/client/save", data);
      const rdata = JSON.parse(o);
      
      await Alert(rdata.msg);
      if (rdata.ok) {
        this.hide({ 
          ok: true,
          search: `${fname.getValue()}${mname.getValue()}${lname.getValue()}`
        });
      }

    });

    const remove = new Button("Remove", "danger", "trash");
    remove.control.style.marginLeft = "5px";
    remove.addEventListener("click", async () => {
      const id = ids.getValue(); 

      if (!await Confirm(`Delete this employee?`)) {
        return;
      }

      const data = JSON.parse(await AppHttp2("/employee/remove", { id: id }));
      
      if (data.ok === 1) {
        await Alert(data.msg);
        this.hide({
          ok: true,
          search: `${fname.getValue()}${mname.getValue()}${lname.getValue()}`
        });
      } else {
        await Alert(data.msg);
      }

    });

    this.form.add([
      [ids, "id"],
      [pref_name, "pref_name"],
      [fname, "fname"],
      [mname, "mname"],
      [lname, "lname"],
      [ename, "ename"],
      [sufname, "suf_name"],
      [gender, "gender"],
      [dob, "dob"],
      [address, "addr"],
      [hr_id, "hr_id"]
    ]);

    this.add([
      this.form,
      new Panel().add([
        submit, remove
      ]).setAttr({
        marginTop: "10px"
      })
    ]);
  }


  getForm() {
    return this.form;
  }


}

/// entry point
class Employee extends Panel {
  constructor() {
    super();
    this.setStyle({
      padding: "10px"
    });

    // top input
    this.search = new TextBox(null, "text", "search", null, "Search.... Lastname, Firstname, middlename");
    this.dept_id = new DeptComboBox();
    this.active = new ComboBox(null, null, null, 'cog');
    this.active.add('', 'All');
    this.active.add('y', 'Active');
    this.active.add('n', 'Inactive');

    this.emp_status = new ComboBox(null, null, null, "refresh");
    this.emp_status.add("", "[ All ]");
    this.emp_status.add("j", "Job Orders");
    this.emp_status.add("c", "Contract Of Service");
    this.emp_status.add("r", "Regular(Permanent.Temporary.Elective.etc...)");

    // grid
    const grid = new Grid(1);
    grid.cell(this.search, ['md-3', 'sm-3']);
    grid.cell(this.dept_id, ['md-3', 'sm-3']);
    grid.cell(this.emp_status, ['md-3', 'sm-3']);
    grid.cell(this.active, ['md-3', 'sm-3']);

    this.table = new EmployeeTable().setStyle({
      marginTop: "10px"
    });


    const newbtn = new Button("Add Employee", "success", "user-plus");
    newbtn.control.style.marginBottom = "5px";
    newbtn.addEventListener("click", async () => {
      const modal = new EmployeeModal();
      const res = await modal.show();
      if (res != null && res["ok"]) {
        this.search.setValue(res["search"]);
        this.dept_id.setValue("");
        this.emp_status.setValue("");
        this.reloadTable();
      }
    });


    this.add([
      newbtn,
      new Panel().addClass("container-fluid").add(grid),
      this.table
    ]);
    
    this.addInputEvents();
  }

  addInputEvents() {
    let time = null;
    this.search.addEventListener("keyup", () => {
      clearTimeout(time);
      time = setTimeout(() => {
        this.reloadTable();
      }, 500); // this avoid overload in the server
    });

    this.dept_id.addEventListener("change", () => {
      this.reloadTable();
    });

    this.emp_status.addEventListener("change", () => {
      this.reloadTable();
    });

    this.active.addEventListener("change", () => {
      this.reloadTable();
    });

  }

  reloadTable() {
    this.table.reload(
      this.search.getValue(),
      this.dept_id.getValue(),
      this.emp_status.getValue(),
      this.active.getValue()
    );
  }

}



export default Employee;
export {
  EmployeeTable,
  searchEmployee
};