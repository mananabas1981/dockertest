var ClientRegister = function() {
  this.id = "";
  this.pref_name = null;
  this.fname = null;
  this.mname = null;
  this.lname = null;
  this.gender = null;
  this.suf_name = null;
  this.dob = null;
  this.pres_addr = null;
  this.ename = null;
  this.submit = null;

  this.clear = function() {
    this.id = "";
    this.pref_name.setValue("");
    this.fname.setValue("");
    this.mname.setValue("");
    this.lname.setValue("");
    this.gender.setValue("");
    this.suf_name.setValue("");
    this.dob.setValue("");
    this.pres_addr.setValue("");
    this.ename.setValue("");
  };

  this.submit_success = null;

  this.init = function() {
    var me = this;
    this.modal = new Modal("Client Registration", "user");
    this.pref_name = new TextBox("Prefix", "text", "user", "ex: Dr., Hon, etc...", "Enter Prefix");
    this.fname = new TextBox("Firstname", "text", "user", "Enter firstname", "Enter Firstname");
    this.mname = new TextBox("Middlename", "text", "user", "Middlename", "Enter middlename");
    this.lname = new TextBox("Lastname", "text", "user", "Enter Lastname", "Enter Lastname");
    this.ename = new TextBox("Extension Name", "text", "user", "Enter Extension name ex: jr, sr, || etc...", "Enter Extension name");
    this.gender = new ComboBox([["", "[Select Gender]"], ["f", "Female"], ["m", "Male"]], "Gender", "text", "transgender-alt", "Gender");
    this.suf_name = new TextBox("Suffix", "text", "user", "Enter Suffix: ex.. Phd, LET, etc...", "Enter Suffix");
    this.dob = new TextBox("Date of Birth", "date", "calendar", "Birth date");
    this.pres_addr = new TextBox("Address", "text", "address-card", "Address of the client", "Enter Address");
    
    this.submit = new Button("Save", "success", "save", "Save client");
    this.submit.control.style.marginTop = "5px";

    this.submit.addEventListener("click", function() {
      var data = {
        id: me.id,
        pref_name: me.pref_name.getValue(),
        fname: me.fname.getValue(),
        mname: me.mname.getValue(),
        lname: me.lname.getValue(),
        ename: me.ename.getValue(),
        suf_name: me.suf_name.getValue(),
        gender: me.gender.getValue(),
        addr: me.pres_addr.getValue(),
        dob: me.dob.getValue()
      };
      
      confirmBox.show("Save Information?", function() {
        loaderBox.show();
        AppHttp("/client/save", data, {}, function(o) {
          loaderBox.hide();
          var data = JSON.parse(o);
          if (data.ok == 0) {
            messageBox.show('<span style="color:red;">${data.msg}</span>');
            return;
          }
          me.submit_success(o);
        });
      });

    });

    this.modal.add(this.pref_name);
    this.modal.add(this.fname);
    this.modal.add(this.mname);
    this.modal.add(this.lname);
    this.modal.add(this.ename);
    this.modal.add(this.suf_name);
    this.modal.add(this.gender);
    this.modal.add(this.dob);
    this.modal.add(this.pres_addr);
    this.modal.add(this.submit);
  };

  this.update = function(data) {
    this.clear();
    var data = data || null;
    if (data != null) {
      this.id = data["id"];
      this.pref_name.setValue(data["pref_name"]);
      this.fname.setValue(data["fname"]);  
      this.mname.setValue(data["mname"]);
      this.lname.setValue(data["lname"]);
      this.gender.setValue(data["gender"]);
      this.suf_name.setValue(data["suf_name"]);
      this.dob.setValue(data["dob"]);
      this.pres_addr.setValue(data["address"]);
      this.ename.setValue(data["ename"]);
    }
  };

  this.show = function() {
    this.modal.show();
  };

  this.hide = function() {
    this.modal.hide();
  };

  this.getContainer = function() {
    return this.modal.getContainer();
  };

  this.init();
};