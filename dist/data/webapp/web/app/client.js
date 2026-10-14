var AppClientTable = {
  container: null,
  gen: null,
  load_xhr: null,
  getContainer: function() {
    this.container = document.createElement("div");
    this.container.setAttribute("class", "panel");

    var title = document.createElement("div");
    title.classList.add("title");
    title.innerHTML = '<i class="fa fa-user"></i> Client List';
    this.container.append(title);

    // search container
    var search_con = document.createElement("div");
    search_con.style.padding = "5px";
    search_con.style.position = "relative";
    
    
    var search = new TextBox("", "", "search", "Search name here!");
    search.setPlaceHolder("Search here!");
    
    search.addEventListener("keyup", function(e) {
      if (e.key == "Enter") {
        AppClientTable.load_xhr();
      }
    });
    
    search_con.append(search.getContainer());

    this.container.append(search_con);
    // end search

    this.gen = document.createElement("div");
    this.gen.setAttribute("class", "table-responsive");

    this.load_xhr = function() {
      client_table.load();
      AppHttp("/client/list", {search: search.getValue()}, {}, function(o) {
        var r = JSON.parse(o);
        var data = r["data"];
        var data_len = data.length;

        client_table.clear();
        for (var i = 0; i < data_len; i++) {
          var fname = data[i]["lname"] + ", " + data[i]["fname"] + " " + data[i]["mname"];

          var bgroup = new Panel();
          bgroup.control.setAttribute("class", "btn-group");

          var view = new Button("", "success", "eye", "View " + fname);
          view.getContainer().setAttribute("rel", i);
          view.addEventListener("click", function() {
            var index = this.attributes.rel.nodeValue;
            client_viewer.show();
            client_viewer.update(data[index]);
          });

          var edit = new Button("", "primary", "edit", "Edit " + fname);
          edit.getContainer().setAttribute("rel", i);
          edit.addEventListener("click", function() {
            // var index = this.attributes.rel.nodeValue;
            // clientForm.update(data[index]);
            // clientForm.show();
            alert("upudate");
          });

          bgroup.add(view);
          bgroup.add(edit);

          var d = [data[i]["id"], fname.toUpperCase(), data[i]["address"], bgroup];
          client_table.add(d);
        }
        // client_table.show();
        client_table.show();
        AppClientTable.gen.innerHTML = "";
        AppClientTable.gen.append(client_table.getContainer());

      });
    };

    this.load_xhr();

    this.container.style.display = "block";
    this.container.style.marginTop = "20px";
    this.container.append(this.gen);

    return this.container;
  }
};



var ClientView = function() {
  var panel = new Panel();
  panel.control.style.padding = "10px";

  var add = new Button("Add Client", "success", "user-plus", "Click to add new client");
  
  add.addEventListener("click", function() {
    alert('add');
  });

  panel.add(add);
  
  panel.add(AppClientTable);

  return panel;
};

ClientView.prototype = Object.create(Interface.prototype);