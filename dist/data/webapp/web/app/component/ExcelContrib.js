import {ModalV2, Button, Panel, TextBox, ComboBox, MsgLoader} from '../plugin/mcontrol.js';
import { AppHttp2 } from "../classes/lib.js";

export class ExcelContribModal extends ModalV2 {
  constructor() {
    super("Input Loan Contribution", "file-excel-o");
    
    (async () => {
      await this.load_contrib_loan(); 

      const job_status = new ComboBox(null, "Job Status");
      job_status.add('j', 'Job Order');
      job_status.add('c', 'Contract Of Service');
      job_status.add('r', 'Regular Employee(Permanent, Temporary, Cot... etc...)');


      const download = new Button("Download Template For Input", "default", "download");
      
      download.addEventListener('click', async () => {
        const loader = new MsgLoader('Downloading excel template !!!');
        const res = JSON.parse(await AppHttp2('/remittance/template/download', {
          'job_status': job_status.getValue()
        }));
        

        if (res.data == null) {
          alert(res.msg);
          loader.hide("Something went wrong!");
          return;
        }

        const file_name = res.file_name;

        function s2ab(s) {
            var buf = new ArrayBuffer(s.length);
            var view = new Uint8Array(buf);
            for (var i=0; i!=s.length; ++i) view[i] = s.charCodeAt(i) & 0xFF;
            return buf;
        }

        var blob = new Blob([s2ab(atob(res.data))], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });

        // const href = URL.createObjectURL(blob);
        // location.href = href;
        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = file_name + ".xlsx";
        link.click();
        
        loader.hide("Excel Templated Downloaded Successfully!");

      });

      const upload = new Button("Upload Template", "primary", "upload").setStyle({
        marginLeft: '5px'
      });


      const input = new TextBox('Select Template Excel', 'file');
 
      upload.addEventListener('click', () => {
        console.log('upload');
      });

      this.add(download);


      this.add(new Panel().setStyle({
        height: '30px'
      }));

      this.add(new Panel().add(job_status).setStyle({
        'padding': '5px'
      }));

      this.add(new Panel().add(input).setStyle({
        'padding': '5px'
      }));
      this.add(upload);





    })();
  }

  async load_contrib_loan() {

  }

}