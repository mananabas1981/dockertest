import { AppHttp2 } from "../classes/lib.js";
import { Button, ComboBox, Grid, Iframe, Label, ModalV2, Panel, DropDown, TextBox } from "../plugin/mcontrol.js";
import { ObModal } from "../transaction/ob-r.js";
import { StatusForm } from './StatusForm.js';
import { AdaViewer2 } from './../component/AdaViewer.js';
import { Alert, Confirm } from "../util/dialog.js";


class PayrollReports extends ModalV2 {
    constructor(refid) {
        super(`Payroll Reports`, "file-pdf-o");
        
        this.refid = refid;


        this.loadReport();

        this.panel = new Panel();

        this.add(this.panel);

        const btn = new Button("Print", "success", "print", "Please click to print!").setStyle({
            marginTop: "5px"
        });

        btn.addEventListener("click", async () => {
            const html = await this.loadReport(true);

            const win = window.open();
            win.document.write(html);
            setTimeout(() => {
                win.focus();
                win.print();
                win.close();
            }, 1000);
        });
        
        this.add(btn);
    }
    
    async loadReport(is_print = false) {
        const o = JSON.parse(await AppHttp2("/payroll/total/fund", {
            refid: this.refid
        }));

        const html = o.data;
        
        if (!is_print) {
            this.panel.clear();
            const iframe = new Iframe().setStyle({
                width: "100%",
                height: "70vh"
            });
            iframe.control.srcdoc = html;
            this.panel.add(iframe);
        }

        return html;
    }

}

class ObReports extends ModalV2 {
    constructor(refid) {
        super("Obligation Reports", "file-pdf-o");
        
        this.refid = refid;
        
        
        this.panel = new Panel();
        
        this.add(this.panel);

        const print = new Button("Print", "success", "print").setStyle({
            marginTop: "5px"
        });

        print.addEventListener("click", async () => {
            const html = await this.loadReport(true);

            const win = window.open();
            win.document.write(html);
            
            setTimeout(() => {
                win.focus();
                win.print();
                win.close();
            }, 555);

        });

        this.add(print);

        (async () => {
            await this.loadReport();
        })();
    }

    async loadReport(is_print = false) {
        const o = JSON.parse(await AppHttp2("/payroll/ob/reports", {
            refid: this.refid
        }));

        const html = o.data;
        
        if (!is_print) {
            // view the iframe
            this.panel.clear();

            const iframe = new Iframe().setStyle({
                width: "100%",
                height: "70vh"
            });

            iframe.control.srcdoc = html;
            
            this.panel.add(iframe);
        }

        return html;
    }
}


export class PayrollViewer extends ModalV2 {
    constructor({ refid, dept_id, show_all = true }) {

        super(`Payroll Viewer -> Ref: <span style="color: #ff6b6b;">${refid}</span>`, 'print');

        this.setStyle({
            width: `${window.innerWidth - 100}px`
        });

        this.refid = refid;
        this.dept_id = dept_id;
        this.show_all = show_all;
        this.panel = new Panel();

        this.print_btn = new Button('Print', 'success', 'print').setStyle({
            marginBottom: '5px',
            marginTop: '5px'
        }).addEventListener('click', async () => {
            if (!confirm('Are you sure to print the payroll?')) return;

            const req = await AppHttp2('/print/payroll?type=print', { refid: this.refid, dept_id: this.dept_id });
            const res = JSON.parse(req);
            if (res.ok == 0) {
                alert(res.msg);
                return;
            }

            const win = window.open();
            win.document.write(res.data);
            setTimeout(() => {
                win.print();
                win.close();
            }, 444);

        })


        this.drop_item = new DropDown(`<i class="fa fa-star-o"></i> ACTION`, 'danger').setStyle({
            marginBottom: '5px',
            marginLeft: '5px'
        });

        this.add(this.print_btn);

        this.add(new Button("View OB-R", "primary", "search").setStyle({
            marginBottom: "5px",
            marginLeft: "5px",
            marginTop: '5px'
        }).addEventListener("click", () => {
            const modal = new ObModal(this.dept_id);
            
        }));

        console.log(1);

        const rpt_btn = new Button("General Reports", "success", "file-pdf-o").setStyle({
            marginLeft: "4px"
        });

        const ob_rpt = new Button("OB Reports", "success", "file-pdf-o").setStyle({
            marginLeft: "4px"
        });

        const gen_rem = new Button("Download Remittances", "success", "file-pdf-o").setStyle({
            marginLeft: "4px"
        });

        ob_rpt.addEventListener("click", () => {
            const modal = new ObReports(this.refid);
            modal.show();
        });

        rpt_btn.addEventListener("click", () => {
            const modal = new PayrollReports(this.refid);
            modal.show();
        });

        gen_rem.addEventListener("click", async () => {
            
            if (await Confirm("Are you sure?")) {                
                
                
                const res = JSON.parse(await AppHttp2("/remittance/generate", {
                    refid: this.refid
                }));

                await Alert(res.msg);
            }
            
        });

        this.add(this.drop_item);
        
        this.add(rpt_btn);
        this.add(ob_rpt);
        this.add(gen_rem);

        const combo = new ComboBox(null, "Deparment");



        const grid = new Grid(1);
        grid.cell(combo, ["md-6"]);

        const prev = new Button("Prev", "default", "arrow-left");
        const next = new Button("Next", "default", "arrow-right").setStyle({ marginLeft: '2px' });

        const ob_btn = new Button("OB", "default", "bars").setStyle({ marginLeft: '2px' });

        grid.cell(new Panel().add(prev).add(next).add(ob_btn), ["md-3"]);

        this.add(new Panel().addClass("container-fluid").add(grid));
        this.add(this.panel);

        (async () => {
            let prev_next = 0;

            const data = await this.load_department();
            if (this.show_all) {
                //
                data.unshift(['', 'Show', 'All Department']);
            }

            for (let i = 0; i < data.length; i++) {
                combo.add(i, `${i == 0 ? '' : i + '.'} ${data[i][3] !== undefined ? '('+ data[i][3] + ') ' : '' }${data[i][2]}`);
            }

            prev_next = parseInt(combo.getValue());
            this.dept_id = data[prev_next][0];
            this.view_data();

            combo.addEventListener("change", () => {
                prev_next = parseInt(combo.getValue());
                this.dept_id = data[prev_next][0];
                this.view_data();
            });

            prev.addEventListener("click", () => {
                prev_next -= 1;
                if (prev_next <= 0) {
                    prev_next = 0;
                }

                combo.setValue(prev_next);
                prev_next = parseInt(combo.getValue());
                this.dept_id = data[prev_next][0];
                this.view_data();
            });

            next.addEventListener("click", () => {
                prev_next += 1;
                if (prev_next >= data.length - 1) {
                    prev_next = data.length - 1;
                }

                combo.setValue(prev_next);
                prev_next = parseInt(combo.getValue());
                this.dept_id = data[prev_next][0];
                this.view_data();
            });

            ob_btn.addEventListener("click", () => {


                const ob_show = localStorage.getItem("ob_show");

                if (ob_show == null || ob_show == "off") {
                    if (ob_show === null) localStorage.setItem("ob_show", "off");
                    else localStorage.setItem("ob_show", "on");
                } else {
                    localStorage.setItem("ob_show", "off");
                }

                this.view_data();
            });


            this.resolve = true;
        })();

        // (async () => {
        //     await this.load_fund_total();
        // })();
    }

    // async load_fund_total() {
    //     const o = JSON.parse(await AppHttp2("/payroll/total/fund", {
    //         refid: this.refid
    //     }));

    //     console.log(o);
    // }

    async load_department() {
        const o = await AppHttp2(`/department/list?refid=${this.refid}`, {}, null);

        const res = JSON.parse(o);
        const data = res.data;
        return data;
    }

    async drop_item_action(status = null) {

        ///this.drop_item.clear();
        this.drop_item.clearItem();

        if (status == null) {
            this.drop_item.addItem(`<i class="fa fa-close"></i> Close Payroll`, async () => {
                const modal = new StatusForm({
                    title: 'Close Payroll',
                    refid: this.refid,
                    type: 'close_payroll'
                });

                const res = await modal.show();

                if (res != null) {
                    await this.view_data();
                }

            });
        } else {

            let _data = JSON.parse(status);
            const data = _data[_data.length - 1];

            const { step } = data;

            if (step == 0) {
                this.drop_item.addItem(`<i class="fa fa-close"></i> Close Payroll`, async () => {

                    const modal = new StatusForm({
                        title: 'Close Payroll',
                        refid: this.refid,
                        type: 'close_payroll'
                    });

                    const res = await modal.show();

                    if (res != null) {
                        await this.view_data();
                    }
                });
            } else if (step == 6) {
                // 6 is the review the payroll and signatures
                this.drop_item.addItem(`<i class="fa fa-close"></i> Close Payroll Review & Signatures`, async () => {


                    if (!confirm('Note: Before closing the payroll review, make sure that the all signatories are signed or digitally approved!, Would you like to continue?')) return;

                    const modal = new StatusForm({
                        title: 'Close Payroll Review',
                        refid: this.refid,
                        type: 'close_review'
                    });

                    const res = await modal.show();

                    if (res != null) {
                        await this.view_data();
                    }
                });

            } else if (step == 2) {
                // for the Obligation requests

                this.drop_item.addItem(`<i class="fa fa-close"></i> APPROVE OBLIGATION REQUESTS(OB) AND PROCEED TO PAYROLL SALARY FILE OR ADA`, async () => {


                    if (!confirm('Note: Before approving the OB-R, make sure that the all signatories are signed or digitally approved!, Would you like to continue?')) return;

                    const modal = new StatusForm({
                        title: 'APPROVE OBLIGATION REQUESTS',
                        refid: this.refid,
                        type: 'close_ob'
                    });

                    const res = await modal.show();

                    if (res != null) {
                        await this.view_data();
                    }
                });

            } else if (step == 4 || step == 7) {
                this.drop_item.addItem(`<span style="color: green;"><i class="fa fa-money"></i> VIEW ADA OR PAYROLL FILE</span>`, async () => {
                    const modal = new AdaViewer2(this.refid, '');
                    modal.show();
                });

                if (step == 4)
                    this.drop_item.addItem(`<div style="width: 100%; height: 100%; color: green;"><i class="fa fa-lock"></i> PROCEED TO PAYROLL FILE DOWNLOAD!</div>`, async () => {

                        if (!confirm(`After this transaction you cant edit the bank account number!, you can only download the payroll file!`)) return;

                        const modal = new StatusForm({
                            title: 'APPROVE OBLIGATION REQUESTS',
                            refid: this.refid,
                            type: 'ready_download'
                        });

                        const res = await modal.show();

                        if (res != null) {
                            await this.view_data();
                        }
                    });

                if (step == 7)
                    this.drop_item.addItem(`<span style="color: green;">Final close the Payroll(ADA or Payroll File)</span>`, async () => {
                        if (!confirm('This transaction it means that the salary is already been approved by the bank or online bank!, do you want to proceed to this transaction')) return;

                        const modal = new StatusForm({
                            title: 'Final Closed',
                            refid: this.refid,
                            type: 'final_close'
                        });

                        const res = await modal.show();

                        if (res != null) {
                            await this.view_data();
                        }

                    });
            }


            this.drop_item.addItem(`<i class="fa fa-arrow-left"></i> REOPEN THE PAYROLL!`, async () => {
                if (!confirm('Re opening the payroll will remove all the other signatories, be careful!, Would you like to proceed this transaction? This will proceed to OBLIGATION REQUESTS PROCESS')) return;

                const modal = new StatusForm({
                    title: 'Open Payroll',
                    refid: this.refid,
                    type: 'open_payroll'
                });

                const res = await modal.show();

                if (res != null) {
                    await this.view_data();
                }
            });
        }

    }

    async view_data() {
        // this.panel.clear();
        // this.panel.add(new Label('Please wait while loading the payroll!'));

        if (this.dept_id == '') {
            this.print_btn.hide();
        } else {
            this.print_btn.show();
        }

        const req = await AppHttp2('/print/payroll?type=view', { refid: this.refid, dept_id: this.dept_id });
        
        if (req == null) {
            this.panel.clear();
            this.panel.add(new Label('<span style="color: red;">Payroll Server OFFLINE!</span>'));
            return;
        }

        const res = JSON.parse(req);
        if (res.ok == 0) return;

        this.panel.clear();

        const frame = new Iframe().setStyle({
            width: '100%',
            height: `75vh`,
            border: "none",
            boxShadow: "0px 0px 6px rgba(0, 0, 0, 0.4)",
            borderRadius: "5px"
        });
        const { data, payroll_info, action } = res;
        this.drop_item_action(payroll_info['status']);
        // console.log(payroll_info);

        frame.control.srcdoc = data;


        // load the obligation requests

        let ob_html = "";
        try {
            // load here the obligation iframe
            const ob_show = localStorage.getItem("ob_show");
            if (ob_show === null || ob_show === "on") {
                // avoid loading the print_ob if it is  not required to view! increase performance
                const ob_data = JSON.parse(await AppHttp2("/print/ob?v=view", {
                    refid: this.refid,
                    dept_id: this.dept_id
                }));

                ob_html = ob_data.data;
            }

        } catch (er) {

        }

        const ob_show = localStorage.getItem("ob_show");

        const grid = new Grid(8);
        if (ob_html.trim() == "") {
            grid.cell(frame, ["md-12"]);
        } else {

            const ob_frame = new Iframe().setStyle({
                width: '100%',
                height: `75vh`,
                boxShadow: "0px 0px 6px rgba(0, 0, 0, 0.4)",
                border: "none",
                borderRadius: "5px"
            });

            if (this.dept_id !== "") {
                ob_frame.control.srcdoc = ob_html;
            }

            if (ob_show === null || ob_show === "on") {
                grid.cell(frame, ["md-8"]);
                grid.cell(ob_frame, ["md-4"]);
            } else {
                grid.cell(frame, ["md-12"]);
            }
        }

        this.panel.add(grid);


        if (action != null && action.length > 0) {

            if (action[0]['sign_val'] != null && action[0]['sign_val'].trim() != '') return;

            this.panel.add(new Button(`APPROVE WITH DIGITAL SIGNATURE`, 'danger', 'pencil').setStyle({ animation: 'blink 2s ease' }).addEventListener('click', async () => {

                if (!confirm(`You are about to approve digital signature of ${action[0]['name']} ----- ${action[0]['action']}`)) return;

                // create a payload
                const payload = {
                    refid: this.refid,
                    dept_id: this.dept_id,
                    sign_key: action[0]['sign_key']
                };

                const stat = new StatusForm({
                    title: 'Check Logged in!', type: 'check', refid: this.refid, check: true, fn: async () => {
                        const res = JSON.parse(await AppHttp2('/payroll/digital/signature/approve', payload));
                        if (res.ok) {
                            alert(res.msg);
                            this.view_data();
                        } else {
                            alert(res.msg);
                        }
                    }
                });
                stat.show();

            }));
        }
        // AppHttp('/print/payroll?type=view', { refid: refid, dept_id: content.dept_id.getValue() }, null, function (o) {
        //     var res = JSON.parse(o);
        //     if (res.ok == 0) return;

        //     var win = window.open();
        //     win.document.write(res.data);
        //     /*setTimeout(function() {
        //         win.print();
        //         win.close();
        //     }, 444);*/

        // });

        // adding event for frame



        // this is the implementation of the future development
        // like when the user click on the table in iframe
        // show menu for deletion or adding contribution & loans
        frame._c.contentWindow.addEventListener('click', () => {
            setTimeout(() => {
                const refid = this.refid;
                const dept_id = this.dept_id;
                const emp_id = localStorage.getItem('frame_emp_id');
                if (emp_id == null) return;

                // console.log(emp_id);

                localStorage.setItem('frame_emp_id', null);
            }, 100);
        });
    }


}