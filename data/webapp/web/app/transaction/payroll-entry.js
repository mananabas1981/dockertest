import { x_storage, Modal, Form, TextBox, Button, Table, Panel, ComboBox, Label, Grid, MsgLoader, DropDown } from "../plugin/mcontrol.js";
import { AppHttp } from "../plugin/app.js";
import { x_salary_type } from "../plugin/util.js";
import { messageBox, confirmBox } from "../main.js";
import { AdaViewer, AdaViewer2, CloseAda } from "../component/AdaViewer.js";
import { PayrollPage } from "./payroll.js";
//import { ObModal } from "./ob-r.js";
import { EditSignatory } from "../component/signatory.js";
import { PayrollViewer } from "../component/payroll.js";
import { PayrollBaseDeduction } from "../component/PayrollBaseDeduction.js";
import { AppHttp2 } from "../classes/lib.js";
import { CloseOBR } from "./ob-r.js";

import { StatusForm } from './../component/StatusForm.js';

const ApprovePayrollForm = function () {
    /* Approve form */
    var modal = new Modal('Approve Payroll');

    var form = new Form();
    var user = new TextBox('Username', 'text');
    var pass = new TextBox('Password', 'password');
    var remark = new TextBox('Remark', 'text');

    form.add(user, 'username');
    form.add(pass, 'password');
    form.add(remark, 'remark');

    var push = new Button('Approve', 'primary', 'thumbs-up');
    push.control.style.marginTop = '5px';
    form.add(push);

    push.addEventListener('click', function () {
        confirmBox.show('Approved?', function () {
            self.submit(function (o) {
                var data = JSON.parse(o);
                if (data.ok) {
                    messageBox.show(data.msg, function () {
                        /* Code after clicking the messageBox  */

                    });
                } else {
                    alert(data.msg);
                }
            });
        });
    });

    var self = this;
    this.submit = function (__callback) {
        var callback = __callback || null;

        if (callback == null)
            return console.log('callback is required, callback must be a function ');

        if (typeof (callback) != 'function')
            return console.log('callback must be a function');

        var data = form.getValues();
        var pdata = x_storage.getItem('payroll_data');
        var refid = pdata['refid'];
        data['refid'] = refid;

        AppHttp('/payroll/approve', data, null, callback);

    };

    modal.add(form);
    modal.show();

    this.getForm = function () {
        return form;
    };
    this.getModal = function () {
        return modal;
    };
};

/*
 * y_qr_t 
 * is a variable hold the y_qr_t
 */
var payroll_qr = {
    _qr: null,
    open: function (_qrhandler, _time_out) {
        var time_out = _time_out || 2000;
        if (this._qr == null) {
            this._qr = setInterval(_qrhandler, time_out);
        } else {
            console.warn('payroll qr already running!');
        }
    },
    close: function () {
        if (this._qr != null) {
            clearInterval(this._qr);
            this._qr = null;
        } else {
            console.warn('payroll qr already closed!');
        }
    }
};

export function PayrollEntry(appHome) {
    // functions 
    // end functions 
    var payroll_data = x_storage.getItem('payroll_data');

    var calculate_gross = null;

    var is_update = false;

    var create_deduction_form = function () {

        var form = new Form();

        var ded = JSON.parse(payroll_data["deduction_list"]);
        var ded_len = ded.length;

        for (var i = 0; i < ded_len; i++) {
            var data = ded[i];
            var name = data["code"].toLowerCase() + "___" + data["name"].toLowerCase();

            var tf = new TextBox(data["code"] + "->" + data["name"], "text");
            tf.addEventListener("change", function () {
                calculate_gross();
            });
            form.add(tf, name);
        }

        var total_ded = new Panel();
        total_ded.control.style.width = "100%";
        total_ded.control.style.height = "30px";
        total_ded.control.style.padding = "5px";
        total_ded.control.style.border = "1px solid #ddd";
        total_ded.control.style.marginTop = "20px";
        total_ded.control.innerHTML = "Total Deduction: ";

        var net = new Panel();
        net.control.style.width = "100%";
        net.control.style.height = "30px";
        net.control.style.padding = "5px";
        net.control.style.border = "1px solid #ddd";
        net.control.style.marginTop = "20px";
        net.control.innerHTML = "NetPay: ";

        form.add(total_ded);
        form.add(net);

        return {
            form: form,
            deduction_panel: total_ded,
            net: net
        };
    };

    // initialized the deduction form


    const table = new Table([
        "Action",
        'serial',
        'Name',
        'Position',
        'Rate',
        'Day Work',
        'Gross',
        'Deduction',
        'W/TAX',
        'NET',
        'Remark'
    ],
        [
            {
                width: '145px'
            }, // action column style
        ]);

    // reload the table function for drawing the list of payroll
    // submmitted

    var update_form = null;

    var edit_payslip = function () {
        var data = x_storage.getItem("emp_selected");
        // console.log(data);
        // manipulate the data

        var ded_data = data["deduction"];
        var com = data["com"];


        var left_form = g_form.left_form.input;
        var right_form = g_form.right_form.input;;

        left_form.fname.setValue(data["name"]);
        left_form.emp_id.setValue(data["employee_no"]);
        left_form.day_work.setValue(data["no_work_day"]);
        // rate
        left_form.salary.setValue(data["salary"]);
        left_form.absent.setValue(com["a"]);
        left_form.late.setValue(com["l"]);
        left_form.ut.setValue(com["u"]);

        var i = 0;
        while (i < ded_data.length) {
            var ded = ded_data[i];

            right_form[(ded.code + "___" + ded.name).toLowerCase()].setValue(ded.value);
            i++;
        }

        // calculate_gross(); // recalculate gross
        // update_form();

        const loader = new MsgLoader('Fetching employee information');

        AppHttp('/employee/information', { emp_id: data["employee_no"] }, null, function (o) {
            loader.hide();
            var res = JSON.parse(o);
            if (res.ok != 1) return;
            var data = res.data;
            x_storage.setItem('f_info', data);

            calculate_gross(); // recalculate gross
        });

    };

    var reload_table = function (data) {
        //@ data is a dictionary object
        var data = data || {}; // if no value it create and empty object
        var search = data["search"] || "";
        var dept_id = data["dept_id"] || "";

        const loader = new MsgLoader('Reloading payroll items')

        AppHttp('/payroll/get/items', {
            refid: payroll_data.refid,
            search: search,
            dept_id: dept_id
        }, null, function (o) {
            loader.hide('Payroll items reloaded!');
            table.clear();
            const res = JSON.parse(o);

            if (res.ok != 1) return;
            const data = res.data;
            const data_len = data.length;
            if (data_len < 1) return;

            for (let i = 0; i < data_len; i++) {
                var panel = new Panel();
                var edit = new Button(null, "success", "edit");
                edit.control.setAttribute("rel", i);
                edit.addEventListener("click", function () {
                    var index = this.attributes.rel.nodeValue;
                    var info = data[index];
                    info["id"] = info["employee_no"];

                    x_storage.setItem("emp_selected", info);
                    g_form.modal.show();
                    edit_payslip();
                    is_update = true;
                    update_form();
                });

                var tax_btn = new Button(null, "primary", "percent");
                tax_btn.control.style.marginLeft = "2px";

                var trash = new Button(null, "danger", "trash");
                trash.control.setAttribute("rel", i);
                trash.control.style.marginLeft = "2px";
                trash.addEventListener("click", function () {
                    var index = parseInt(this.attributes.rel.nodeValue);
                    var info = data[index];
                    confirmBox.show('<span style="font-size: 8pt;">' + "REMOVE " + info["name"] + " ?" + '</span>', function () {
                        var data = { "emp_id": info["employee_no"], "refid": payroll_data.refid };
                        AppHttp("/payroll/remove/item", data, null, function (o) {
                            var res = JSON.parse(o);
                            if (res.ok) {
                                messageBox.show(res.msg, function () {
                                    reload_table();
                                });
                            } else {
                                alert(res.msg);
                            }
                        })
                    });
                });

                tax_btn.control.setAttribute("rel", i);

                // tax_btn for automatic calculation of the 
                // tax 
                tax_btn.addEventListener("click", function () {

                    var index = this.attributes.rel.nodeValue;
                    var fdata = data[index];
                    var refid = payroll_data.refid;

                    confirmBox.show("calculate tax?", function () {
                        const loader = new MsgLoader('Calculating tax!');
                        AppHttp("/payroll/calculate/tax", {
                            refid: refid,
                            emp_id: fdata.employee_no
                        }, null, function (o) {
                            var data = JSON.parse(o);
                            loader.hide(data.msg);
                        });
                    });
                });


                // panel.add(edit);
                // panel.add(trash);
                // panel.add(tax_btn);


                // panel
                //     .addClass('container-fluid')
                //     .add(
                //         new Grid(1)
                //             .cell(edit, ['md-4'])
                //             .cell(trash, ['md-4'])
                //             .cell(tax_btn, ['md-4'])
                //     );

                const action = new DropDown("Action", "warning", "click to view the menu");
                action.addItem(`<i class="fa fa-edit"></i> Edit`, () => {
                    const info = data[i];
                    info["id"] = info["employee_no"];
                    x_storage.setItem("emp_selected", info);
                    g_form.modal.show();
                    edit_payslip();
                    is_update = true;
                    update_form();
                });

                action.addItem(`<i class="fa fa-trash"></i> Remove`, () => {
                    const info = data[i];
                    confirmBox.show('<span style="font-size: 8pt;">' + "REMOVE " + info["name"] + " ?" + '</span>', function () {
                        const data = { "emp_id": info["employee_no"], "refid": payroll_data.refid };
                        AppHttp("/payroll/remove/item", data, null, function (o) {
                            const res = JSON.parse(o);
                            if (res.ok) {
                                messageBox.show(res.msg, function () {
                                    reload_table();
                                });
                            } else {
                                alert(res.msg);
                            }
                        })
                    });
                });

                panel.add(action);




                var info = data[i];

                /* Withholding tax */
                var wtax = 0.0;
                var ded = info.deduction;
                for (var d in ded) {
                    if (ded[d].code.toUpperCase() == 'TAX') {
                        wtax = ded[d].value;
                    }
                }
                /* End withholding tax */

                /* Department Information */
                var p = info.dept_info;
                //console.log(info);
                var pos_title = p.n;

                const remark = ''; // some remark here like if the ob-r is approved 
                
                const bg = {};
                
                if (info.no_work_day <= 0.0) {
                    bg['backgroundColor'] = '#ff6e6e'; 
                    bg['color']           = 'white';
                }


                table.add([
                    panel,
                    info.serial_no,
                    info.name,
                    info.position + '-' + '<b>' + pos_title.toUpperCase() + '</b>',
                    info.salary,
                    info.no_work_day,
                    info.gross,
                    '<b style="color: red;">' + info.total_ded + '</b>',
                    '<b>' + wtax + '</b>',
                    '<b style="color: green;">' + info.net + '</b>',
                    remark
                ], [], bg);

            };
        });
    };

    reload_table();

    var form = function () {
        var modal = new Modal('Employee Information');

        var form = new Form();

        var search = new TextBox(null, 'text', 'search', 'Search here', 'Search id or name of the employee!');
        var search_list_w = new Panel();
        search_list_w.addClass('search_list_wrap');

        var search_content = new Panel();
        search_content.addClass('search_content');
        search_list_w.add(search_content);
        search_list_w.hide();

        var search_item = new Panel();

        var close = new Button(null, null, 'close');
        close.addClass('search_close');
        search_content.add(close);
        search_content.add(search_item);

        var emp_id = new TextBox('ID', 'text', null, null, 'Generated id');
        emp_id.control.setAttribute('readonly', '');

        var fullname = new TextBox('NAME', 'text', null);
        fullname.control.setAttribute('readonly', '');

        var salary = new TextBox('RATE', 'text', null);
        salary.control.setAttribute('readonly', '');

        var day_work = new TextBox("NO. WORK DAY", 'text', null);
        var late = new TextBox('LATE(MIN)', 'text', null, null);
        var absent = new TextBox('ABSENT', 'text', null);
        var gross = new TextBox('Gross', 'text', null, null);
        var undertime = new TextBox('UNDERTIME(MIN)', 'text', null, null);
        var loader = new Panel();
        loader.control.innerHTML = '<span class="loader"></span>'

        update_form = function () {
            var data = x_storage.getItem("emp_selected");

            var id = data.id;
            var lname = data.lname;
            var mname = data.mname;
            var fname = data.fname;
            var ename = data.ename;
            var gender = data.gender;
            var dob = data.dob;

            var inputs = form.input;
            inputs.emp_id.setValue(id);
            inputs.fname.setValue((lname + ' ' + fname + ' ' + mname).toUpperCase());
            // load other information
            AppHttp('/employee/information', {
                emp_id: id,
                from: payroll_data.from,
                to: payroll_data.to
            }, null, function (o) {
                var res = JSON.parse(o);
                if (res.ok != 1) return;
                var data = res.data;

                var dept_info = data.dept_info;
                var pos_info = data.pos_info;
                var rate_info = data.rate_info;

                var last_ded = data.last_ded || [];

                var rate = 0.0;
                var rate_type = null;

                if (rate_info != null) {
                    rate = rate_info.rate;
                    rate_type = rate_info.rate_type;
                    inputs.salary.setValue(parseFloat(rate) + ' ' + x_salary_type(rate_type));
                }

                // plot the right inputs
                var rinput = g_form.right_form.input;

                for (var i = 0; i < last_ded.length; i++) {

                    for (var key in rinput) {
                        var code = last_ded[i]["code"] + "___" + last_ded[i]["name"];
                        code = code.toLowerCase();
                        var last_value = last_ded[i]["value"];

                        if (code == key) {
                            rinput[key].setValue(last_value);
                        }
                    }
                }

                x_storage.setItem('f_info', data);
                x_storage.setItem('last_ded', last_ded); // get the last deduction information

                calculate_gross();
            });

        };

        var search_xhr = function (v) {
            search_item.add(loader);
            AppHttp('/client/list', { search: v }, null, function (o) {
                search_item.clear();
                var res = JSON.parse(o);
                if (res.ok != 1) return;

                var data = res.data.data;
                var data_len = data.length;

                // draw table() {}
                if (data_len < 1) return;

                // table
                var table = new Table(["Action", "name", 'Active?']);


                let i = 0;
                do {

                    const add = new Button('Add', 'success', 'plus-circle', 'please click to add it on the payroll item');
                    add.control.setAttribute('rel', i);
                    add.addEventListener('click', function () {
                        var index = this.attributes.rel.nodeValue;
                        var odata = data[index];

                        if (odata.active == 'n')
                            if (!confirm('Are you sure you want to add this employee to the payroll, note it is inactive in the system')) return;


                        x_storage.setItem('emp_selected', odata); // selected data 
                        search_list_w.hide();
                        update_form(); // update form and show the total deductions
                    });

                    table.add([
                        add,
                        `${data[i].lname} ${data[i].fname} ${data[i].mname}`.toString(),
                        data[i].active == 'y'
                            ? new Label('Active').setStyle({ color: 'white', backgroundColor: 'green' })
                            : new Label('Not Active').setStyle({ color: 'white', backgroundColor: 'red' })
                    ]); // add the content in the table

                    search_item.add(table); // add the item panel

                    i++;

                } while (i < data_len);
            });

        };

        var time_flag = null;

        search.addEventListener('keyup', function () {
            var v = this.value.trim();
            search_list_w.show();

            // if (xhr_flag != null) return;
            search_item.clear();

            if (time_flag != null) {
                clearTimeout(time_flag);
            }

            time_flag = setTimeout(function () {
                search_xhr(v);
            }, 500);

            if (v == '') {
                search_list_w.hide();
            }
        });

        close.addEventListener('click', function () {
            search_list_w.hide();
        });

        calculate_gross = function () {

            const info = x_storage.getItem('f_info');

            var rate_info = info.rate_info;

            var rate = parseFloat(rate_info.rate);
            var rate_type = rate_info.rate_type;

            var isnum = new RegExp('^[0-9]+([.][0-9]+)?$');
            var _work = day_work.getValue();
            var _late = late.getValue();

            var total_work = 0.0;
            var total_late = 0.0;

            if (isnum.test(_work)) {
                total_work = parseFloat(_work);
            }

            if (isnum.test(_late)) {
                total_late = parseFloat(_late);
            } else {
                if (/^[0-9]+[\:][0-9]+$/.test(_late)) {
                    var time = _late.split(':');
                    var h = parseFloat(time[0]);
                    var m = parseFloat(time[1]);

                    // total late hour times 60 after add it to minute 
                    // to get the total minute
                    total_late = (h * 60) + m;
                    late.setValue(total_late); // auto update to total_late
                }
            }

            var total_absent = 0.0;
            if (isnum.test(absent.getValue())) {
                total_absent = parseFloat(absent.getValue());
            }
            var total_undertime = 0.0;
            if (isnum.test(undertime.getValue())) {
                total_undertime = parseFloat(undertime.getValue());
            } else {
                if (/^[0-9]+[\:][0-9]+$/.test(undertime.getValue())) {
                    var time1 = undertime.getValue().split(':');
                    var h1 = parseFloat(time1[0]);
                    var m1 = parseFloat(time1[1]);

                    // total late hour times 60 after add it to minute 
                    // to get the total minute
                    total_undertime = (h1 * 60) + m1;
                    undertime.setValue(total_undertime); // auto update to total_late
                }
            }

            // get the value of the deduction

            var ded_input = g_form.right_form.input;

            var ded = JSON.parse(payroll_data["deduction_list"]);
            var ded_len = ded.length;

            var ded_data = [];

            for (var i = 0; i < ded_len; i++) {

                var ded_stat = ded[i];
                var n = ded_stat["code"].toLowerCase() + "___" + ded_stat["name"].toLowerCase();
                var input = ded_input[n];

                var v = 0.0;
                if (isnum.test(input.getValue())) {
                    v = parseFloat(input.getValue());
                } else {
                    input.setValue(0);
                }

                ded_data.push({
                    code: ded_stat["code"],
                    name: ded_stat["name"],
                    value: v
                });

            }
            // the deduction calculation is on the server
            AppHttp("/payroll/pre/calculate", {
                emp_id: info.dept_info.emp_id,
                rate: rate,
                rate_type: rate_type,
                payroll_refid: payroll_data.refid,
                work_day: total_work,
                late: total_late,
                undertime: total_undertime,
                total_absent: total_absent,
                ded_data: ded_data
            }, null, function (res) {
                const d = JSON.parse(res);
                //console.log(d);
                if (!d.ok) return;
                const data = d.data;

                gross.setValue(data.gross_amount);

                right_form.deduction_panel.control.innerHTML = "Total Deduction: " +
                    '<span style="color: red; font-weight: bold;">'
                    + data.total_deduction +
                    "</span>";

                right_form.net.control.innerHTML = "NetPay: " + '<span style="color: green; font-weight: bold;">'
                    + data.net_amount +
                    "</span>";
            });


            return {
                late: total_late,
                absent: total_absent,
                undertime: total_undertime,
                ded_data: ded_data,
                work: total_work
            }
        };

        day_work.addEventListener('keyup', function () {
            calculate_gross();
        });

        late.addEventListener('keyup', function (e) {
            if (/:/.test(late.getValue())) {
                if (e.keyCode == 13) {
                    calculate_gross();
                }
                return;
            }

            calculate_gross();
        });

        undertime.addEventListener('keyup', function (e) {
            if (/:/.test(undertime.getValue())) {
                if (e.keyCode == 13) {
                    calculate_gross();
                }
                return;
            }
            calculate_gross();
        });

        absent.addEventListener('keyup', function () {
            calculate_gross();
        });

        form.add(search_list_w);
        form.add(search, 'search');
        form.add(emp_id, 'emp_id');
        form.add(fullname, 'fname');
        form.add(salary, 'salary');
        form.add(day_work, 'day_work');
        form.add(absent, 'absent');
        form.add(undertime, 'ut');
        form.add(late, 'late');
        form.add(gross, 'gross');

        var submit = new Button('Submit', 'success', null);
        submit.control.style.marginTop = '5px';
        form.add(submit);

        submit.addEventListener('click', function () {
            var comdata = calculate_gross();
            var emp_data = x_storage.getItem('emp_selected');
            AppHttp('/payroll/add/item', {
                is_update: is_update,
                emp_id: emp_data.id,
                late: comdata.late,
                work: comdata.work,
                absent: comdata.absent,
                undertime: comdata.undertime,
                payroll_refid: payroll_data.refid,
                deduction_value: comdata.ded_data
            }, null, function (o) {
                is_update = false;
                var data = JSON.parse(o);
                if (data.ok) {
                    messageBox.show(data.msg, function () {
                        reload_table();
                    });
                } else {
                    alert(data.msg);
                }
            });
        });

        var left_panel = new Panel();
        left_panel.control.style.width = "50%";
        left_panel.control.style.float = "left";
        left_panel.control.style.padding = "10px";
        left_panel.add(form);

        var right_panel = new Panel();
        right_panel.control.style.width = "50%";
        right_panel.control.style.float = "left";
        right_panel.control.style.padding = "10px";

        modal.add(left_panel);
        modal.add(right_panel);

        modal.control.style.minHeight = "920px";
        //modal.control.style.minHeight = right_panel.control.offsetHeight + 'px';
        // setTimeout(function() {
        //     console.dir(right_panel.control);
        // }, 500);


        return {
            modal: modal,
            right_panel: right_panel,
            left_form: form
        };
    };

    var g_form = null; // the instance of the modal forms

    var removeResponse = function (o) {
        var data = JSON.parse(o);
        if (data.ok) {
            messageBox.show(data.msg, function () {
                // route to the main  payroll list items
                appHome.setContent(PayrollPage, "Payroll");
            });
        } else {
            alert(data.msg);
        }
    };

    var deletePayrollCallBack = function () {
        var payroll_data = x_storage.getItem('payroll_data');
        var refid = payroll_data.refid;
        AppHttp('/payroll/remove', { refid: refid }, null, removeResponse);
    };

    var content = {
        panel: new Panel,
        back: new Button("Back", "primary", "arrow-left"),
        nbtn: new Button('New', 'success', 'plus-circle'),
        trash: new Button('Delete Payroll', 'danger', 'trash'),
        dept_id: new ComboBox(null, null, null, "home"),
        search: new TextBox(null, "text", "search", "Enter Here to search", "Filter..."),
        qrcode: new TextBox(null, "password", "qrcode", "Focus you mouse", "Focus your mouse to scan dtr qrcode"),
        menu: new Panel(),
        init: function () {
            this.panel.addClass("card");
            // this.back.addEventListener("click", function () {
            //     appHome.setContent(PayrollPage, "Payroll");
            // });
            // this.nbtn.control.style.marginBottom = '5px';
            // this.nbtn.control.style.marginLeft = '5px';
            // this.nbtn.addEventListener('click', function () {
            //     // open form
            //     is_update = false;
            //     g_form.left_form.clear();
            //     g_form.right_form.clear();
            //     g_form.modal.show();
            // });

            // this.trash.control.style.marginBottom = '5px';
            // this.trash.control.style.marginLeft = '50px';
            // this.trash.addEventListener('click', function () {
            //     confirmBox.show('Are you sure?', deletePayrollCallBack);
            // });

            g_form = form();

            // print payroll
            var tool_box = new Panel();
            tool_box.control.style.padding = '5px';
            // var payroll_print = new Button('View Payroll', 'success', 'print', 'please click to print');
            // const edit_signatory = new Button('Edit Signatory', 'success', 'pencil', 'please click to edit signatories').setStyle({
            //     marginRight: '5px'
            // });

            // var view_ada = new Button("View Ada", "success", "eye", "please click to print the Authority to Debit Account (ADA)");
            // view_ada.control.style = "margin-left: 5px;";


            // const view_ob = new Button('View Ob-R', 'success', 'search').setStyle({
            //     marginLeft: '5px'
            // }).addEventListener('click', function () {
            //     const modal = new ObModal(content.dept_id.getValue());
            //     // modal.show();
            // });


            //var approve = new Button('Close Payroll', 'warning', 'close');
            // approve.control.style.marginLeft = '50px';
            var approve_content = new Panel();
            // approve.addEventListener('click', function () {
            //     approve_content.clear();
            //     approve_content.add(new ApprovePayrollForm().getModal());
            // });

            // edit_signatory.addEventListener('click', () => {
            //     const p = x_storage.getItem('payroll_data');
            //     if (p == null) return;

            //     const refid = p['refid'];
            //     const dept_id = content.dept_id.getValue()

            //     const edit = new EditSignatory(refid, dept_id);
            //     // edit.show();

            // });

            // const edit_base_deduction = new Button("Edit Header", "success", "edit").setStyle({
            //     marginRight: "5px"
            // });

            // edit_base_deduction.addEventListener("click", async () => {
            //     const p = x_storage.getItem('payroll_data');
            //     if (p == null) return;

            //     const refid = p['refid'];
            //     const base = new PayrollBaseDeduction(refid);


            //    const d = await base.show();
            //    if (d != null)  
            //         reload_table({
            //             "search": content.search.getValue(),
            //             "dept_id": content.dept_id.getValue()
            //         });

            // });


            const pay_menu = new DropDown("Payroll Menu", "success", "click to view the menu");
            pay_menu.addItem(`<i class="fa fa-eye"></i> View Payroll`, async () => {
                const p = x_storage.getItem('payroll_data');
                if (p == null) return;

                const refid = p['refid'];
                const modal = new PayrollViewer({
                    refid: refid,
                    dept_id: content.dept_id.getValue()
                });

                await modal.show();
            });

            pay_menu.addItem(`<i class="fa fa-heart"></i> CLOSE RECV. DTR`, () => {
                // approve_content.clear();
                // approve_content.add(new ApprovePayrollForm().getModal());
                const p = x_storage.getItem('payroll_data');
                if (p == null) return;
                const refid = p['refid'];

                const modal = new StatusForm({
                    title: 'CLOSE PAYROLL',
                    refid: refid,
                    type: 'close_payroll'
                });

                modal.show();
            });

            pay_menu.addItem(`<i class="fa fa-close"></i> Close Obligation Requests`, async () => {
                const p = x_storage.getItem('payroll_data');
                if (p == null) return;
                const refid = p['refid'];

                const close = new CloseOBR(refid);
                await close.show();
            });

            pay_menu.addItem(`<i class="fa fa-money"></i> View ADA`, async () => {
                const p = x_storage.getItem('payroll_data');
                if (p == null) return;
                const refid = p['refid'];
                const dept_id = content.dept_id.getValue();


                // _ada_viewer.clear();
                // _ada_viewer.add(new AdaViewer(refid, dept_id).container());

                // the below implementation is for the future release
                const ada = new AdaViewer2(refid, dept_id);
                await ada.show();
            });

            pay_menu.addItem(`<i class="fa fa-close"></i>Approve Ada`, async () => {

                const p = x_storage.getItem('payroll_data');
                if (p == null) return;
                const refid = p['refid'];

                const close = new CloseAda(refid);
                await close.show();
            });

            pay_menu.addItem(`<i class="fa fa-list"> Remittance`, () => {
                console.log("remittancess");
            });


            pay_menu.addItem(`<i class="fa fa-pencil"></i> Edit Signatory`, () => {
                const p = x_storage.getItem('payroll_data');
                if (p == null) return;

                const refid = p['refid'];
                const dept_id = content.dept_id.getValue()

                const edit = new EditSignatory(refid, dept_id);
            });

            pay_menu.addItem(`<i class="fa fa-edit"></i> Edit Payroll Header`, async () => {
                const p = x_storage.getItem('payroll_data');
                if (p == null) return;

                const refid = p['refid'];
                const base = new PayrollBaseDeduction(refid);


                const d = await base.show();
                if (d != null)
                    reload_table({
                        "search": content.search.getValue(),
                        "dept_id": content.dept_id.getValue()
                    });
            });


            tool_box.add(pay_menu);
            // tool_box.add(edit_base_deduction);
            // tool_box.add(edit_signatory);
            // tool_box.add(payroll_print);
            // // tool_box.add(view_ob);
            // tool_box.add(view_ada);
            // tool_box.add(approve);


            var _ada_viewer = new Panel();
            tool_box.add(_ada_viewer);
            tool_box.add(approve_content);


            // payroll_print.addEventListener('click', async () => {
            //     const p = x_storage.getItem('payroll_data');
            //     if (p == null) return;

            //     const refid = p['refid'];
            //     const modal = new PayrollViewer({
            //         refid: refid,
            //         dept_id: content.dept_id.getValue()
            //     });

            //     await modal.show();
            // });

            // event for the print ada button
            // view_ada.addEventListener("click", function () {
            //     var p = x_storage.getItem('payroll_data');
            //     if (p == null) return;
            //     var refid = p['refid'];
            //     var dept_id = content.dept_id.getValue();


            //     _ada_viewer.clear();
            //     _ada_viewer.add(new AdaViewer(refid, dept_id).container());

            //     // the below implementation is for the future release
            //     // const ada = new AdaViewer2(refid, dept_id);
            //     // ada.show();
            // });

            this.panel.setStyle({
                overflowY: 'auto',
                position: 'relative'
            });

            this.panel.add(tool_box);
            this.panel.add(new Panel().setStyle({
                minHeight: "400px"
            }).add(table));
            this.panel.add(g_form.modal);

            this.menu.addClass("row");
            this.menu.control.style.marginBottom = "5px";

            var p1 = new Panel();
            p1.addClass("col-md-3");
            p1.addClass("p-2");
            p1.add(this.dept_id);

            var p2 = new Panel();
            p2.addClass("col-md-3");
            p2.addClass("p-2");
            p2.add(this.search);

            var p3 = new Panel();
            p3.addClass("col-md-3");
            p3.addClass("p-3")
            p3.add(this.qrcode);

            this.menu.add(p1);
            this.menu.add(p2);
            this.menu.add(p3);
        },
        draw: function () {
            return this.panel;
        }
    };

    var panel = new Panel();
    panel.control.style.padding = "5px";
    content.init();


    // load the department
    function loadDepartment() {
        content.dept_id.clear();
        AppHttp("/department/list", {}, null, function (o) {
            var res = JSON.parse(o);
            var data = res.data;
            content.dept_id.add("", "[All Department]");
            for (var i = 0; i < data.length; i++) {
                content.dept_id.add(data[i][0], data[i][1] + " - " + data[i][2]);
            }
        });
    }

    loadDepartment();

    content.search.addEventListener("change", function () {
        reload_table({
            "search": content.search.getValue(),
            "dept_id": content.dept_id.getValue()
        });
    });

    content.dept_id.addEventListener("change", function () {
        reload_table({
            "search": content.search.getValue(),
            "dept_id": content.dept_id.getValue()
        });
    });

    var process_data = function (data) {
        const loader = new MsgLoader('Retrieving dtr...');

        AppHttp("/api/hrms/dtr", { qrcode: data, refid: payroll_data.refid }, null, function (o) {
            var res = JSON.parse(o);
            //console.log(res);
            if (res.ok == 0 || res.ok == false) return loader.hide(res.msg, true);
            reload_table();
            loader.hide(res.msg);
        });
    };

    var scan_timeout = null;
    content.qrcode.addEventListener("keyup", function (e) {
        content.qrcode.control.style.backgroundColor = "red";
        content.qrcode.control.style.color = "rgba(0, 0, 0, 0)";
        // keycode 13 is the enter key ascii
        // 13 is the default of the qr code scanner and barcode scanner
        // clear the input after the scanner
        clearTimeout(scan_timeout);
        if (e.keyCode == 13) {
            // some of the qrcode is not working so we use the timeoutfunction 
            process_data(content.qrcode.getValue());
            content.qrcode.setValue("");
            content.qrcode.control.style.backgroundColor = "white";
            content.qrcode.control.style.color = "black";
        } else {
            scan_timeout = setTimeout(function () {
                process_data(content.qrcode.getValue());
                content.qrcode.setValue("");
                content.qrcode.control.style.backgroundColor = "white";
                content.qrcode.control.style.color = "black";
            }, 800);
        }
    });

    var is_connected = false;

    var qr_status_panel = new Panel();
    qr_status_panel.addClass("qr_status_panel");

    var dot = new Panel();
    qr_status_panel.add(dot);
    qr_status_panel.control.style.padding = "10px";

    var slabel = new Panel();
    slabel.control.style.fontSize = "5pt";
    slabel.control.style.fontWeight = "bold";
    slabel.control.style.marginLeft = "10px";
    qr_status_panel.add(slabel);

    var qr_status = function () {
        dot.removeClass("red-circle");
        dot.removeClass('green-circle');
        if (is_connected) {
            dot.addClass("green-circle");
            slabel.control.innerHTML = '<i class="fa fa-qrcode"></i> QR Code Connected!';
            slabel.control.style.color = "green";
        } else {
            dot.addClass("red-circle");
            slabel.control.innerHTML = '<i class="fa fa-qrcode"></i> QR Code Not Connected!';
            slabel.control.style.color = "red";
        }
    };


    content.qrcode.addEventListener("focusout", function () {
        is_connected = false;
        qr_status();
    });

    content.qrcode.addEventListener("focusin", function () {
        is_connected = true;
        qr_status();
    });

    var right_form = create_deduction_form();
    g_form.right_panel.add(right_form.form); // add the deduction form
    g_form.right_form = right_form.form;
    g_form.total_deduction = right_form.deduction_panel;
    g_form.net_pay = right_form.net;



    const top_menu = new DropDown(`<i class="fa fa-list"></i> Menu`, "default", "click to view the option");
    top_menu.addItem(`<i class="fa fa-arrow-left"></i> Back`, () => {
        appHome.setContent(PayrollPage(appHome), "Payroll");
    });
    top_menu.addItem(`<i class="fa fa-plus-circle"></i> New`, () => {
        is_update = false;
        g_form.left_form.clear();
        g_form.right_form.clear();
        g_form.modal.show();
    });
    top_menu.addItem(`<i class="fa fa-trash"></i> Delete Payroll`, () => {
        confirmBox.show('Are you sure?', deletePayrollCallBack);
    });

    // panel.add(content.back);
    // panel.add(content.nbtn);
    // panel.add(content.trash);
    const p = x_storage.getItem('payroll_data');
    let grefid = "";
    if (p == null) return;
    grefid = p['refid'];

    panel.add(top_menu);
    panel.add(new Label(`Refid: <span style="color: red;">${grefid}</span>`).setStyle({ marginLeft: "5px" }));
    panel.add(content.menu);
    panel.add(content.draw());
    panel.add(qr_status_panel);

    return panel;
};
