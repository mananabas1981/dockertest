import { ModalV2, Form, TextBox, Button, MsgLoader, ComboBox } from '../plugin/mcontrol.js';
import { AppHttp2 } from './../classes/lib.js';
import { messageBox } from './../main.js';

export class SignForm extends ModalV2 {
  constructor(gdata = null) {
    super('Signatory Form');

    (async () => {

      const form = new Form();
      const certify = new TextBox("Certify", "text", "");
      const name = new TextBox("Name", "text", null);
      const pos_title = new TextBox("Position", "text", null);
      const pos_index = new TextBox("Index", "text", null, null, "0,0");
      const sign_id = new ComboBox(null, 'Signature ID');

      const loader = new MsgLoader('Loading list of digital signatures');
      const sign_list = await this.load_digital_signature();
      loader.hide('Digital signature loaded!');

      sign_id.add('', '[ SELECT DIGITAL SIGNATURE ]');
      for (const sign of sign_list) {
        const { id, name, pos_title } = sign;
        sign_id.add(id, `${name} ${pos_title}`);
      }

      if (gdata != null) {
        certify.setValue(gdata.certify);
        name.setValue(gdata.name);
        pos_title.setValue(gdata.pos_title);
        sign_id.setValue(gdata.sign_id);
        const _index = JSON.parse(gdata.index);

        pos_index.setValue(_index[0] + "," + _index[1]);
      }

      var submit = new Button("Save", "success", "plus-circle");

      submit.control.style.marginTop = "10px";

      submit.addEventListener("click", async () => {
          const data = form.getValues();

          data["is_update"] = gdata != null;
          if (gdata != null)
              data["datecreated"] = gdata["datecreated"]

          const res = JSON.parse(await AppHttp2('/setting/sign/save', data));

          if (res.ok) {
              messageBox.show(res.msg);
              // modal.hide();
              // ReloadTable();
              this.resolve = true;
          } else {
              alert(res.msg);
          }
         
      });

      form.add(certify, "certify");
      form.add(name, "name");
      form.add(pos_title, "pos_title");
      form.add(pos_index, "index");
      form.add(sign_id, 'sign_id');

      form.add(submit);
      this.add(form);

    })(); // anonymouse function async
   
  }

  async load_digital_signature() {
    const data = JSON.parse(await AppHttp2('/digital/signature/list'));
    return data.data;
  }


}