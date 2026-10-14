import { Application, MessageBox, ConfirmBox, LoaderBox } from './plugin/mcontrol.js';
import { AppHome } from './home.js';
import { AppLogin } from './login.js';
import { AppHttp } from './plugin/app.js';
import { AppWait } from './waiting.js';
import { CSS, JS } from './util/file.js';




// import "./../css/app.css";
// import "./../app/plugin/core.css";
// import "./../app/plugin/font-awesome/css/font-awesome.min.css";

// // bs5
// import "./../app/plugin/bt/bs/css/bs5.css";
// import "./../app/plugin/bt/bs/js/bs5.js";






// end bs5

/// bs 3
// import "./../app/plugin/bt/bs/css/bootstrap.min.css";
// import "./../app/plugin/bt/bs/js/bootstrap.min.js";
/// end bs 3

// anonymous function for setting global variable
(function (global) {
  global.fernet = window.fernet;
}(window));

// load required css
// new JS().load("app/plugin/jquery")
// new CSS()
//   .load('app/plugin/bt/bs/css/bootstrap.min')
//   //.load('app/plugin/td')
//   .load('app/plugin/font-awesome/css/font-awesome.min')
//   .load('css/app');
// new JS().load("app/plugin/bt/bs/js/bootstrap.min");



// load required javascript
new JS()
  .load('app/plugin/fernet');
//.load('app/plugin/td');

export const App = new Application();

const App2 = new Application();

export const messageBox = new MessageBox();
export const confirmBox = new ConfirmBox();
export const loaderBox = new LoaderBox();


// dialog information
App2.add(messageBox);
App2.add(confirmBox);
App2.add(loaderBox);
// end dialog information

// route list
// export const appHome = new AppHome(); // Home page
// export const appLogin = new AppLogin(); // appLogin Page
// waiting area
// end route list

// Checking if logged in or not

let appHome = null;

const app_init = function () {
  const xml = AppHttp("/verify", {});
  xml.onload = function () {
    const data = JSON.parse(this.response);
    if (data.ok == 1) {
      appHome = new AppHome();
      App.open(appHome);
    } else if (data.ok == 2) {
      App.open(new AppWait());
    }
    else {
      App.open(new AppLogin());
    }
  };
};

const setHome = (homeObj) => {
  appHome = homeObj;
};

export default app_init;

export {appHome, setHome};