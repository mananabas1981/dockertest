import { Panel, TextBox } from "../plugin/mcontrol.js";

export class ChatBox extends Panel{
  constructor() {
    super();

    this.setStyle({
      backgroundColor: "#dddd",
      position: "fixed",
      width: "360px",
      height: "240px",
      right: "1px",
      bottom: "1px",
      zIndex: "20",
      border: "2px solid grey"
    });

    //document.body.appendChild(this._c);

    this.body.appendChild(this.control);

    this.hostname = window.location.hostname;
    
    this.chat_box = new Panel().setStyle({
      height: "205px",
      backgroundColor: "orange",
      overflowY: "scroll"
    });

    this.tf = new TextBox("Send", "text", "comments-o");
    
    this.tf.addEventListener("keyup", (e) => {
      if (e.keyCode == 13) {
        const send = {
          'type': 'all',
          'msg': this.tf.getValue()
        };
        this.ws.send(JSON.stringify(send));
      }
    });


    this.add(this.chat_box);
    this.add(this.tf);

    this.connect();

    this.list_user = [];

    this.hide();

    this.is_close = false;
  }

  show() {
    super.show();
  }
  hide() {
    super.hide();
  }

  connect() {
    this.ws = new WebSocket(`ws://${this.hostname}:7777/live-app`);

    this.ws.onopen = () => {
      console.log("connected!");
      this.onOpen();
    };

    this.ws.onmessage = (evt) => {
      this.message(evt.data);
    };

    this.ws.onclose = () => {
      if (!this.is_close) {
        console.log("disconnected!");

        console.log("reconnected in 2 seconds");
        setTimeout(() => {
          this.connect();
        }, 2000);
      }
    }
  
  }

  message(o) {
    const data = JSON.parse(o);
    const{type, msg, user, list} = data;
    if (type == 'all') {

      // const chat = this.chat_box;
      
      // const panel = new Panel(); 
    
    } else if (type == "total") {
      this.list_user = list;
    }
    
  }

  getUsers() {
    return this.list_user;
  }

  onOpen() {;
    setTimeout(() => {
      this.ws.send(JSON.stringify({
        id: localStorage.getItem('_token')
      }));

      setTimeout(() => {
        this.ws.send('watch');
      }, 500);
      
    }, 1000);
  }

  close() {
    this.is_close = true;
    this.ws.close();
    this.delete();
  }
}
