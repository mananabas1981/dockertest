const employee_page1 = function (appHome) {

  e_info = emp_info();
  emp_info_modal = e_info.modal;

  var panel = new Panel();
  panel.control.style.padding = "5px";
  //create table

  table = new Table(["Action", "Profile", "Name", "Position", "Status", 'Active', 'Last Process']);
  var panel2 = new Panel();
  panel2.addClass("card");

  var emp_view = employee_viewer();
  emp_modal = emp_view.modal;
  emp_form = emp_view.form;



  // load client
  reload_table();

  var newbtn = new Button("Add Employee", "success", "user-plus");
  newbtn.control.style.marginBottom = "5px";
  newbtn.addEventListener("click", function () {
    emp_form.clear();
    emp_modal.show();
  });

  const loan_contrib_btn = new Button("Loan & Contribution", "success", "refresh").setStyle({
    marginLeft: '5px',
    marginBottom: '5px'
  });
  loan_contrib_btn.addEventListener('click', async () => {
    // const modal = new ExcelContribModal();
    // await modal.show();

    const modal = new HtmlConLoan();
    await modal.show();
    
  });

  var sync_modal = new Modal("HR System");
  var sync_loader = new LoaderBox();
  sync_modal.add(sync_loader);

  // loaderBox.show();
  var sync = new Button("Sync", "success", "refresh");
  sync.control.style.marginBottom = "5px";
  sync.control.style.marginLeft = "5px";

  var sheader = new Panel();

  var scontent = new Panel();
  sync_modal.add(sheader);
  sync_modal.add(scontent);

  var rate_info = { a: "Yearly", m: "Monthly", "d": "Daily", "h": "Hourly" };

  sync.addEventListener("click", function () {

    var date_reg = new RegExp('^[0-9]{4}-[0-9]{2}-[0-9]{2}$');

    var from = prompt('Date From(YYYY-MM-DD):');

    if (!date_reg.test(from)) {
      return alert('Invalid Date (From)');
    }

    var to = prompt('Date To(YYYY-MM-DD):');

    if (!date_reg.test(to)) {
      return alert('Invalid Date (To)');
    }

    sync_modal.show();
    loaderBox.show("Connecting to HR System...");

    var table = new Table(["Action", "Name", "Rate", "Status", "DeptInfo"]);

    AppHttp("/api/hrms/employee", { from: from, to: to }, null, function (o) {
      loaderBox.hide();
      var data = JSON.parse(o);
      if (!data.ok) return alert(data.msg);
      scontent.clear();
      var fdata = data.data;
      var fdata_len = fdata.length;
      for (var i = 0; i < fdata_len; i++) {
        // parse the department information if it is not null
        var dept_info = fdata[i].dept_info != null ? JSON.parse(fdata[i].dept_info) : null;
        var dept_code = "";
        if (dept_info != null) {
          dept_code = dept_info["code"];
        }
        var add = null;
        if (!fdata[i]["found"]) {
          add = new Button("", "success", "plus-circle", null);
          add.control.setAttribute("rel", i);
        }
        else {
          add = new Button("", "default", "plus-circle", null);
          add.control.setAttribute("rel", i);
        }
        add.addEventListener("click", function () {
          var index = this.attributes.rel.nodeValue;
          var data = JSON.stringify(fdata[index]);
          loaderBox.show("Saving... Please wait...");
          AppHttp("/api/hrms/save", data, null, function (o) {
            var data = JSON.parse(o);
            if (data.ok) {
              messageBox.show(data.msg);
            } else {
              alert(data.msg);
            }
            loaderBox.hide();
          });
        });

        var status = fdata[i]["found"] ? 'Added' : 'Not Added';

        table.add([
          add,
          fdata[i].lname + ", " + fdata[i].fname + " " + fdata[i].mname + " " + fdata[i].ename,
          parseFloat(fdata[i].rate).toLocaleString() + "/" + rate_info[fdata[i].rate_type],
          fdata[i].stat,
          dept_code
        ]);

      }
      sheader.control.innerHTML = "Total Result: " + fdata_len;
      var sync_id = new Button('Sync HR System ID', 'success', 'refresh');
      sync_id.control.style.marginBottom = '10px';

      sync_id.addEventListener('click', function () {

        var data = [];

        for (var i = 0; i < fdata_len; i++) {
          var x = fdata[i];
          data.push({
            'emp_id': x.no,
            'fname': x.fname,
            'mname': x.mname,
            'lname': x.lname,
            'ename': x.ename
          });
        }

        if (!confirm('Proceed? Make to backup your system database!!!')) return;

        AppHttp('/api/hrms/sync_all_id', data, null, function (o) {
          var data = JSON.parse(o);
          if (data.ok) {
            messageBox.show(data.msg);
          } else {
            alert(data.msg);
          }
        });

      });

      scontent.add(sync_id);
      scontent.add(table);
      sync_modal.add(scontent);
    });
  });

  search = new TextBox(null, "text", "search", null, "Search.... Lastname, Firstname, middlename");
  dept_id = new ComboBox(null, null, null, "home");
  emp_status = new ComboBox(null, null, null, "refresh");

  emp_status.add("", "[ All ]");
  emp_status.add("j", "Job Orders");
  emp_status.add("c", "Contract Of Service");
  emp_status.add("r", "Regular(Permanent.Temporary.Elective.etc...)");

  active = new ComboBox(null, null, null, 'cog');
  active.add('', 'All');
  active.add('y', 'Active');
  active.add('n', 'Inactive');

  var srow = new Panel();
  srow.addClass("container-fluid");

  // var std1 = new Panel();
  // std1.addClass("col-md-3");
  // std1.add(search);

  // var std2 = new Panel();
  // std2.addClass("col-md-3");
  // std2.add(dept_id);

  // var std3 = new Panel();
  // std3.addClass("col-md-3");
  // std3.add(emp_status);

  // srow.add(std1);
  // srow.add(std2);
  // srow.add(std3);

  const grid = new Grid(2);
  grid.cell(search, ['md-3', 'sm-3']);
  grid.cell(dept_id, ['md-3', 'sm-3']);
  grid.cell(emp_status, ['md-3', 'sm-3']);
  grid.cell(active, ['md-3', 'sm-3']);

  srow.add(grid);

  search.addEventListener("change", function () {
    reload_table({
      "search": search.getValue(),
      "dept_id": dept_id.getValue(),
      "emp_status": emp_status.getValue(),
      'active': active.getValue()
    });
  });
  dept_id.addEventListener("change", function () {
    reload_table({
      "search": search.getValue(),
      "dept_id": dept_id.getValue(),
      "emp_status": emp_status.getValue(),
      'active': active.getValue()
    });
  });
  emp_status.addEventListener("change", function () {
    reload_table({
      "search": search.getValue(),
      "dept_id": dept_id.getValue(),
      "emp_status": emp_status.getValue(),
      'active': active.getValue()
    });
  });

  active.addEventListener('change', () => {
    reload_table({
      "search": search.getValue(),
      "dept_id": dept_id.getValue(),
      "emp_status": emp_status.getValue(),
      'active': active.getValue()
    });
  });

  // loadDept function
  var loadDepartment = function () {
    AppHttp("/department/list", {}, null, function (o) {
      var res = JSON.parse(o);
      var data = res.data;
      var data_len = data.length;
      dept_id.clear();
      dept_id.add("", "All Department");
      for (var i = 0; i < data_len; i++) {
        dept_id.add(data[i][0], data[i][1] + " - " + data[i][2]);
      }
    });
  };
  loadDepartment();
  // end load dept
  panel2.add(srow);
  panel2.add(table);
  panel.add(newbtn);
  panel.add(loan_contrib_btn);
  // panel.add(sync); remove sync 
  panel.add(cardInfo);
  panel.add(panel2);
  panel.add(emp_modal);
  panel.add(emp_info_modal);

  panel.add(sync_modal);
  return panel;
};





// table


const reload_table = function (param) {
  // @ param is an dict
  var param = param || {}; // default value
  var search = param["search"] || "";
  var dept_id = param["dept_id"] || "";
  var emp_status = param["emp_status"] || "";
  const active = param['active'] || '';

  search_employee({
    "search": search,
    "dept_id": dept_id,
    "emp_status": emp_status,
    'active': active
  }, function (o) {
    table.clear();
    var total = o["data"]["total"];
    var data = o["data"]["data"];
    var data_len = data.length;
    card_emp_total.control.innerHTML = "Total: " + total + " Results   |  Max Display: 200 data";
    for (let i = 0; i < data_len; i++) {
      let error = data[i]["error"];
      let pos_info = data[i]["pos_info"];
      let view = new Button(null, "success", "user").setStyle({ width: '40px' });
      view.control.setAttribute("rel", i);
      view.addEventListener("click", function () {
        const index = this.attributes.rel.nodeValue;
        const fdata = data[index];
        /// open the modal
        // console.log(emp_form.getValues());
        var input = emp_form.input;
        input.pref_name.setValue(fdata.pref_name);
        input.fname.setValue(fdata.fname);
        input.mname.setValue(fdata.mname);
        input.lname.setValue(fdata.lname);
        input.ename.setValue(fdata.ename);
        input.gender.setValue(fdata.gender);
        input.dob.setValue(fdata.dob);
        input.suf_name.setValue(fdata.suf_name);
        input.addr.setValue(fdata.address);
        input.id.setValue(fdata.id);
        input.hr_id.setValue(fdata.hr_id);
        emp_modal.show();
      });

      var update = new Button(null, "primary", "edit").setStyle({ width: '40px' });
      update.control.setAttribute("rel", i);
      update.addEventListener("click", function () {
        var index = this.attributes.rel.nodeValue;
        var emp_data = data[index];
        emp_info_modal.show();
        e_info.name.control.innerHTML = (emp_data.lname + ", " + emp_data.fname).toUpperCase();
        GLOBAL_DATA["emp_id"] = emp_data.id;
      });

      var err_panel = new Panel();

      for (var k = 0; k < error.length; k++) {
        var p1 = new Panel();
        if (error[k].error) {
          p1.control.innerHTML = '<span style="color: black; text-decoration: underline;"><i class="fa fa-close" style="color: red;"></i> ' + error[k].msg + '</span>';
        } else {
          p1.control.innerHTML = '<span style="color: black; text-decoration: underline;"><i class="fa fa-check" style="color: green;"></i> ' + error[k].msg + '</span>';
        }
        err_panel.add(p1);
      }

      var _p = new Panel();
      var pos_panel = new Panel();
      _p.control.innerHTML = 'Created: ' + data[i].created + " ago";

      pos_panel.add(_p);

      for (var m = 0; m < pos_info.length; m++) {
        var _p = new Panel();
        _p.control.innerHTML = pos_info[m].key + " : " + pos_info[m].value;
        pos_panel.add(_p);
      }

      var panel = new Panel().addClass('container-fluid').setStyle({ width: '180px' });

      var profile = new Panel();
      profile.control.style.width = "50px";
      profile.control.style.height = "50px";
      profile.control.style.borderRadius = "50%";
      profile.control.style.border = "1px solid #ddd";

      const active = new Button(null, 'default', 'cog').setStyle({ width: '40px' });


      // panel.add(view);
      // panel.add(update);
      // panel.add(active);

      // const action = new Grid(2);
      // action.cell(view, ['md-3', 'sm-3', 'xs-3']);
      // action.cell(update, ['md-3', 'sm-3', 'xs-3']);
      // action.cell(active, ['md-3', 'sm-3', 'xs-3']);
      
      const menu = new DropDown(`ACTION`);
      menu.addItem(`<i class="fa fa-edit"></i> Edit Employee`, () => {
        const fdata = data[i];
        /// open the modal
        // console.log(emp_form.getValues());
        var input = emp_form.input;
        input.pref_name.setValue(fdata.pref_name);
        input.fname.setValue(fdata.fname);
        input.mname.setValue(fdata.mname);
        input.lname.setValue(fdata.lname);
        input.ename.setValue(fdata.ename);
        input.gender.setValue(fdata.gender);
        input.dob.setValue(fdata.dob);
        input.suf_name.setValue(fdata.suf_name);
        input.addr.setValue(fdata.address);
        input.id.setValue(fdata.id);
        input.hr_id.setValue(fdata.hr_id);
        emp_modal.show();
      });

      menu.addItem(`<i class="fa fa-pencil"></i> Update Rate, Position, Department etc...`, () => {
        const emp_data = data[i];
        emp_info_modal.show();
        e_info.name.control.innerHTML = (emp_data.lname + ", " + emp_data.fname).toUpperCase();
        GLOBAL_DATA["emp_id"] = emp_data.id;
      });


      menu.addItem(`<i class="fa fa-money"></i> Update loan & Contribution`, () => {
        const { id, fname, lname, mname, ename, pref_name, suf_name, pos_status } = data[i];
        const cl = new ContribLoan(id, pos_status, `${pref_name} ${fname} ${mname} ${lname} ${ename} ${suf_name}`.toUpperCase());
        cl.show();
      });

      menu.addItem(`<i class="fa fa-flag"></i> Activation or Deactivation`, async () => {
        const info = data[i];
        const ac = new ActiveModal(info.id, `${info.pref_name} ${info.fname} ${info.mname} ${info.lname} ${info.suf_name}`.toUpperCase(), info.active);
        const res = await ac.show();
      });

      panel.add(menu);

      active.addEventListener('click', async () => {
        const info = data[i];
        const ac = new ActiveModal(info.id, `${info.pref_name} ${info.fname} ${info.mname} ${info.lname} ${info.suf_name}`.toUpperCase(), info.active);
        const res = await ac.show();
      });


      const claim =  data[i]["claim"];
      let last_refid = '';
      if (claim) {
        last_refid = claim[2]
      }

      table.add([
        panel,
        profile,
        (data[i].lname + ", " + data[i]["fname"] + " " + data[i].mname).toUpperCase(),
        pos_panel,
        err_panel,
        new Panel().add(new Label(data[i].active == 'y' ? 'YES' : 'NO')).setStyle({ color: (data[i].active == 'y' ? 'green' : 'red'), padding: '2px' }),
        new Label(`${last_refid}`)
      ]);
    }
  });
};