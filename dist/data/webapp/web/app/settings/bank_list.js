import { Panel, Button, Form, Modal, Table, TextBox } from "../plugin/mcontrol.js";
import { AppHttp } from '../plugin/app.js';
import { messageBox, confirmBox } from "../main.js";

export const BankList = function () {
    var panel = new Panel();
    panel.addClass("card");
    panel.control.style.padding = "5px";
    // list of bank
    var bank_table = new Table(["Date", "Code", "Name", "Regex"]);
    var load_bank_table = function () {
        AppHttp("/bank/list", {}, null, function (o) {
            var res = JSON.parse(o);
            var data = res.data;
            var data_len = data.length;
            bank_table.clear();
            for (var i = 0; i < data_len; i++) {
                var code = data[i][0];
                var name = data[i][1];
                var regex = data[i][2];
                var date = data[i][3];
                var remove = new Button(null, "danger", "trash", "click to remove the bank");
                remove.control.setAttribute("rel", i);
                remove.addEventListener("click", function () {
                    var code = data[this.attributes.rel.nodeValue][0];
                    confirmBox.show("Remove this bank?", function () {
                        AppHttp("/bank/remove", { code: code }, null, function (o) {
                            var data = JSON.parse(o);
                            if (data.ok == 1) {
                                messageBox.show(data.msg, function () {
                                    load_bank_table();
                                });
                            } else {
                                messageBox.show(data.msg);
                            }
                        });
                    });
                });
                bank_table.add([date, code, name, regex, remove]);
            }
        });
    };
    load_bank_table();
    // end list of bank

    // modal
    var bank_form = function () {


        var is_valid_branch = function (name) {
            return /^[A-Z0-9\Ñ\,\. ]+[;]{1}[A-Z0-9\Ñ\. ]+[;]{1}[A-Z0-9\Ñ\. ]+[;]{1}[A-Z0-9\Ñ\. ]+[;]{1}[A-Z0-9\Ñ\,\. ]+$/.test(name)
        };

        var modal = new Modal("Bank Information");
        var form = new Form();

        var type = new TextBox("Code", "text", null, "bank code sample (DPB, PNB, FCB, etc...)", "Bank Code");
        var name = new TextBox("Name", "text", null, null, "Enter fullname of the bank");

        var branch_head = new TextBox("Branch Head", "text", null, "PREFIX;FIRSTNAME;MIDDLENAME;LASTNAME;SUFFIX -> ex: MR.;JOHN;T.;DOE;JR.,PHD.,LPT", "PREFIX;FIRSTNAME;MIDDLENAME;LASTNAME;SUFFIX");

        var regex = new TextBox("Acc No. Regex", null, null, null, "Regex bank number validation");

        var submit = new Button("Submit", "success", "save");
        submit.control.style.marginTop = "2px";

        submit.addEventListener("click", function () {
            var data = form.getValues();
            if (data["branch_head"] != "") {
                if (!is_valid_branch(data["branch_head"])) {
                    messageBox.show('<span style="color:red;">Branch Head Pattern Invalid</span>');
                    return;
                }
            }

            AppHttp("/bank/save", data, null, function (o) {
                var data = JSON.parse(o);
                if (data.ok == 1) {
                    messageBox.show(data.msg, function () {
                        // reload table and close the modal
                        modal.hide();
                        load_bank_table();
                    });
                } else {
                    messageBox.show(data.msg);
                }
            });
        });

        form.add(type, "code");
        form.add(name, "name");
        form.add(regex, "regex");
        form.add(branch_head, "branch_head");

        form.add(submit);
        modal.add(form);
        return {
            getForm: function () {
                return form;
            },
            getModal: function () {
                return modal;
            }
        }
    };
    // end modal

    var bank_obj = bank_form();
    var _bank_form = bank_obj.getForm();
    var _bank_modal = bank_obj.getModal();

    var newBank = new Button("Add Bank", "success", "plus-circle");
    newBank.addEventListener("click", function () {
        _bank_modal.show();
    });

    panel.add(newBank);
    panel.add(_bank_modal);
    panel.add(bank_table);
    return panel;
};