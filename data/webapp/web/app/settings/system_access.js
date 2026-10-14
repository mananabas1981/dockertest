import { Panel, Button, Form, Modal, Table, TextBox, ComboBox, CheckBox, Label } from "../plugin/mcontrol.js";
import { AppHttp } from '../plugin/app.js';
import { messageBox } from "../main.js";
import { AppHttp2 } from "../classes/lib.js";
import { UserForm } from './UserForm.js';
import { AccessForm } from './AccessForm.js';

// var UserForm = function (title, data, sys) {
//     var title = title || '';
//     var data = data || null; // data is useful insterm of the update of the user information
//     var sys = sys || null;

//     var modal = new Modal(title);

//     var name = new TextBox('name', 'text');
//     var username = new TextBox('Username', 'text');
//     var password = new TextBox('Password', 'password');
//     var gender = new ComboBox(null, 'Gender');
//     var dob = new TextBox('Date Of Birth', 'date');

//     const sign_id = new TextBox('Signature ID', 'text');
//     gender.add('m', 'Male');
//     gender.add('f', 'Female');
//     gender.add('o', 'Other');

//     var pos = new TextBox('Position', 'text');

//     var type = 'insert';

//     var submit_label = 'Add';
//     var uid = '';
//     if (data != null) {
//         submit_label = 'Update';
//         type = 'update';
//         // set the uid
//         uid = data.id;

//         name.setValue(data.name);
//         username.setValue(data.username);
//         gender.setValue(data.gender);
//         dob.setValue(data.dob);
//         sign_id.setValue(data.sign_id);
//     }

//     var submit = new Button(submit_label, 'success');
//     submit.control.style.marginTop = '5px';

//     submit.addEventListener('click', function () {
//         var data = form.getValues();
//         data['type'] = type;
//         data['uid'] = uid;
//         AppHttp('/user/save', data, null, function (o) {
//             var data = JSON.parse(o);
//             if (data.ok) {
//                 messageBox.show(data.msg, function () {
//                     if (sys != null) {
//                         sys.loadUser();
//                     }
//                 });
//             } else {
//                 alert(data.msg);
//             }
//         });
//     });

//     var form = new Form();


//     form.add(name, 'name');
//     form.add(gender, 'gender');
//     form.add(dob, 'dob');
//     form.add(pos, 'pos_title');
//     form.add(username, 'username');
//     form.add(password, 'password');
//     form.add(sign_id, 'sign_id');
//     form.add(submit);


//     modal.add(form);

//     modal.show();

//     if (data != null) {
//         // fillup the data for the update 
//         console.log(data);
//     }

//     this.getForm = function () {
//         return form;
//     };
//     this.container = function () {
//         return modal;
//     };
// };


var AccessList = function () {
    var panel = new Panel();



    this.container = function () {
        return panel;
    };

};


// var AccessForm = function (emp_id, systemAccess) {

//     var systemAccess = systemAccess || null;
//     var modal = new Modal("Access Roles of " + systemAccess.fname);

//     // load the access defaults

//     var drawTree = function (data) {
//         var data_len = data.length;

//         // this is the main tree
//         var panel = new Panel();
//         for (var i = 0; i < data_len; i++) {
//             var tree = data[i].tree;
//             var tree_len = tree.length;
//             var main_panel = new Panel();
//             var label = new Panel();
//             var next_panel = new Panel();
//             next_panel.control.style.paddingLeft = '50px';
//             label.control.innerHTML = '<i class="fa fa-cogs"></i> ' + data[i]['value'];
//             label.control.style.fontWeight = 'bold';
//             main_panel.add(label);
//             main_panel.add(next_panel);

//             for (var j = 0; j < tree_len; j++) {

//                 var s = new Panel();
//                 s.control.style.position = 'relative';
//                 s.control.style.padding = '5px';

//                 var check = new CheckBox(tree[j].check);
//                 check.control.style.cursor = 'pointer';
//                 check.control.setAttribute('code', tree[j].key);

//                 check.addEventListener('click', function () {
//                     var code = this.attributes.code.nodeValue;
//                     var is_check = this.checked;

//                     AppHttp('/user/access/state', { code: code, is_check, emp_id: emp_id }, null, function (o) {
//                         var data = JSON.parse(o);

//                         if (systemAccess != null) {
//                             systemAccess.loadUser();
//                         }
//                         if (!data.ok) {
//                             alert(data.msg);
//                         }

//                     });

//                 });

//                 check.control.style.position = 'absolute';
//                 check.control.style.left = '-20px';
//                 check.control.style.top = '0px';

//                 s.add(check);
//                 var label = new Label();
//                 label.control.innerHTML = '<i class="fa fa-cog"></i> ' + tree[j].value;
//                 s.add(label);
//                 next_panel.add(s);
//             }
//             panel.add(main_panel);
//         }
//         modal.add(panel);
//     };

//     const loadAccess = async function () {

//         const o = await AppHttp2('/user/default/access', { emp_id: emp_id }, null);
//         const data = JSON.parse(o);
//         if (data.ok) {
//             drawTree(data.data);
//         }

//     };

//     loadAccess();

//     this.container = function () {
//         return modal;
//     }
// };


// this is  system access main pages
export const SystemAccess = function () {


    var panel = new Panel();
    //panel.addClass("card");

    var content = new Panel();
    content.addClass('card');

    var new_user_btn = new Button('New User', 'success', 'plus-circle');
    new_user_btn.control.style.marginBottom = '5px'

    panel.add(new_user_btn);
    panel.add(content);

    var modal = new Panel();
    panel.add(modal);

    var self = this;
    this.fname = '';

    new_user_btn.addEventListener('click', async ()  => {
        const modal = new UserForm('Add New User', null, self);
        await modal.show();
    });

    const drawTable = (data) => {

        var data_len = data.length;

        var table = new Table(["Name", 'Username', 'Position', 'Date', 'Role', 'Access', 'Action']);

        for (let i = 0; i < data_len; i++) {
            let newbtn = new Button('Access', 'success', 'cogs');
            let edit = new Button('Edit', 'success', 'edit');

            edit.addEventListener('click', async () => {
                
                const info = data[i];

                const modal = new UserForm('Update User Information', info);
                const resolve = await modal.show();
                if (resolve) this.loadUser();
            });



            newbtn.addEventListener('click', function () {
                var index = this.attributes.rel.nodeValue;
                var emp_id = data[index].id;
                self.fname = data[index].name;

                //modal.clear();
                const ac = new AccessForm(emp_id, self);
                ac.show();
                // ac.container().show();
                // modal.add(ac.container());
            });


            edit.control.setAttribute('rel', i);
            newbtn.control.setAttribute('rel', i);

            newbtn.control.style.marginLeft = '2px';

            var panel = new Panel();
            panel.add(edit);
            panel.add(newbtn);

            // panel.add(new Button('Signature', 'success', 'pencil').setStyle({
            //     marginLeft: '5px'
            // }).addEventListener('click', async () => {
            //     const info = data[i];

            //     console.log(info);
            //     const modal = new SignModal(info.id, info.username, info.name);
            //     await modal.show();
            // }));

            table.add(
                [
                    data[i].name || "",
                    data[i].username || "",
                    data[i].pos_title || "",
                    data[i].datecreated || "",
                    data[i].role || "",
                    data[i].roles != null ? JSON.parse(data[i].roles).length + ' Roles granted!' : 'No Role granted!',
                    panel
                ]
            );
        }

        content.clear();
        content.add(table);
        return table;
    }

    this.loadUser = async function () {

        const o = await AppHttp2('/user/list', {});
        const data = JSON.parse(o);
        if (data.ok) drawTable(data.data);
    }

    this.loadUser();

    this.container = function () {
        return panel;
    }
};
