import { Panel, Button, Table, Label, TextBox2, Container } from "./plugin/mcontrol.js";
import { AppHttp } from "./plugin/app.js";
//import { appLogin } from "./main.js";
import { App } from "./main.js";
import { AppLogin } from "./login.js";
import { Alert, Confirm, DialogModal2 } from "./util/dialog.js";
import { AppHttp2 } from "./classes/lib.js";

// home left view
const HomeLeftView = function () {
  var panel = new Panel().addClass('col-md-4');

  var content = new Panel().addClass('card');
  content.control.style.padding = '10px';

  var pic = new Panel().addClass('profile-pic');
  content.add(pic);

  var table = new Table(['Profile Information', '']);




  table.add(['Name', ""]);
  table.add(['Age', '']);

  content.add(table);
  panel.add(content);


  var loadData = function (data) {
    table.clear();
    for (var x in data) {
      table.add([x, data[x] == null ? '' : data[x]]);
    }
  };

  AppHttp('/dashboard/data?q=profile', {}, null, function (o) {
    loadData(JSON.parse(o).data);
  });

  this.container = function () {
    return panel;
  };
};


class EditPassword extends DialogModal2 {
  constructor() {
    super("Update Password", "lock");

    const old_password = new TextBox2("Old Password", "password");
    const new_password = new TextBox2("New Password", "password");
    const confirm_password = new TextBox2("Confirm New Password", "password");

    const submit = new Button("Update Password", "primary", "save").style({ marginTop: "5px" });

    submit.addEventListener("click", async () => {
      
      if (!await Confirm("Are you sure to change your password?")) return;

      const res = JSON.parse(await AppHttp2("/update/password", {
        old_pass: old_password.getValue(),
        new_pass: new_password.getValue(),
        con_pass: confirm_password.getValue()
      }));

      if (!res.ok) {
        await Alert(res.msg);
        return;
      }
      await Alert(res.msg);
      this.hide(true);
    });

    this.add(new Container([
      old_password,
      new_password,
      confirm_password,
      submit
    ]));
  }
}

// middle view

const HomeMidView = function () {
  var panel = new Panel().addClass('col-md-4');

  var content = new Panel().addClass('card');
  panel.add(content);

  const edit_password = new Button("Edit Password", "success", "edit");

  content.add(edit_password);

  edit_password.addEventListener("click", async () => {
    const modal = new EditPassword();
    await modal.show();
  });

  this.container = function () {
    return panel;
  };
};


// right viewer
let interval = null;
class HomeRightView extends Panel {
  constructor(appHome) {
    super();
    

    const content = new Panel().addClass('card').setStyle({
      padding: "10px",
      background: "#d4edda"
    });
    
    content.add(new Label("ACTIVE USER!"));
    
    const list_container = new Panel().addClass("list-group");
    
    clearInterval(interval);
    interval = setInterval(() => {``
      list_container.clear();
      const users = appHome.chat.getUsers();
      for (const user of users) {
        list_container.add(new Panel().addClass("list-group-item").add(new Label(user)));
      }
    }, 1000);
    
    content.add(list_container);
    this.add(content);
    this.addClass("col-md-4");
  }
 
}


export function HomeView(appHome) {
  var panel = new Panel();
  panel.control.style.padding = "5px";

  var content = new Panel();
  content.addClass("card");
  content.control.style.padding = "5px";

  var logout = new Button("Log-Out", "success", "sign-out", "click to sign out").style({
    width: "100px"
  });
  content.add(logout);

  logout.addEventListener("click",  async () => {

    if (!await Confirm("Sign Out?")) {
      return;
    }

    AppHttp("/sign-out", {}, null,  (o) => {
      var data = JSON.parse(o);
      if (data.ok == 1) {
        // app_ws.close(); // close the websocket
        App.open(new AppLogin());
      }
    });
  });


  const row = new Panel().addClass('row');
  row.control.style.marginTop = '5px';

  row.add(new HomeLeftView().container());

  row.add(new HomeMidView().container());

  row.add(new HomeRightView(appHome));


  content.add(row);

  panel.add(content);


  return panel;
};
