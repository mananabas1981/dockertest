// end deduction pages
import { Panel, Button, Form, Modal, Table, TextBox } from "../plugin/mcontrol.js";

class ChargedPage extends Panel {

    constructor() {
        super();
        this.addClass("card")
        .setStyle({
            padding: "10px"
        });

        const add = new Button("Add", "success", "plus-circle", "click to add new Charge Group");

        this.tbl = new Panel();
        this.add(add);
        this.add(this.tbl);

        // init
        this.loadTable();
    }

    loadTable() {
        
        this.tbl.clear();

        const table = new Table([ "Code", "Name", "Total Department" ]);
        
        this.tbl.add(table);

    }
}

export default ChargedPage;