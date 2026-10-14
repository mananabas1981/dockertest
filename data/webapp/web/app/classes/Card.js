import { Panel, ComboBox, Button, TextBox, Grid, Table } from "../plugin/mcontrol.js";
import { AppHttp2 } from "./lib.js";

export class CardInfo extends Panel {
    constructor(type = null) {
        super();
        this.type = type;

        this.init();
    }

    async init() {
        this.addClass("card");
        this.setStyle({
            marginTop: "5px",
            padding: "10px"
        });


        this.content = new Panel().setStyle({ marginTop: "10px" });
        this.add(await this.getMenu());
        this.add(this.content);
    }

    async getMenu() {
        const self = this;

        const select = new ComboBox(null, "Select");
        this.select = select;

        const o = await AppHttp2("/setting/deduction/list");
        const res = JSON.parse(o);
        const data = res.data;
        const col = {};

        for (let index in data) {
            if (col[data[index].code]) continue;
            if (data[index].type != 'c') continue;

            col[data[index].code] = data[index].code;

            //select.add(data[index].code, data[index].code);
        }

        for (let key in col) {
            select.add(key, key);
        }


        const button = new Button("View", "primary", 'search').setStyle({
            marginTop: "3px"
        })
            .addEventListener("click", function () {
                const value = select.getValue();
                self.__loadClients(value);
            });

        const grid = new Grid(-1)
            .cell(select, ["md-2"])
            .cell(button, ["md-2"]);

        return grid;
    }

    async __loadClients(value) {
        if (this.type == null) alert("Cant load from the server type must be not null!");
        const info = JSON.parse(await AppHttp2("/client/list", {
            search: ""
        }));

        const data = info.data.data;

        this.__createPanel(data);
    }

    __createPanel(data) {
        this.content.clear();
        const table = new Table(["Name"]);
        let type = this.select.getValue();

        if (type == 'TAX') type = "TIN";

        type += " NO."

        for (let i in data) {
            table.add([
                new Panel().add(new TextBox(type, "text")),
                `${data[i].lname} ${data[i].fname}, ${data[i].mname}`.toUpperCase()
            ]);
        }

        this.content.add(table);
    };
}