// var PayrollEntryForm = function(payroll_data) {
//     var modal = new Modal('Employee Information');

//     var form   = new Form();
    
//     var search = new TextBox(null, 'text', 'search', 'Search here', 'Search id or name of the employee!');
//     var search_list_w = new Panel();
//     search_list_w.addClass('search_list_wrap');

//     var search_content = new Panel();
//     search_content.addClass('search_content');
//     search_list_w.add(search_content);
//     search_list_w.hide();

//     var search_item = new Panel();

//     var close = new Button(null, null, 'close');
//     close.addClass('search_close');
//     search_content.add(close);
//     search_content.add(search_item);
    
//     var emp_id = new TextBox('ID', 'text', null, null, 'Generated id');
//     emp_id.control.setAttribute('readonly', '');
    
//     var fullname = new TextBox('NAME', 'text', null);
//     fullname.control.setAttribute('readonly', '');
    
//     var salary = new TextBox('RATE', 'text', null);
//     salary.control.setAttribute('readonly', '');
    
//     var day_work = new TextBox("NO. WORK DAY", 'text', null);
//     var late = new TextBox('LATE(MIN)' , 'text', null, null);
//     var absent = new TextBox('ABSENT', 'text', null);
//     var gross = new TextBox('Gross', 'text', null, null);
//     var undertime = new TextBox('UNDERTIME(MIN)', 'text', null, null);
//     var loader = new Panel();
//     loader.control.innerHTML = '<span class="loader"></span>'
    
//     update_form = function() {
//         var data = x_storage.getItem("emp_selected");
        
//         var id     = data.id;
//         var lname  = data.lname;
//         var mname  = data.mname;
//         var fname  = data.fname;
//         var ename  = data.ename;
//         var gender = data.gender;
//         var dob    = data.dob;
        
//         var inputs = form.input;
//         inputs.emp_id.setValue(id);
//         inputs.fname.setValue((lname + ' ' + fname + ' ' + mname).toUpperCase());
//         // load other information
//         AppHttp('/employee/information', {
//             emp_id: id,
//             from: payroll_data.from,
//             to: payroll_data.to 
//         }, null, function(o) {
//             var res = JSON.parse(o);
//             if (res.ok != 1) return;
//             var data = res.data;

//             var dept_info = data.dept_info;
//             var pos_info  = data.pos_info;
//             var rate_info = data.rate_info;

//             var last_ded  = data.last_ded || [];
            
//             var rate      = 0.0;
//             var rate_type = null;

//             if (rate_info != null) {
//                 rate = rate_info.rate;
//                 rate_type = rate_info.rate_type;
//                 inputs.salary.setValue(parseFloat(rate) + ' ' + x_salary_type(rate_type));
//             }
            
//             // plot the right inputs
//             var rinput = g_form.right_form.input;
            
//             for (var i = 0; i < last_ded.length; i++) {
               
//                 for (var key in rinput) {
//                     var code = last_ded[i]["code"] + "___" + last_ded[i]["name"];
//                     code = code.toLowerCase();
//                     var last_value = last_ded[i]["value"];

//                     if (code == key) {
//                         rinput[key].setValue(last_value);
//                     }
//                 }
//             }

//             x_storage.setItem('f_info', data);
//             x_storage.setItem('last_ded', last_ded); // get the last deduction information
            
//             calculate_gross();
//         });
        
//     };

//     var search_xhr = function(v) {
//         search_item.add(loader);
//         AppHttp('/client/list', {search: v}, null, function(o) {
//             search_item.clear();
//             var res = JSON.parse(o);
//             if (res.ok != 1) return;
            
//             var data = res.data.data;
//             var data_len = data.length;
            
//             // draw table() {}
//             if (data_len < 1) return;

//             // table
//             var table = new Table(["Action", "name"]);

//             var i = 0;
//             do {
                
//                 var add = new Button('Add', 'success', 'plus-circle', 'please click to add it on the payroll item');
//                 add.control.setAttribute('rel', i);
//                 add.addEventListener('click', function() {
//                     var index = this.attributes.rel.nodeValue;
//                     var odata = data[index];
//                     x_storage.setItem('emp_selected', odata); // selected data 
//                     search_list_w.hide();
//                     update_form(); // update form and show the total deductions
//                 });

//                 table.add([
//                     add, 
//                     data[i].lname  + ' ' + data[i].fname + ' ' + data[i].mname
//                 ]); // add the content in the table
                
//                 search_item.add(table); // add the item panel
                
//                 i++;

//             } while(i < data_len);
//         });

//     };

//     var time_flag = null;
    
//     search.addEventListener('keyup', function() {
//         var v = this.value.trim();
//         search_list_w.show();
        
//         // if (xhr_flag != null) return;
//         search_item.clear();
        
//         if (time_flag != null) {
//             clearTimeout(time_flag);
//         }

//         time_flag = setTimeout(function() {
//             search_xhr(v);
//         }, 500);

//         if (v == '') {
//             search_list_w.hide();
//         }
//     });

//     close.addEventListener('click', function() {
//         search_list_w.hide();
//     });

//     calculate_gross = function() {
        
//         var info = x_storage.getItem('f_info');
//         var rate_info = info.rate_info;

//         var rate = parseFloat(rate_info.rate);
//         var rate_type = rate_info.rate_type;

//         var isnum = new RegExp('^[0-9]+([.][0-9]+)?$');
//         var _work = day_work.getValue();
//         var _late = late.getValue();
        
//         var total_work = 0.0;
//         var total_late = 0.0;

//         if (isnum.test(_work)) {
//             total_work = parseFloat(_work);
//         }

//         if (isnum.test(_late)) {
//             total_late = parseFloat(_late);
//         } else {
//             if (/^[0-9]+[\:][0-9]+$/.test(_late)) {
//                var time = _late.split(':');
//                var h = parseFloat(time[0]);
//                var m = parseFloat(time[1]);
               
//                // total late hour times 60 after add it to minute 
//                // to get the total minute
//                total_late = (h * 60) + m;                   
//                late.setValue(total_late); // auto update to total_late
//             }
//         }
        
//         var total_absent = 0.0;
//         if (isnum.test(absent.getValue())) {
//             total_absent = parseFloat(absent.getValue());
//         }
//         var total_undertime = 0.0;
//         if (isnum.test(undertime.getValue())) {
//             total_undertime = parseFloat(undertime.getValue());
//         } else {
//             if (/^[0-9]+[\:][0-9]+$/.test(undertime.getValue())) {
//                 var time1 = undertime.getValue().split(':');
//                 var h1 = parseFloat(time1[0]);
//                 var m1 = parseFloat(time1[1]);
                
//                 // total late hour times 60 after add it to minute 
//                 // to get the total minute
//                 total_undertime = (h1 * 60) + m1;                   
//                 undertime.setValue(total_undertime); // auto update to total_late
//              }
//         }
        
//         // get the value of the deduction

//         var ded_input = g_form.right_form.input;
        
//         var ded = JSON.parse(payroll_data["deduction_list"]);
//         var ded_len = ded.length;
        
//         var ded_data = [];

//         for ( var i = 0; i < ded_len; i++ ) {
            
//             var ded_stat = ded[i];
//             var n = ded_stat["code"].toLowerCase() + "___" + ded_stat["name"].toLowerCase();
//             var input = ded_input[n];
            
//             var v = 0.0;
//             if (isnum.test(input.getValue())) {
//                 v = parseFloat(input.getValue());
//             } else {
//                 input.setValue(0);
//             }

//             ded_data.push({
//                 code: ded_stat["code"],
//                 name: ded_stat["name"],
//                 value: v
//             });

//         }
//         // the deduction calculation is on the server
//         AppHttp("/payroll/pre/calculate", {
//             rate:          rate,
//             rate_type:     rate_type,
//             payroll_refid: payroll_data.refid,
//             work_day:      total_work,
//             late:          total_late,
//             undertime:     total_undertime,
//             total_absent:  total_absent,
//             ded_data:      ded_data
//         }, null, function(res) {
//             var d = JSON.parse(res);
//             if (!d.ok) return;
//             var data = d.data;
            
//             gross.setValue(data.gross_amount);
            
//             right_form.deduction_panel.control.innerHTML = "Total Deduction: " +
//                                                             '<span style="color: red; font-weight: bold;">'
//                                                                 + data.total_deduction + 
//                                                             "</span>";

//             right_form.net.control.innerHTML = "NetPay: " + '<span style="color: green; font-weight: bold;">' 
//                                                                 + data.net_amount + 
//                                                             "</span>";
//         });


//         return {
//             late: total_late,
//             absent: total_absent,
//             undertime: total_undertime,
//             ded_data: ded_data,
//             work: total_work
//         }
//     };
    
//     day_work.addEventListener('keyup', function() {
//         calculate_gross();
//     });

//     late.addEventListener('keyup', function(e) {
//         if (/:/.test(late.getValue())) {
//             if (e.keyCode == 13) {
//                 calculate_gross();        
//             }
//             return;
//         }
        
//         calculate_gross();
//     });

//     undertime.addEventListener('keyup', function(e) {
//         if (/:/.test(undertime.getValue())) {
//             if (e.keyCode == 13) {
//                 calculate_gross();        
//             }
//             return;
//         }
//         calculate_gross();
//     });

//     absent.addEventListener('keyup', function() {
//         calculate_gross();
//     });

//     form.add(search_list_w);
//     form.add(search, 'search');
//     form.add(emp_id, 'emp_id');
//     form.add(fullname, 'fname');
//     form.add(salary, 'salary');
//     form.add(day_work, 'day_work');
//     form.add(absent, 'absent');
//     form.add(undertime, 'ut');
//     form.add(late, 'late');
//     form.add(gross, 'gross');

//     var submit = new Button('Submit', 'success', null);
//     submit.control.style.marginTop = '5px';
//     form.add(submit);

//     submit.addEventListener('click', function() {
//         var comdata = calculate_gross();
//         var emp_data = x_storage.getItem('emp_selected');     
//         AppHttp('/payroll/add/item', { 
//             is_update: is_update,
//             emp_id: emp_data.id,
//             late: comdata.late,
//             work: comdata.work,
//             absent: comdata.absent,
//             undertime: comdata.undertime,
//             payroll_refid: payroll_data.refid,
//             deduction_value: comdata.ded_data
//         }, null, function(o) {
//             is_update = false;
//             var data = JSON.parse(o);
//             if (data.ok) {
//                 messageBox.show(data.msg, function() {
//                     reload_table();
//                 });
//             } else {
//                 alert(data.msg);
//             }
//         });
//     });
          
//     var left_panel = new Panel();
//     left_panel.control.style.width = "50%";
//     left_panel.control.style.float = "left";
//     left_panel.control.style.padding = "10px";
//     left_panel.add(form);
    
//     var right_panel = new Panel();
//     right_panel.control.style.width = "50%";
//     right_panel.control.style.float = "left";
//     right_panel.control.style.padding = "10px";

//     modal.add(left_panel);
//     modal.add(right_panel);

//     modal.control.style.minHeight = "920px";
//     //modal.control.style.minHeight = right_panel.control.offsetHeight + 'px';
//     // setTimeout(function() {
//     //     console.dir(right_panel.control);
//     // }, 500);
    

//     return {
//         modal: modal,
//         right_panel: right_panel,
//         left_form: form
//     };
// };


// var payroll_create_deduction_form = function(payroll_data) {

//     var form = new Form();

//     var ded = JSON.parse(payroll_data["deduction_list"]);
//     var ded_len = ded.length;
    
//     for (var i = 0; i < ded_len; i++) {
//         var data = ded[i];
//         var name = data["code"].toLowerCase() + "___" + data["name"].toLowerCase();
        
//         var tf = new TextBox(data["code"] + "->" + data["name"], "text");
//         tf.addEventListener("change", function() {
//             calculate_gross();
//         });
//         form.add(tf, name);
//     }
    
//     var total_ded = new Panel();
//     total_ded.control.style.width = "100%";
//     total_ded.control.style.height = "30px";
//     total_ded.control.style.padding = "5px";
//     total_ded.control.style.border = "1px solid #ddd";
//     total_ded.control.style.marginTop = "20px";
//     total_ded.control.innerHTML = "Total Deduction: ";

//     var net = new Panel();
//     net.control.style.width = "100%";
//     net.control.style.height = "30px";
//     net.control.style.padding = "5px";
//     net.control.style.border = "1px solid #ddd";
//     net.control.style.marginTop = "20px";
//     net.control.innerHTML = "NetPay: ";

//     form.add(total_ded);
//     form.add(net);
    
//     return { 
//         form: form,
//         deduction_panel: total_ded,
//         net: net
//     };
// };