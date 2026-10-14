// end deduction pages
import { Panel, Button, Form, Modal, Table, TextBox } from "../plugin/mcontrol.js";
import { AppHttp } from '../plugin/app.js';
import { messageBox, confirmBox } from "../main.js";

const SystemInfo = function (title = '') {
  var modal = new Modal(title, 'System Information');

  var form = new Form();

  var name = new TextBox('Name', 'text', null, null, 'Name of the company');
  form.add(name, 'name');
  var addr = new TextBox('Address', 'text', null, null, 'Address of the company');
  form.add(addr, 'addr');
  var tin = new TextBox('Tin', 'text', null, null, 'Company Tin Number');
  form.add(tin, 'tin');

  var submit = new Button('Save', 'success', 'save', 'click to save the changes!');
  submit.control.style.marginTop = '5px';
  form.add(submit);



  submit.addEventListener('click', function () {
    var data = form.getValues();

    AppHttp('/setting/setup/save', data, null, function (o) {
      var data = JSON.parse(o);
      if (data['ok'] == 1) {
        messageBox.show(data['msg'], function () {
          modal.hide();
        });
      } else {
        messageBox.show(data['msg']);
      }
    });
  });

  modal.add(form);
  return {
    modal: modal,
    form: form
  };
};

// system setting
export const PageSystemSetting = function () {
  var panel = new Panel();
  panel.addClass("card");
  const content = new Panel();
  content.control.style.padding = "10px";


  var table = new Table(["Information", "Value"]);


  AppHttp('/setting/setup/get', {}, null, function (o) {
    var msg = JSON.parse(o);
    var data = msg['data'];

    table.add(["Name", data['name']]); // Name of the company
    table.add(["Address", data['addr']]); // Address of the company
    table.add(["TIN", data['tin']]); // Comany tin tax indefication number
  });

  var regForm = SystemInfo().modal; // this is the system form

  var add = new Button("Edit Company", "primary", "edit", "Please click to edit the company");
  add.addEventListener("click", function () {

    regForm.show();
  });
  add.control.style.marginBottom = "10px";

  content.add(add);
  content.add(table);
  panel.add(content);


  panel.add(regForm);

  return panel;
};
// end system setting






var BankForm = function () {
  var modal = new Modal('Bank Information');
  var form = new Form();
  var code = new TextBox('code', 'text', null, null, 'Enter Bank code');
  var bankno = new TextBox('Bank Acct No.', 'text', null, null, 'Enter Bank Number');

  form.add(code, 'code');

  var name = new TextBox('name', 'Text', null, null, 'Enter Bank Name');
  form.add(name, 'name');
  form.add(bankno, 'bankno');

  var submit = new Button('Save', 'primary', 'save', 'please click to submit bank information');
  submit.control.style.marginTop = '5px';
  form.add(submit);

  modal.add(form);
  return {
    form: form,
    submit: submit,
    modal: modal
  }
};

// Company Bank Information
export const CompanyBankInformation = function () {
  var panel = new Panel();
  panel.addClass('card');
  panel.control.style.padding = '5px';

  var _bankForm = BankForm();
  var form = _bankForm['form'];
  var modal = _bankForm['modal'];
  var submit_form = _bankForm['submit'];

  var newBank = new Button('New Bank', 'success', '', 'Please click to add new bank');
  newBank.control.style.marginBottom = '5px';
  newBank.addEventListener('click', function () {
    modal.show();
  });
  var table = new Table(['Code', 'Name', 'Acct No.', 'Action']);

  var loadTable = function () {
    AppHttp('/setting/bank/list', {}, null, function (o) {

      var fdata = JSON.parse(o);
      if (fdata.ok == 0) return;
      table.clear();

      var data = fdata.data;
      var data_len = data.length;
      for (var i = 0; i < data_len; i++) {
        var code = data[i][0];
        var name = data[i][1];
        var no = data[i][2];

        var remove = new Button('', 'danger', 'trash', 'click to remove bank account!');
        remove.control.setAttribute('rel', code);
        remove.addEventListener('click', function () {
          var code_bot = this.attributes.rel.nodeValue;
          confirmBox.show("Do you want to remove this account?", function () {
            // request for removing the account
            AppHttp('/setting/bank/remove', { code: code_bot }, null, function (o) {
              var res = JSON.parse(o);
              if (res.ok == 1) {
                messageBox.show(res.msg, function () {
                  loadTable();
                });
              } else {
                messageBox.show(res.msg);
              }
            });
          });
        });

        table.add([code, name, no, remove]);
      }
    });
  };
  loadTable();

  submit_form.addEventListener('click', function () {
    var data = form.getValues();
    AppHttp('/setting/bank/save', data, null, function (o) {
      var res = JSON.parse(o);
      if (res.ok == 1) {
        messageBox.show(res.msg, function () {
          // reload changes of the bank or reload the table
          loadTable();
        });
      } else {
        messageBox.show(res.msg);
      }
    });
  });

  panel.add(newBank);
  panel.add(table);
  panel.add(modal);
  return panel;
};


var DepartmentForm = function () {
  var modal = new Modal("Department Form");
  var form = new Form();

  var id = new TextBox("id", "text", null);
  var code = new TextBox("Code", "text", null);
  var title = new TextBox("Title", "text", null);
  var submit = new Button(null, "success", "save");
  submit.control.style.marginTop = "5px";
  form.add(id, "id");
  form.add(code, "code");
  form.add(title, "title");
  form.add(submit);

  submit.addEventListener("click", function () {
    var data = form.getValues();
    AppHttp("/department/save", data, null, function (o) {
      var data = JSON.parse(o);
      if (data.ok == 1) {
        messageBox.show(data.msg, function () {
          load_dept_table(form, modal);
          modal.hide();
        });
      } else {
        messageBox.show(data.msg);
      }
    });
  });

  modal.add(form);
  return {
    modal: modal,
    form: form
  };
};


var dept_table = new Table(["Action", "id", "code", "title"]);
var load_dept_table = function (form, modal) {
  dept_table.clear();
  AppHttp("/department/list", {}, null, function (o) {
    var fdata = JSON.parse(o);
    var data = fdata.data;
    var data_len = data.length;
    for (var i = 0; i < data_len; i++) {
      var id = data[i][0];
      var code = data[i][1];
      var title = data[i][2];

      var panel = new Panel();
      var edit = new Button(null, "primary", "edit", "click to edit");
      edit.control.setAttribute("rel", i);
      edit.addEventListener("click", function () {
        var index = this.attributes.rel.nodeValue;
        var idata = data[index];
        var input = form.input;
        input.id.setValue(idata[0]);
        input.code.setValue(idata[1]);
        input.title.setValue(idata[2]);
        modal.show();
      });

      var trash = new Button(null, "danger", "trash", "click to remove the deparment");
      trash.control.style.marginLeft = "5px";
      trash.control.setAttribute("rel", i);

      trash.addEventListener("click", function () {
        var index = this.attributes.rel.nodeValue;
        var id = data[index][0];
        confirmBox.show("remove? are you sure?", function () {
          AppHttp("/department/remove", { id: id }, null, function (o) {
            var data = JSON.parse(o);
            if (data.ok == 1) {
              messageBox.show(data.msg, function () {
                load_dept_table(form, modal);
              });
            } else {
              messageBox.show(data.msg);
            }
          });
        });
      });

      panel.add(edit);
      panel.add(trash);

      dept_table.add([panel, id, code, title]);
    }
  });
};

export const SettingDepartmentPage = function () {
  var panel = new Panel();

  var dept = DepartmentForm();
  var modal = dept.modal;
  var form = dept.form;

  panel.addClass("card");
  panel.control.style.padding = "5px";

  var newdept = new Button("New Department", "success", "plus-circle");
  newdept.addEventListener("click", function () {
    modal.show();
  });

  load_dept_table(form, modal);

  panel.add(newdept);
  panel.add(dept_table);
  panel.add(modal);
  return panel;
};