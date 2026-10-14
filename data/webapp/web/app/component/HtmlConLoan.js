import { AppHttp2 } from "../classes/lib.js";
import { Button, ModalV2, ComboBox, Panel, Iframe, MsgLoader } from "../plugin/mcontrol.js";

class HtmlConLoan extends ModalV2 {

  constructor() {
    super("Contribution and Loans", "edit");

    const job_status = new ComboBox(null, "Job Status");
    job_status.add('j', 'Job Order');
    job_status.add('c', 'Contract Of Service');
    job_status.add('r', 'Regular Employee(Permanent, Temporary, Cot... etc...)');

    const submit = new Button("Generate", "success", "refresh").setStyle({
      marginTop: "5px",
      marginBottom: "5px"
    });

    submit.addEventListener("click", async () => {
      const loader = new MsgLoader("Generating Information...");
      const res = await this.load();
      loader.hide("Successfully Generated!");
      
      
      console.log(res);
      
      this.drawFrame(res.data);  
    });
    

    this.panel = new Panel();

    this.job_status = job_status;
    this.add(job_status);
    this.add(submit);
    this.add(this.panel);
    

    
  }

  async load() {
    const res = JSON.parse(await AppHttp2('/remittance/template/download', {
      'job_status': this.job_status.getValue()
    }));
    
    return res;
  }

  drawFrame(data) {
    this.panel.clear();

    const frame = new Iframe().setStyle({
      width: "100%",
      height: "60vh"
    });
    
    frame.control.srcdoc = data;

    this.panel.add(frame);
  }
}


export default HtmlConLoan;