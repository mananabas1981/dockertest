import { ModalV2, Grid, TextBox, Button, Panel, ComboBox } from '../plugin/mcontrol.js';
import { AppHttp2 } from './../classes/lib.js';
import { RecentTransaction } from './../component/recent_transaction.js';

export class RemittanceForm extends ModalV2 {

  constructor({ done = null }) {
    super('Remittance Form');

    this.setStyle({
      width: `${window.outerWidth - 100}px`
    });

    (async () => {


      const code = new ComboBox(null, 'Code');
      const name = new TextBox('Name', 'text');
      const from = new TextBox('From', 'date');
      const to = new TextBox('To', 'date');

      if (localStorage.getItem('from') != null) {
        from.setValue(localStorage.getItem('from'));
      }

      if (localStorage.getItem('to') != null) {
        to.setValue(localStorage.getItem('to'));
      }

      const collect_ded = {

      };

      const ded = await this.load_base_ded();

      for (const item of ded) {
        const { code, type } = item;
        if (type != 'a') {
          collect_ded[code] = code;
        }
      }

      for (let item in collect_ded) {
        code.add(item, item);
      }

      const create = new Button('Create Remittance', 'success', 'plus-circle').setStyle({
        marginTop: '3px',
        width: '100%'
      });

      const grid = new Grid(3);
      grid.cell(code, ['md-3']);
      grid.cell(name, ['md-3']);
      grid.cell(from, ['md-2']);
      grid.cell(to, ['md-2']);
      grid.cell(create, ['md-2']);


      this.panel = new Panel();
      this.panel.addClass('container-fluid');
      this.panel.add(grid);


      this.rc = new RecentTransaction({
          type: 'remittance'
      });

      this.add(this.panel);

      this.add(new Panel().setStyle({
          padding: '5px'
      }).add(this.rc));

      create.addEventListener('click', async () => {

        const refids = [];

        for (const item of this.rc.checks) {
          if (item.getValue()) {
            refids.push(item.control.attributes.key.nodeValue);
          }
        }


        const payload = {
          'refid': refids,
          'code': code.getValue(),
          'name': name.getValue(),
          'from': from.getValue(),
          'to': to.getValue()
        }

        const res = JSON.parse(await AppHttp2('/remittance/create/base', payload));

        if (done != null) {
          if (res.ok) {
            alert(res.msg);
            done(this);
          } else {
            alert(res.msg);
          }
        }

      });

      from.addEventListener('change', () => {
        localStorage.setItem('from', from.getValue());
      });

      to.addEventListener('change', () => {
        localStorage.setItem('to', to.getValue());
      });

    }) ();
  }

  async load_base_ded() {
    const res = JSON.parse(await AppHttp2('/setting/deduction/list'));
    return res.data;

    
  }

}