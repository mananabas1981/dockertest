import { Panel, Button, Label, TextBox, x_storage } from "./plugin/mcontrol.js";
import { TransactionMain } from "./transaction.js";
import { HomeView } from "./dashboard.js";
import { UserApproval } from "./user_approval.js";
import { AboutView } from "./about.js";
import { SettingView } from "./settings.js";
import { PaySlipView } from "./payslip.js";
import { ChatBox } from "./component/chat.js";
import { RemittanceMainPage } from './transaction/rem.js';
import { Notification } from './component/notification.js';

var _clearActive = function (me) {
  var h = document.getElementsByClassName("side-menu-btn");
  for (var x of h) {
    x.classList.remove("side-menu-active");
  }
  me.classList.add("side-menu-active");
};

// function htmlEscape(str) {
//   return str.replace(/&/g, '&amp;')
//     .replace(/</g, '&lt;')
//     .replace(/>/g, '&gt;')
//     .replace(/"/g, '&quot;')
//     .replace(/'/g, '&#39;');
// }

// var app_ws = null;
// var app_attemps = 0;
// // socket connection

// var gmessage_box = null; // input box
// var gtf = null; // textfield
// var gtop = null;

// var ConnectSocket = function () {
//   app_attemps += 1;

//   app_ws = new WebSocket('ws://' + location.hostname + ':7777/live-app');

//   app_ws.onopen = function () {

//     setTimeout(function () {
//       app_ws.send(JSON.stringify({
//         id: localStorage.getItem('_token')
//       }));

//       setTimeout(function () {

//         app_ws.send('watch');
//       }, 500);
//     }, 1000);

//   };

//   app_ws.onmessage = function (evt) {
//     var data = JSON.parse(evt.data);

//     if (data['type'] == 'all') {
//       var user = data['user']

//       var user_panel = new Panel().setStyle({
//         width: '100%',
//         marginBottom: '5px',
//         fontWeight: 'bold',
//         padding: '5px'
//       });

//       user_panel.control.innerHTML = '<i class="fa fa-user-circle"></i> ' + user.toUpperCase();

//       var panel = new Panel().setStyle({
//         width: '100%',
//         backgroundColor: '#5a5a5a',
//         color: 'white',
//         marginBottom: '5px',
//         padding: '5px',
//         borderRadius: '5px'
//       });


//       var msg_panel = new Panel().setStyle({
//         textAlign: 'justify'
//       });

//       msg_panel.control.innerHTML = htmlEscape(data['msg']) + '<hr />' + '<i>Date Sent: ' + data['date'] + '</i>';

//       panel.add(user_panel);
//       panel.add(msg_panel);


//       gmessage_box.add(panel);

//       gmessage_box.control.scrollTop = gmessage_box.control.scrollHeight;
//     } else if (data['type'] == 'total') {

//       console.log(data['list']);

//       var label = new Panel().setStyle({});

//       label.control.innerHTML = '<div style="padding: 15px"> <i class="fa fa-user-plus"></i> ' + data['msg'] + '</div>';
//       gtop.clear();
//       gtop.add(label);

//     }

//     // app_ws.send('watch');
//   };

//   app_ws.onclose = function () {

//     // if (app_attemps >= 20) {

//     //   app_attemps = 0;
//     //   return;
//     // }
    
//     var label = new Panel().setStyle({});

//     label.control.innerHTML = '<div style="padding: 15px"> <i class="fa fa-close" style="color: red;"></i> Disconnected!</div>';
//     gtop.clear();
//     gtop.add(label);

//     setTimeout(function () {
//       ConnectSocket();
//     }, 5000);

//     console.log("Connection Closed!");

//   };
// };

export class AppHome extends Panel {
  constructor() {
      // ConnectSocket(); // connect the socket if this function trigger
    super();

    // Loading Notification
    
    (async() => {
      const notif = new Notification({
        show: true
      });
       // show this if it is completely loaded
    })();
    // end Loading the notification

    this.addClass("main-panel");

    // initialized chat box
    this.chat = new ChatBox();

    var SIDE_WIDTH = 260;
    // create top navigation
    var side_panel = new Panel();
    side_panel.addClass("side-panel");
    side_panel.control.style.width = SIDE_WIDTH + "px";

    // background
    var side_panel_bg = new Panel();
    side_panel_bg.addClass("side-panel-bg");
    side_panel_bg.control.style.width = SIDE_WIDTH + "px";

    // create title for side panel

    var side_title = new Panel();
    side_title.control.style.padding = "12px";
    side_title.control.style.paddingTop = "5px";

    var side_title_c = new Panel();
    side_title_c.addClass("side-title");

    var logo = new Panel();
    logo.addClass("side-logo");

    side_title_c.add(logo);

    var title_txt = new Panel();
    title_txt.control.innerHTML = "Payroll System"
    title_txt.control.style.fontSize = "18pt";
    title_txt.control.style.position = "absolute";
    title_txt.control.style.left = "60px";
    title_txt.control.style.top = "10px";
    title_txt.control.style.color = "#aba5a5";

    side_title_c.add(title_txt);

    side_title.add(side_title_c);
    side_panel.add(side_title);
    // end title side panel


    // create button menu
    var btn_cont_panel = new Panel();
    btn_cont_panel.control.style.padding = "20px";
    btn_cont_panel.control.style.paddingTop = "10px";

    function clearGlobal() {
      if (x_storage.getItem('timer') != null) {
        clearInterval(x_storage.getItem('timer'));
      }
      // free up the memory of the global variable to avoid the overloaded memory
    };

    var dash_menu = this.createButton("My Profile", "user-circle");
    dash_menu.addEventListener("click",  (e) => {
      _clearActive(e.currentTarget);
      this.setContent(HomeView(this), "My Profile");

      clearGlobal();
    });

    var trans_menu = this.createButton("Transaction", "windows");
    trans_menu.addEventListener("click", (e) => {
      _clearActive(e.currentTarget);
      // this.setContent(TransactionView(this), "Transaction");

      this.setContent(new TransactionMain(), "Transaction");

      clearGlobal();
    });

    const rem_menu = this.createButton("Remittance Mgt.", "id-card");
    rem_menu.addEventListener("click", (e) => {
      _clearActive(e.currentTarget);
      // this.setContent(TransactionView(this), "Remittance Management");
      this.setContent(new RemittanceMainPage({appHome: this}), 'Remittance Management');
      clearGlobal();
    });


    const payslip_menu = this.createButton('PaySlip', 'money');
    payslip_menu.addEventListener('click', (e) => {
      _clearActive(e.currentTarget);
      this.setContent(PaySlipView, "PaySlip Viewer");
      clearGlobal();
    });

    var setting_menu = this.createButton("Settings", "cogs");
    setting_menu.addEventListener("click", (e) => {
      _clearActive(e.currentTarget);
      this.setContent(SettingView, "Setting");

      clearGlobal();
    });

    var about_menu = this.createButton("About", "question-circle");
    about_menu.addEventListener("click", (e) => {
      _clearActive(e.currentTarget);
      this.setContent(AboutView, "About");

      clearGlobal();
    });

    var login_app = this.createButton('User Approval', 'folder-o');

    login_app.addEventListener('click', (e) => {
      _clearActive(e.currentTarget);
      this.setContent(UserApproval, "User Login Approval");

      clearGlobal();
    });


    this.title = new Label("");
    this.title.control.style.fontSize = "12pt";
    this.title.control.style.fontWeight = "regular";
    this.title.control.style.padding = "10px 10px 0 10px";
    this.title.control.style.color = "#666060";

    this.content = new Panel();
    this.content.addClass("content");
    this.content.control.style.paddingLeft = SIDE_WIDTH + "px";
    this.setContent();

    btn_cont_panel.add(dash_menu);
    btn_cont_panel.add(trans_menu);
    //btn_cont_panel.add(rem_menu);
    btn_cont_panel.add(payslip_menu);
    btn_cont_panel.add(login_app);
    btn_cont_panel.add(setting_menu);
    btn_cont_panel.add(about_menu);
    side_panel.add(btn_cont_panel);
    // end create button menu

    this.add(side_panel_bg);
    this.add(side_panel);
    this.add(this.content);

    var body_content = this.content;
    // bars
    var bar_toggle = true;

    var bars = new Button(null, 'primary', 'bars')
      .setStyle({
        position: 'fixed',
        top: '2px',
        right: '2px',
        zIndex: 100,
        backgroundColor: 'rgba(0, 0, 0, 0.3)'
      })
      .addEventListener('click', function () {
        // body_content.setStyle({
        //   width: '0px'
        // })

        if (bar_toggle) {

          side_panel.setStyle({
            width: '0px'
          });
          side_panel_bg.setStyle({
            width: '0px'
          });
          body_content.setStyle({
            paddingLeft: '0px'
          });
        } else {
          side_panel.setStyle({
            width: SIDE_WIDTH + 'px'
          });
          side_panel_bg.setStyle({
            width: SIDE_WIDTH + 'px'
          });
          body_content.setStyle({
            paddingLeft: SIDE_WIDTH + 'px'
          });
        }
        bar_toggle = !bar_toggle;
      });

    this.add(bars);
    // end bars

    // add bell notifications
    const bell = new Button("", "", "bell");
    bell.setStyle({
      position: "fixed",
      top: "5px",
      right: "50px",
      zIndex: "10",
      color: "white",
      backgroundColor: "#D32F2F",
      width: "35px",
      border: "1px solid #dddd",
      borderRadius: "5px"
    });
    bell.addEventListener("click", async function() {
      const notif = new Notification();
      notif.show();
    });

    this.add(bell);
    // end bell


    // chat application


  }
  dispose() {
    this.chat.close();
    console.log("home is disposed");
    
  }


  createButton = function (title, icon) {
    const btn = new Button(title, null, icon);
    btn.addClass("side-menu-btn");
    return btn;
  };
  
  setContent = function (_, title = "") {
    var _ = _ || null;
    if (_ != null) {
      this.content.clear();
      this.title.html(title);
      this.content.add(this.title);
      try {
        this.content.add(_());
      } catch (e) {
        this.content.add(_);
      }
    }
  };
}

// end of AppHome


