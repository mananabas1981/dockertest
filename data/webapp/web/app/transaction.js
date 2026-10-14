import { Panel, Label, Button, TextBox, Table, Modal, Form, ComboBox, LoaderBox, Grid, DropDown } from "./plugin/mcontrol.js";
import { AppHttp } from "./plugin/app.js";
import { messageBox, confirmBox, loaderBox } from "./main.js";
import { PayrollPage } from "./transaction/payroll.js";
import { UpdateView } from "./transaction/update.js";
import { ActiveModal } from "./transaction/active.js";
import { ContribLoan } from "./component/ContribLoan.js";
import { ExcelContribModal } from './component/ExcelContrib.js';
import { RecentTransaction } from './component/recent_transaction.js';
import DTRReceiver from './transaction/DTRReceiver.js';
import HtmlConLoan from "./component/HtmlConLoan.js";

import { appHome } from "./main.js";
import Employee from "./transaction/employee.js";

export function search_employee(param = {}, fun) {
  //param is a dict
  let search = param["search"] || "";
  let dept_id = param["dept_id"] || ""
  let emp_status = param["emp_status"] || "";
  const active = param['active'] || '';

  AppHttp('/client/list', { search: search, dept_id: dept_id, emp_status: emp_status, active: active }, null, function (o) {
    fun(JSON.parse(o));
  });
}

// export function TransactionView(appHome) {

//   // functions
//   // end of the transactions
//   // search employee

//   // function for searching the employee


//   // employee viewer
//   var employee_viewer = function () {
//     var modal = new Modal("Employee Information");

//     var form = new Form();

//     // create field for the form
//     var ids = new TextBox("refid", "text", null);
//     ids.control.setAttribute("readonly", "");
//     var pref_name = new TextBox("Prefix", "text", null);
//     var fname = new TextBox("Firstname", "text", null);
//     var mname = new TextBox("Middlename", "text", null);
//     var lname = new TextBox("Lastname", "text", null);
//     var ename = new TextBox("Ex. name", "text", null);
//     var sufname = new TextBox("Suffix", "text", null);
//     var dob = new TextBox("Birth", "date", null);
//     var gender = new ComboBox([
//       ["", ""],
//       ["m", "Male"],
//       ["f", "Female"]
//     ], "Gender", null, null);
//     var address = new TextBox("Address", "text", null);

//     var hr_id = new TextBox("HR System employee Id", "text", null);

//     var submit = new Button("Save", "success", "plus-circle");
//     submit.control.style.marginTop = "5px";

//     var remove = new Button("Remove", "danger", "trash");
//     remove.control.style.marginTop = "5px";
//     remove.control.style.marginLeft = "5px";
//     remove.addEventListener("click", function () {
//       var id = form.input.id.getValue();
//       confirmBox.show("Are you sure?", function () {
//         AppHttp("/employee/remove", { id: id }, null, function (o) {
//           var data = JSON.parse(o);
//           if (data.ok == 1) {
//             messageBox.show(data.msg, function () {
//               modal.hide();
//             });
//             reload_table();
//           } else {
//             messageBox.show(data.msg);
//           }
//         });
//       });
//     });

//     submit.addEventListener("click", function () {
//       var data = form.getValues();
//       AppHttp("/client/save", data, null, function (o) {
//         var rdata = JSON.parse(o);
//         messageBox.show(rdata.msg, function () {
//           modal.hide();
//           reload_table();
//         });
//       });
//     });
//     // end create field for form
//     form.add(ids, "id");
//     form.add(pref_name, "pref_name");
//     form.add(fname, "fname");
//     form.add(mname, "mname");
//     form.add(lname, "lname");
//     form.add(ename, "ename");
//     form.add(sufname, "suf_name");
//     form.add(gender, "gender");
//     form.add(dob, "dob");
//     form.add(address, "addr");
//     form.add(hr_id, "hr_id");
//     form.add(submit);
//     form.add(remove);

//     modal.add(form);
//     return {
//       modal: modal,
//       form: form
//     };
//   };

//   const GLOBAL_DATA = {};

//   // Status of the employee information
//   const STATUS = {
//     j: "Job Order",
//     r: "Regular",
//     c: "Contract Of Service"
//   };


//   const emp_info = function () {
//     var modal = new Modal("Employee Information");
//     var name = new Panel();
//     name.control.style.fontWeight = "bold";
//     name.control.style.fontSize = "12pt";
//     name.control.innerHTML = "";


//     var rate_info = new Button("Rate Info", "success");
//     var position_info = new Button("Position Info", "success");
//     position_info.control.style.marginLeft = "2px";
//     var dept_info = new Button("Department Info", "success");
//     dept_info.control.style.marginLeft = "2px";

//     var bank_account = new Button("Bank Account", "success", null, "Click to add bank information");
//     bank_account.control.style.marginLeft = "2px";

//     var content = new Panel();
//     content.addClass("card");
//     content.control.style.marginTop = "5px";


//     var rate_content = new Panel();
//     rate_content.control.style.padding = "5px";

//     var rate_table = new Table(["Date", "Rate", "Type", 'NWPD', "Action"]);

//     var reload_rate_table = function () {
//       AppHttp("/employee/rate/list", { emp_id: GLOBAL_DATA["emp_id"] }, null, function (o) {
//         var fdata = JSON.parse(o);
//         var data = fdata.data;
//         var data_len = data.length;
//         rate_table.clear();
//         for (let i = 0; i < data_len; i++) {
//           var remove = new Button(null, "danger", "trash", "Please click to remove the rate!");
//           remove.addEventListener("click", function () {
//             const index = i;
//             const emp_id = GLOBAL_DATA["emp_id"];
//             const odata = data[index];

//             const date = odata[2];
//             const rdata = {
//               "date": date,
//               "emp_id": emp_id
//             };

//             confirmBox.show("Are you sure?", function () {
//               AppHttp("/employee/rate/remove", rdata, null, function (o) {
//                 var data = JSON.parse(o);
//                 if (data.ok == 1) {
//                   messageBox.show(data.msg, function () {
//                     reload_rate_table();
//                     reload_table_v2();
//                   });
//                 } else {
//                   messageBox.show(data.msg);
//                 }
//               });
//             });
//           });
          
//           const no_type = data[i][3] != null ? data[i][3] : '';
//           rate_table.add([
//             data[i][2], data[i][0], data[i][1] == "m" ? "Monthly" : "Daily", no_type, remove
//           ]);
//         }
//       });
//     };


//     rate_info.addEventListener("click", function () {
//       content.clear();
//       rate_content.clear();
//       // rate contents goes here
//       var title = new Panel();
//       title.control.innerHTML = "Rate Information";
//       title.control.style.fontWeight = "bolder";
//       rate_content.add(title);


//       var form = new Form();
//       var rate = new TextBox("Rate", "text");
//       var rate_type = new ComboBox([
//         ["d", "Daily"],
//         ["m", "Monthly"]
//       ], "Rate Type");
//       var submit = new Button("Save", "success", "save");
//       submit.control.style.marginTop = "5px";
//       submit.addEventListener("click", function () {
//         var data = form.getValues();

//         data.rate = data.rate.replace(",", "").replace(" ", "").trim();
//         if (!/^[0-9\.]+$/.test(data.rate)) {
//           alert("Invalid Rate");
//           return;
//         }

//         var rate = parseFloat(data.rate);
//         var rate_type = data.rate_type;
//         if (rate_type == "d") {
//           if (rate >= 800) {
//             if (!confirm(rate + " is perday?")) {
//               return;
//             }
//           }
//           if (rate <= 50) {
//             if (!confirm(rate + " is perday?")) {
//               return;
//             }
//           }
//         }

//         AppHttp("/employee/rate/save", { emp_id: GLOBAL_DATA["emp_id"], rate: rate, rate_type: rate_type }, null, function (o) {
//           var data = JSON.parse(o);
//           if (data.ok == 1) {
//             messageBox.show(data.msg, function () {
//               reload_rate_table();
//               reload_table_v2();
//             });
//             // reload the table
//           } else {
//             messageBox.show(data.msg);
//           }
//         });
//       });

//       form.add(rate, "rate");
//       form.add(rate_type, "rate_type");
//       form.add(submit);
//       rate_content.add(form);

//       rate_content.add(rate_table);
//       content.add(rate_content);

//       reload_rate_table();
//     });

//     var tbl_pos = new Table(["Date", "Title", "Status", "Action"]);
//     // reload the position of employee
//     var reload_tbl_pos = function () {
//       tbl_pos.clear();
//       AppHttp("/employee/position/list", { emp_id: GLOBAL_DATA["emp_id"] }, null, function (o) {
//         var fdata = JSON.parse(o);
//         var data = fdata.data;
//         var data_len = data.length;

//         for (var i = 0; i < data_len; i++) {
//           var title = data[i][0];
//           var date = data[i][1];
//           var status = data[i][2];
//           var remove = new Button(null, "danger", "trash");

//           remove.control.setAttribute("rel", i);

//           remove.addEventListener("click", function () {
//             var index = this.attributes.rel.nodeValue;
//             var _data = data[index];
//             var rdata = {
//               emp_id: GLOBAL_DATA["emp_id"],
//               date: _data[1]
//             };

//             confirmBox.show("Are you sure?", function () {
//               AppHttp("/employee/position/remove", rdata, null, function (o) {
//                 var data = JSON.parse(o);
//                 if (data.ok == 1) {
//                   messageBox.show(data.msg, function () {
//                     reload_tbl_pos();
//                     reload_table_v2();
//                   });
//                 } else {
//                   messageBox.show(data.msg);
//                 }
//               });
//             });
//           });

//           tbl_pos.add([date, title, STATUS[status], remove]);
//         }
//       });
//     };

//     position_info.addEventListener("click", function () {
//       content.clear();
//       var pos_content = new Panel();
//       pos_content.addClass("card");
//       pos_content.control.style.padding = "5px";
//       content.add(pos_content);

//       var form = new Form();
//       var title = new TextBox("Position", "text", null);
//       var status = new ComboBox(null, "Status", null);
//       status.add("j", "Job Order");
//       status.add("c", "Contract Of Service");
//       status.add("r", "Regular Employee");
//       var submit = new Button("Save", "success", "save");
//       submit.control.style.marginTop = "5px";
//       submit.addEventListener("click", function () {
//         var data = form.getValues();
//         data["emp_id"] = GLOBAL_DATA["emp_id"];
//         AppHttp("/employee/position/save", data, null, function (o) {
//           var data = JSON.parse(o);
//           if (data.ok == 1) {
//             messageBox.show(data.msg, function () {
//               reload_tbl_pos();
//               reload_table_v2();
//             });
//           } else {
//             messageBox.show(data.msg);
//           }
//         });
//       });

//       form.add(title, "title");
//       form.add(status, "status");
//       form.add(submit);

//       reload_tbl_pos();

//       pos_content.add(form);
//       pos_content.add(tbl_pos);
//     });

//     var tbl = new Table(["Date", "Title", "Action"]);
//     // for loading the department history

//     var reload_dept_history = function () {
//       tbl.clear();
//       AppHttp("/employee/dept/list", { emp_id: GLOBAL_DATA["emp_id"] }, null, function (o) {
//         var fdata = JSON.parse(o);
//         var data = fdata.data;
//         var data_len = data.length;
//         for (var i = 0; i < data_len; i++) {
//           var date = data[i][3];
//           var title = data[i][2];
//           var remove = new Button(null, "danger", "trash");
//           remove.control.setAttribute("rel", i);
//           tbl.add([date, title, remove]);
//           remove.addEventListener("click", function () {
//             var index = this.attributes.rel.nodeValue;
//             var data1 = data[index];
//             var emp_id = GLOBAL_DATA["emp_id"];
//             var dept_id = data1[1];
//             var date = data1[3];

//             var rdata = {
//               "emp_id": emp_id,
//               "dept_id": dept_id,
//               "date": date
//             };

//             confirmBox.show("Are you sure?", function () {
//               AppHttp("/employee/dept/remove", rdata, null, function (o) {
//                 var data = JSON.parse(o);
//                 if (data.ok == 1) {
//                   messageBox.show(data.msg, function () {
//                     reload_dept_history();
//                     reload_table_v2();
//                   });
//                 } else {
//                   messageBox.show(data.msg);
//                 }
//               });
//             });

//           });

//         }
//       });
//     };

//     dept_info.addEventListener("click", function () {
//       var dept_panel = new Panel();
//       dept_panel.addClass("card");
//       dept_panel.control.style.padding = "5px";
//       content.clear();
//       content.add(dept_panel);
//       // load department
//       var dept_input = new ComboBox(null, "Department", null, null, null, null);
//       dept_input.add("", "[ Select Department ]")
//       AppHttp("/department/list", {}, null, function (o) {
//         var fdata = JSON.parse(o);
//         var data = fdata.data;
//         var data_len = data.length;
//         for (var i = 0; i < data_len; i++) {
//           var name = data[i][2];
//           var id = data[i][0];
//           dept_input.add(id, name);
//         }
//       });
//       dept_panel.add(dept_input);
//       var submit = new Button("Save", "success", "save", "click to save the employee department");
//       submit.control.style.marginTop = "5px";
//       submit.addEventListener("click", function () {
//         AppHttp("/employee/dept/save", { emp_id: GLOBAL_DATA["emp_id"], dept_id: dept_input.getValue() }, null, function (o) {
//           var data = JSON.parse(o);
//           if (data.ok == 1) {
//             messageBox.show(data.msg, function () {
//               reload_dept_history();
//               reload_table_v2();
//             });
//           } else {
//             messageBox.show(data.msg);
//           }
//         });
//       });

//       dept_panel.add(submit);

//       // load the dept_list
//       reload_dept_history();
//       dept_panel.add(tbl);
//     });



//     // function of bank_account

//     var bank_table = new Table(["Date", "Bank", "Account Number", "Action"]);
//     var bank_data = [];

//     var load_bank = function () {
//       AppHttp("/employee/bank/list", { emp_id: GLOBAL_DATA["emp_id"] }, null, function (o) {
//         var res = JSON.parse(o);
//         var data = res.data;
//         var data_len = data.length;
//         bank_table.clear();
//         for (var i = 0; i < data_len; i++) {
//           var date = data[i][2];
//           var code = data[i][0];
//           var account = data[i][1];
//           var remove = new Button(null, "danger", "trash");
//           remove.control.setAttribute("rel", i);
//           remove.addEventListener("click", function () {
//             var index = this.attributes.rel.nodeValue;
//             var data_index = data[index];
//             var code = data_index[0];
//             var account_number = data_index[1];

//             var rdata = {
//               code: code,
//               account_number: account_number,
//               emp_id: GLOBAL_DATA["emp_id"]
//             };

//             confirmBox.show("Remove?", function () {
//               AppHttp("/employee/bank/remove", rdata, null, function (o) {
//                 var data = JSON.parse(o);
//                 if (data.ok == 1) {
//                   messageBox.show(data.msg, function () {
//                     load_bank();
//                     reload_table_v2();
//                   });
//                 } else {
//                   messageBox.show(data.msg);
//                 }
//               });
//             });

//           });
//           bank_table.add([date, code, account, remove]);
//         }
//       });
//     };

//     var BankModal = function () {
//       var modal = new Modal("Bank Information");
//       var form = new Form();

//       var type = new ComboBox(null, "Bank In.");
//       // type.add("dbp", "DBP Account");
//       var loadBank = function () {
//         AppHttp("/bank/list", {}, null, function (o) {
//           var dataf = JSON.parse(o);
//           var data = dataf.data;
//           bank_data = data;
//           var data_len = data.length;
//           for (var i = 0; i < data_len; i++) {
//             type.add(i, data[i][1]);
//           }
//         });

//       };
//       loadBank();

//       form.add(type, "bank_index");



//       var submit = new Button("Submit", "success", "plus-circle", "Click to add bank account!");
//       submit.control.style.marginTop = "2px";

//       function is_valid() {
//         var v = account_number.getValue();

//         var index = type.getValue();
//         var _regex = bank_data[index][2];
//         var pattern = new RegExp(_regex);

//         var is_ok = pattern.test(v);
//         if (!is_ok) {
//           account_number.control.style.border = "1px solid red";
//         } else {
//           account_number.control.style.border = "1px solid white";
//         }
//         return is_ok;
//       }

//       type.addEventListener("change", function () {
//         is_valid();
//       });


//       var account_number = new TextBox("Account", "text", null);
//       account_number.addEventListener("keyup", function () {
//         is_valid();
//       });

//       form.add(account_number, "account_number");
//       form.add(submit);

//       submit.addEventListener("click", function () {
//         var data = bank_form.getValues();
//         var emp_id = GLOBAL_DATA.emp_id;
//         data["emp_id"] = emp_id;
//         data["bank_code"] = bank_data[data["bank_index"]][0];

//         if (!is_valid()) {
//           messageBox.show("Invalid Bank Account!");
//           return;
//         }
//         // proceed to the add bank account

//         AppHttp("/employee/bank/save", data, null, function (o) {
//           var data = JSON.parse(o);
//           if (data.ok == 1) {
//             messageBox.show(data.msg, function () {
//               // reload the table and close the modal or forms
//               modal.hide();
//               load_bank();
//               reload_table_v2();
//             });
//           } else {
//             messageBox.show(data.msg);
//           }
//         });
//       });
//       modal.add(form);
//       return {
//         getModal: function () {
//           return modal;
//         },
//         getForm: function () {
//           return form;
//         },
//         getSubmitButton: function () {
//           return submit;
//         }
//       }
//     };

//     var bank_obj = BankModal();
//     var bank_form = bank_obj.getForm();
//     var bank_modal = bank_obj.getModal();
//     var bank_submit_form = bank_obj.getSubmitButton();


//     bank_account.addEventListener("click", function () {
//       var bank_panel = new Panel();
//       bank_panel.addClass("card");
//       bank_panel.control.style.padding = "5px";
//       content.clear();
//       content.add(bank_panel);

//       var newAccount = new Button("New Account", "primary", "plus-circle");
//       newAccount.addEventListener("click", function () {
//         bank_modal.show();
//       });

//       load_bank();

//       bank_panel.add(newAccount);
//       bank_panel.add(bank_table);
//       bank_panel.add(bank_modal);
//     });

//     // end function of bank_account

//     modal.add(name);
//     modal.add(rate_info);
//     modal.add(position_info);
//     modal.add(dept_info);
//     modal.add(bank_account);
//     modal.add(content);
//     return {
//       modal: modal,
//       name: name
//     };
//   };

//   var e_info = null;
//   var emp_info_modal = null;
//   var emp_form = null; // form global
//   var emp_modal = null;
//   var table = null;
//   const reload_table = function (param) {
//     // @ param is an dict
//     var param = param || {}; // default value
//     var search = param["search"] || "";
//     var dept_id = param["dept_id"] || "";
//     var emp_status = param["emp_status"] || "";
//     const active = param['active'] || '';

//     search_employee({
//       "search": search,
//       "dept_id": dept_id,
//       "emp_status": emp_status,
//       'active': active
//     }, function (o) {
//       table.clear();
//       var total = o["data"]["total"];
//       var data = o["data"]["data"];
//       var data_len = data.length;
//       card_emp_total.control.innerHTML = "Total: " + total + " Results   |  Max Display: 200 data";
//       for (let i = 0; i < data_len; i++) {
//         let error = data[i]["error"];
//         let pos_info = data[i]["pos_info"];
//         let view = new Button(null, "success", "user").setStyle({ width: '40px' });
//         view.control.setAttribute("rel", i);
//         view.addEventListener("click", function () {
//           const index = this.attributes.rel.nodeValue;
//           const fdata = data[index];
//           /// open the modal
//           // console.log(emp_form.getValues());
//           var input = emp_form.input;
//           input.pref_name.setValue(fdata.pref_name);
//           input.fname.setValue(fdata.fname);
//           input.mname.setValue(fdata.mname);
//           input.lname.setValue(fdata.lname);
//           input.ename.setValue(fdata.ename);
//           input.gender.setValue(fdata.gender);
//           input.dob.setValue(fdata.dob);
//           input.suf_name.setValue(fdata.suf_name);
//           input.addr.setValue(fdata.address);
//           input.id.setValue(fdata.id);
//           input.hr_id.setValue(fdata.hr_id);
//           emp_modal.show();
//         });

//         var update = new Button(null, "primary", "edit").setStyle({ width: '40px' });
//         update.control.setAttribute("rel", i);
//         update.addEventListener("click", function () {
//           var index = this.attributes.rel.nodeValue;
//           var emp_data = data[index];
//           emp_info_modal.show();
//           e_info.name.control.innerHTML = (emp_data.lname + ", " + emp_data.fname).toUpperCase();
//           GLOBAL_DATA["emp_id"] = emp_data.id;
//         });

//         var err_panel = new Panel();

//         for (var k = 0; k < error.length; k++) {
//           var p1 = new Panel();
//           if (error[k].error) {
//             p1.control.innerHTML = '<span style="color: black; text-decoration: underline;"><i class="fa fa-close" style="color: red;"></i> ' + error[k].msg + '</span>';
//           } else {
//             p1.control.innerHTML = '<span style="color: black; text-decoration: underline;"><i class="fa fa-check" style="color: green;"></i> ' + error[k].msg + '</span>';
//           }
//           err_panel.add(p1);
//         }

//         var _p = new Panel();
//         var pos_panel = new Panel();
//         _p.control.innerHTML = 'Created: ' + data[i].created + " ago";

//         pos_panel.add(_p);

//         for (var m = 0; m < pos_info.length; m++) {
//           var _p = new Panel();
//           _p.control.innerHTML = pos_info[m].key + " : " + pos_info[m].value;
//           pos_panel.add(_p);
//         }

//         var panel = new Panel().addClass('container-fluid').setStyle({ width: '180px' });

//         var profile = new Panel();
//         profile.control.style.width = "50px";
//         profile.control.style.height = "50px";
//         profile.control.style.borderRadius = "50%";
//         profile.control.style.border = "1px solid #ddd";

//         const active = new Button(null, 'default', 'cog').setStyle({ width: '40px' });


//         // panel.add(view);
//         // panel.add(update);
//         // panel.add(active);

//         // const action = new Grid(2);
//         // action.cell(view, ['md-3', 'sm-3', 'xs-3']);
//         // action.cell(update, ['md-3', 'sm-3', 'xs-3']);
//         // action.cell(active, ['md-3', 'sm-3', 'xs-3']);
        
//         const menu = new DropDown(`ACTION`);
//         menu.addItem(`<i class="fa fa-edit"></i> Edit Employee`, () => {
//           const fdata = data[i];
//           /// open the modal
//           // console.log(emp_form.getValues());
//           var input = emp_form.input;
//           input.pref_name.setValue(fdata.pref_name);
//           input.fname.setValue(fdata.fname);
//           input.mname.setValue(fdata.mname);
//           input.lname.setValue(fdata.lname);
//           input.ename.setValue(fdata.ename);
//           input.gender.setValue(fdata.gender);
//           input.dob.setValue(fdata.dob);
//           input.suf_name.setValue(fdata.suf_name);
//           input.addr.setValue(fdata.address);
//           input.id.setValue(fdata.id);
//           input.hr_id.setValue(fdata.hr_id);
//           emp_modal.show();
//         });

//         menu.addItem(`<i class="fa fa-pencil"></i> Update Rate, Position, Department etc...`, () => {
//           const emp_data = data[i];
//           emp_info_modal.show();
//           e_info.name.control.innerHTML = (emp_data.lname + ", " + emp_data.fname).toUpperCase();
//           GLOBAL_DATA["emp_id"] = emp_data.id;
//         });


//         menu.addItem(`<i class="fa fa-money"></i> Update loan & Contribution`, () => {
//           const { id, fname, lname, mname, ename, pref_name, suf_name, pos_status } = data[i];
//           const cl = new ContribLoan(id, pos_status, `${pref_name} ${fname} ${mname} ${lname} ${ename} ${suf_name}`.toUpperCase());
//           cl.show();
//         });

//         menu.addItem(`<i class="fa fa-flag"></i> Activation or Deactivation`, async () => {
//           const info = data[i];
//           const ac = new ActiveModal(info.id, `${info.pref_name} ${info.fname} ${info.mname} ${info.lname} ${info.suf_name}`.toUpperCase(), info.active);
//           const res = await ac.show();
//         });

//         panel.add(menu);

//         active.addEventListener('click', async () => {
//           const info = data[i];
//           const ac = new ActiveModal(info.id, `${info.pref_name} ${info.fname} ${info.mname} ${info.lname} ${info.suf_name}`.toUpperCase(), info.active);
//           const res = await ac.show();
//         });


//         const claim =  data[i]["claim"];
//         let last_refid = '';
//         if (claim) {
//           last_refid = claim[2]
//         }

//         table.add([
//           panel,
//           profile,
//           (data[i].lname + ", " + data[i]["fname"] + " " + data[i].mname).toUpperCase(),
//           pos_panel,
//           err_panel,
//           new Panel().add(new Label(data[i].active == 'y' ? 'YES' : 'NO')).setStyle({ color: (data[i].active == 'y' ? 'green' : 'red'), padding: '2px' }),
//           new Label(`${last_refid}`)
//         ]);
//       }
//     });
//   };

//   // textfield
//   var search = null; // this variable textfield for the search
//   var dept_id = null; // dept_id id of the department select field
//   var emp_status = null; // emp_status is the employee status input select, jo, cos, regular
//   var active = null;

//   // function for reload table
//   var reload_table_v2 = function () {

//     // this is the reload_table_v2 
//     // it is a reusable function

//     reload_table({
//       "search": search.getValue(),
//       "dept_id": dept_id.getValue(),
//       "emp_status": emp_status.getValue(),
//       'active': active.getValue()
//     }); // reload_table 

//   };

//   var cardInfo = new Panel(); // information of the card like the information of total result
//   cardInfo.control.style.marginBottom = "5px";
//   cardInfo.addClass("small-card");
//   cardInfo.control.style.padding = "5px";

//   var card_emp_total = new Label("Total:");
//   cardInfo.add(card_emp_total);

//   // this is a employee_page1 route
//   const employee_page1 = function (appHome) {

//     e_info = emp_info();
//     emp_info_modal = e_info.modal;

//     var panel = new Panel();
//     panel.control.style.padding = "5px";
//     //create table

//     table = new Table(["Action", "Profile", "Name", "Position", "Status", 'Active', 'Last Process']);
//     var panel2 = new Panel();
//     panel2.addClass("card");

//     var emp_view = employee_viewer();
//     emp_modal = emp_view.modal;
//     emp_form = emp_view.form;



//     // load client
//     reload_table();

//     var newbtn = new Button("Add Employee", "success", "user-plus");
//     newbtn.control.style.marginBottom = "5px";
//     newbtn.addEventListener("click", function () {
//       emp_form.clear();
//       emp_modal.show();
//     });

//     const loan_contrib_btn = new Button("Loan & Contribution", "success", "refresh").setStyle({
//       marginLeft: '5px',
//       marginBottom: '5px'
//     });
//     loan_contrib_btn.addEventListener('click', async () => {
//       // const modal = new ExcelContribModal();
//       // await modal.show();

//       const modal = new HtmlConLoan();
//       await modal.show();
      
//     });

//     var sync_modal = new Modal("HR System");
//     var sync_loader = new LoaderBox();
//     sync_modal.add(sync_loader);

//     // loaderBox.show();
//     var sync = new Button("Sync", "success", "refresh");
//     sync.control.style.marginBottom = "5px";
//     sync.control.style.marginLeft = "5px";

//     var sheader = new Panel();

//     var scontent = new Panel();
//     sync_modal.add(sheader);
//     sync_modal.add(scontent);

//     var rate_info = { a: "Yearly", m: "Monthly", "d": "Daily", "h": "Hourly" };

//     sync.addEventListener("click", function () {

//       var date_reg = new RegExp('^[0-9]{4}-[0-9]{2}-[0-9]{2}$');

//       var from = prompt('Date From(YYYY-MM-DD):');

//       if (!date_reg.test(from)) {
//         return alert('Invalid Date (From)');
//       }

//       var to = prompt('Date To(YYYY-MM-DD):');

//       if (!date_reg.test(to)) {
//         return alert('Invalid Date (To)');
//       }

//       sync_modal.show();
//       loaderBox.show("Connecting to HR System...");

//       var table = new Table(["Action", "Name", "Rate", "Status", "DeptInfo"]);

//       AppHttp("/api/hrms/employee", { from: from, to: to }, null, function (o) {
//         loaderBox.hide();
//         var data = JSON.parse(o);
//         if (!data.ok) return alert(data.msg);
//         scontent.clear();
//         var fdata = data.data;
//         var fdata_len = fdata.length;
//         for (var i = 0; i < fdata_len; i++) {
//           // parse the department information if it is not null
//           var dept_info = fdata[i].dept_info != null ? JSON.parse(fdata[i].dept_info) : null;
//           var dept_code = "";
//           if (dept_info != null) {
//             dept_code = dept_info["code"];
//           }
//           var add = null;
//           if (!fdata[i]["found"]) {
//             add = new Button("", "success", "plus-circle", null);
//             add.control.setAttribute("rel", i);
//           }
//           else {
//             add = new Button("", "default", "plus-circle", null);
//             add.control.setAttribute("rel", i);
//           }
//           add.addEventListener("click", function () {
//             var index = this.attributes.rel.nodeValue;
//             var data = JSON.stringify(fdata[index]);
//             loaderBox.show("Saving... Please wait...");
//             AppHttp("/api/hrms/save", data, null, function (o) {
//               var data = JSON.parse(o);
//               if (data.ok) {
//                 messageBox.show(data.msg);
//               } else {
//                 alert(data.msg);
//               }
//               loaderBox.hide();
//             });
//           });

//           var status = fdata[i]["found"] ? 'Added' : 'Not Added';

//           table.add([
//             add,
//             fdata[i].lname + ", " + fdata[i].fname + " " + fdata[i].mname + " " + fdata[i].ename,
//             parseFloat(fdata[i].rate).toLocaleString() + "/" + rate_info[fdata[i].rate_type],
//             fdata[i].stat,
//             dept_code
//           ]);

//         }
//         sheader.control.innerHTML = "Total Result: " + fdata_len;
//         var sync_id = new Button('Sync HR System ID', 'success', 'refresh');
//         sync_id.control.style.marginBottom = '10px';

//         sync_id.addEventListener('click', function () {

//           var data = [];

//           for (var i = 0; i < fdata_len; i++) {
//             var x = fdata[i];
//             data.push({
//               'emp_id': x.no,
//               'fname': x.fname,
//               'mname': x.mname,
//               'lname': x.lname,
//               'ename': x.ename
//             });
//           }

//           if (!confirm('Proceed? Make to backup your system database!!!')) return;

//           AppHttp('/api/hrms/sync_all_id', data, null, function (o) {
//             var data = JSON.parse(o);
//             if (data.ok) {
//               messageBox.show(data.msg);
//             } else {
//               alert(data.msg);
//             }
//           });

//         });

//         scontent.add(sync_id);
//         scontent.add(table);
//         sync_modal.add(scontent);
//       });
//     });

//     search = new TextBox(null, "text", "search", null, "Search.... Lastname, Firstname, middlename");
//     dept_id = new ComboBox(null, null, null, "home");
//     emp_status = new ComboBox(null, null, null, "refresh");

//     emp_status.add("", "[ All ]");
//     emp_status.add("j", "Job Orders");
//     emp_status.add("c", "Contract Of Service");
//     emp_status.add("r", "Regular(Permanent.Temporary.Elective.etc...)");

//     active = new ComboBox(null, null, null, 'cog');
//     active.add('', 'All');
//     active.add('y', 'Active');
//     active.add('n', 'Inactive');

//     var srow = new Panel();
//     srow.addClass("container-fluid");

//     // var std1 = new Panel();
//     // std1.addClass("col-md-3");
//     // std1.add(search);

//     // var std2 = new Panel();
//     // std2.addClass("col-md-3");
//     // std2.add(dept_id);

//     // var std3 = new Panel();
//     // std3.addClass("col-md-3");
//     // std3.add(emp_status);

//     // srow.add(std1);
//     // srow.add(std2);
//     // srow.add(std3);

//     const grid = new Grid(2);
//     grid.cell(search, ['md-3', 'sm-3']);
//     grid.cell(dept_id, ['md-3', 'sm-3']);
//     grid.cell(emp_status, ['md-3', 'sm-3']);
//     grid.cell(active, ['md-3', 'sm-3']);

//     srow.add(grid);

//     search.addEventListener("change", function () {
//       reload_table({
//         "search": search.getValue(),
//         "dept_id": dept_id.getValue(),
//         "emp_status": emp_status.getValue(),
//         'active': active.getValue()
//       });
//     });
//     dept_id.addEventListener("change", function () {
//       reload_table({
//         "search": search.getValue(),
//         "dept_id": dept_id.getValue(),
//         "emp_status": emp_status.getValue(),
//         'active': active.getValue()
//       });
//     });
//     emp_status.addEventListener("change", function () {
//       reload_table({
//         "search": search.getValue(),
//         "dept_id": dept_id.getValue(),
//         "emp_status": emp_status.getValue(),
//         'active': active.getValue()
//       });
//     });

//     active.addEventListener('change', () => {
//       reload_table({
//         "search": search.getValue(),
//         "dept_id": dept_id.getValue(),
//         "emp_status": emp_status.getValue(),
//         'active': active.getValue()
//       });
//     });

//     // loadDept function
//     var loadDepartment = function () {
//       AppHttp("/department/list", {}, null, function (o) {
//         var res = JSON.parse(o);
//         var data = res.data;
//         var data_len = data.length;
//         dept_id.clear();
//         dept_id.add("", "All Department");
//         for (var i = 0; i < data_len; i++) {
//           dept_id.add(data[i][0], data[i][1] + " - " + data[i][2]);
//         }
//       });
//     };
//     loadDepartment();
//     // end load dept
//     panel2.add(srow);
//     panel2.add(table);
//     panel.add(newbtn);
//     panel.add(loan_contrib_btn);
//     // panel.add(sync); remove sync 
//     panel.add(cardInfo);
//     panel.add(panel2);
//     panel.add(emp_modal);
//     panel.add(emp_info_modal);

//     panel.add(sync_modal);
//     return panel;
//   };
//   // end functions




//   var panel = new Panel();
//   panel.control.style.padding = "10px";

//   var button = new Button("Employee", "default", "user", "click to manage employee");
//   button.addEventListener("click",  () => {
//     // go to employee page
//     appHome.setContent(employee_page1(appHome), "Employee Management");
//   });


//   var trans = new Button("Payroll", "default", "clock-o", "click to start the payroll transaction");
//   trans.control.style.marginLeft = "5px";
//   trans.addEventListener("click", () => {
//     appHome.setContent(PayrollPage(appHome), "Payroll");
//   });


//   // var update = new Button('Update', "default", "user").setStyle({ marginLeft: "5px" })
//   //   .addEventListener("click", function () {
//   //     appHome.setContent(UpdateView, "Employee Update");
//   //   });

//   // creating a receiver button for the dtr of the regular employee
  
//   const reg_dtr = new Button('DTR Receiver (Regular)', 'default', 'folder-file-o', 'click to view the dtr receiver panel');
//   reg_dtr.setStyle({ marginLeft: '5px' });
//   reg_dtr.addEventListener('click', () => {
//     appHome.setContent(new DTRReceiver(appHome), 'DTR Receiver for regular employee');
//   });

//   // main menu
//   panel.add(button); // button
//   panel.add(trans); // transactions
//   panel.add(reg_dtr);

//   panel.add(new Panel().add(new Label('RECENT TRANSACTION')).setStyle({
//     marginTop: '20px'
//   }));
//   panel.add(new RecentTransaction({}));

//   // panel.add(update);
//   return panel;
// };



/*
 * TransactionView must be removed in the future because of the new implementations
 * 
 */



class TransactionMain extends Panel {
  constructor() {
    super();
    this.setStyle({
      padding: "10px"
    });

    const button = new Button("Employee", "default", "user", "click to manage employee");
    button.addEventListener("click",  () => {
      // go to employee page
      appHome.setContent(new Employee(), "Employee Management");
    });


    const trans = new Button("Payroll", "default", "clock-o", "click to start the payroll transaction");
    trans.control.style.marginLeft = "5px";
    trans.addEventListener("click", () => {
      appHome.setContent(PayrollPage(appHome), "Payroll");
    });


    // var update = new Button('Update', "default", "user").setStyle({ marginLeft: "5px" })
    //   .addEventListener("click", function () {
    //     appHome.setContent(UpdateView, "Employee Update");
    //   });

    // creating a receiver button for the dtr of the regular employee
    
    const reg_dtr = new Button('DTR Receiver (Regular)', 'default', 'folder-file-o', 'click to view the dtr receiver panel');
    reg_dtr.setStyle({ marginLeft: '5px' });
    reg_dtr.addEventListener('click', () => {
      appHome.setContent(new DTRReceiver(appHome), 'DTR Receiver for regular employee');
    });


    this.add([
      button, trans, reg_dtr,
      new Panel().add(new Label('RECENT TRANSACTION')).setStyle({
        marginTop: '20px'
      }).add(new RecentTransaction({}))
    ]);


  }



}

export {
  TransactionMain
};