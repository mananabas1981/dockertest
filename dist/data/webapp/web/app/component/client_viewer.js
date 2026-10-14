var ClientViewer = function() {
  
  // initialized the components
  
  this.fname = null;
  this.container = null;
  this.modal = null;

  this.getContainer = function() {
    return this.container;
  };

  this.show = function() {
    this.modal.show();
  };

  this.hide = function() {
    this.modal.hide();
  };  

  this.init = function() {

    // this.container.append(modal);
    this.modal = new Modal("Client Information", "user");
    var table = new Table(["", ""]);
    
    this.fname = new Label();
    this.gender = new Label();
    this.dob = new Label();

    table.add(["Name", this.fname]);
    table.add(["Gender", this.gender]);
    table.add(["Date of Birth", this.dob]);

    this.modal.add(table);

    this._vm = new Button("View Meters", "warning", "", "View Meter List");
    this._vm.setIcon("tachometer");
    this._vm.addEventListener("click", function() {
      meterpage = new MeterPage();
      App.open(meterpage);
    });
    this.modal.add(this._vm);
    this.container = this.modal.getContainer();
  };
  
  this.update = function(data, id) {
    var data = data || null;
    var id = id || null;
    if (data != null) {
      // var fname = `${data["lname"]} ${data["ename"]}, ${data["fname"]} ${data["mname"]}`.toUpperCase();
      var fname = (data["lname"] + " " + data["ename"] + ", " + data["fname"] + " " + data["mname"]).toUpperCase();

      var gender = "";
      if (data["gender"] == "m") gender = "MALE";
      if (data["gender"] == "f") gender = "FEMALE";
      this.fname.setValue(fname);
      this.gender.setValue(gender);
      this.dob.setValue(data["address"]);
    }
    if (id != null) {
      // render the data from the server
    }
  };

  this.init();

};