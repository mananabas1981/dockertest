import { AppHttp2 } from "../classes/lib.js";
import { FUND_CHARGES } from "../config.js";
import { confirmBox, messageBox } from "../main.js";
import { Panel, ModalV2, x_storage, Button, Form, TextBox, MsgLoader, ComboBox, Iframe, Label, Table } from "../plugin/mcontrol.js";
// edit form

// ObModal
export class ObModal extends ModalV2 {
    constructor(dept_id = '') {
        super('Ob-R Viewer', 'cog');
        this.dept_id = dept_id;
        this.frame = new Panel();
        this.data = '';
        this.init();
        this.add(this.frame);

        // print
        const print = new Button('Print', 'primary', 'print', 'click to print');
        print.addEventListener('click', async () => {
            const p = x_storage.getItem('payroll_data');
            if (p == null) return null;

            const refid = p['refid'];

            const loader = new MsgLoader("Requesting for printing...");
            const res = JSON.parse(await AppHttp2('/print/ob?v=print', { refid: refid, dept_id: this.dept_id, type: p['type'] }, null));

            const { ok, msg, data } = res;

            if (!ok) {
                loader.hide(`<span style="color: red;">${msg}</span>`);
                return;
            }

            loader.hide(msg);

            const win = window.open();
            win.document.write(data);

            setTimeout(() => {
                win.print();
                win.close();
            }, 500);
        });

        const update = new Button('Update', 'primary', 'edit', 'click to update').setStyle({ marginLeft: '5px' });
        update.addEventListener('click', async () => {
            const p = x_storage.getItem('payroll_data');
            const form = new ObForm(p['refid'], dept_id, p['type']);
            const res = await form.show();

            if (res != null) {
                this.load_frame(); // reload the info
            }
        });


        if (this.dept_id == '' || this.dept_id == null) {
            print.hide();
            update.hide();
        }

        const check_list = new Button('Check List', 'primary', 'list', 'click to view checklists').setStyle({ marginLeft: '5px' });
        check_list.addEventListener('click', () => {
            const p = x_storage.getItem('payroll_data');
            const refid = p['refid'];

            const check = new ObCheckList(refid);
            check.show();
        });

        this.add(print);
        this.add(update);
        this.add(check_list);

    }

    async init() {

        this.load_frame();
    }

    async load_frame() {

        this.data = await this.get_data();
        this.frame.clear();
        const frame = new Iframe().setStyle({
            width: '100%',
            height: '80vh'
        });
        frame.control.srcdoc = this.data;
        this.frame.add(frame);
        // this.frame.control.innerHTML = this.data;
    }

    async get_data() {
        const p = x_storage.getItem('payroll_data');
        if (p == null) return null;

        const refid = p['refid'];

        const loader = new MsgLoader('Fetching OB data...');
        const res = JSON.parse(await AppHttp2('/print/ob?v=view', { refid: refid, dept_id: this.dept_id, type: p['type'] }, null));
        loader.hide('Ob Data loaded!');

        this.show();

        if (res.ok == 0) return null;

        return res.data;
    }
}

// ObCheckList class

class ObCheckList extends ModalV2 {
    constructor(refid) {
        super('OB-R Checklist', 'list');
        this.refid = refid;

        this.panel = new Panel();
        this.add(this.panel);

        this.init(); // initialized the design 
    }

    async init() {
        const loader = new MsgLoader("Loading OB check list");
        const res = JSON.parse(await AppHttp2('/ob/check_list', { refid: this.refid }));
        loader.hide("Check list loaded!");

        if (!res.ok) return;

        this.panel.clear();

        const { msg, data } = res;

        const table = new Table(["status", "name", "Print Count"]);
        for (let item of data) {
            const { dept_code, dept_name, has_ob, dept_id } = item;

            table.add([
                new Panel()
                    .addClass(has_ob ? `alert-success` : `alert-danger`).setStyle({ padding: "5px" }).add(new Label(has_ob ? `<i class="fa fa-check"></i>` : `<i class="fa fa-close"></i>`)),
                new Label(`${dept_code} - ${dept_name}`),
                new Label("")
            ]);

        }

        this.panel.add(table);

    }

}

// update form class
class ObForm extends ModalV2 {
    constructor(payroll_code, dept_id, type = '') {
        super('Update', '');

        (async () => {

            const form = new Form();

            const fund = new ComboBox(null, 'Funds');

            const charges = FUND_CHARGES;

            for (let item of charges) {
                fund.add(item.key, item.value);
            }


            form.add(fund, 'fund');

            form.add(new TextBox('Particular', 'text'), 'particular');
            form.add(new TextBox('Account Code', 'text'), 'account_code');
            form.add(new TextBox('F.P.P', 'text'), 'fpp');

            form.add(new TextBox('Head Name', 'text'), 'head_name');
            form.add(new TextBox('Head Pos', 'text'), 'head_pos');

            const sign_id = new ComboBox(null, 'DIGITAL KEY');
            sign_id.add('', '[ SELECT DIGITAL KEY ]');

            form.add(sign_id, 'sign_id');

            form.add(new TextBox('No.: ', 'text'), 'ob_no');


            const sign_res = JSON.parse(await AppHttp2('/digital/signature/list'));
            if (sign_res.ok) {
                const sign_list = sign_res.data;
                const sign_list_len = sign_list.length;
                
                for (let i = 0; i < sign_list_len; i++) {
                    sign_id.add(sign_list[i]['id'], sign_list[i]['name']);
                }
            }
            

            form.add(new Button('Submit', 'primary', 'save').setStyle({
                marginTop: '5px'
            }).addEventListener('click', async () => {
                const payload = form.getValues();
                payload['payroll_code'] = payroll_code;
                payload['dept_id'] = dept_id;
                payload['type'] = type;

                const res = JSON.parse(await AppHttp2('/ob/update', payload, null));
                if (res.ok) {
                    alert(res.msg);
                    this.resolve = res.ok;
                    return;
                } 
                alert(res.msg);
            }));

            this.add(form);

            this.form = form;
            this.load(payroll_code, dept_id, type);


        })();
    }

    async load(payroll_code, dept_id, type) {
        const payload = {
            'payroll_code': payroll_code,
            'dept_id': dept_id,
            'type': type
        };

        const loader = new MsgLoader("Fetching ob");
        const res = JSON.parse(await AppHttp2('/ob/load', payload, null));
        loader.hide("Ob Loaded");

        const inputs = this.form.input;
        const data = res['data'];

        if (res.ok && data != null) {
            inputs['account_code'].setValue(data.account_code);
            inputs['particular'].setValue(data.particular);
            inputs['fpp'].setValue(data.fpp);
            inputs['head_name'].setValue(data.head_name);
            inputs['head_pos'].setValue(data.head_pos);

            inputs['fund'].setValue(data.fund_code);
            inputs['ob_no'].setValue(data.ob_no);
            inputs['sign_id'].setValue(data.sign_id);
        }

    }

}



/*

// printing of payroll
const p = x_storage.getItem('payroll_data');
                if (p == null) return;

                const refid = p['refid'];
                AppHttp('/print/ob', { refid: refid, dept_id: content.dept_id.getValue() }, null, function (o) {
                    const res = JSON.parse(o);
                    if (res.ok == 0) return;

                    const win = window.open();
                    win.document.write(res.data);
                    setTimeout(function () {
                        win.print();
                        win.close();
                    }, 444);

                });

*/


export class CloseOBR extends ModalV2 {
    constructor(refid) {
        super("Closing Obligation Requests", "close");
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
            
            const loader = new MsgLoader("Closing Obligation requests");
            const res = JSON.parse(await AppHttp2("/ob/close", payload));
            loader.hide(res.msg);
            
            if (res.ok) {
                messageBox.show(res.msg);
            } else {
                messageBox.show(`<span style="color: red;">${res.msg}</span>`);
            }
        }));
    }
}