// import { AppHttp2 } from "../classes/lib.js";
// import { confirmBox, messageBox } from "../main.js";
// import { AppHttp } from "../plugin/app.js";
// import { DropDown, Grid, Label, ModalV2, Panel, Table, TextBox, Button, MsgLoader, ComboBox } from "../plugin/mcontrol.js";

// export class ContribLoan extends ModalV2 {
//   constructor(emp_id, status, fullname = "") {
//     super(`LOAN & CONTRIBUTION - ${fullname}`, "money");
//     this.emp_id = emp_id;
//     this.status = status;

//     this.setting = [];

//     this.load_settings();
//     this.panel = new Panel();
//     this.add(this.panel);


//     this.menu = new DropDown(`Menu`, "default", "Click to view items");
    
//     this.panel.add(this.menu);
    
//     this.content = new Panel().addClass("card");
//     this.header = new Panel().setStyle({marginBottom: "5px"});

//     this.panel.add(this.header);
//     this.panel.add(this.content);
//   }

//   async loadCardNo(code) {
//     // AppHttp2();
//   }
  
//   async loadDefaultDeduction(code, name) {
//     const loader = new MsgLoader("Loading Contrib List");
//     const data = JSON.parse(await AppHttp2("/default/contrib/load", {id: this.emp_id, code: code, name: name}))["data"];
//     loader.hide("Loaded!");
//     return data;
//   }

//   async reloadTable(table, code, name) {
//     const type = {
//       "1": "1st Half of the Month",
//       "2": "2nd Half of the Month",
//       "0": "If the Payroll is Whole Month"
//     };

//     table.clear();
//     const data = await this.loadDefaultDeduction(code, name);
//     const data_len = data.length;
//     for (let i = 0; i < data_len; ++i) {
//       const {code, name, value, type_ded, end_term, datecreated, emp_id} = data[i];
      
//       const action = new DropDown("Action", "warning", "click to show items");
//       action.addItem(`<i class="fa fa-close"></i> Remove`, async () => {
//         const payload = {code: code, name: name, datecreated: datecreated, emp_id: emp_id};

        
//       // const res = await AppHttp2("/default/contrib/remove", payload);
//         if (await confirmBox.show_r("Are you sure?") == null) return;
//         const res = JSON.parse(await AppHttp2("/default/contrib/remove", payload));
//         messageBox.show(res.msg);
//         if (res.ok) {
//           this.reloadTable(table, code, name);
//         }
//       });
      
//       table.add([
//         action,
//         code,
//         name,
//         value,
//         type[type_ded.toString()],
//         end_term == null ? "" : end_term
//       ]);
//     }
//   }

//   async load_settings() {
//     const res = JSON.parse(await AppHttp2(`/setting/deduction/list?status=${this.status}`));
//     if (!res.ok) return;
//     this.setting = res["data"];
//     const data_len = this.setting.length;
    
//     for (let i = 0; i < data_len; ++i) {
//       const {code, name} = this.setting[i];
//       this.menu.addItem(`${code} - ${name}`.toUpperCase(), async () => {
//         this.header.clear();
//         this.content.clear();
        
//         const label = new Label(`Title: <b>${code} ${name}</b>`);

//         const grid = new Grid(2);

//         const id = new TextBox(`${code} No.`, "text");

//         // load the default value of the id example gsis no. or sss no.
//         const idres = JSON.parse(await AppHttp2("/card/load", {emp_id: this.emp_id, code: code}));
//         id.setValue(idres.data);

//         grid.cell(id, ["md-9"]);
//         grid.cell(new Button("Update", "default", "refresh").setStyle({
//           height: "37px"
//         }).addEventListener("click", async () => {
//           const res = JSON.parse(await AppHttp2("/card/update", {
//             emp_id: this.emp_id, 
//             code: code,
//             value: id.getValue()
//           }));
//           messageBox.show(res.msg);

//         }), ["md-3"]);

//         const table = new Table(["Action", "Code", "Name", "Amount", "Paid On", "End Term"]);
//         this.reloadTable(table, code, name);
        
//         this.header.add(new Panel().add(grid).addClass("container"));
//         this.header.add(new Panel().add(label.setStyle({marginTop: "10px"})));

//         this.header.add(new Button("Add New", "success", "plus-circle").addEventListener("click", async () => {
//           const modal = new ContribModal(this.emp_id, code, name);
//           if(await modal.show() != null) {
//             this.reloadTable(table, code, name);
//           }
//         }));
        
//         this.content.add(table);
//       });
//     }

//   }
// }


// class ContribModal extends ModalV2 {
//   constructor(id, code, name) {
//     super(`New ${code} - ${name}`, "list");

//     this.id = id;
//     this.code = code;
//     this.name = name;

//     const value = new TextBox("Amount", "text");
//     const type = new ComboBox(null, "Pay every");
//     type.add("1", "First half of the month");
//     type.add("2", "Second half of the month");
//     type.add("0", "Whole month");
//     const term = new TextBox("EndTerm", "date");

//     this.add(value);
//     this.add(type);
//     this.add(term);
    
//     this.add(new Button("Submit", "text", "save").setStyle({
//       marginTop: "5px"
//     }).addEventListener("click", async () => {
      
//       const payload = {
//         code: this.code,
//         name: this.name,
//         emp_id: this.id,
//         value: value.getValue(),
//         type_ded: type.getValue(),
//         end_term: term.getValue()
//       };
//       const res = JSON.parse(await AppHttp2("/default/contrib/submit", payload));
//       if (!res.ok) {alert(res.msg); return};
//       messageBox.show(res.msg);
//       this.resolve = true;
//     }));
//   }

  



// }











import { AppHttp2 } from "../classes/lib.js";
import { confirmBox, messageBox } from "../main.js";
import { AppHttp, Config } from "../plugin/app.js";
import { DropDown, Grid, Label, ModalV2, Panel, Table, TextBox, Button, MsgLoader, ComboBox, BasicTab, DropdownTab } from "../plugin/mcontrol.js";
import { Alert, Confirm } from "../util/dialog.js";



class ContribLoan extends ModalV2 {
  constructor(emp_id, status, fullname = "") {
    super(`LOAN & CONTRIBUTION - ${fullname}`, "money");

    this.mwidth(20);

    this.emp_id = emp_id;
    this.status = status;

    

    this.tab = new DropdownTab();


    (async () => {
      this.loadTab();
    })();
    
    this.add([
      this.tab
    ]);
  }

  async loadTab() {
    const res = JSON.parse(await AppHttp2(`/setting/deduction/list?status=${this.status}`));
    if (!res.ok) return;
    const data = res.data;
    const data_len = data.length;
    
    const key = {};

    for (let i = 0; i < data_len; ++i) {
      const {code, name} = data[i];
      
      if (!(code in key)) {
        key[code] = [name];
      } else {
        key[code].push(name);
      }
    }

    for (const item in key) {
      const narr = [];
      const arr = key[item];
      const arr_len = arr.length;
      for (let i = 0; i < arr_len; i++) {
        narr.push([arr[i], async (o) => { 
          const code = item;
          const name = arr[i]; 

          // here the dynamic tab content

          o.add(await this.loadContent(code, name));
        }]);
      }

      this.tab.add(item, narr);
    }

  }

  async loadContent(code, name) {

    // const default_data = await this.loadDefaultDeduction(code, name);
    const idres = JSON.parse(await AppHttp2("/card/load", {emp_id: this.emp_id, code: code}));

    const panel = new Panel().style({
      marginTop: "10px"
    });
    const card = new TextBox(`${code} No. (Autosave)`, "text");
    card.setValue(idres.data);
    
    let time = null;
    card.addEventListener("keyup", () => {
      if (time != null) clearTimeout(time);
      // autosave when type

      time = setTimeout(async () => {
        const res = JSON.parse(await AppHttp2("/card/update", {
          emp_id: this.emp_id, 
          code: code,
          value: card.getValue()
        }));

        if (!res.ok) {
          await Alert(res.msg);
        }
      }, 500);
    });



    const table = new Table(["Action", "Code", "Name", "Amount", "Paid On", "End Term"]);
    this.reloadTable(table, code, name);
    const add = new Button("Add", "success", "plus-circle").setStyle({
      marginTop: "5px"
    });

    add.addEventListener("click", async () => {
      const modal = new ContribModal(this.emp_id, code, name);

      const res = await modal.show();

      if (res != null && res) {
        this.reloadTable(table, code, name);
      }
    });

    panel.add(card);
    panel.add(add);
    panel.add(table.setStyle({
      marginTop: "10px"
    }));

    return panel;
  }
  
  async loadDefaultDeduction(code, name) {
    const loader = new MsgLoader("Loading Contrib List");
    const data = JSON.parse(await AppHttp2("/default/contrib/load", {id: this.emp_id, code: code, name: name}))["data"];
    loader.hide("Loaded!");
    return data;
  }

  async reloadTable(table, code, name) {
    const type = {
      "1": "1st Half of the Month",
      "2": "2nd Half of the Month",
      "0": "If the Payroll is Whole Month"
    };

    table.clear();
    const data = await this.loadDefaultDeduction(code, name);
    const data_len = data.length;
    for (let i = 0; i < data_len; ++i) {
      const {code, name, value, type_ded, end_term, datecreated, emp_id} = data[i];
      
      const action = new DropDown("Action", "warning", "click to show items");
      action.addItem(`<i class="fa fa-close"></i> Remove`, async () => {
        const payload = {code: code, name: name, datecreated: datecreated, emp_id: emp_id};

        
      // const res = await AppHttp2("/default/contrib/remove", payload);
        if (!await Confirm("Are you sure?")) return;
        const res = JSON.parse(await AppHttp2("/default/contrib/remove", payload));
        await Alert(res.msg);
        if (res.ok) {
          this.reloadTable(table, code, name);
        }

      });
      
      table.add([
        action,
        code,
        name,
        value,
        type[type_ded.toString()],
        end_term == null ? "" : end_term
      ]);
    }
  }

  async load_settings() {
    const res = JSON.parse(await AppHttp2(`/setting/deduction/list?status=${this.status}`));
    if (!res.ok) return;
    this.setting = res["data"];
    const data_len = this.setting.length;
    
    for (let i = 0; i < data_len; ++i) {
      const {code, name} = this.setting[i];
      this.menu.addItem(`${code} - ${name}`.toUpperCase(), async () => {
        this.header.clear();
        this.content.clear();
        
        const label = new Label(`Title: <b>${code} ${name}</b>`);

        const grid = new Grid(2);

        const id = new TextBox(`${code} No.`, "text");

        // load the default value of the id example gsis no. or sss no.
        const idres = JSON.parse(await AppHttp2("/card/load", {emp_id: this.emp_id, code: code}));
        id.setValue(idres.data);

        grid.cell(id, ["md-9"]);
        grid.cell(new Button("Update", "default", "refresh").setStyle({
          height: "37px"
        }).addEventListener("click", async () => {
          const res = JSON.parse(await AppHttp2("/card/update", {
            emp_id: this.emp_id, 
            code: code,
            value: id.getValue()
          }));
          messageBox.show(res.msg);

        }), ["md-3"]);

        const table = new Table(["Action", "Code", "Name", "Amount", "Paid On", "End Term"]);
        this.reloadTable(table, code, name);
        
        this.header.add(new Panel().add(grid).addClass("container"));
        this.header.add(new Panel().add(label.setStyle({marginTop: "10px"})));

        this.header.add(new Button("Add New", "success", "plus-circle").addEventListener("click", async () => {
          const modal = new ContribModal(this.emp_id, code, name);
          if(await modal.show() != null) {
            this.reloadTable(table, code, name);
          }
        }));
        
        this.content.add(table);
      });
    }

  }
}


class ContribModal extends ModalV2 {
  constructor(id, code, name) {
    super(`New ${code} - ${name}`, "list");

    this.id = id;
    this.code = code;
    this.name = name;

    const value = new TextBox("Amount", "text");
    const type = new ComboBox(null, "Pay every");
    type.add("1", "First half of the month");
    type.add("2", "Second half of the month");
    type.add("0", "Whole month");
    const term = new TextBox("EndTerm", "date");

    this.add(value);
    this.add(type);
    this.add(term);
    
    this.add(new Button("Submit", "text", "save").setStyle({
      marginTop: "5px"
    }).addEventListener("click", async () => {
      
      const payload = {
        code: this.code,
        name: this.name,
        emp_id: this.id,
        value: value.getValue(),
        type_ded: type.getValue(),
        end_term: term.getValue()
      };
      const res = JSON.parse(await AppHttp2("/default/contrib/submit", payload));
      if (!res.ok) {alert(res.msg); return};
      await Alert(res.msg);
      this.hide(res.ok);
    }));
  }

  



}


export {
  ContribLoan
}