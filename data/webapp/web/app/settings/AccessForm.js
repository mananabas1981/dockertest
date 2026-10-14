import { ModalV2, Panel, CheckBox, Label } from '../plugin/mcontrol.js';
import { AppHttp2 } from './../classes/lib.js';

export class AccessForm extends ModalV2 {
  constructor(emp_id, systemAccess) {

    var systemAccess = systemAccess || null;
    
    super("Access Roles of " + systemAccess.fname);


    // load the access defaults

    var drawTree = (data) => {
        var data_len = data.length;

        // this is the main tree
        var panel = new Panel();
        for (var i = 0; i < data_len; i++) {
            var tree = data[i].tree;
            var tree_len = tree.length;
            var main_panel = new Panel();
            var label = new Panel();
            var next_panel = new Panel();
            next_panel.control.style.paddingLeft = '50px';
            label.control.innerHTML = '<i class="fa fa-cogs"></i> ' + data[i]['value'];
            label.control.style.fontWeight = 'bold';
            main_panel.add(label);
            main_panel.add(next_panel);

            for (var j = 0; j < tree_len; j++) {

                var s = new Panel();
                s.control.style.position = 'relative';
                s.control.style.padding = '5px';

                var check = new CheckBox(tree[j].check);
                check.control.style.cursor = 'pointer';
                check.control.setAttribute('code', tree[j].key);

                check.addEventListener('click', async function () {
                    var code = this.attributes.code.nodeValue;
                    var is_check = this.checked;

                    const o = await AppHttp2('/user/access/state', { code: code, is_check, emp_id: emp_id });
                    const data = JSON.parse(o);

                    if (systemAccess != null) {
                      systemAccess.loadUser();
                    }
                    if (!data.ok) {
                        alert(data.msg);
                    }
                    
                });

                check.control.style.position = 'absolute';
                check.control.style.left = '-20px';
                check.control.style.top = '0px';

                s.add(check);
                var label = new Label();
                label.control.innerHTML = '<i class="fa fa-cog"></i> ' + tree[j].value;
                s.add(label);
                next_panel.add(s);
            }
            panel.add(main_panel);
        }
        this.add(panel);
    };

    const loadAccess = async function () {

        const o = await AppHttp2('/user/default/access', { emp_id: emp_id }, null);
        const data = JSON.parse(o);
        if (data.ok) {
            drawTree(data.data);
        }

    };

    loadAccess();

  }
}
