import { AppHttp2 } from "../classes/lib.js";
import { Button, ComboBox, Grid, Label, ModalV2, MsgLoader, Panel, TextBox  } from "../plugin/mcontrol.js";

class HeaderCreator extends ModalV2 {
    constructor({done = null}) {
        super('Create Custom Header', 'edit');

        this.data = {
            'createdby': '',
            'datecreated': '1970-01-01 11:36:40',
            "payroll_design": "[\"rc\"]",
            "bracket": null
        };

        const code = new TextBox('Code', 'text');
        const name = new TextBox('name', 'text');
        const floor = new TextBox('floor', 'text');
        const ceil = new TextBox('ceil', 'text');
        const value = new TextBox('value', 'text');

        floor.setValue(0);
        ceil.setValue(0);
        value.setValue(0);

        const view_only = new ComboBox(null, 'view_only');
        view_only.add('n', 'No');
        view_only.add('y', 'Yes');
        
        const active = new ComboBox(null, 'Active');
        active.add('y', 'Yes');
        active.add('n', 'No');  

        const type = new ComboBox(null, 'Type');
        type.add('a', 'Additional To SALARY');
        type.add('c', 'Contribution');
        type.add('l', 'Loan'); 

        this.add(code);
        this.add(name);
        this.add(floor);
        this.add(ceil);
        this.add(value);
        this.add(view_only);
        this.add(active);
        this.add(type);

        this.add(new Button('SUBMIT', 'primary').setStyle({
            marginTop: '5px'
        }).addEventListener('click', () => {

            this.data['code'] = code.getValue();
            this.data['name'] = name.getValue();
            this.data['floor'] = floor.getValue();
            this.data['ceil'] = ceil.getValue();
            this.data['value'] = value.getValue();
            this.data['view_only'] = view_only.getValue();
            this.data['active'] = active.getValue();
            this.data['type'] = type.getValue();
            if (done != null) {
                done(this.data);
                this.hide();
            }
            this.resolve = this.data;
        }));
    }
}

export class PayrollBaseDeduction extends ModalV2 {
    constructor(refid) {
        super("Payroll Header Contribution and Deduction", "edit");

        this.refid = refid;


        this.data = [];
        this.base_data = [];
        this.panel = new Panel().addClass("list-group");

        this.cm = new ComboBox(null, "Select Addional Contrib and Deduction").setStyle({
            marginBottom: "5px"
        });

        this.add(this.cm);
        this.add(new Button("Add", "success", "plus-circle").addEventListener("click", () => {
            const index = this.cm.getValue();
            const one = this.base_data[index];
            this.data.push(one);
            this.draw();
        }).setStyle({
            marginBottom: "5px"
        }));

        this.add(new Button('Add Custom', 'default', 'plus').setStyle({
            marginBottom: '5px'
        }).addEventListener('click', () => {
            const h = new HeaderCreator({
                done: (data) => {
                    this.data.push(data);
                    this.draw();
                }
            });
            h.show();
        }));

        this.add(this.panel);
        this.add(new Button("Submit", "type", "save").addEventListener("click", async () => {
            const payload = this.data;
            const loader = new MsgLoader("Updating the base contribution and deduction");
            const res = JSON.parse(await AppHttp2("/payroll/info/update", { refid: this.refid, data: payload }));
            loader.hide("Update Completed!");
            if (res.ok) this.resolve = true;

        }));
        this.init();
        this.load();
    }
    async init() {
        this.base_data = JSON.parse(await AppHttp2("/setting/deduction/list", {}, null)).data;

        for (let i = 0; i < this.base_data.length; i++) {
            const { code, name } = this.base_data[i];
            this.cm.add(i, `${code} - ${name}`);
        }
    }
    async load() {
        const data = JSON.parse(await AppHttp2("/payroll/info", { refid: this.refid }));
        if (!data.ok) return;

        this.data = data.data;
        this.draw();
    }
    draw() {
        this.panel.clear();

        const data_len = this.data.length;

        for (let i = 0; i < data_len; ++i) {
            const { code, name } = this.data[i];

            const panel = new Panel().addClass("list-group-item");

            panel.add(new Button(null, "default", "close").addEventListener("click", () => {
                if (!confirm("Removed?")) return;
                this.data.splice(i, 1);
                this.draw();
            })).add(new Label(`${code} - ${name}`).setStyle({ marginLeft: "5px" }));

            this.panel.add(panel);
        }
    }
}