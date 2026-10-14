
import { Panel, MsgLoader, Table, Button, Label, x_storage, ComboBox, CheckBox } from '../plugin/mcontrol.js';
import { AppHttp2 } from './../classes/lib.js';
import { PayrollViewer } from './../component/payroll.js';
import { date_string1 } from './../util/date.js';

export class RecentTransaction extends Panel {
  constructor({ type = '' }) {
    super();
    this.type = type;

    this.panel = new Panel();

    this.checks = [];

    (async () => {
      this.yr_combo = new ComboBox(null, 'Year');

      await this.loadTransaction();

      this.setStyle({
        marginTop: '2px'
      });

      this.panel.addClass('card');

      
    
      const cyr = new Date().getFullYear();

      for (let i = cyr; i >= 2023; i--) {
        this.yr_combo.add(i, i);
      }

      this.yr_combo.addEventListener('change', async () => await this.loadTransaction());

      this.add(this.yr_combo);
      this.add(this.panel.setStyle({ marginTop: '5px' }));
    })();
  }

  dispose() {
    console.log("calling the disposed method from recent");
  }

  async loadTransaction() {

    this.checks = [];

    const type_t = {
      'j': `<span class="badge" style="background-color: #6767ff;">JOB ORDER</span>`,
      'c': `<span class="badge" style="background-color: orange;">CONTRACT OF SERVICE</span>`,
      'r': `<span class="badge" style="background-color: #6bcf6b;">REGULAR&nbsp;&nbsp;&nbsp;</span>`
    };

    this.panel.clear();

    const loader = new MsgLoader('Getting latest transaction');
    const gdata = JSON.parse(await AppHttp2('/payroll/list', { date: `${this.yr_combo.getValue()}`, type: '' }));
    loader.hide('Transaction loaded!');

    if (!gdata.ok) { alert(gdata.msg); return; }

    const data = gdata.data;
    const data_len = data.length;
    // create table
    const table = new Table(['ACTION', 'REF', 'NAME', 'STATUS', 'ATM','']);

    for (let i = 0; i < data_len; i++) {
      const { name, refid, total_item, status, from, to, type, ago, atm_info } = data[i];
      let bank_code = "";
            
      if (atm_info != null && "code" in atm_info) {
        bank_code = atm_info["code"];
      }


      let status_htm = '';

      if (!status) {
        status_htm = '<span class="badge" style="background-color: #eb9800;">Payroll Created!</span>';
      } else {
        const stat = JSON.parse(status);
        const stat_len = stat.length;

        const last_step = stat[stat_len - 1].step;


        const last_status = stat[stat_len - 1].remark;
        
        let bgcolor = ''
        if (last_step == 0)
          bgcolor = 'background-color: orange;';
        else if (last_step == 6)
          bgcolor = 'background-color: #ed6aa8;';
        else if (last_step == 2)
          bgcolor = 'background-color: blue;';
        else if (last_step == 4)
          bgcolor = 'background-color: green;';
        else if (last_step == 5)
          bgcolor = 'background-color: #ddd';
        else if (last_step == 7)
          bgcolor = 'background-color: brown;'

        status_htm = `<span class="badge" style="${bgcolor}">${last_status}</span>`;
      }

      let ac = null;

      if (this.type == 'remittance') {
          
        const check = new CheckBox();
        check.control.setAttribute('key', refid);

        this.checks.push(check);

        ac = new Panel().add(check);
        ac.add(new Label(`${total_item} items`).addClass('badge').setStyle({marginLeft: '5px', backgroundColor: 'orange', color: 'white'}));
        
      } else {
        ac = new Button(`VIEW <span class="badge">${total_item}</span>`, 'default', 'folder-open')
          .setStyle({
            width: '140px',
            textAlign: 'left'
          })
          .addEventListener('click', async () => {
            x_storage.setItem('payroll_data', data[i]);
            const p = new PayrollViewer({
              refid: refid,
              dept_id: '',
              show_all: true
            });

            const a = await p.show();
            if (a != null) {
              await this.loadTransaction();
            }

        });
      }

      table.add([
        ac,
        new Label(`<span style="color: red;">${refid}</span>`),
        new Label(`${type_t[type]} | <span style="color: #ff6969; text-decoration: underline;">${date_string1(from)}</span> - <span style="color: #ff6969; text-decoration: underline;">${date_string1(to)}</span> : <span style="color: #6a6a6a;">${name}</span> 
          <br /> <span style="font-size: 10px; color: grey;">(Created ${ago} ago)</span>`),
        new Label(status_htm),
        new Label(`<div style="padding: 10px;width: 100px; text-align:center; color: white; background-color: #00a1ff; border-radius: 5px;">${bank_code}</div>`),
        new Label('')
      ]);
    }

    this.panel.add(table);
  }
}