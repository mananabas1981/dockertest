import { Panel, Label, Button } from "./plugin/mcontrol.js";
import { AppHttp } from "./plugin/app.js";
import { App, setHome } from "./main.js";
import { messageBox } from "./main.js";
import { AppLogin } from "./login.js";
import { AppHome } from "./home.js";

export const AppWait = function () {
  var panel = new Panel();
  panel.control.style.padding = '20px';
  var box = new Panel();
  box.addClass('box');
  box.control.style.padding = '20px';
  box.control.style.height = '200px';

  var label = new Label();
  label.control.innerHTML = '<label style="font-weight: bolder; font-size: 20px;">Payroll System</label><br /> Please Wait! while waiting for approval!!!';

  var logout = new Button('Logout', 'danger', 'sign-out');

  var n = setInterval(function () {

    var xml = AppHttp("/verify", {});
    xml.onload = function () {
      var data = JSON.parse(this.response);
      if (data.ok == 1) {

        clearInterval(n);
        messageBox.show('Successfully approved', function () {
          const app = new AppHome();
          setHome(app);
          App.open(app);
          //App.open(new AppHome());
        });

      }
      else if (data.ok == 0) {
        clearInterval(n); // this mean it is dis-approved!
        App.open(new AppLogin());
      }
    };
  }, 2000);


  logout.addEventListener('click', function () {
    if (!confirm('Logout?')) return;
    clearInterval(n);
    AppHttp('/sign-out', {}, null, function () {
      App.open(new AppLogin());
    });
  });

  var loader = new Panel();
  loader.addClass('loader');

  var waiting = new Panel();
  waiting.control.style.textAlign = 'center';
  waiting.control.innerHTML = 'Waiting for approval ...';
  waiting.control.style.fontWeight = 'bolder';
  waiting.control.style.fontSize = '20px';

  box.add(logout);
  box.add(waiting);
  box.add(loader);





  panel.add(label);
  panel.add(box);

  return panel;
};