import { x_storage } from "../plugin/mcontrol.js";
import { Panel, ComboBox, Button, Grid, Table, Label, ModalV2, DropDown } from "../plugin/mcontrol.js";
import { AppHttp } from "../plugin/app.js";
import { RemittanceForm } from './../component/RemittanceForm.js';
import { AppHttp2 } from './../classes/lib.js';
import { PayrollViewer } from './../component/payroll.js';

export var RemittanceView = function () {

    /* All Information  */
    var info = x_storage.getItem('payroll_info');
    var ded = JSON.parse(info.deduction_list);

    var con = {};
    for (var index in ded) {
        var _d = ded[index];
        if (!con[_d.code]) {
            con[_d.code] = _d.type;
        }
    }

    /* End Information  */




    var panel = new Panel().setStyle({ padding: '20px' });

    var option = new ComboBox(null, 'Select');
    /* Plot the option */
    for (var key in con) {
        if (con[key] == 'a') continue;
        option.add(key, key);
    }

    var file_type = new ComboBox(null, "Type")
        .add("html", "HTML")
        .add("excel", "EXCEL")
        .add("pdf", "PDF");

    var print_data = '';

    var gen = new Button('Generate', 'success', 'refresh', 'Click to generate the remittance').setStyle({
        width: '100%',
        marginTop: '4px',
        height: '32px',
        fontSize: '9pt'
    })
        .addEventListener('click', function () {
            var data = { key: option.getValue(), refid: info.refid, file: file_type.getValue() };

            AppHttp('/payroll/generate/remittance', data, null, function (res) {
                var data = JSON.parse(res);

                if (!data.ok) {
                    alert(data.msg);
                    return;
                }

                print_data = data["data"];
                card.setStyle({
                    padding: '30px'
                });
                const gen_type = file_type.getValue();
                if (gen_type == "html") {
                    card.control.innerHTML = print_data; // preview the remittances
                } else if (gen_type == "excel") {

                    generate_excel(data.file_name, print_data);
                }

            });

        });


    const generate_excel = (file_name, data) => {
        function s2ab(s) {
            var buf = new ArrayBuffer(s.length);
            var view = new Uint8Array(buf);
            for (var i=0; i!=s.length; ++i) view[i] = s.charCodeAt(i) & 0xFF;
            return buf;
        }

        var blob = new Blob([s2ab(atob(data))], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });
      
        // const href = URL.createObjectURL(blob);
        // location.href = href;
        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = file_name + ".xlsx";
        link.click();
    }



    var oprint = new Button("Print", 'primary', 'print').setStyle({
        marginTop: '4px',
        height: '32px',
        fontSize: '9pt'
    })
        .addEventListener('click', function () {
            var win = window.open();
            if (print_data == '') return alert('Please click the generate button');

            win.document.write(print_data);
            win.focus();
            setTimeout(function () {
                win.print();
                win.close();
            }, 500);
        });

    var grid = new Grid(12)
        .cell(option, ['md-3'])
        .cell(file_type, ["md-3"])
        .cell(gen, ['md-1'])
        .cell(oprint, ['md-1']);

    var card = new Panel().addClass('card').setStyle({
        marginTop: '5px'
    });


    panel.add(grid);
    panel.add(card);

    return panel;
};



// Remittance Viewer

class RemittanceViewer extends ModalV2 {
    constructor({ id = null, done = null }) {

        super(`Remittance (<span style="color: red;">${ id }</span>)`, 'list');

        this.ids = id;

        

        (async () => {

            if (done != null) {
                done();
            }

            const gen = new Button('Generate', 'success', 'refresh');
            const excel = new Button('Download Remittance (Excel)', 'success', 'file-excel-o').setStyle({
                marginLeft: '5px'
            });

            this.add(gen);
            this.add(excel);

            excel.addEventListener('click', async () => {

                const res = JSON.parse(await AppHttp2('/remittance/base/download', {
                    id: id
                }));

                if (!res.ok) return alert('Transaction Failed');
                alert(res.msg);

                const data = res.data;
                const file_name = res.filename;

                function s2ab(s) {
                  const buf = new ArrayBuffer(s.length);
                  let view = new Uint8Array(buf);
                  for (var i=0; i!=s.length; ++i) view[i] = s.charCodeAt(i) & 0xFF;
                  return buf;
                }

                var blob = new Blob([s2ab(atob(data))], {
                  type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                });

                // const href = URL.createObjectURL(blob);
                // location.href = href;
                var link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = file_name;
                link.click();

            });


            gen.addEventListener('click', async () => {
                const res = JSON.parse(await AppHttp2('/remittance/base/regenerate', { id: id }));
                if (res.ok) {
                    alert(res.msg);
                    this.resolve = true;
                } else alert(res.msg);
            });

            const data = await this.load();

            if ( !data ) return;


            const table = new Table(['Key', 'Value'], [
                { width: '100px' }
            ]);

            const drop_item = new DropDown('See Payroll Reference Control No.');

            for (const item of data.refids) {
                drop_item.addItem(`<span style="color: red; font-weight: bold;">#${item}</span>`, async () => {
                    console.log(item);

                    const modal = new PayrollViewer({ refid: item });
                    await modal.show();

                });
            }

            table.add(['Name', data.name], [{}, {fontWeight: 'bold', color: '#4db74d'}]);
            table.add(['Range', `${data.from} - ${data.to}`], [{}, {fontWeight: 'bold', color: '#4db74d'}]);
            table.add(['Total Item', new Label(`${data.total_item}`).addClass('badge').setStyle({color: 'white', backgroundColor: '#efaf3b'})], [{}, {fontWeight: 'bold', color: '#4db74d'}]);
            table.add(['RefID', drop_item], [{}, {fontWeight: 'bold', color: '#4db74d'}]);
            table.add(['Status', ``], [{}, {fontWeight: 'bold', color: '#4db74d'}]);
            
            this.add(new Panel().addClass('card').add(table).setStyle({
                marginTop: '5px'
            }));

        })();




        


        


    }

    async load() {

        // prepation for the future use
        const res = JSON.parse(await AppHttp2('/remittance/base/info', { id: this.ids }));
        const data = res.data;  
        return data

    }
}



// main page of the remittance

export class RemittanceMainPage extends Panel {

    constructor({appHome = null}) {
        super();

        this.setStyle({
            padding: '10px'
        });

        

        this.add(new Button('Create Remittance', 'primary', 'pencil').addEventListener('click', async () => {
            
            const modal = new RemittanceForm({
                done: (self) => {
                    self.hide(); // reload the list of recent_remittances
                    this.load_remittance(); 
                }
            });

            const res = await modal.show();
        }));

        this.load_remittance();

        this.panel = new Panel().setStyle({
            marginTop: '5px'
        });

        this.add(this.panel);
    }

    async load_remittance() {
        const res = JSON.parse(await AppHttp2('/remittance/lists/base'));
        const data = res.data;
        const data_len = data.length;
        this.panel.clear();

        const table = new Table(['Control', 'Code', 'Range', 'Name', 'Status']);

        for (let i = 0; i < data_len; i++) {
            
            const { ids, code, name, from, to, refids, datecreated, status, total_item } = data[i];

            table.add([
                
                new Panel().add(
                    new Label(ids).addClass('badge').setStyle({
                        backgroundColor: '#ff7676',
                        color: 'white',
                        width: '200px',
                        textAlign: 'left',
                        cursor: 'pointer',
                        padding: '5px 5px 5px 20px'
                    }).addEventListener('click', async () => {

                        const rv = new RemittanceViewer({
                            id: ids,
                            done: () => {
                                console.log('done');
                            }
                        });
                        const res = await rv.show();

                        if (res != null) {
                            // reload the remittance table
                            this.load_remittance();
                        }
                    })
                ).add(
                    new Label(total_item.toString()).addClass('badge').setStyle({
                        backgroundColor: '#4caf50',
                        color: 'white',
                        padding: '5px',
                        marginLeft: '10px'
                    })
                ),
                code,
                `${from} - ${to}`,
                name,
                ''
            ]);
        }

        this.panel.add(new Panel().addClass('card').add(table));
    }
}

// end main page of the remitance
