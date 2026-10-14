import { Table, Panel, Modal, Form, TextBox, ComboBox, Button, x_storage, DropDown } from "../plugin/mcontrol.js";
import { AppHttp } from "../plugin/app.js";
import { x_human_date } from "../plugin/util.js";
import { messageBox, confirmBox } from "../main.js";
import { PayrollEntry } from "./payroll-entry.js";
import { RemittanceView } from "./rem.js";
import { AppHttp2 } from "../classes/lib.js";
import TransaferBank from "../component/payroll-form.js";
import PayrollEntryMain from "./payroll-entry-v2.js";
import CopyPayrollForm from "../component/copy.js";

export const PayrollPage = function (appHome) {
  /* Functions */

  const type_key = {
    "j": "Job Order",
    "c": "Contract",
    "r": "Regular"
  };

  const PanelEntity = function (panel, server_date, cutoff) {
    this.panel = panel;
    this.server_date = server_date;
    this.cutoff = cutoff;
  };

  const payroll_table = new Table(['Action', "Type", "Title", "Total Item", "Date", 'Timer', "Remark", "ATM"]);
  const reload_payroll = function (obj = {}) {

    if (x_storage.getItem('timer') == null)
      x_storage.setItem('timer', null);


    var fnTimer = function (glabel, is_add) {
      // live running time in js
      /* This function is use in the timer counter in the payroll */
      var is_add = is_add || true;

      for (var x in glabel) {
        var obj = glabel[x];
        if (is_add) {
          obj.server_date += 1000;
        }

        if (obj.cutoff != null) {

          var r = dateCount(obj.cutoff, obj.server_date);
          //var index = obj.panel.control.attributes.rel.nodeValue;
          if (r[0]) {
            obj.panel.control.innerHTML = '<div class="alert alert-warning" style="font-weight: bold;"> <i class="fa fa-clock-o"></i> ' + r[1] + '</div>';
          } else {
            obj.panel.control.innerHTML = '<div class="alert alert-success"><i class="fa fa-hand-paper-o"></i>Time\'s Up</div>';
          }
        } else {
          obj.panel.control.innerHTML = '<div class="alert alert-warning"><i class="fa fa-clock-o"></i>Time was not set</div>';
        }
      }
    };

    AppHttp("/payroll/list", obj, null, function (o) {
      payroll_table.clear();
      var data = JSON.parse(o);

      var server_date = data['date'];

      if (data.ok === 1) {
        const rdata = data.data;
        const rdata_len = rdata.length;

        
    

        if (rdata_len > 0) {



          // clear timer
          if (x_storage.getItem('timer') != null) {
            clearInterval(x_storage.getItem('timer'));
          }

          var glabel = []; // storage of the timer label

          for (let i = 0; i < rdata_len; i++) {

            let bank_code = "";
            
            if (rdata[i]["atm_info"] != null && "code" in rdata[i]["atm_info"]) {
              bank_code = rdata[i]["atm_info"]["code"];
            }

            const menu = new DropDown("Action", "primary", "Click the show menu");

            menu.addItem(`<i class="fa fa-eye"></i> View Payroll`, () => {

              // const data = rdata[i];
              // x_storage.setItem("payroll_data", data);
              // appHome.setContent(PayrollEntry(appHome), "Payroll Entry");
              clearInterval(x_storage.getItem('timer'));
              //x_storage.setItem('count_obj', glabel[index]);

              appHome.setContent(new PayrollEntryMain(rdata[i].refid), "Payroll Entry");
              
            });

            if (rdata[i].type == "r") {
              // this only work on regular payroll
              menu.addItem('<i class="fa fa-copy"></i> Copy Payroll', async () => {
                console.log("copying the payroll");
                const refid = rdata[i].refid;
                console.log(refid);

                const modal = new CopyPayrollForm(refid);
                const res = await modal.show();
                if (res != null) {
                  
                }
              });
            }

            menu.addItem(`<i class="fa fa-edit"></i> Switch ATM BANK`, async () => {
              const data = rdata[i];
              const modal = new TransaferBank(data["refid"], data["atm_info"]);
              const ret = await modal.show();

              if (ret != null && ret == true) {
                reload_v2();
              }

            });

            menu.addItem(`<i class="fa fa-refresh"></i> Recompute the Contribution & Loan`, async () => {
              if (!confirm("Recompute, warning: only those are empty are computed!")) return;

              const data = rdata[i];
              const refid = data["refid"];

              const res = JSON.parse(await AppHttp2("/payroll/recompute/con/loan/t", { refid: refid }));
              
              alert(res.msg);

            });

            menu.addItem(`<i class="fa fa-refresh"></i> AutoCal Payroll`, () => {
              const refid = rdata[i]["refid"];

              confirmBox.show("Auto Calculate this payroll?", function () {
                const data = { "refid": refid };
                AppHttp("/payroll/auto/calculate", data, null, function (o) {
                  var res = JSON.parse(o);
                  if (res.ok) {
                    // reload_payroll();
                    alert(res.msg);
                    reload_v2();
                  } else {
                    alert(res.msg);
                  }
                });
              });
            });

            menu.addItem(`<i class="fa fa-money"></i> Remittances`, () => {
              const data = rdata[i];
              x_storage.setItem('payroll_info', data);
              appHome.setContent(RemittanceView, "REMITTANCES");
            });


            const pan = new Panel();
            pan.add(menu);
            // pan.add(edit);
            // pan.add(view);
            // pan.add(regen);
            // pan.add(rem);

            const remark = rdata[i]['status'];
            let msg = "";
            if (remark != null) {
              const _r = JSON.parse(remark);
              msg = _r[_r.length - 1].remark;
            }

            let stat = remark != null ? `<div class="alert alert-success">${msg}</div>` :
              '<div class="alert alert-danger"><i class="fa fa-spinner rotate"></i> Ongoing! </div>';

            var label_timer = new Panel();
            label_timer.control.setAttribute('rel', i);

            var cutoff = rdata[i].cutoff;
            cutoff = cutoff != null ? new Date(cutoff).getTime() : null;

            var lbl = new PanelEntity(label_timer, new Date(server_date).getTime(), cutoff);

            glabel.push(lbl);

            payroll_table.add([
              pan,
              type_key[rdata[i]["type"]],
              "<b>" + rdata[i]["name"] + " - " + x_human_date(rdata[i]["from"]) + " to " + x_human_date(rdata[i]["to"]) + '</b>',
              rdata[i]["total_item"],
              rdata[i]["datecreated"] + " - created: " + rdata[i]["ago"] + " ago",
              lbl.panel,
              stat,
              bank_code
            ]);

          }


          fnTimer(glabel, false);
          x_storage.setItem('timer', setInterval(function () { fnTimer(glabel, false); }, 1000));

        }
      } else {
        messageBox.show(data.msg);
      }
    });
  };

  // reload_payroll(); // reload payroll at payroll page

  const payroll_modal = function () {
    var modal = new Modal("Payroll");
    var form = new Form();
    var name = new TextBox("Name", "text", null, null, "ex: SB-BRGY, MO-BRGY, SB-JO, MO-JO, etc.");
    var from = new TextBox("From", "date", null);
    var to = new TextBox("To", "date", null);
    var type = new ComboBox(null, "Status");

    const bank = new ComboBox(null, "Bank Format");

    // bank.add("t", "DBP 1");
    (async () => {
      const data = JSON.parse(await AppHttp2("/bank/list"));
      if (data.ok !== 1) {
        return;
      }

      const items = data.data;
      const items_len = items.length;

      for (let i = 0; i < items_len; ++i) {
        const code = items[i][0];
        const name = items[i][1];
        bank.add(code, `${code} - ${name}`);
      }

    })();


    var submit = new Button("Save", "success", "calendar", "Please click to create payroll period");
    submit.control.style.marginTop = "5px";

    type.add("j", "Job Order");
    type.add("c", "Contract of Service");
    type.add("r", "Regular");

    form.add(name, "name");
    form.add(from, "from");
    form.add(to, "to");
    form.add(type, "status");
    form.add(bank, "bank");
    form.add(submit);

    var row = new Panel(); row.addClass("row");
    // column 1
    var col1 = new Panel(); col1.addClass("col-md-6");
    row.add(col1);
    col1.add(form);
    modal.add(row);
    // end column1
    // col2 button
    var col2 = new Panel(); col2.addClass("col-md-6");

    // var ada_plus = new Button("Add Ada Signature", "primary", "plus-circle", "click to add add signature");
    // col2.add(ada_plus);

    row.add(col2);
    // end col2

    from.addEventListener("change", function () {

    });

    // ada_plus.addEventListener("click", function () {
    //   alert(1);
    // });

    return {
      modal: modal,
      form: form,
      submit: submit
    }
  };
  /* End Functions */


  var pmodal = payroll_modal();
  var modal = pmodal.modal;
  var submit_payroll = pmodal.submit;
  var form_payroll = pmodal.form;

  var panel = new Panel();
  panel.control.style.padding = "5px";


  var content = new Panel();
  content.addClass("card");

  var newpayroll = new Button("Create Payroll", "success", "plus-circle");
  newpayroll.control.style.marginBottom = "5px";

  newpayroll.addEventListener("click", function () {
    modal.show();
  });

  const date_t = [
    "JANUARY",
    "FEBRUARY",
    "MARCH",
    "APRIL",
    "MAY",
    "JUNE",
    "JULY",
    "AUGUST",
    "SEPTEMBER",
    "OCTOBER",
    "NOVEMBER",
    "DECEMBER"
  ];

  // initial value of the input list
  var date_filter = new ComboBox(null, "Month");
  var year = new ComboBox(null, "Year");
  var stype = new ComboBox(null, "Payroll Type");


  // stype.add("", "[ All ]");
  stype.add("j", "Job Order");
  stype.add("c", "Contract Of Service");
  stype.add("r", "Regular/Permanent/temporary/etc...");


  // set default date_filter based on localStorage

  year.addEventListener("change", function () {
    localStorage.setItem('year', year.getValue());
    reload_v2();
  });

  date_filter.addEventListener("change", function () {
    localStorage.setItem('date', date_filter.getValue());
    reload_v2();
  });

  stype.addEventListener("change", function () {
    localStorage.setItem('type', stype.getValue());
    reload_v2();
  });

  var cur_month = new Date().getMonth() + 1; // getMonth index + 1 to get the real month
  cur_month = cur_month < 10 ? '0' + cur_month : cur_month.toString(); // add 0 prefix if number is less than 10

  for (var i = 0; i < 12; i++) {
    var index = (i + 1);
    date_filter.add(index < 10 ? '0' + index : index.toString(), date_t[i]);
  }

  var start = 2023;

  var cur_year = new Date().getYear() + 1900; // 1900 is the year started the get the current year

  for (var i = start; i <= cur_year; i++) {
    year.add(i, i);
  }

  year.setValue(cur_year);
  date_filter.setValue(cur_month);

  if (localStorage.getItem('date') != null) date_filter.setValue(localStorage.getItem('date'));

  if (localStorage.getItem('year') != null) year.setValue(localStorage.getItem('year'));

  if (localStorage.getItem('type') != null) stype.setValue(localStorage.getItem('type'));


  // end initial value of the input list

  var row = new Panel();
  row.addClass("row");
  row.control.style.marginBottom = "5px";

  var col1 = new Panel();
  col1.addClass("col-md-3");
  col1.add(date_filter);
  row.add(col1);

  var col2 = new Panel();
  col2.addClass("col-md-3");
  col2.add(year); //
  row.add(col2);

  var col3 = new Panel();
  col3.addClass("col-md-3");
  col3.add(stype);
  row.add(col3);

  panel.add(newpayroll);
  panel.add(row);
  panel.add(content);

  // content
  content.add(payroll_table);
  content.add(modal);
  // end content

  var reload_v2 = function () {
    var m = date_filter.getValue();
    var y = year.getValue();
    var dt = y + "-" + m;
    var type = stype.getValue();

    reload_payroll({
      date: dt,
      type: type
    });
  };

  reload_v2(); // reload the table

  submit_payroll.addEventListener("click", function () {
    var data = form_payroll.getValues();
    var from = data.from;
    var to = data.to;
    var status = data.status;
    var name = data.name;

    if (from == "") return messageBox.show("start date is required!");
    if (to == "") return messageBox.show("to date is required!");
    if (status == "") return messageBox.show("status is required!");
    if (name == "") return messageBox.show("name is required!");

    AppHttp("/payroll/create", data, null, function (o) {
      var data = JSON.parse(o);
      if (data.ok === 1) {
        messageBox.show(data.msg, function () {
          // process the payroll here or reload the table for 
          // generation of the payroll system
          // reload_payroll();
          reload_v2();
        });
      } else {
        messageBox.show(data.msg);
      }
    });
  });

  return panel;
};