import { Button, Grid, ModalV2, MsgLoader, Panel, TextBox, Table } from "../plugin/mcontrol.js";
import { AppHttp2 } from "../classes/lib.js";

export class SignModal extends ModalV2 {
  constructor(id = '', name = '', position = '') {
    super(`About Digital Signature - @${name}`, 'pencil');
    
    (async () => {
      this.id = id;
      this.name = name;
      this.position = position;


      const name_in = new TextBox('NAME', 'text');
      const pos_in = new TextBox('POSITION', 'text');
      const sign_in = new TextBox('SIGNATURE DATA', 'file');


      if (id != '') {
        name_in.setValue(name);
        pos_in.setValue(position);

      }

      this.add(name_in);
      this.add(pos_in);
      this.add(sign_in);

      this.add(new Button('Upload', 'default', 'upload').setStyle({
        marginTop: '5px'
      }).addEventListener('click', async () => {

        const files = sign_in.control.files;


        if (files.length <= 0) {
          alert('No file please select a file');
          return;
        }

        const file = files[0];
        if (file['type'] != 'image/png') {
          alert(`File must be: image/png, png file is required! not ${file.type}`);
          return;
        }

        // FileReader
        const reader = new FileReader();

        reader.onload = async (evt) => {
            var binary = '';
            var bytes = new Uint8Array(reader.result);
            var len = bytes.byteLength;
            for (var i = 0; i < len; i++) {
                binary += String.fromCharCode(bytes[i]);
            }

            const image_data = 'data:image/png;base64,' + btoa(binary); 


            const loader = new MsgLoader('Saving & Uploading of esignature');
            const res = JSON.parse(await AppHttp2('/digital/signature/save', {
              'id': this.id,
              'name': name_in.getValue(),
              'pos_title': pos_in.getValue(),
              'data': image_data
            }));

            loader.hide(res.msg);
            this.resolve = true;
            console.log(res);

        }

        reader.readAsArrayBuffer(file)
        // End File Reader

      }));
    })();
  }
}





// page of the signature
export class DigitalSignaturePage extends Panel {
  constructor() {
    super();

    (async () => {

      this.table = new Table(['ACTION', 'SIGN ID', 'NAME', 'POS_TITLE']);


      const add = new Button('Add', 'success', 'plus-circle');

      add.addEventListener('click', async () => {
        const modal = new SignModal();
        const res = await modal.show();
        if (res != null) {
          await this.loadTable();
        }

      });

      this.add(add);
      this.add(new Panel().setStyle({
        marginTop: '5px'
      }).addClass('card').add(this.table));

      await this.loadTable();

    })();

  }

  async loadTable() {
    const res =  JSON.parse(await AppHttp2('/digital/signature/list'));

    if (!res.ok) return;

    this.table.clear();
    const data = res.data;
    const data_len = data.length;

    for (let i = 0; i < data_len; i++) {
      const item = data[i];
      this.table.add([
        new Panel().add(new Button('EDIT', 'success', 'edit').addEventListener('click', async () => {
          const modal = new SignModal(item['id'], item['name'], item['pos_title']);
          const res = await modal.show();
          console.log(res);
        })),
        item['id'],
        item['name'],
        item['pos_title']
      ]);
    }
  }

}