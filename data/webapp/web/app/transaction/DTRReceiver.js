import { Panel, ModalV2, TextBox, Table, Button, Label, Iframe, MsgLoader } from '../plugin/mcontrol.js';
import { AppHttp2 } from './../classes/lib.js';


class DtrInfoPrintView extends ModalV2 {
  constructor(data) {
    super("DTR Report Preview", "file-pdf-o");
    
    const frame = new Iframe().setStyle({
      width: "100%",
      height: "75vh"
    });
    
    frame.control.srcdoc = data;

    const submit = new Button("Print", "primary", "print");
    this.add(frame);
    this.add(submit);

    submit.addEventListener("click", () => {
      const win = window.open();

      win.document.write(data);
      setTimeout(() => {
        win.focus();
        win.print();
        win.close();
      }, 1000);
    });
  }
}

class DtrReport extends ModalV2 {
  constructor() {
    super("DTR Received Reports", "file-pdf-o");
    
    const from_t = new TextBox("From", "date");
    const to_t   = new TextBox("To", "date");


    const submit = new Button("Generate", "success", "refresh").setStyle({
      marginTop: "5px"
    });
    
    this.add(from_t);
    this.add(to_t);
    this.add(submit);

    submit.addEventListener("click", async () => {
      const payload = {
        from: from_t.getValue(),
        to: to_t.getValue()
      };
      
      const loader = new MsgLoader("Creating a reports...");
      const res = JSON.parse(await AppHttp2("/dtr/regular/reports", payload));
      if (res.ok) {
        const r = new DtrInfoPrintView(res.data);
        r.show();
      }

      loader.hide("Done!");



    }); 
    
  }
  

}

class DtrInfo extends ModalV2 {
  constructor(param = {}) {
    super('DTR Info', 'calendar');

    this.absent = new TextBox('Absent (day)', 'text');
    this.late = new TextBox('Late (min)', 'text');
    this.ut = new TextBox('UnderTime (min)');
    this.total_leave = new TextBox('Total Leave Deduction', 'text').setStyle({
      marginTop: '20px'
    });



    (async () => {

      const { 
        code = '',
        is_update = false, 
        dtr_data = [], 
        header = {}, 
        from = '', 
        to = '', 
        emp_id = '', 
        hr_id = '',
        name = '',
        late = 0.0,
        ut = 0.0,
        status = 0
      } = param;

      const table = new Table([ 'Info', 'value' ]);

      let _code = code;

      if (!is_update) {
        // create new data
        const res = JSON.parse(await AppHttp2('/dtr/create/transaction/code', {
          data: dtr_data,
          header: header,
          from: from,
          to: to,
          emp_id: emp_id,
          hr_id: hr_id
        }));

        if (!res.ok) {
          this.resolve = false;
          return alert(res.msg);
        }

        _code = res.code;

        table.add([ 'ref', _code ], [ {fontWeight: 'bold', width: '80px'}, { color: 'red', fontWeight: 'bold' } ]);
        table.add([ 'name', name ]);
        table.add([ 'range', `${from} to ${to}` ]);
        table.add([ 'Warning', '<span style="color: red;">Please Check the absent, late, undertime carefully!</span>' ]);
        table.add([ 'Status',  status == 0 ? '<span style="padding: 5px;color: white;  background-color: red;">Processing</span>' : '<span style="color: white; background-color: green; padding: 5px;">Approved</span>']);

        this.late.setValue(late);
        this.ut.setValue(ut);

        this.compute_leave();
      } else {
        // if update
        _code = code;
        table.add([ 'ref', _code ], [ {fontWeight: 'bold', width: '80px'}, { color: 'red', fontWeight: 'bold' } ]);
        table.add([ 'name', name ]);
        table.add([ 'range', `${from} to ${to}` ]);
        table.add([ 'Warning', '<span style="color: red;">Please Check the absent, late, undertime carefully!</span>' ]);
        table.add([ 'Status',  status == 0 ? '<span style="padding: 5px;color: white;  background-color: red;">Processing</span>' : '<span style="color: white; background-color: green; padding: 5px;">Approved</span>']);

        this.late.setValue(late);
        this.ut.setValue(ut);

        this.compute_leave();
      }

      this.resolve = true;

      this.add(table);

      

      this.absent.addEventListener('keyup', () => { this.compute_leave() });
      this.late.addEventListener('keyup', () => { this.compute_leave() });
      this.ut.addEventListener('keyup', () => { this.compute_leave() });

    
      const submit = new Button('Submit', 'primary').setStyle({
        marginTop: '5px'
      });

      this.add(new Panel().addClass('card').setStyle({
        padding: '10px'
      }).add([
        this.absent, this.late, this.ut, this.total_leave, submit
      ]));

      submit.addEventListener('click', async () => {
        if (!confirm('Submit?')) return;

        this.compute_leave();

        const payload = {
          code: _code,
          absent: this.absent.getValue(),
          late: this.late.getValue(),
          ut: this.ut.getValue(),
          total_leave: this.total_leave.getValue()
        };

        const res = JSON.parse(await AppHttp2('/dtr/approve', payload));

        if (!res.ok) return alert(res.msg);

        alert(res.msg);
        this.resolve = true;

        this.hide(true);

      });

    })(); // anon function

  }

  compute_leave() {
    const perday = 1.0;
    const perhour = perday / 8.0; // leave credit for 1 day
    const permin = (perhour / 60.0); // per minute leave credit

    let absent = this.absent.getValue().trim();
    let late = this.late.getValue().trim();
    let ut = this.ut.getValue().trim();

    let total = 0.0;

    absent = absent != '' ? parseFloat(absent) : 0.0;
    late = late != '' ? parseFloat(late) : 0.0;
    ut = ut != '' ? parseFloat(ut) : 0.0;



    total += perday * absent;
    total += late * permin;
    total += ut * permin;

    this.total_leave.setValue(total.toFixed(3));
  }
}

class DTRReceiver extends Panel {
  constructor(appHome) {
    super();
    
    this.setStyle({
      padding: '10px'
    });

    const text = new TextBox('QRCode Scanner for DTR', 'password', 'qrcode', 'Scan DTR QrCode here!', 'Scan DTR QrCode here!');

    const rpt = new Button('Reports', 'success', 'file-pdf-o', 'click to generate report');
    
    this.add(rpt);

    this.add(text);


    this.card = new Panel().addClass('card').setStyle({
      marginTop: '5px'
    });

    text.addEventListener('keyup', (e) => {
      const value = text.getValue();
      if (e.keyCode == 13) {
        // if the enter key is pressed,,
        // the barcode scanner has a feature where after the data collected from the qrcode
        // then it has the end of enter, where the enter key is equivalent to 13 in keycode in programming

        text.setValue('');

        // connecting the the server for qrcode scanning
        (async () => {
          const loader = new MsgLoader('Getting DTR Information....');
          const res = JSON.parse(await AppHttp2('/api/hrms/dtr/info', { 'qrcode': value }));
          loader.hide('DTR loaded!');

          if (!res.ok) return alert(res.msg);
          if (res.data.length == 0) return alert(res.msg);
          
          const data = res.data;

          const dtr_data = data.dtr;
          const dtr_header = data.header;

          if (!dtr_header['valid'][0]) return alert('The Position Status Expired please check!');

          const dtr = new DtrInfo({
            dtr_data: dtr_data,
            header: dtr_header,
            from: dtr_header.range[0],
            to: dtr_header.range[1],
            hr_id: dtr_header.emp_id,
            emp_id: dtr_header.payroll_emp_id,
            name: dtr_header.name.fullname2,
            late: dtr_header.total_late,
            ut: dtr_header.total_undertime
          });
          const r = await dtr.show();
          if (r == null) return;
          await this.loadTable();

        })();
      }
    });


    rpt.addEventListener('click', async () => {
      
      const rpt = new DtrReport();

      await rpt.show();
      
    });


    ( async () => {
      await this.loadTable();
    })();    
    this.add(this.card);
  }

  async loadTable() {
    const res = JSON.parse(await AppHttp2('/dtr/list'));

    if (!res.ok) return alert(res.msg);

    const rdata = res.data;
    const rdata_len = rdata.length;

    const table = new Table([ 'Status', 'Sent Status', 'No.' , 'Range', 'Name', 'Absent', 'Late', 'Undertime', 'Leave Deduction' ]);

    for (let i = 0; i < rdata_len; ++i) {
      
      const {
        code,
        credit_deduction,
        data,
        emp_id,
        from_t,
        header,
        hr_id,
        scannedby,
        status,
        to_t,
        total_absent,
        total_late,
        total_undertime,
        sent_status
      } = rdata[i];


      table.add([
        new Label(status == 1 ? `<span style="background-color: #15b715;color: white; padding: 5px;"><i class="fa fa-check"></i> Approved</span>` 
          : `<span style="background-color: #ff6c6c; color: white; padding: 5px;"><i class="fa fa-refresh"></i> Pending</span>`)
        .addEventListener('click', async () => {
          
          const dtr = new DtrInfo({
            dtr_data: data,
            header: header,
            from: header.range[0],
            to: header.range[1],
            hr_id: header.emp_id,
            emp_id: header.payroll_emp_id,
            name: header.name.fullname2,
            late: header.total_late,
            ut: header.total_undertime,
            is_update: true,
            code: code,
            status: status,
            sent_status: sent_status
          });

          const r = await dtr.show();

          if (r != null && r) {
            this.loadTable();
          }

        }).setStyle({
          cursor: 'pointer'
        })
        ,
        new Label(sent_status == 1 
          ? `<span style="background-color: green; color: white; padding: 5px;"><i class="fa fa-check"></i> Sent Ok</span>`
          : `<span style="background-color: red; color: white; padding: 5px;"><i class="fa fa-close"></i> Not Sent</span>`
        )
        ,
        new Label(code),
        new Label(`${from_t} - ${to_t}`),
        new Label(header.name.fullname2),
        new Label(`${total_absent != null ? total_absent : ''}`),
        new Label(`${total_late != null ? total_late : ''}`),
        new Label(`${total_undertime != null ? total_undertime : ''}`),
        new Label(`${credit_deduction != null ? credit_deduction : ''}`)
      ], [
        { width: '110px' }, { width: '110px' }
      ]);
      
    }

    this.card.clear();
    this.card.add(table);
  }
}


export default DTRReceiver;