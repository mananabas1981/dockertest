import { Text } from "./text.js";
function dateCountDown(date_adv, cur_date) {
  var date_adv = new Date(date_adv);
  var cur_date = new Date(cur_date);
  var ms = date_adv - cur_date;

  var is_ps = ms > 0;


  var label_key = ['Y', 'M', 'd', 'h', 'm', 's'];
  var label_value = [31104000000, 2592000000, 86400000, 3600000, 60000, 1000];
  var ln = label_key.length;

  var label = [];

  var i = 0;
  while (i < ln) {
    var value = label_value[i];
    var dv = ms / value;
    /* Fixed for large number  problem in javascript  */
    if (dv > 0 && ms < value) {
      dv = 0;
    }
    /* End Fixed for large number */

    var rem = ms % value; // remainder
    ms = rem;

    label.push([label_key[i], parseInt(dv)]);
    i++;
  }

  return { positive: is_ps, data: label };

}

function dateCount(date_adv, cur_date) {
  var dos = dateCountDown(date_adv, cur_date);
  var d = dos.data;


  var i = 0;

  for (i = 0; i < 5; i++) {
    if (d[i][1] > 0) {
      break;
    }
  }

  var str = "";

  for (; i <= 5; i++) {
    str += d[i][1] + '' + d[i][0] + ' ';
  }

  return [dos.positive, str];
}

var AppStorage = {
  data: {},
  setItem: function (key, value) {
    this.data[key] = value;
  },
  getItem: function (key) {
    return this.data[key] || null;
  },
  removeItem: function (key) {
    var d = this.data[key] || null;
    if (d != null) {
      delete this.data[key];
    }
  }
};

var AppFormInput = function (input_class, _data) {
  var data = _data || {};

  var input = AppClass(input_class);
  var input_len = input.length;
  for (var i = 0; i < input_len; i++) {
    for (var key in data) {
      if (key == input[i].attributes.name.nodeValue) {
        input[i].value = data[key];
      }
    }
  }
};

function FormInfo(input_class) {
  this.input = input_class;
  this.data = {};

  this.__process = function () {
    var input = AppClass(this.input);
    var input_len = input.length;
    for (var i = 0; i < input_len; i++) {
      this.data[input[i].attributes.name.nodeValue] = input[i].value;
    }
  };

  this.getData = function () {
    return this.data;
  };

  this.__process();
}
// end class

var AppComponent = {};

var AppId = function (_id) {
  return document.getElementById(_id);
};

var AppClass = function (_class) {
  return document.getElementsByClassName(_class);
};

var AppAlert = function (_m) {
  alert(_m);
};

var AppConfirm = function (_m, func_) {
  var fn = func_ || null;
  if (confirm(_m)) {
    if (fn != null) {
      fn();
    }
  }
};

var AppRoute = function (_id, _html, _param) {
  var param = _param || {};
  if (typeof (_html) == "function") {
    AppId(_id).innerHTML = _html(true, param);
    _html(false, param);
  }
  else {
    AppAlert("Invalid App gui");
  }
};

var AppForm = function (input_class) {
  var appForm = new FormInfo(input_class);
  return appForm.getData();
};

var AppFormClear = function (input_class) {
  var el = AppClass(input_class);
  for (var x of el) {
    x.value = "";
  }
};

var AppIdEvent = function (_el, _e, _calback) {
  var x = AppId(_el);
  x.addEventListener(_e, function (e) {
    _calback(e);
  });
};

var AppClassEvent = function (_el, _e, _calback) {
  var x = AppClass(_el);
  var callback = _calback || null;
  var evt = _e || null;
  if (evt == null) {
    alert("Invalid Event");
    return;
  }
  if (callback == null) {
    alert("Invalid callback");
    return;
  }
  for (var y of x) {
    y.addEventListener(evt, function (e) {
      _calback(e);
    });
  }
};


export var Config = {
  url: "",
  token: localStorage.getItem("_token"),
  fkey: localStorage.getItem("_fkey"),
  getKey: function () {
    return "HZRIHcFraxLP-s0HJtHO7vYRvyYSVeFKTZU1OopNY5A=";
  }
};

export var AppHttp = function (_url, _data, _param, __callback, __error) {
  var url = _url || null;
  var data = _data || null;
  var param = _param || {};
  var __callback = __callback || null;
  var __error = __error || null;

  var method = param["method"] || "POST";
  var headers = param["headers"] || [];

  var xml = new XMLHttpRequest();
  xml.open(method, Config["url"] + url);
  if (data instanceof FormData) {
    //xml.setRequestHeader("Content-Type", "application/json");
  } else if (typeof (data) == "object") {
    xml.setRequestHeader("Content-Type", "application/json");
    data = JSON.stringify(data);
  }
  if (Config.token != null) {
    xml.setRequestHeader("Auth", '_token=' + Config.token);
  }
  for (var h of headers) {
    xml.setRequestHeader(h[0], h[1]);
  }
  if (method.toLowerCase() == "get") {
    data = null;
  }
  if (Config.fkey != null) {
    if (typeof (__callback) == "function") {
      if (data != null) {
        if (typeof (data) == "object") {
          data["token"] = Config["token"];
          data = JSON.stringify(data);
        } else {
          data = JSON.parse(data);
          data["token"] = Config["token"];
          data = JSON.stringify(data);
        }
      }
      var txt = new Text(Config.fkey);
      xml.send(txt.encrypt(data));
    } else {
      xml.send(data);
    }
  } else {
    xml.send(data);
  }
  // this is a callback function for the data
  // this callback is the response encrypted data
  if (typeof (__callback) == "function") {
    var txt = new Text(Config.fkey);
    xml.onload = function () {
      __callback(txt.decrypt(this.response));
    };
  }
  xml.onerror = function (e) {
    if (__error != null) __error(e);
  };
  return xml;
};
