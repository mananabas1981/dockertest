import { AppHttp2 } from "./classes/lib.js";
import { Panel, Grid, Label, TextBox, Button, Scaffold, ModalV2, Iframe } from "./plugin/mcontrol.js";
import { search_employee } from "./transaction.js";


class PaySlipViewer extends ModalV2 {
    constructor(id, from, to, refid) {
        super("Payslip Viewer", "print");
        this.id = id;
        this.from = from;
        this.to = to;
        this.refid = refid;

        (async () => {
            const res = JSON.parse(await AppHttp2('/PaySlip/Print', { id: this.id, from: this.from, to: this.to, refid: this.refid }));
            const html = res["data"];
            
            const frame = new Iframe().setStyle({
                width: "100%",
                height: "70vh"
            });

            frame.control.srcdoc = html;

            this.add(frame);
            this.add(new Button("Print", "success", "print", "Click to print")
            .setStyle({
                marginTop: "10px"
            })
            .addEventListener("click", function() {
                const win = window.open();
                win.document.write(html);
                setTimeout(function () {
                    win.print();
                    win.close();
                }, 500);
            }));
        })();
    }
}

class PaySlipList extends ModalV2 {
    constructor(info) {
        const fullname = `${info['pref_name']} ${info['fname']} ${info['mname']} ${info['lname']} ${info['suf_name']}`.toUpperCase();
        super(`PaySlip List : ${fullname}`, "list");
        this.fullname = fullname;
        const pos_info = info['pos_info'];
        this.rate = '';
        this.id = info['id'];

        if (pos_info.length > 0) {
            this.rate = pos_info[0]['value'].toUpperCase();
        }

        (async () => {
            const panel = new Panel();
            
            const res = await AppHttp2('/payslip/list', {
                id: this.id
            });

            const data = JSON.parse(res)['data'];

            for (let i = 0; i < data.length; ++i) {
                const pay = data[i];


                const from = pay[0];
                const to = pay[1];

                const refid = pay[7];

                panel
                    .add(new Panel()
                        .setStyle({
                            width: '100%',
                            height: '50px',
                            backgroundColor: 'white',
                            boxShadow: '0 0 3px rgba(0, 0, 0, 0.3)',
                            padding: '15px',
                            position: 'relative',
                            marginBottom: '5px'
                        })
                        .add(new Label(`${from} to ${to}`))
                        .add(new Button('View', 'success', 'eye').addEventListener('click', async () => {
                            //await Scaffold(null, new PrintPayslip(this.id, from, to, refid));
                            const modal = new PaySlipViewer(this.id, from, to, refid);
                            modal.show();
                        }).setStyle({
                            position: 'absolute',
                            right: '10px',
                            top: '10px'
                        })));
            }

            this.add(panel);
        })();

    }
}



// view for the SalarySlipViw
class SalarySlipView extends Panel {

    leftPanel() {

        const panel = new Panel().setStyle({
            padding: '10px',
            width: '100%'
        });
        panel
            .add(new Label(this.fullname).setStyle({
                letterSpacing: '2px',
                fontWeight: 'bolder'
            }))
            .add(new Label(this.rate).setStyle({
                letterSpacing: '2px',
                color: '#8d8d8d'
            }));

        return panel;
    }

    rightPanel() {
        const panel = new Panel().setStyle({
            padding: '10px'
        });

        const load_payslip = async () => {

            const res = await AppHttp2('/payslip/list', {
                id: this.id
            });

            const data = JSON.parse(res)['data'];

            for (let i = 0; i < data.length; ++i) {
                const pay = data[i];


                const from = pay[0];
                const to = pay[1];

                const refid = pay[7];

                panel
                    .add(new Panel()
                        .setStyle({
                            width: '100%',
                            height: '50px',
                            backgroundColor: 'white',
                            boxShadow: '0 0 3px rgba(0, 0, 0, 0.3)',
                            padding: '15px',
                            position: 'relative',
                            marginBottom: '5px'
                        })
                        .add(new Label(`${from} to ${to}`))
                        .add(new Button('View', 'success', 'eye').addEventListener('click', async () => {
                            //await Scaffold(null, new PrintPayslip(this.id, from, to, refid));
                            const modal = new PaySlipViewer(this.id, from, to, refid);
                            modal.show();
                        }).setStyle({
                            position: 'absolute',
                            right: '10px',
                            top: '10px'
                        })));
            }

        };

        load_payslip();




        return panel;
    }

    title() {
        const panel = new Panel().setStyle({
            padding: '15px',
            letterSpacing: '5px'
        }).add(new Label('PaySlip History'));
        return panel;
    }

    constructor(info) {
        super();
        this.fullname = `${info['pref_name']} ${info['fname']} ${info['mname']} ${info['lname']} ${info['suf_name']}`.toUpperCase();
        const pos_info = info['pos_info'];
        this.rate = '';
        this.id = info['id'];

        if (pos_info.length > 0) {
            this.rate = pos_info[0]['value'].toUpperCase();
        }

        const grid = new Grid();

        grid
            .cell(this.leftPanel(), ['md-3'])
            .cell(this.rightPanel(), ['md-9']);

        this
            .addClass('container-fluid')
            .add(grid);
    }
}



const create_list = function (data) {
    const panel = new Panel();



    for (let i = 0; i < data.length; ++i) {

        const pos_info = data[i]['pos_info'];



        var info = new Panel().setStyle({
            width: '100%',
            height: '100px',
            backgroundColor: 'white',
            position: 'relative',
            marginTop: '10px',
            borderTopRightRadius: '15px',
            borderBottomLeftRadius: '15px',
            boxShadow: '3px 1px 3px 3px rgba(0, 0, 0, 0.1)'
        });
        info.add(new Label(`<i class="fa fa-user"></i> ` + `${data[i]['pref_name']} ${data[i]['fname']} ${data[i]['mname']} ${data[i]['lname']} ${data[i]['suf_name']}`.toUpperCase()).setStyle({
            position: 'absolute',
            top: '10px',
            left: '10px'
        }));

        if (pos_info.length > 1) {
            info.add(new Label(`${pos_info[1]['value']}`.toUpperCase()).setStyle({
                position: 'absolute',
                top: '30px',
                left: '25px',
                color: '#878585'
            }));
        }

        info.add(new Button('PaySlip', 'default', 'search').setStyle({
            position: 'absolute',
            bottom: '10px',
            left: '10px'
        }).addEventListener('click', async function () {
            const index = i;
            const info = data[index];

            //const salview = new SalarySlipView(info);

            //await Scaffold(salview.title(), salview);
            const modal = new PaySlipList(info);
            modal.show();
        }));

        panel.add(
            info
        );
    }

    return panel;
};

const top_search = function () {
    const panel = new Panel();
    const search_res = new Panel();
    search_res.setStyle({
        marginTop: '20px',
        paddingTop: '10px'
    });

    const search = new TextBox(null, 'search', 'search', 'Type to search employee', 'Search Employee...');
    search.addEventListener('keyup', function (e) {
        if (e.keyCode == 13) {
            search_res.clear();
            search_employee({ 'search': search.getValue() }, function (res) {
                const data = res['data']['data'];
                search_res.add(create_list(data));
            });
        }
    });

    panel.add(search);
    panel.add(search_res);
    return panel;
};


export function PaySlipView() {


    // bootstrap container
    const panel = new Panel().addClass('container-fluid');


    panel.add(top_search());

    return panel;
}