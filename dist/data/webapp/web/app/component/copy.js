import { AppHttp2 } from "../classes/lib.js";
import { Button, Container, TextBox2 } from "../plugin/mcontrol.js";
import { Alert, Confirm, DialogModal2 } from "../util/dialog.js";

class CopyPayrollForm extends DialogModal2 {
  constructor(refid) {
    super(`Copy Payroll | ref: <span style="color: red;">${refid}</span>`, "copy");

    const name = new TextBox2("Name", "text");
    const frm = new TextBox2("From", "date");
    const to = new TextBox2("To", "date");

    const copy = new Button("Create Copy", "primary", "copy").style({
      marginTop: "5px"
    });

    super.add(new Container([
      name,
      frm, 
      to,
      copy
    ]));

    copy.addEventListener("click", async () => {
      if (!await Confirm("Create a copy of payroll now?")) {
        return;
      }

      const n = name.getValue();
      const f = frm.getValue();
      const t = to.getValue();

      if (f.trim() == "") return await Alert("From field is required!");
      if (t.trim() == "") return await Alert("To field is required!");
      if (n.trim() == "") return await Alert("Name field is required!")

      const payload = {
        name: n,
        refid: refid,
        from: f,
        to: t
      };

      copy.showLoader();
      const res = JSON.parse(await AppHttp2("/payroll/copy", payload));
      copy.hideLoader();
      
      if (!res.ok) return await Alert(res.msg);

      await Alert(res.msg);

      this.hide({
        from: f,
        to: t
      });

    });
    
  }
}

export default CopyPayrollForm;