import { AppHttp2 } from "../classes/lib.js";
import { ModalV2, Label, Panel, TextBox, Form, Button, Modal } from "../plugin/mcontrol.js";

export class ActiveModal extends ModalV2 {
    constructor(id, name, status) {
        super('Employee Status', 'user');

        this.id = id;
        this.name = name;
        this.status = status;

        this.add(new Label(`Sys Id: ${id}`));
        this.add(new Panel());
        this.add(new Label(`Name: ${name.toUpperCase()}`).setStyle({
            letterSpacing: '2px'
        }));
        this.add(new Panel());
        this.add(new Label(`Status: ${status == 'y' ? '<span style="background-color: green; padding: 2px;color: white;">Active</span>' : '<span style="background-color: red; padding: "2px; color: white;"">Not Active</span>'}`));

        this.add(new Panel());


        this.init();
    }

    init() {



        const active = new Button(`${this.status == 'y' ? 'Deactivate' : 'Activate'}`, 'default', 'check', 'click to if employee is active');


        active.addEventListener('click', async () => {
            if (this.status == 'y') {
                const status = new ActiveForm(this.id, this.name, this.status);
                const r = await status.show();
                if (r != null) {
                    this.resolve = true;
                }
            }
        });

        this.add(active);

    }
}

class ActiveForm extends ModalV2 {
    constructor(id, name, status) {

        super(`Activation Form - ${name.toUpperCase()}`);

        this.id = id;
        this.name = name;
        this.status = status;

        this.add(new Label(`Reason for ${status == 'y' ? 'Deactivation' : 'Activation'}`));

        this.form = new Form();
        this.form.add(new TextBox('Remark', 'text'), 'remark');
        this.form.add(new TextBox('Date Effect', 'date'), 'from');

        this.add(this.form);
        this.add(new Button('submit', 'default', 'save').addEventListener('click', async () => {
            const payload = this.form.getValues();
            payload['emp_id'] = this.id;

            if (payload.remark.trim() == '') return alert('remark is required!');
            if (payload.from.trim() == '') return alert('date is required!');

            const res = JSON.parse(await AppHttp2('/employee/status/change', payload, null));

            this.resolve = true;
            this.hide(true);
        }).setStyle({
            marginTop: '5px'
        }));

        this.init();
    }

    init() {

    }
}