import { Button, Panel, TextBox, MsgLoader } from "./plugin/mcontrol.js";
import { AppHttp } from "./plugin/app.js";
import { messageBox, setHome } from "./main.js";
import { Text } from "./plugin/text.js";
import { Config } from "./plugin/app.js";
import { App } from "./main.js";
import { AppWait } from "./waiting.js";
import { AppHome } from "./home.js";
import { Alert, Confirm } from "./util/dialog.js";

export class AppLogin extends Panel {
  constructor() {
    super();  
    this.class("login-bg").style({
      width: "100%",
      height: "100%",
      position: "fixed",
      top: "0",
      left: "0",
      display: "flex",
      justifyContent: "center",
      alignItems: "center"
    });

    const title = new Panel();
    title.control.innerHTML = '<center><b style="letter-spacing: 5px; color: #0064ff; font-size: 16px;">PAYROLL SYSTEM 1.0</b></center>';
    title.control.style.fontWeight = "bold";
    title.control.style.color = "#7e7e7e";
    title.control.style.fontSize = "15px";
    title.control.style.marginBottom = "20px";


    
    const form = new Panel().class("login-card").add(title).class("c-fade");

    const username_ = new TextBox("Username", "text", null, "Enter Username", "username").style({
      marginBottom: "15px"
    });

    const password_ = new TextBox("Password", "password", null, "Enter Password", "password").style({
      marginBottom: "15px"
    });

    const signin = new Button("Sign In", "primary", "key", "Click to sign in").setStyle({
      marginTop: "10px"
    });

    form.add([ 
      username_, password_, signin
    ]);

    this.add([form]);


    password_.action("keyup", async (e) => {
      if (e.keyCode == 13) {
        await goLogin();
      }
    });


    const goLogin = async () => {
      const username = username_.getValue();
      const password = password_.getValue();

      if (await Confirm("Sign In?")) {
          const txt = new Text(Config.getKey());
          const encrypt_data = txt.encrypt(JSON.stringify({
            username: username,
            password: password
          }));

          const loader = new MsgLoader('Authenticating...');

          var xhr = AppHttp("/user/login", encrypt_data);
          xhr.onload = async function () {
            var dec = txt.decrypt(this.response);
            var data = JSON.parse(dec);

            if (data.ok == 1 && data.status == -1) {
              loader.hide(data.msg);
              messageBox.show(data.msg, function () {
                localStorage.setItem("_fkey", data["fkey"]);
                localStorage.setItem("_token", data["token"]);
                Config["token"] = data["token"];
                Config["fkey"] = data["fkey"];

                App.open(new AppWait());
              });
              return;
            }

            if (data.ok == 1) {
              loader.hide(data.msg);
              localStorage.setItem("_fkey", data["fkey"]);
              localStorage.setItem("_token", data["token"]);
              Config["token"] = data["token"];
              Config["fkey"] = data["fkey"];


              await Alert(data.msg);
              const app = new AppHome();
              setHome(app);
              App.open(app);

              // messageBox.show(data.msg, function () {
              //   // App.open(new AppHome());
              //   const app = new AppHome();
              //   setHome(app);
              //   App.open(app);
              // });

            } else if (data.ok == 2) {
              loader.hide(data.msg);

              await Alert(data.msg);
              const app = new AppHome();
              setHome(app);
              App.open(app);

              // messageBox.show(data.msg, function () {
              //   const app = new AppHome();
              //   setHome(app);
              //   App.open(app);

              // });
            } else if (data.ok == 0) {
              // AppAlert(data.msg);
              loader.hide(data.msg);
              await Alert(data.msg);
              //messageBox.show(data.msg);
            }
        };
      }
    }

    signin.action("click", async () => {
      await goLogin();
    });

  }

  dispose() {
    console.log("login disposed!");
  }
}
