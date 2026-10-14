import { Panel, Modal, Button, Table, ComboBox, TextBox, Grid, ModalV2, Iframe, MsgLoader } from "../plugin/mcontrol.js";
import { AppHttp } from "../plugin/app.js";
import { confirmBox, messageBox } from "../main.js";
import { AppHttp2 } from "../classes/lib.js";
import { FUND_CHARGES } from "../config.js";
import { StatusForm } from './../component/StatusForm.js';

function AdaSign(refid, dept_id) {

  var label = {
    "p": "Prefix: (MS or MR)",
    "f": "Firstname",
    "m": "Middlename",
    "l": "Lastname",
    "g": "Gender: m or f",
    "s": "Suffix, ex. CPA, MPA.. etc..",
    "lh": "ex: Branch Head, Development..."
  };

  var modal = new Modal("Bank Information");


  var content = new Panel();
  content.addClass("row");


  var left = new Panel();
  left.addClass("col-md-6");
  var right = new Panel();
  right.addClass("col-md-6");

  content.add(left);
  content.add(right);

  this.list_sign = [];

  var me = this;
  var rsubmit = new Button("Save", "primary", "save");
  rsubmit.addEventListener("click", function () {
    var len = me.list_sign.length;
    var sign_data = [];
    for (var i = 0; i < len; i++) {
      sign_data.push({
        name: me.list_sign[i].name.getValue(),
        pos: me.list_sign[i].pos.getValue()
      });
    }

    var head_info = me.head_info;
    var len = head_info.length;

    var head_data = {};

    for (var i = 0; i < len; i++) {
      head_data[head_info[i].key] = head_info[i].tf.getValue();
    }

    var all_data = {
      acc_no: acc_no.getValue(),
      refid: refid,
      head_info: head_data,
      sign_info: sign_data
    }

    AppHttp("/payroll/bank/update", all_data, null, function (o) {
      var data = JSON.parse(o);
      if (data.ok) {
        messageBox.show(data.msg);
      } else {
        alert(data.msg);
      }
    });

  });
  //left content

  // end left content


  // right content
  var plus_sign = new Button("Add Signatory", "success", "plus");
  right.add(plus_sign);
  plus_sign.addEventListener("click", function () {
    var index = me.list_sign.length;

    var data = createSign(me, index);
    me.list_sign.push({
      name: data.name,
      pos: data.pos,
      panel: data.panel
    });
    me.rcontent.add(data.panel);
  });

  this.lcontent = new Panel();

  var ltitle = new Panel();
  ltitle.control.innerHTML = "Branch Head Information: ";
  ltitle.control.style.fontWeight = "bold";
  ltitle.control.style.fontSize = "16pt";

  var acc_no = new TextBox("Bank Account No.", "text");

  this.lcontent.add(acc_no);
  this.lcontent.add(ltitle);

  this.rcontent = new Panel();

  left.add(this.lcontent);

  right.add(this.rcontent);
  right.add(rsubmit);
  // end right content


  modal.add(content);
  modal.show(); // show the modal sign list

  // storage for the list of inputs

  this.head_info = []; // storage of the head information

  function createSign(self, index, name_val, pos_val) {
    var name_val = name_val || "";
    var pos_val = pos_val || "";

    var panel = new Panel();
    var name = new TextBox("Name");
    var pos = new TextBox("Position");
    var remove = new Button("Remove", "danger", "trash");
    remove.control.style.marginTop = "2px";
    remove.control.setAttribute("index", index);

    remove.addEventListener("click", function (o) {
      var index = this.attributes.index.nodeValue;

      var p = self.list_sign[index];
      p.panel.hide();
      self.list_sign.splice(index, 1);

    });

    panel.add(name);
    panel.add(pos);
    panel.add(remove);
    panel.control.style.marginBottom = "20px";

    name.setValue(name_val);
    pos.setValue(pos_val);

    return {
      name: name,
      pos: pos,
      panel: panel
    }
  }

  function loadSign(self) {

    AppHttp("/ada/sign/list", { dept_id: dept_id, refid: refid }, null, function (o) {
      var fdata = JSON.parse(o);

      var branch = fdata.data.branch;
      var ada_sign = fdata.data.ada_sign;
      var head = branch["head"];

      acc_no.setValue(fdata.data.acc_no);
      //acc_no.setValue(branch.acc_no);

      for (var key in head) {
        var tf = new TextBox(label[key], "text");
        tf.setValue(head[key]);
        self.head_info.push({
          key: key,
          tf: tf
        });

        self.lcontent.add(tf);
      }


      for (var i = 0; i < ada_sign.length; i++) {
        // generate a text field here for the ada siggnatoryi
        // the key are the name and the pos
        //

        var sn = createSign(self, i, ada_sign[i].name, ada_sign[i].pos);

        self.list_sign.push({
          name: sn.name,
          pos: sn.pos,
          panel: sn.panel
        });

        self.rcontent.add(sn.panel);
      }
    });
  }

  loadSign(this);

  this.container = function () {
    return modal;
  };
}




export function AdaViewer(refid, dept_id) {
  const panel = new Panel();
  const modal = new Modal("Ada Viewer");
  panel.add(modal);

  const funds = FUND_CHARGES;


  const modal_content = new Panel();

  const print = new Button("Print", "success", "print");

  const fund = new ComboBox(null, 'Funds');

  // initialized the fund charges
  for (let item of funds) {
    fund.add(item.key, item.value);
  }

  const view_sign = new Button("View Bank Info", "success", "list");


  const menu_panel = new Panel().addClass('container-fluid');

  menu_panel.add(new Grid(2)
    .cell(fund, ['md-3'])
    // .cell(print, ['md-3'])
    .cell(view_sign, ['md-3']));


  print.addEventListener("click", async function () {

    const ok = await confirmBox.show_r('Print Ada & Generate ADA No.');
    if (ok == null) return;

    const o = await AppHttp2('/print/ada?print=1', {
      refid: refid,
      dept_id: dept_id,
      fund: fund.getValue()
    });

    const res = JSON.parse(o);
    const win = window.open();
    win.document.write(res.data);

  });

  var _sign_list = new Panel();

  view_sign.addEventListener("click", function () {
    var ada_sign = new AdaSign(refid, dept_id);
    _sign_list.clear();
    _sign_list.add(ada_sign.container());

  });

  modal.add(menu_panel);
  // modal.add(print);
  // modal.add(view_sign);

  modal.add(modal_content);
  modal.add(_sign_list);
  modal.show();

  this._panel = panel;
  this._content = modal_content;
  this._load = function (refid, dept_id, bank_list) {

    var me = this._content;
    me.control.innerHTML = "Loading...";

    AppHttp("/view/ada", {
      refid: refid,
      dept_id: dept_id,
      fund: fund.getValue()
    }, null, function (o) {
      me.clear();

      var fdata = JSON.parse(o);
      var data = fdata["data"];
      var data_len = data.length;

      var bank_list_len = bank_list.length;

      var table = new Table(["NAME", "REFFERENCE/ACCOUNT NUMBER", "amount"]);

      var bank = [];

      for (var i = 0; i < data_len; i++) {
        var acc = data[i]["acc"];
        var name = data[i]["name"];
        var net = data[i]["net"];

        var type = new ComboBox(null, "B.Code");
        bank.push(type);

        type.add("", "[Please Select Bank]");
        for (var j = 0; j < bank_list_len; j++) {
          type.add(bank_list[j][0], bank_list[j][1]);
        }

        if (acc != null) {
          type.setValue(data[i].acc_type);
        }

        var tf = new TextBox("Ref No.", "text", null, "Please press the enter key to save");
        tf.control.setAttribute("rel", i);

        var p = new Panel();
        p.add(type);
        p.add(tf);

        tf.addEventListener("keyup", function (e) {

          var index = this.attributes.rel.nodeValue;
          var value = this.value;
          var info = data[index];
          var emp_id = info.emp_id;

          var rdata = {
            account_number: value,
            bank_code: bank[index].getValue(),
            bank_index: index,
            emp_id: emp_id,
            refid: refid
          };

          if (e.keyCode == 13) {
            // AppHttp("/employee/bank/save", rdata, null, function(o) {
            //     var data = JSON.parse(o);
            //     console.log(data);
            // });

            AppHttp("/payroll/item/bank/update", rdata, null, function (o) {
              var data = JSON.parse(o);
              if (data.ok) {
                messageBox.show(data.msg);
              } else {
                alert(data.msg);
              }
            });
          }
        });

        tf.setValue(acc != null ? acc : "");

        table.add([
          name != null ? name : "",
          p,
          net != null ? net : ""
        ]);

      }

      me.add(table);
    });
  };

  this._load_bank = function (refid, dept_id) {
    // load bank here
    var me = this;
    AppHttp("/bank/list", {}, null, function (o) {
      var data = JSON.parse(o);
      me._load(refid, dept_id, data.data);
    });
  };

  this._load_bank(refid, dept_id); // load the data from the network

  this.container = function () {
    return panel;
  };
};



// Version 2 of the AdaViewer

class EditAdaSign extends ModalV2 {
  constructor(refid, dept_id) {
    super("Edit Ada Information", "edit");

    this.refid = refid;
    this.dept_id = dept_id;
    
    this.resolve = true;

    this.init();
  }
  init() {
    const label = {
      "p": "Prefix: (MS or MR)",
      "f": "Firstname",
      "m": "Middlename",
      "l": "Lastname",
      "g": "Gender: m or f",
      "s": "Suffix, ex. CPA, MPA.. etc..",
      "lh": "ex: Branch Head, Development..."
    };

    const grid = new Grid();
    // grid.cell();

    this.add(grid);


  }
}



class AdaUpdate extends ModalV2 {
  constructor(refid, fund) {
    super("Update Ada Number.", "pencil");

    this.refid = refid;
    this.fund = fund;
    
    const ada_no = new TextBox("Ada Number: ", "text");

    const submit = new Button("Submit", "primary").setStyle({
      marginTop: "5px"
    });

    submit.addEventListener("click", async () => {
      const payload = {
        refid: this.refid,
        fund: this.fund,
        ada_no: ada_no.getValue()
      };

      const res = JSON.parse(await AppHttp2("/ada/update/no", payload));
      if (res.ok) {
        this.resolve = true; 
      }
      messageBox.show(res.msg);
    });

    this.add(ada_no).add(submit);

    // anonymouse function to retrieve the ada number
    (async () => {

      const payload = {
        refid: this.refid,
        fund: this.fund
      };
      
      const loader = new MsgLoader("Retrieving ada number!");
      const res = JSON.parse(await AppHttp2("/ada/get_number", payload));
      loader.hide("Ada number retrieved!");
      ada_no.setValue(res.data);
    
    })();
  }
  

}

class AdaPrintView extends ModalV2 {
  constructor(refid, dept_id) {
    super("Ada Printing View", "print");
    
    this.refid = refid;
    this.dept_id = dept_id;
    this.panel = new Panel();

    this.modal = new Panel();
    

    const funds = FUND_CHARGES;
    const fund = new ComboBox(null, 'Funds').setStyle({
      marginBottom: "5px"
    });
    // this.fund = fund;
    // initialized the fund charges
    for (let item of funds) {
      fund.add(item.key, item.value);
    }

    fund.addEventListener("change", () => {
      this.init();
    });

    const grid = new Grid(3);
    grid.cell(fund, ["md-3"]);
    // grid.cell(new Button("Print", "success", "print").addEventListener("click", async () => {
    //   const ok = await confirmBox.show_r('Print Ada & Generate ADA No.');
    //   if (ok == null) return;
    //   // for now this is a printing in the future this will be a view
    //   const o = await AppHttp2('/print/ada?print=1', {
    //     refid: this.refid,
    //     dept_id: this.dept_id,
    //     fund: this.fund.getValue()
    //   });

    //   const res = JSON.parse(o);
    //   const win = window.open();
    //   win.document.write(res.data);
    //   setTimeout(() => {
    //     win.print();
    //   }, 500);

    // }), ["md-2"]);
    
    grid.cell(new Button("Print Excel", "success", "file-excel-o").addEventListener("click", async () => {
      const payload = { 
        refid: this.refid,
        dept_id: this.dept_id,
        fund: this.fund.getValue()
      };
      
      const res = JSON.parse(await AppHttp2("/print/ada/file/excel", payload));
      if (!res.ok) {
        alert(res.msg);
        return;
      }
      const data = res["data"];
      const file_name = res["file"];
    
      function s2ab(s) {
        var buf = new ArrayBuffer(s.length);
        var view = new Uint8Array(buf);
        for (var i=0; i!=s.length; ++i) view[i] = s.charCodeAt(i) & 0xFF;
        return buf;
      }

      var blob = new Blob([s2ab(atob(data))], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      
      // const href = URL.createObjectURL(blob);
      // location.href = href;
      var link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = file_name + ".xlsx";
      link.click();

    }), ["md-2"]);

    grid.cell(new Button('Download Payroll File(PRN & TXT)', 'success').addEventListener('click', async () => {

      const modal = new StatusForm({
        refid: this.refid,
        dept: this.dept_id,
        title: 'Check LogIn',
        type: 'check',
        fn: async (obj) => {
            const loader = new MsgLoader('Downloading PAYROLL FILE');
            const res = JSON.parse(await AppHttp2('/payroll/file/download', {
              refid: this.refid,
              fund: fund.getValue(),
              dept_id: this.dept_id
            }));

            loader.hide('Payroll File Downloaded!');

            const data = res["data"];
            const file_name = res["file"];
          
            function s2ab(s) {
              var buf = new ArrayBuffer(s.length);
              var view = new Uint8Array(buf);
              for (var i=0; i!=s.length; ++i) view[i] = s.charCodeAt(i) & 0xFF;
              return buf;
            }

            var blob = new Blob([s2ab(atob(data))], {
                type: 'application/zip'
            });
            
            // const href = URL.createObjectURL(blob);
            // location.href = href;
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = file_name + ".zip";
            link.click();
            obj.hide();
        }
      });

      modal.show();
      
    }), ['md-3']);

    grid.cell(new Button("Update Ada No.", "warning", "pencil").addEventListener("click", async () => {
      const update = new AdaUpdate(this.refid, fund.getValue());
      const res = await update.show();
      if (res == null) return;

      this.init(); // reload the printview

    }), ["md-2"]);

    // grid.cell(new Button("Edit Information", "primary", "edit").addEventListener("click", async () => {
    //   // const edit = new EditAdaSign(this.refid, this.dept_id);
    //   // const r = await edit.show();
    //   // if (r != null) {
    //   //   this.init();
    //   // }
    //   this.modal.clear();
    //   const ada = new AdaSign(this.refid, this.dept_id);
    //   this.modal.add(ada.container());
    //   ada.show();

    // }), ["md-2"]);

    this.fund = fund;

    this.add(new Panel().addClass("container-fluid").add(grid));

    this.add(this.panel);
    this.add(this.modal);
    this.init();
  }
  async init() {
    // const ok = await confirmBox.show_r('Print Ada & Generate ADA No.');
    // if (ok == null) return;
    
    // for now this is a printing in the future this will be a view
    const o = await AppHttp2('/print/ada?print=1', {
      refid: this.refid,
      dept_id: this.dept_id,
      fund: this.fund.getValue()
    });
    const data = JSON.parse(o);

    const frame = new Iframe().setStyle({
      width: "100%",
      height: "75vh"
    });
    frame.control.srcdoc = data.data;
    
    this.panel.clear();
    this.panel.add(frame);
  }
}

export class AdaViewer2 extends ModalV2 {
  constructor(refid, dept_id) {
    super("Ada Viewer", "list");
    this.refid = refid;
    this.dept_id = dept_id;

    const funds = FUND_CHARGES;
    const fund = new ComboBox(null, 'Funds');
    // this.fund = fund;

    // initialized the fund charges
    for (let item of funds) {
      fund.add(item.key, item.value);
    }

    const view = new Button("View Ada", "success", "print");
    view.addEventListener("click", () => {
      // const ok = await confirmBox.show_r('Print Ada & Generate ADA No.');
      // if (ok == null) return;
      // // for now this is a printing in the future this will be a view
      // const o = await AppHttp2('/print/ada?print=1', {
      //   refid: refid,
      //   dept_id: dept_id,
      //   fund: fund.getValue()
      // });

      // const res = JSON.parse(o);
      // const win = window.open();
      // win.document.write(res.data);

      const ada = new AdaPrintView(this.refid, this.dept_id);
      ada.show();
    });

    this.panel = new Panel();

    this.load();

    this.add(view);
    // this.add(fund);

    this.add(this.panel);

  }

  async load_bank() {
    // AppHttp("/bank/list", {}, null, function (o) {
    //   var data = JSON.parse(o);
    //   me._load(refid, dept_id, data.data);
    // });
    return await AppHttp2("/bank/list", {}, null);
  }

  async load() {
    const bank_list = JSON.parse(await this.load_bank()).data;
    const bank_len = bank_list.length;

    const res = JSON.parse(await AppHttp2("/view/ada", {
      refid: this.refid,
      dept_id: this.dept_id
    }, null));
    if (!res.ok) return;
    
    this.panel.clear();
    
    const data = res.data;
    const data_len = data.length;
    

    const table = new Table(["NAME", "REFFERENCE/ACCOUNT NUMBER", "amount"]);

    for (let i = 0; i < data_len; ++i) {
      const {acc, name, net, acc_type} = data[i];
      
      const type = new ComboBox(null, "B.Code");
      type.add("", "[Please Select Bank]");

      for (let j = 0; j < bank_len; j++) {
        type.add(bank_list[j][0], bank_list[j][1]);
      }


      if (acc_type != null) {
        type.setValue(acc_type);
      }

      // control for p
      const tf = new TextBox("Ref No.", "text", null, "Please press the enter key to save");
      // tf.control.setAttribute("rel", i);
      tf.addEventListener("keyup", async (e) => {
        const value = tf.getValue();
        const info = data[i];
        const emp_id = info.emp_id;

        const rdata = {
          account_number: value,
          bank_code: type.getValue(),
          // bank_index: i,
          emp_id: emp_id,
          refid: this.refid
        };

        if (e.keyCode == 13) {
          // AppHttp("/employee/bank/save", rdata, null, function(o) {
          //     var data = JSON.parse(o);
          //     console.log(data);
          // });

          const res = await AppHttp2("/payroll/item/bank/update", rdata, null);
          const data = JSON.parse(res);
          if (data.ok) {
            messageBox.show(data.msg);
          } else {
            alert(data.msg);
          }
          
        }
      });

      if (acc != null) {
        tf.setValue(acc);
      }

      const p = new Panel();
      p.add(type);
      p.add(tf);

      table.add([
        name != null ? name : "",
        p,
        net != null ? net : ""
      ]);



    }

    this.panel.add(table);
    
  }
}


export class CloseAda extends ModalV2 {
  constructor(refid) {
    super("Approve Ada", "close");
    
    this.refid = refid;

    const username = new TextBox("Username", "text");
    const password = new TextBox("Password", "password");
    const remark = new TextBox("Remark", "text");

    this.add(username).add(password).add(remark);
    this.add(new Button("Submit", "warning", "save").setStyle({
        marginTop: "5px"
    }).addEventListener("click", async () => {
        const payload = {
            username: username.getValue(),
            password: password.getValue(),
            remark: remark.getValue(),
            refid: this.refid
        };

        if (!await confirmBox.show_r("Are you sure?")) return;
        
        const loader = new MsgLoader("Approving ada requests");
        const res = JSON.parse(await AppHttp2("/ada/close", payload));
        loader.hide(res.msg);
        
        if (res.ok) {
            messageBox.show(res.msg);
        } else {
            messageBox.show(`<span style="color: red;">${res.msg}</span>`);
        }
    }));
  }

}