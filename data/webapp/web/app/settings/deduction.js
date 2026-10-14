// end deduction pages
import { Panel, Button, Form, Modal, Table, TextBox, CheckBox, ComboBox, RadioButton } from "../plugin/mcontrol.js";
import { AppHttp } from '../plugin/app.js';
import { messageBox, confirmBox } from "../main.js";
// start of the signatory page


export const PageDeduction = function () {

    var table = new Table([
        'Action',
        "Type",
        'Code',
        'Name',
        'Floor',
        'Ceil',
        'value',
        'View',
        'Active',
        '@',
        'Casual|Regular'
    ]);

    var dtype = {
        'a': 'Addional to Salary',
        'l': 'Loan',
        'c': 'Contribution'
    };
    var reload_table = function () {
        table.clear();
        AppHttp('/setting/deduction/list', {}, null, function (o) {

            var res = JSON.parse(o);
            if (res.ok == 0) return;

            var data = res.data;
            var data_len = data.length;
            var i = 0;



            do {

                // load the data table here
                var f = data[i];
                var remove = new Button(null, 'danger', 'trash');
                var edit = new Button(null, 'primary', 'edit').setStyle({ marginRight: '2px' }).setAttr({ rel: i });

                edit.addEventListener('click', function () {
                    var index = this.attributes.rel.nodeValue;
                    var fdata = data[index];

                    modal_content.clear();
                    modal_content.add(new ModalDed(fdata, 'update').getModal());
                });

                var menu = new Panel()
                    .add(edit)
                    .add(remove);

                remove.control.setAttribute('rel', i);
                remove.addEventListener('click', function () {
                    var index = this.attributes.rel.nodeValue;
                    var _data = data[index];

                    confirmBox.show('Are you sure?', function () {

                        AppHttp('/settings/deduction/remove', {
                            'code': _data.code,
                            'name': _data.name
                        },
                            null,
                            function (o) {
                                var data = JSON.parse(o);
                                if (data.ok == 1) {
                                    messageBox.show(data.msg, function () {
                                        reload_table();
                                    });
                                } else {
                                    messageBox.show(data.msg);
                                }
                            });

                    });

                });


                var check = new CheckBox();
                check.control.setAttribute('rel', i);
                if (f.active == 'y') {
                    check.setValue(true);
                }

                check.addEventListener('change', function () {
                    var index = this.attributes.rel.nodeValue;
                    var fdata = data[index];
                    var state = this.checked;
                    AppHttp("/settings/deduction/state", {
                        "code": fdata.code,
                        "name": fdata.name,
                        "state": state
                    }, null, function (res) {
                        var data = JSON.parse(res);
                        if (data.ok) {
                            messageBox.show(data.msg);
                        } else {
                            alert(data.msg);
                        }
                    });
                });

                var payroll_design = f.payroll_design;
                var panel = new Panel();

                var cas = new CheckBox();

                var reg = new CheckBox();

                var pd = JSON.parse(payroll_design);


                for (var u = 0; u < pd.length; u++) {
                    if (pd[u] == "r") {
                        reg.setValue(true);
                    }

                    if (pd[u] == "c") {
                        cas.setValue(true);
                    }
                }

                cas.control.setAttribute("rel", i);
                reg.control.setAttribute("rel", i);

                cas.addEventListener("change", function () {
                    var index = this.attributes.rel.nodeValue;
                    var fdata = data[index];

                    var is_checked = this.checked;

                    var tmp = JSON.parse(fdata.payroll_design);
                    if (!is_checked) {
                        for (var h = 0; h < tmp.length; h++) {
                            if (tmp[h] == "c") {
                                tmp.splice(h, 1);
                            }
                        }
                    } else {
                        tmp.push("c");
                    }

                    fdata.payroll_design = JSON.stringify(tmp);

                    status_state_change(fdata);
                });

                reg.addEventListener("change", function () {
                    var index = this.attributes.rel.nodeValue;
                    var fdata = data[index];

                    var is_checked = this.checked;

                    var tmp = JSON.parse(fdata.payroll_design);
                    if (!is_checked) {
                        for (var h = 0; h < tmp.length; h++) {
                            if (tmp[h] == "r") {
                                tmp.splice(h, 1);
                            }
                        }
                    } else {
                        tmp.push("r");
                    }

                    fdata.payroll_design = JSON.stringify(tmp);

                    status_state_change(fdata);
                });

                reg.control.style.marginLeft = "10px";
                panel.add(cas);
                panel.add(reg);



                table.add([
                    menu,
                    dtype[f.type],
                    f.code,
                    f.name,
                    f.floor,
                    f.ceil,
                    f.value,
                    f.view_only,
                    f.active,
                    check,
                    panel
                ]);

                i++;
            } while (i < data_len);

        });
    };

    var status_state_change = function (data) {
        AppHttp("/settings/deduction/status_change", {
            "name": data.name,
            "code": data.code,
            "status": data.payroll_design
        }, null, function (res) {
            var data = JSON.parse(res);
            messageBox.show(data.msg);
        });
    };

    reload_table();

    var ModalDed = function (data, ttype) {
        var data = data || null;

        var ttype = ttype || 'insert';

        if (data != null && typeof (data) != 'object') throw new TypeError('data must be a dictionary');

        var modal = new Modal("Form", "money");

        var form = new Form();
        form.add(new TextBox("CODE", "text", null, "Enter Deduction code"), "code");
        form.add(new TextBox("TITLE", "text", null, "Enter title"), "title");

        form.add(new TextBox("FLOOR", "text", null, null), 'floor');
        form.add(new TextBox('CEIL', 'text', null, null), 'ceil');
        form.add(new TextBox('VALUE', 'text', null, null), 'value');

        var is_view = new ComboBox(null, 'View Only', null, null);
        is_view.add('n', 'No');
        is_view.add('y', 'Yes');

        var active = new ComboBox(null, 'Activate', null, null);
        active.add('y', 'Yes');
        active.add('n', 'No');

        var type = new RadioButton("ded_type");
        type.add("Contribution", "c");
        type.add("Loan", "l");
        type.add('Additional Compensation', 'a');


        form.add(is_view, 'view');
        form.add(active, 'active');

        form.add(type, "type");


        var table = new Table(['bracket', 'fix_tax', 'from', 'to', 'rate_on_excess']);
        var spanel = new Panel()
            .add(table)
            .add(new Button(null, 'success', 'plus-circle')
                .addEventListener('click', function () {
                    table.add([
                        new TextBox(null, null, null, null, null),
                        new TextBox(null, null, null, null, null),
                        new TextBox(null, null, null, null, null),
                        new TextBox(null, null, null, null, null),
                        new TextBox(null, null, null, null, null)
                    ]);
                }));

        form.add(spanel);

        spanel.hide();



        if (data != null) {

            if (data.code.toLowerCase() == 'tax') {
                spanel.show();
            }

            var inputs = form.input;

            inputs.code.setValue(data.code);
            inputs.title.setValue(data.name);
            inputs.floor.setValue(data.floor);
            inputs.ceil.setValue(data.ceil);
            inputs.value.setValue(data.value);
            inputs.view.setValue(data.view_only);
            inputs.active.setValue(data.active);
            inputs.type.setValue(data.type);

            var bracket = [];

            if (data.bracket != '')
                bracket = JSON.parse(data.bracket);

            var bracket_len = bracket != null ? bracket.length : 0;

            for (var i = 0; i < bracket_len; i++) {
                var brack_input = new TextBox(null, null, null, null, null).setValue(bracket[i].bracket);
                var fix_tax = new TextBox(null, null, null, null, null).setValue(bracket[i].fix_tax);
                var from = new TextBox(null, null, null, null, null).setValue(bracket[i].from);
                var to = new TextBox(null, null, null, null, null).setValue(bracket[i].to);
                var excess = new TextBox(null, null, null, null, null).setValue(bracket[i].rate_on_excess);

                table.add([
                    brack_input,
                    fix_tax,
                    from,
                    to,
                    excess
                ]);
            }

        }

        var submit = new Button("SUBMIT", "primary", "save", "click to submit");
        submit.control.style.marginTop = "5px";
        form.add(submit);

        submit.addEventListener("click", function () {
            var data_table = table.getValue();

            var ndata = [];
            for (var i = 0; i < data_table.length; i++) {
                var dic = {
                    bracket: data_table[i][0],
                    fix_tax: data_table[i][1],
                    from: data_table[i][2],
                    to: data_table[i][3],
                    rate_on_excess: data_table[i][4]
                };

                ndata.push(dic);
            }

            var data = form.getValues();
            data['t_type'] = ttype
            data['t_bracket'] = ndata

            AppHttp('/setting/deduction/save', data, null, function (o) {
                var data = JSON.parse(o);
                alert(data.msg);
                if (data.ok) {
                    modal.hide();
                    reload_table();
                    return;
                }
            });
        });

        modal.add(form);
        modal.show();

        this.getForm = function () {
            return form;
        };

        this.getModal = function () {
            return modal;
        };
    };



    var panel = new Panel();


    var modal_content = new Panel();

    panel.addClass("card");
    panel.control.style.padding = "5px";

    var add = new Button("Add", "success", "plus-circle", "click to add new deduction");

    add.addEventListener("click", function () {
        modal_content.clear();
        modal_content.add(new ModalDed().getModal());
    });

    panel.add(add);
    panel.add(table);
    panel.add(modal_content);

    return panel;
};