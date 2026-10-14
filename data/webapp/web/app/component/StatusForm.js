import { AppHttp2 } from "../classes/lib.js";
import { Button, ComboBox, Grid, Iframe, Label, ModalV2, Panel, DropDown, TextBox } from "../plugin/mcontrol.js";

export class StatusForm extends ModalV2 {
    constructor({refid = '', dept_id = '', title = '', type = '', check = false, fn = null}) {
        super(`${title} @ref: <span style="color: #ff7878;">${refid}</span>`, 'star-o');

        this.setStyle({
            width: '480px',
            top: '20%'
        });

        this.add(new Label(`SYSTEM NEED USER VERIFICATION FOR THIS PROCESS`).setStyle({color: '#a9a9a9'}));

       
        const username = new TextBox('USERNAME', 'text', 'user', null, 'Please input username');
        const password = new TextBox('PASSWORD', 'password', 'key', null, 'Please input password');
        const remark = new TextBox('REMARK', 'text', 'star-o', null, 'Please input remark');
        if (check) {
            remark.hide();
        }

        this.add(new Panel().add(new Label('ENTER USERNAME')).setStyle({marginTop: '10px', color: 'rgb(255 36 36)', fontSize: '1rem', letterSpacing: '2px'})); 
        this.add(username);
        this.add( new Panel().add(new Label('ENTER PASSWORD')).setStyle({marginTop: '10px', color: 'rgb(255 36 36)', fontSize: '1rem', letterSpacing: '2px'}));
        this.add(password);    
        this.add( new Panel().add(new Label('REMARK')).setStyle({marginTop: '10px', color: 'rgb(255 36 36)', fontSize: '1rem', letterSpacing: '2px'}));
        this.add(remark);

        this.add(new Button('SUBMIT', 'default', 'sign-in')
            .setStyle({
                marginTop: '10px',
                letterSpacing: '2px'
            })
            .addEventListener('click', async () => {
                // username = data['username']
                // password = data['password']
                // remark   = data['remark']
                // refid    = data['refid']

            const payload = {
                refid: refid,
                type: type,
                dept_id: dept_id,
                username: username.getValue(),
                password: password.getValue(),
                remark: remark.getValue()
            };

            const res = JSON.parse(await AppHttp2('/status/state/change', payload));

            if (res.ok) {
                
                if (fn == null) {
                    this.resolve = true;
                    alert(res.msg);    
                } else {
                    fn(this);
                }
                this.hide(true);

            } else {
                alert(res.msg);
            }

        }));

    }
}
