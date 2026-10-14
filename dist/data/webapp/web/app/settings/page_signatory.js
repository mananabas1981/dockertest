// end deduction pages
import { Panel, Button, Form, Modal, Table, TextBox, CheckBox } from "../plugin/mcontrol.js";
import { AppHttp } from '../plugin/app.js';
import { messageBox } from "../main.js";
import { SignForm } from './SignForm.js';

// start of the signatory page
export const PageSignatory = function () {

    var table = new Table(["Action", "Name", "Position", "Info", "Active", "Casual|Regular"]);

    var is_form_update = false;
    var update_data = null;

    var UpdateStatus = function (data, is_check, type) {

        var type_arr = JSON.parse(data["type"]);

        for (var i = 0; i < type_arr.length; i++) {
            if (type_arr[i] == type) {
                type_arr.splice(i, 1);
            }
        }

        if (is_check) {
            type_arr.push(type);
        }

        data["type"] = JSON.stringify(type_arr);

        AppHttp("/settings/sign/type/change", {
            name: data["name"],
            certify: data["certify"],
            type: type_arr
        }, null, function (res) {
            var data = JSON.parse(res);
            console.log(data);
        });
    };

    var ReloadTable = function () {
        table.clear();
        AppHttp("/settings/sign/list", {}, null, function (res) {

            var o = JSON.parse(res);

            var data = o.data;
            var data_len = data.length;

            for (var i = 0; i < data_len; i++) {

                var d = data[i];
                var active = new CheckBox();
                active.control.setAttribute("rel", i);
                active.addEventListener("click", function () {
                    var index = this.attributes.rel.nodeValue;
                    var f = data[index];
                    var check = this.checked;

                    AppHttp("/settings/sign/active/change", {
                        "name": f.name,
                        "certify": f.certify,
                        "check": check
                    }, null, function (res) {
                        var data = JSON.parse(res);
                        if (data.ok) {
                            messageBox.show(data.msg);
                        } else {
                            alert(data.msg);
                        }
                    });
                });

                if (d.active == 'y') {
                    active.setValue(true);
                } else if (d.active == 'n') {
                    active.setValue(false);
                }

                var panel = new Panel();
                panel.control.style.textAlign = "center";
                var cas = new CheckBox();
                var reg = new CheckBox();
                reg.control.style.marginLeft = "5px";

                cas.control.setAttribute("rel", i);
                reg.control.setAttribute("rel", i);

                var __types = JSON.parse(data[i]["type"]);

                for (var j = 0; j < __types.length; j++) {

                    if (__types[j] == "r") {
                        reg.setValue(true);
                    }

                    if (__types[j] == "c") {
                        cas.setValue(true);
                    }

                }

                cas.addEventListener("click", function () {

                    var index = this.attributes.rel.nodeValue;
                    var f = data[index];
                    UpdateStatus(f, this.checked, "c");

                });

                reg.addEventListener("click", function () {

                    var index = this.attributes.rel.nodeValue;
                    var f = data[index];
                    UpdateStatus(f, this.checked, "r");

                });

                panel.add(cas);
                panel.add(reg);

                var action_panel = new Panel();
                var edit = new Button("Edit", "success", "edit", null);
                edit.control.setAttribute("rel", i);
                edit.addEventListener("click", async function () {
                    var index = this.attributes.rel.nodeValue;
                    var _data = data[index];

                    // update_data = _data;
                    // is_form_update = true;

                    // var input = form.input;
                    // input.certify.setValue(_data.certify);
                    // input.name.setValue(_data.name);
                    // input.pos_title.setValue(_data.pos_title);
                    // input.sign_id.setValue(_data.sign_id);

                    // const _index = JSON.parse(_data.index);
                    // input.index.setValue(_index[0] + "," + _index[1]);

                    const sign_form = new SignForm(_data);
                    const res = await sign_form.show();
                    if (res != null) ReloadTable();

                });

                action_panel.add(edit);

                table.add([
                    action_panel,
                    d["name"],
                    d["pos_title"],
                    d["certify"],
                    active,
                    panel
                ]);

            }

        });
    };

    ReloadTable();

    // var SignForm = function () {
    //     var modal = new Modal("Signatory Form");

    //     var form = new Form();


    //     var certify = new TextBox("Certify", "text", "");
    //     var name = new TextBox("Name", "text", null);
    //     var pos_title = new TextBox("Position", "text", null);
    //     var pos_index = new TextBox("Index", "text", null, null, "0,0");

    //     const sign_id = new TextBox('Signature ID', 'text', null, null);
    //     var submit = new Button("Save", "success", "plus-circle");

    //     submit.control.style.marginTop = "10px";

    //     submit.addEventListener("click", function () {
    //         var data = form.getValues();

    //         data["is_update"] = is_form_update

    //         if (is_form_update)
    //             data["datecreated"] = update_data["datecreated"]

    //         is_form_update = false;

    //         AppHttp("/setting/sign/save", data, null, function (res) {
    //             var data = JSON.parse(res);
    //             if (data.ok) {
    //                 messageBox.show(data.msg);
    //                 modal.hide();
    //                 ReloadTable();
    //             } else {
    //                 alert(data.msg);
    //             }
    //         });
    //     });

    //     form.add(certify, "certify");
    //     form.add(name, "name");
    //     form.add(pos_title, "pos_title");
    //     form.add(pos_index, "index");
    //     form.add(sign_id, 'sign_id');

    //     form.add(submit);
    //     modal.add(form);
    //     return {
    //         "form": form,
    //         "modal": modal
    //     };
    // };

    
    // var modal = _sign_form.modal;
    // var form = _sign_form.form;


    var panel = new Panel();
    panel.addClass("card");
    panel.control.style.padding = "5px";
    var newsign = new Button("New Signatory", "success", "pen");

    newsign.addEventListener("click", async () => {
        is_form_update = false;
        update_data = null;
        // form.clear();
        // modal.show();
        const sign_form = new SignForm();
        const res = await sign_form.show();
        if (res != null) ReloadTable();
    });

    panel.add(newsign);
    // panel.add(modal);
    panel.add(table);

    return panel;
};
// end of the signatory page
