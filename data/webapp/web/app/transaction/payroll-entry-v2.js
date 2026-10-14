import { AppHttp2 } from "../classes/lib.js";
import { PayrollViewer } from "../component/payroll.js";
import { DepartmentSelect, EmployeeSelect } from "../helper/select.js";
import { appHome, setHome } from "../main.js";
import { Button, ComboBox3, Container, Grid, Label, Loader, Panel, Table2, TextBox2, x_storage } from "../plugin/mcontrol.js";
import { TransactionMain } from "../transaction.js";

import { Alert, Confirm, DialogModal2 } from "../util/dialog.js";
import { PayrollPage } from "./payroll.js";

const Payroll = {
  load: async (refid = "", dept_id = "", search = "") => {
    const res = await AppHttp2("/payroll/get/items", {
      refid: refid,
      dept_id: dept_id,
      search: search
    });

    return JSON.parse(res);
  },
  getDept: async () => {

    return JSON.parse(await AppHttp2("/department/list", {}));
  },
  getInfo: async (refid) => {
    return JSON.parse(await AppHttp2("/payroll/get/info", {
      refid: refid
    })).data;
  },
  empInfo: async (id, from, to) => {
    console.log(id, from, to);
    const res = JSON.parse(await AppHttp2("/employee/information", {
      emp_id: id,
      from: from,
      to: to
    }));

    return res.data;
  },
  type: (key) => {

    return {
      "m": "Monthly",
      "d": "Daily",
      "h": "Hourly",
      "a": "Yearly"
    }[key];
  },
  dedType: (key) => {
    return {
      "l": "Loan",
      "c": "Contribution",
      "a": "Additional to Compansation" 
    }[key];
  }
  
}


class PayrollEntryForm extends DialogModal2 {
  constructor(refid, emp_id = null) {
    super(`Payroll Entry`, "pencil", "1360px");

    this.refid = refid;
    this.from_t = null;
    this.to_t = null;
    


    // input
    this.id = new TextBox2("Id", "text");
    this.name = new TextBox2("Name", "text");
    this.work_day = new TextBox2("No. Work Day", "text");
    this.absent = new TextBox2("Absent", "text");
    this.undertime = new TextBox2("Undertime(Minute)", "text");
    this.late = new TextBox2("Late(Minute)", "text");

    this.salary_input = new TextBox2("Rate", "text");
    this.salary_input.label.style({ fontSize: "7pt" });
    this.salary_input.tf.style({ height: "25px" });
    this.salary_input.tf.attr("readonly", "");


    this.id.tf.attr("readonly", "");
    this.name.tf.attr("readonly", "");

    ////// sized and height
    this.id.label.style({ fontSize: "7pt" });
    this.id.tf.style({ height: "25px" });

    this.name.label.style({ fontSize: "7pt" });
    this.name.tf.style({ height: "25px" });

    this.work_day.label.style({ fontSize: "7pt" });
    this.work_day.tf.style({ height: "25px" });

    this.absent.label.style({ fontSize: "7pt" });
    this.absent.tf.style({ height: "25px" });

    this.undertime.label.style({ fontSize: "7pt" });
    this.undertime.tf.style({ height: "25px" });

    this.late.label.style({ fontSize: "7pt" });
    this.late.tf.style({ height: "25px" });
    //// sized and height


    this.gross = new TextBox2("Gross", "text");
    this.deducation = new TextBox2("Deduction", "text");
    this.net = new TextBox2("Net");

    this.gross.tf.attr("readonly", "");
    this.deducation.tf.attr("readonly", "");
    this.net.tf.attr("readonly", "");

    this.gross.tf.style({
      fontWeight: "bold"
    });

    this.deducation.tf.style({
      fontWeight: "bold",
      color: "red"
    });

    this.net.tf.style({
      fontWeight: "bold",
      color: "green"
    });


    this.work_day.addEventListener("change", async () => {
      await this.preCalculate();
    });

    this.absent.addEventListener("change", async () => {
      await this.preCalculate();
    });

    this.undertime.addEventListener("change", async () => {
      await this.preCalculate();
    });

    this.late.addEventListener("change", async () => {
      await this.preCalculate();
    });



    this.rate = null;
    this.rate_type = null;

    this.submit = new Button("Save", "success", "save").style({
      width: "100px"
    });
    // end input

    this.tax_cal_btn = new Button("Calculate Tax", "danger", "refresh").style( {
      width: "150px"
    });

    
    const label = new Panel();
    const search = new EmployeeSelect("Search Employee", "", async () => {

      for (const input of this.inputs) {
        input.widget.setValue(0);
      }

      this.id.setValue("");
      this.name.setValue("");
      const id = search.getValue();

      const info = await Payroll.empInfo(id, this.from_t, this.to_t);

      console.log(info);

      this.id.setValue(id);
      this.name.setValue(`${info.emp_info.l}, ${info.emp_info.f} ${info.emp_info.m} ${info.emp_info.e}`);

      this.rate = info.rate_info.rate;
      this.rate_type = info.rate_info.rate_type;

      this.salary_input.setValue(`${this.rate} / ${Payroll.type(this.rate_type)}`);

      /// if it is new then reload the pre computed

      const res = JSON.parse(await AppHttp2("/payroll/emp_ded/default", {
        refid: this.refid,
        emp_id: id
      }));

      console.log(res);

      if (res.ok) {

        const data = res.data;

        for (const input of this.inputs) {
          for (const item of data) {
            if (item.code == input.code && item.name == input.name) {
              
              input.widget.setValue(item.value);

              break;
            }
          }
        }
      } else {
        await Alert(res.msg);
      }

      /// end if


      this.preCalculate();
      
    });

    if (emp_id != null) {
      search.tf.attr("disabled", "");
    }

    const grid = new Grid(10);


    // panel1
    grid.cell(new Panel([
      this.id,
      this.name,
      this.salary_input,
      this.work_day,
      this.absent,
      this.undertime,
      this.late,
      new Panel([this.submit.style({ marginRight: "5px" }), this.tax_cal_btn]).style({ marginTop: "5px" })
    ]).class("card").style({ padding: "10px" }), ["md-4"]);
    
    

    // panel2 
    this.panel2 = new Container();
    grid.cell(new Panel().class("card").add(this.panel2), ["md-4"]);

    this.panel3 = new Container();
    // panel3
    grid.cell(new Panel().class("card").add(this.panel3), ["md-4"]);

    const sgrid = new Grid(10);
    sgrid.cell(search, ["md-3"]);
    sgrid.cell(this.gross, ["md-3"]);
    sgrid.cell(this.deducation, ["md-3"]);
    sgrid.cell(this.net, ["md-3"]);

    this.inputs = [];

    (async () => {
      const info = await this.init();

      this.from_t = info.from;
      this.to_t = info.to;

      this.add(new Container([
        label.text(`refid#${info.refid}-${info.name}`),
        sgrid,
        grid
      ]));

      if (emp_id != null) {
        this.id.setValue(emp_id);
  
        const loader = new Loader().show();

        const id = search.getValue();

        const info = await Payroll.empInfo(emp_id, this.from_t, this.to_t);

        this.id.setValue(emp_id);
        this.name.setValue(`${info.emp_info.l}, ${info.emp_info.f} ${info.emp_info.m} ${info.emp_info.e}`);

        this.rate = info.rate_info.rate;
        this.rate_type = info.rate_info.rate_type;

        this.salary_input.setValue(`${this.rate} / ${Payroll.type(this.rate_type)}`);

  
        await this.getPayrollItem();
        await this.preCalculate();
        loader.hide();
    
      }


      this.submit.addEventListener("click", async () => {
        
        const is_update = emp_id != null;

        const payload = await this.preCalculate();

        this.submit.showLoader();

        const res = JSON.parse(await AppHttp2("/payroll/add/item", {
          is_update: is_update,
          emp_id: payload.emp_id,
          late: payload.late,
          work: payload.work_day,
          absent: payload.total_absent,
          undertime: payload.undertime,
          payroll_refid: payload.payroll_refid,
          deduction_value: payload.ded_data
        })); 


        this.submit.hideLoader();

        await Alert(res.msg);

        if (res.ok) {
          this.hide(true);
        }

        
        // emp_id: this.id.getValue(),
        // rate: this.rate,
        // rate_type: this.rate_type,
        // payroll_refid: this.refid,
        // work_day: this.work_day.getValue(),
        // late: this.late.getValue(),
        // undertime: this.undertime.getValue(),
        // total_absent: this.absent.getValue(),
        // ded_data: ded_data

      });

      this.tax_cal_btn.addEventListener("click", async () => {
        if (!await Alert("Calculate Tax?")) return;
        const res = JSON.parse(await AppHttp2("/payroll/calculate/tax", {
          emp_id: this.id.getValue(),
          refid: this.refid
        }));
        

        if (res.ok) {
          await Alert(`
            <div>
              <span style="color: red; font-weight: bold; ">Warning!</span>: This Computation is under on testing!
            </div>
            <hr />
            <div>Suggested Tax!</div>
            <div style="font-weight: bold; font-size: 20pt;">Monthly Tax: <span style="color: red;">${res.data.tax}</span></div>
            <div style="font-weight: bold; font-size: 20pt;">Half Month Tax: <span style="color: orange;">${res.data.tax / 2}</span></div>
          `);
        }

      });

    })();
  }

  async getPayrollItem() {
    const res = JSON.parse(await AppHttp2("/payroll/get/item", {
      refid: this.refid,
      emp_id: this.id.getValue()
    }));

  
    if (!res.ok) return await Alert(res.msg);

    const data = res.data;

    const com = data.com;
    console.log(com);

    this.absent.setValue(com.a);
    this.late.setValue(com.l);
    this.undertime.setValue(com.u);
    this.work_day.setValue(com.w);


    const deduction = data.deduction;

    for (const item of deduction) {
      for (const input of this.inputs) {
        if (item.code == input.code && item.name == input.name) {
          input.widget.setValue(item.value);
          break
        }
      } 
    }

    return res;
    
  }

  async init() {
    
    const loader = new Loader().show();

    const info = await Payroll.getInfo(this.refid);
    const ded_list = info.deduction_list;
    this.gen_deds(ded_list);

    loader.hide();
    return info;
  }

  async preCalculate() {
    // ded_data.push({
    //   code: ded_stat["code"],
    //   name: ded_stat["name"],
    //   value: v
    // });

    // const res = JSON.parse(await AppHttp2("/payroll/pre/calculate", {
    //   emp_id: info.dept_info.emp_id,
    //   rate: rate,
    //   rate_type: rate_type,
    //   payroll_refid: payroll_data.refid,
    //   work_day: total_work,
    //   late: total_late,
    //   undertime: total_undertime,
    //   total_absent: total_absent,
    //   ded_data: ded_data
    // }));

    // console.log("calculate");

    if (this.id.getValue() == "") return;
    if (this.rate == null) return;
    if (this.rate_type == null) return;


    const ded_data = [];
    for (const item of this.inputs) {

      if (item.widget.getValue() == "") {
        item.widget.setValue(0);
      }

      ded_data.push({
        code: item.code,
        name: item.name,
        value: parseFloat(item.widget.getValue())
      });
    } 

    if (this.work_day.getValue() == "") {
      this.work_day.setValue(0);
    }
    
    if (this.late.getValue() == "") {
      this.late.setValue(0);
    }

    if (this.undertime.getValue() == "") {
      this.undertime.setValue(0);
    }

    if (this.absent.getValue() == "") {
      this.absent.setValue(0);
    }
    
    const payload = {
      emp_id: this.id.getValue(),
      rate: this.rate,
      rate_type: this.rate_type,
      payroll_refid: this.refid,
      work_day: this.work_day.getValue(),
      late: this.late.getValue(),
      undertime: this.undertime.getValue(),
      total_absent: this.absent.getValue(),
      ded_data: ded_data
    };

;
    // console.log(payload);
    const res = JSON.parse(await AppHttp2("/payroll/pre/calculate", payload));

    if (res.ok) {
      const data = res.data;
      this.deducation.setValue(data.total_deduction);
      this.net.setValue(data.net_amount);
      this.gross.setValue(data.gross_amount);
    }

    return payload;
  }

  gen_deds(items) {
    // 
    this.inputs = [];

    this.panel3.style({
      paddingBottom: "10px"
    });
    this.panel2.style({
      paddingBottom: "10px"
    });
    this.panel3.clear();
    this.panel2.clear();

    const grid3 = new Grid(5);
    const grid2 = new Grid(5);

    for (const item of items) {

      const tb = new TextBox2(`${item.code}  ${item.name != item.code ? item.name : ""}`);

      tb.label.style({ fontSize: "7pt" });
      tb.tf.style({ height: "25px" });

      if (item.view_only == "n" && item.type == "c") {
        tb.tf.style({
          color: "orange",
          fontWeight: "bold"
        });
      } else if (item.type == "l") {
        tb.tf.style({
          color: "red",
          fontWeight: "bold"
        });
      } else if (item.type == "a") {
        tb.tf.style({
          color: "green",
          fontWeight: "bold"
        });
      } else if (item.view_only == "y" && item.type == "c") {
        tb.tf.style({
          fontWeight: "bold"
        }); // goverment shares
      }

      let time = null;
      tb.addEventListener("keyup", async () => {
        clearTimeout(time);
        time = setTimeout(async () => {
          await this.preCalculate();
        }, 500);
      });
        
      this.inputs.push({
        code: item.code,
        name: item.name,
        widget: tb
      });

      if (item.type == "l" || item.type == "c") {
        grid3.cell(tb, ["md-6"]);
      } else if (item.type == "a") {
        grid2.cell(tb, ["md-6"]);
      }
    
    }

    this.panel3.add(grid3);
    this.panel2.add(grid2);
    
  }

}


class CustomHeader extends DialogModal2 {
  constructor() {
    super("Custom Header", "edit");

    const code = new TextBox2("Code", "text");
    const name = new TextBox2("Name", "text");
    const floor = new TextBox2("Floor", "text");
    const ceil = new TextBox2("Ceil", "text");
    const value = new TextBox2("Value", "text");
    const view_only = new ComboBox3("View Only");
    const active = new ComboBox3("Active");
    const type = new ComboBox3("Type");
    
    const submit = new Button("Add", "success", "plus-circle").style({ marginTop: "10px" });
    
    floor.setValue(0);
    ceil.setValue(0);
    value.setValue(0);

    view_only.add("n", "No");
    view_only.add("y", "Yes");
    
    active.add("y", "Yes");
    active.add("n", "No");

    type.add("a", "Additional Compensation");
    type.add("l", "Loan");
    type.add("c", "Contribution");

    this.add(new Container([
      code, 
      name,
      floor,
      ceil,
      value,
      view_only,
      active,
      submit
    ]));

    submit.addEventListener("click", () => {
      const data = {
        "code": code.getValue(),
        "name": name.getValue(),
        "floor": floor.getValue(),
        "ceil": ceil.getValue(),
        "value": value.getValue(),
        "view_only": view_only.getValue(),
        "active": active.getValue(),
        "createdby": null,
        "datecreated": null,
        "type": type.getValue(),
        "payroll_design": "[\"j\"]",
        "bracket": null
      };

      this.hide(data);
    });
  }
}

class EditHeader extends DialogModal2 {
  constructor(refid) {
    super("Edit Payroll Header", "edit", "720px");
    this.refid = refid;

    this.default_list   = null;
    this.deduction_list = null;

    const grid = new Grid(10);
    
    this.ded_input = new ComboBox3("Deduction List");
    const add = new Button("Add", "primary", "plus-circle").style({ marginTop: "27px", marginRight: "2px" });

    const addcustom = new Button("Add Custom").style({ marginTop: "27px" });
    
    grid.cell(this.ded_input, ["md-9"]);
    grid.cell(new Panel([ add, addcustom ]), ["md-3"]);
    

    this.deduction_input = [];

    this.table = new Table2([
      "Code", "Name", "Type", "Action"
    ]);

    const submit = new Button("Submit", "primary", "save");

    

    (async () => {
      
      const loader = new Loader().show();
      
      const info_data = await Payroll.getInfo(this.refid);
      
      this.deduction_list = info_data.deduction_list;
      
      
      const ded_list = JSON.parse(await AppHttp2("/setting/deduction/list", { refid: this.refid }));
      loader.hide();

      if (!ded_list.ok) {
        await Alert("You are not authorized!");
        this.hide(false);
        return; 
      } 

      const default_list = ded_list.data;

      this.default_list = default_list;

      console.log(this.deduction_list);
      console.log(this.default_list);

      for (let i = 0; i < this.default_list.length; i++) {
        this.ded_input.add(i, `${this.default_list[i]["code"]} - ${this.default_list[i]["name"]}`);
      }
      
      this.add(new Container([
        grid,
        this.table,
        submit.style({
          marginTop: "5px"
        })
      ]));

      await this.load();


      add.addEventListener("click", () => {
        const index = this.ded_input.getValue();
        const item = this.default_list[index];
        
        this.addList(item);
      });

      submit.addEventListener("click", async () => {

        submit.showLoader();
        const res = JSON.parse(await AppHttp2("/payroll/info/update", { refid: this.refid, data: this.deduction_list }));
        submit.hideLoader();
        if (res.ok) {
          await Alert(res.msg);
          this.hide(true);
        } else {
          await Alert(res.msg);
        }
      });


      addcustom.addEventListener("click", async () => {
        const modal = new CustomHeader();
        const res = await modal.show(); // it return the required object

        if (res != null) {
          this.addList(res);
        }

      });
      
    })();
  }


  async addList(item) {
    const len = this.deduction_list.length;
    
    for (let i = 0; i < len; i++) {
      const item2 = this.deduction_list[i];

      if (item2.code == item.code && item.name == item2.name) {
        await Alert("Item Already Added!");
        return;
      }
    }
    
    this.deduction_list.push(item);
    this.load();
  }

  removeList(code, name) {
    

    const len = this.deduction_list.length;
    
    for (let i = 0; i < len; i++) {
      const item = this.deduction_list[i];
      
      if (code == item.code && name == item.name) {
        this.deduction_list.splice(i, 1);
        this.load();
        break;
      }

    }
  }

  async load() {
    this.table.clearBody();
    const len = this.deduction_list.length;

    for (let i = 0; i < len; i++) {

      const item = this.deduction_list[i];
      const remove = new Button("Remove", "danger", "trash");

      let label = null;

      if (item.type == "l")
        label = new Panel().text(`${Payroll.dedType(item.type)}`).class(["badge", "bg-danger"]);
      else if (item.type == "c")
        label = new Panel().text(`${Payroll.dedType(item.type)}`).class(["badge", "bg-warning"]);
      else if (item.type == "a")
        label = new Panel().text(`${Payroll.dedType(item.type)}`).class(["badge", "bg-success"]);

      const tr = this.table.add([
        item.code,
        item.name,
        label,
        remove
      ]);
      

      remove.addEventListener("click", async () => {
        if (!await Confirm("Remove?")) return;
        const code = item.code;
        const name = item.name;
        console.log(code, name);

        this.removeList(code, name);

      });

    }


  }

}


class PayrollEntryMain extends Panel {


  dispose() {
    document.getElementsByTagName("title")[0].innerHTML = `Payroll System`; // go back to the default name of the system
  }

  constructor(refid) {
    super();

    this.refid = refid;
    
    const add = new Button("Add Entry", "primary", "plus-circle").style({
      marginRight: "2px"
    });

    const signatory = new Button("Signatory", "success", "pencil").style({
      marginRight: "2px"
    });

    const header = new Button("Edit Header", "primary", "file-pdf-o").style({
      marginRight: "2px"
    });

    const cal_tax = new Button("Recalculate Tax", "warning", "refresh").style({
      marginRight: "2px"
    });

    const view_payroll = new Button("View Payroll", "success", "file-pdf-o").style({
      marginRight: "50px"
    });
    
    const del = new Button("Delete Payroll", "danger", "trash");
    

    this.table = new Table2([ "Action", "Period", "Name", "Position", "Rate", "Day Work", "Gross", "Deduction", "W/Tax", "Net", "Remark" ]);

    this.dept_id = new DepartmentSelect("Department", async (v) => {
      await this.load();
    });
    this.search = new TextBox2("Search", "text");
    this.qrscan = new TextBox2("QRCode", "text");

    const grid = new Grid(10);

    grid.cell(this.search, ["md-3"]);
    grid.cell(this.dept_id, ["md-3"]);
    grid.cell(this.qrscan, ["md-3"]);

    this.payroll_info = null;

    (async () => {

      // const r = await Payroll.getDept();
      // const data = r.data;
      // this.dept_id.add("", "[ All Department ]");
      // for (let i = 0; i < data.length; i++) {
      //   this.dept_id.add(data[i][0], data[i][1] + " - " + data[i][2]);
      // }

      const payroll_info = await Payroll.getInfo(this.refid);
      payroll_info["deduction_list"] = JSON.stringify(payroll_info["deduction_list"]);
      payroll_info["signatory_list"] = JSON.stringify(payroll_info["signatory_list"]);
    

      this.payroll_info = payroll_info;

      document.getElementsByTagName("title")[0].innerHTML = `${payroll_info["from"]} ${payroll_info["to"]} ${payroll_info["name"]}`;

      
      const title_txt = `<span style="color: red;">ref: ${this.refid}</span> | <span style="color: red; font-weight: bold;">${payroll_info["from"]}</span> to <span style="color: red; font-weight: bold;">${payroll_info["to"]}</span> (${payroll_info["name"]})`;

      const ded_info = JSON.parse(payroll_info["deduction_list"]);

      let tax_bracket = null;
      for (const item of ded_info) {
        if (item.code == "TAX") {
          tax_bracket = item;
          break;
        }
      }

      if (tax_bracket != null) {
        tax_bracket = JSON.parse(tax_bracket.bracket);
      }

      console.log(tax_bracket);
      
      await this.load();
      this.add(new Container([
        new Panel([ add, signatory, header , cal_tax, view_payroll, del ]),
        new Panel().html(title_txt),
        grid,
        new Panel(this.table).class(["table-responsive", "card"])
      ]));

      // header information
      header.addEventListener("click", async () => {
        const modal = new EditHeader(this.refid);
        await modal.show();
      });

      let time = null;
      this.search.addEventListener("keyup", () => {
        clearTimeout(time);
        time = setTimeout(async () => {
          await this.load();
        }, 500);
      });


      add.addEventListener("click", async () => {
        const modal = new PayrollEntryForm(this.refid);
        const res = await modal.show();
        if (res != null && res) {
          await this.load();
        }
      });

      this.qrscan.addEventListener("keyup", async (e) => {
        if (e.keyCode == 13) {
          // AppHttp("/api/hrms/dtr", { qrcode: data, refid: payroll_data.refid }, null, function (o) {
          //             var res = JSON.parse(o);
          //             //console.log(res);
          //             if (res.ok == 0 || res.ok == false) return loader.hide(res.msg, true);
          //             reload_table();
          //             loader.hide(res.msg);
          //         });
          //     };

          const data = this.qrscan.getValue();
          this.qrscan.setValue("");

          const loader = new Loader().show();
          const res = JSON.parse(await AppHttp2("/api/hrms/dtr", {
            qrcode: data, refid: this.refid
          }));
          loader.hide();

          if (res.ok) {
            await this.load();

            if (res.data.work <= 0) {
              const modal = new PayrollEntryForm(res.data.refid, res.data.emp_id);
              const r = await modal.show();
              if (r != null && r) {
                await this.load();
              }
            }
          } else {
            await Alert(`<div style="color: red">${res.msg}</div>`);
          }

        } 

      
      });

      view_payroll.addEventListener("click", async () => {
        console.log(payroll_info);
        x_storage.setItem('payroll_data', payroll_info);
        const p = new PayrollViewer({
          refid: this.refid,
          dept_id: '',
          show_all: true
        });

        const a = await p.show();
        if (a != null) {
          await this.load();
        }
      });

      del.addEventListener("click", async () => {
        if (!await Confirm("Delete Payroll?")) return;
        
        const res = JSON.parse(await AppHttp2("/payroll/remove", { refid: this.refid }));

        if (res.ok) {
          await Alert(res.msg);
          appHome.setContent(new TransactionMain());
        } else {
          await Alert(`<span style="color: red;">${res.msg}</span>`);
        }
      
      });

      cal_tax.addEventListener("click", async () => {
        
        await Alert(`<span style="color: red;">Warning: </span> <br> Recalculate tax is based on tax bracket system, 
          make sure to check the contributions, all contributions must be set first before doing this process!  

          here the current bracket: 
          
        `);

        if (!await Confirm("Recalculate the tax?")) return;


      });

    })();

  }

  async load() {
    const res = await Payroll.load(this.refid, this.dept_id.getValue(), this.search.getValue());

    if (!res.ok) return;

    const data = res.data;
    const data_len = data.length;
    this.table.clearBody();
    for (let i = 0; i < data_len; i++) {
      const edit = new Button("", "primary", "edit").style({ marginRight: "2px" });
      const trash = new Button("", "danger", "trash").style({ marginRight: "2px" });
      const tax_cal = new Button("TAX", "warning", "refresh");
      const item = data[i];
      console.log(item);

      edit.addEventListener("click", async () => {
        console.log();
        const modal = new PayrollEntryForm(this.refid, item.employee_no);
        const res = await modal.show();
        if (res != null && res) {
          await this.load();
        }
      });

      let tax = '';
      for (const ded of item.deduction) {

        if(ded.code.toLowerCase() == "tax") {
          tax = ded.value;
          break;
        }
      }

      const from = item["from"];
      const to = item["to"];

      console.log(item);


      let period = "";
      if (this.payroll_info["from"] == from && this.payroll_info["to"] == to) {

      } else {
        period = `<span style="color: green;font-weight: bold;">${from} - ${to}</span>`;
      }

      
      const tr = this.table.add([
        new Panel([ edit, trash, tax_cal ]).style({ width: "140px" }),
        new Panel().html(period),
        item.name.toUpperCase(),
        item.position,
        item.salary,
        item.no_work_day,
        item.gross,
        item.total_ded,
        `${tax}`,
        item.net,
        ``
      ]);

      trash.addEventListener("click", async () => {

        if (!await Confirm("Are you sure to remove?")) return;

        const res = JSON.parse(await AppHttp2("/payroll/remove/item", {
          refid: this.refid,
          emp_id: item.employee_no
        }));

        await Alert(res.msg);
        if (res.ok) {
          tr.delete();
        }
      });

      tax_cal.addEventListener("click", async () => {
        if (!await Confirm("Calculate Tax?")) return;
        const res = JSON.parse(await AppHttp2("/payroll/calculate/tax", {
          emp_id: item.employee_no,
          refid: this.refid
        }));
        

        if (res.ok) {
          await Alert(`
            <div>
              <span style="color: red; font-weight: bold; ">Warning!</span>: This Computation is under on testing!
            </div>
            <hr />
            <div>Suggested Tax!</div>
            <div style="font-weight: bold; font-size: 20pt;">Monthly Tax: <span style="color: red;">${res.data.tax}</span></div>
            <div style="font-weight: bold; font-size: 20pt;">Half Month Tax: <span style="color: orange;">${res.data.tax / 2}</span></div>
          `);
        }
      });
    }

  }
}


export default PayrollEntryMain;