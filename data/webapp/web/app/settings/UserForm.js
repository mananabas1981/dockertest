import { ModalV2, TextBox, ComboBox, Button, Form, MsgLoader } from '../plugin/mcontrol.js';
import { AppHttp2 } from './../classes/lib.js';
import { messageBox } from './../main.js';

export class UserForm extends ModalV2 {
  constructor(title = '', data = null, sys = null) {
    super(title, '');

    // var modal = new Modal(title);

    let name = new TextBox('name', 'text');
    let username = new TextBox('Username', 'text');
    let password = new TextBox('Password', 'password');
    let gender = new ComboBox(null, 'Gender');
    let dob = new TextBox('Date Of Birth', 'date');

    const sign_id = new ComboBox(null, 'Signature ID', 'text');
    sign_id.add('', '[ PLEASE SELECT ]');

    gender.add('m', 'Male');
    gender.add('f', 'Female');
    gender.add('o', 'Other');

    let pos = new TextBox('Position', 'text');

    let type = 'insert';

    let submit_label = 'Add';
    let uid = '';

    this.form = new Form();

    const submit = new Button(submit_label, 'success');
    submit.control.style.marginTop = '5px';
    
    (async () => {
      const loader = new MsgLoader('Loading signature list...');
      const sign_list = await this.load_digital_signature();
      for (const sign of sign_list) {
        const { id, name, pos_title } = sign;

        sign_id.add(id, `${name} ${pos_title}`);
      }

      loader.hide('loaded');

      if (data != null) {
          submit_label = 'Update';
          type = 'update';
          // set the uid
          uid = data.id;

          name.setValue(data.name);
          username.setValue(data.username);
          gender.setValue(data.gender);
          dob.setValue(data.dob);
          
          for (const sign of sign_list) {
            const {id} = sign;
            if (id == data.sign_id) {
              sign_id.setValue(data.sign_id);
              break;
            }
          }
      }

      submit.addEventListener('click', async () => {
          const payload = this.form.getValues();
          payload['type'] = type;
          payload['uid'] = uid;

          const o = await AppHttp2('/user/save', payload);
          const data = JSON.parse(o);
          this.resolve = true;
          if (data.ok) {
            messageBox.show(data.msg, () => {
              if (sys != null) {
                  sys.loadUser();
              }
            });
          } else {
            alert(data.msg);
          }

      });

    })(); // anonymouse function async


    this.form.add(name, 'name');
    this.form.add(gender, 'gender');
    this.form.add(dob, 'dob');
    this.form.add(pos, 'pos_title');
    this.form.add(username, 'username');
    this.form.add(password, 'password');
    this.form.add(sign_id, 'sign_id');
    this.form.add(submit);


    this.add(this.form);

    if (data != null) {
        // fillup the data for the update 
        // console.log(data);
    }
     
  }

  getForm() {
    return this.form;

  }

  async load_digital_signature() {
    const data = JSON.parse(await AppHttp2('/digital/signature/list'));
    return data.data;
  }
}