import { Button, ComboBox, Grid, Iframe, Label, ModalV2, Panel, DropDown, TextBox, Table, x_storage } from "../plugin/mcontrol.js";
import { AppHttp2 } from './../classes/lib.js';
import { PayrollViewer } from './payroll.js';


class Notification extends ModalV2 {
    constructor(param = {}) {
        super('Need Your Action', 'bell', false);
        
        if (typeof(param) != 'object') {
            console.log('Notification parmeter must be a object');
            return;
        }

        const {show = false} = param;

        // if (show == true) {
        //     /// show if it is auto show after loaded in the server
        //     this.show(); // showing if there is an item of the payroll that need a signatory
        // }

        const panel = new Panel();
        this.panel = panel;
        this.add(panel);
        
        this.update();
        
    }

    update() {
        (async () => {
            this.panel.clear();
            
            const res = await this.load();
            const {ok, msg, data} = res;
            if (ok == false) return alert('Something went wrong of the notification!');

            console.log(data);

            const table = new Table(['Action', 'ref#', "Total Item", 'title']);

            const data_len = data.length;
            for (let i = 0; i < data_len; ++i) {
                const item = data[i];
                const view = new Button('View Payroll', 'warning', 'money', 'click to view the payroll and approved!');

                view.addEventListener('click', async () => {
                    // view the payroll modal and approved
                    const {refid} = item;
                    x_storage.setItem('payroll_data', item);
                    // open the The Payroll
                    const payroll = new PayrollViewer({
                        refid: refid,
                        dept_id: ''
                    });
                    
                    const ret = await payroll.show();
                    if (ret != null && ret == true) {
                        this.update(); // reupdate after the transaction of the payroll viewer
                        // to update like a live viewing
                    }
                });

                table.add([
                    view,
                    `${item['refid']}`,
                    `
                        <span style="color: white; background-color: #43A047; padding: 5px 10px 5px 10px; border-radius: 10px;">
                            ${item["total_item"]}
                        </span>
                    `,
                    `${item['from']} to ${item['to']} - ${item['title']}`
                ]);
            }

            
            
            this.panel.add(new Label(`Total Need Action: <span style="color: white; background-color: #E53935; padding: 5px; border-radius: 5px;">${data_len} items</span>`));
            
            if (data_len > 0) {
                const last_note = data[0]['last_need_action'];
                this.panel.add(
                    new Panel().setStyle({
                        marginTop: '10px'
                    }).add(new Label(` 
                        Message: <span style="padding: 5px;color: white; background-color: green; border-radius: 5px;">
                        ${last_note.c}
                        </span>
                    `))
                )
                .add(
                    new Panel().add(new Label(`
                        <span style="font-size: 10pt;">
                            Notification To: <span style="color: red; font-weight: bold;">${last_note.n}</span>
                        </span>    
                    `))
                );
            }

            this.panel.add(table);

            if (data_len > 0) this.show(); // show this if there is a data found 
        })();
    }

    async load() {
        const data = JSON.parse(await AppHttp2('/load/action', {}));

        return data;
    }
}


export { 
    Notification 
};