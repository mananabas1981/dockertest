export var x_human_date_time = function (server_date_time) {
    // convert the server time  to human date
    var s = server_date_time.split(" ");
    console.log(s);

    return server_date_time;
};

export var x_human_date = function (server_date) {
    var s = server_date.split("-");

    return s[1] + '/' + s[2] + '/' + s[0]; // mm/dd/yyyy
};


export var x_emp_status = function (key) {
    return {
        "j": "Job Order",
        'c': 'Contract Of Service',
        'r': 'Regular...'
    }[key];
};

export var x_salary_type = function (key) {
    return {
        'd': 'Per Day',
        'm': 'Per Month',
        'y': 'Per Year'
    }[key];
};