import { Panel, Table, Button } from "./plugin/mcontrol.js";
import { AppHttp } from "./plugin/app.js";
import { confirmBox, messageBox } from "./main.js";
import { AppHttp2 } from "./classes/lib.js";

export const PayrollUserSessionList = function () {
    var panel = new Panel();
    panel.addClass('card');



    var table = new Table(['Action', 'name', 'date', 'Remark']);
    panel.add(table);

    var self = this;

    this.reload = async function () {

        const o = await AppHttp2('/session/list', {}, null);

        const res = JSON.parse(o);
        if (!res.ok) return alert(res.msg);
        const data = res.data;
        const data_len = data.length;

        table.clear(); /* clear the table data for fresh data */

        /* Add data to the table */
        for (let i = 0; i < data_len; i++) {
            var menu = new Panel();

            var approve = new Button('Approve', 'primary', 'thumbs-up');
            approve.control.setAttribute('rel', i);

            approve.addEventListener('click', function () {
                var index = this.attributes.rel.nodeValue;
                var info = data[index];
                confirmBox.show('Approve?', function () {
                    AppHttp('/session/approve', { key: info.key }, null, function (o) {
                        const data = JSON.parse(o);
                        if (data.ok) {
                            messageBox.show(data.msg, function () {
                                self.reload();
                            });
                        } else {
                            alert(data.msg);
                        }
                    });
                });
            });

            var disapprove = new Button('Disapprove', 'danger', 'thumbs-down');
            disapprove.control.setAttribute('rel', i);
            disapprove.control.style.marginLeft = '5px';

            disapprove.addEventListener('click', function () {
                var index = this.attributes.rel.nodeValue;
                console.log(data[index]);
            });

            menu.add(approve);
            menu.add(disapprove);
            table.add([menu, data[i].name, data[i].date, '']);
        }


    };

    this.getContainer = function () {
        return panel;
    };
};


export const UserApproval = function () {
    var panel = new Panel();
    panel.control.style.padding = '5px';
    var plist = new PayrollUserSessionList();
    plist.reload();



    panel.add(plist.getContainer());
    return panel;
};

