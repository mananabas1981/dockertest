export var Text = function (key) {
  this.__key = key;
  this.__fernetSecret = new window.fernet.Secret(key);

  this.encrypt = function (data) {
    var token = new fernet.Token({
      secret: this.__fernetSecret
    });
    return token.encode(data);
  };
  this.decrypt = function (data) {
    var token = new window.fernet.Token({
      secret: this.__fernetSecret,
      token: data
    });
    return token.decode();
  };
};