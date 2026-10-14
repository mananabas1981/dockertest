import { AppHttp2 } from "../classes/lib.js";
import { Button, Grid, ModalV2, MsgLoader, Panel, TextBox, ComboBox } from "../plugin/mcontrol.js";

export class EditSignatory extends ModalV2 {
    constructor(refid, dept_id) {
        super('Edit Signatory', 'pencil');

        this.index = 0;

        this.refid = refid;
        this.dept_id = dept_id;

        this.panel = new Panel().addClass('container-fluid');
        this.add(this.panel);

        this.form = [];

        this.add(new Button(null, 'success', 'plus-circle').setStyle({ marginTop: '10px', marginRight: '10px' }).addEventListener('click', () => {
            this.panel.add(this.create_grid());

        }));

        this.add(new Button('Submit Edit', 'success', 'save').setStyle({ marginTop: '10px' }).addEventListener('click', async () => {
            const data = [];
            for (let item of this.form) {
                data.push({
                    n: item.n.getValue(),
                    p: item.p.getValue(),
                    c: item.c.getValue(),
                    sign_key: item.sign_key_in.getValue(),
                    sign_val: item.sign_val_in.getValue(),
                    sign_date: item.sign_date_in.getValue()
                });
            }
            const payload = {
                data: data,
                refid: this.refid,
                dept_id: this.dept_id
            };
            const load = new MsgLoader('Saving....');
            const res = JSON.parse(await AppHttp2('/payroll/signatory/default/submit', payload));
            load.hide(res.msg, !res.ok);

        }));

        this.sign_list = [];
        this.digital_sign();

        this.load_sign();
    }

    async digital_sign() {
        const data = JSON.parse(await AppHttp2('/digital/signature/list'));
        this.sign_list = data.data;

    }

    async load_sign() {
        this.panel.clear();

        const load = new MsgLoader('Loading signatory list...')
        const res = JSON.parse(await AppHttp2('/payroll/signatory/default/load', {
            refid: this.refid,
            dept_id: this.dept_id
        }));
        load.hide('Signatory loaded!');

        this.show();

        const data = res.data;

        for (let item of data) {
            const { n, p, c, sign_date, sign_key, sign_val} = item;

            this.panel.add(this.create_grid(n, p, c, sign_date, sign_key, sign_val));
        }

    }

    create_grid(n = '', p = '', c = '', sign_date = '', sign_key = '', sign_val) {
        const name = new TextBox('Name', 'text').setValue(n);
        const pos = new TextBox('Position', 'text').setValue(p);
        const fun = new TextBox('Function', 'text').setValue(c);

        const sign_date_in = new TextBox('Sign Date', 'text');
        const sign_key_in = new ComboBox(null, 'Sign Key', 'text');

        sign_key_in.add('', '[SELECT SIGNATORE]');
        for (let item of this.sign_list) {
            sign_key_in.add(item.id, item.name);
        }
        sign_key_in.setValue(sign_key);

        const sign_val_in = new TextBox('Sign Val', 'text');

        const index = this.index++;

        const grid = new Grid(2)
            .cell(name, ['md-2'])
            .cell(pos, ['md-2'])
            .cell(fun, ['md-2'])
            .cell(sign_key_in, ['md-2'])
            .cell(sign_date_in, ['md-1'])
            .cell(sign_val_in, ['md-2'])
            .cell(new Button(null, 'default', 'close', 'click to remove').addEventListener('click', () => {
                let form_len = this.form.length;
                for (let i = 0; i < form_len; i++) {
                    if (this.form[i].key == index) {
                        this.form[i].grid.clear();
                        this.form.splice(i, 1);
                        break;
                    }
                }
            }), ['md-1']);

        const panel = new Panel().add(grid);
        this.form.push({
            key: index,
            n: name,
            p: pos,
            c: fun,
            sign_key_in,
            sign_val_in, 
            sign_date_in,
            grid: panel
        });

        return panel;
    }
}