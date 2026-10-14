import { AppHttp2 } from "../classes/lib.js";
import { Button, ComboBox, Label, ModalV2, Table } from "../plugin/mcontrol.js";


class AtmNotFound extends ModalV2 {
  constructor(lists) {
    super("ATM Not Found", "home");

    

    const table = new Table(["ATM NOT FOUND"]);

    for (let list of lists) {
      table.add([
        list
      ]);
    }

    this.add(new Label(`<span style="color: red;">Transaction Failed!</span>`));
    this.add(new Label(`TOTAL NOT FOUND: ${lists.length}`));
    this.add(table);

  }
}


class TransaferBank extends ModalV2 {
  constructor(refid, atm_info) {
    super("Change ATM Information", "home");

    this.refid = refid;
    console.log(this.refid);
    

    console.log(atm_info);


    const cb = new ComboBox(null, "BANK ATM");
    (async () => {
      const atms = await this.loadATM();
      
      for (let atm of atms) {
        cb.add(atm[0], `${atm[1]} - ${atm[1]}`);
      }


      cb.setValue(atm_info["code"]); // load the confirm
      
    })();

    const submit = new Button("Change ATM", "danger", "refresh").setStyle({
      marginTop: "30px"
    });

    
    this.add(new Label(`Ref ID: ${refid}`));
    this.add(cb);
    this.add(submit);

    submit.addEventListener("click", async () => {
      if (!confirm("Are you sure?")) return;
      if (cb.getValue() === atm_info["code"]) return alert("No change made!");


      const payload = {
        refid: refid,
        atm: cb.getValue()
      };

      const ret = JSON.parse(await AppHttp2("/payroll/change/atm", payload));

      if (ret.ok == false) {
        
        alert(ret.msg);

        if (ret.err.length > 0) {
          const atm = new AtmNotFound(ret.err);
          atm.show();
        }

      } else {
        alert(ret.msg);
        this.hide(true);
      }
      
      // this.hide(true);
    });


  }

  


  async loadATM () {

    const data = JSON.parse(await AppHttp2("/bank/list")).data;
    
    return data;
  }




}

export default TransaferBank;