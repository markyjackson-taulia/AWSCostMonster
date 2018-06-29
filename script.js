function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false );
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

var month_costs = httpGet("http://127.0.0.1:5000/api/getmonthtotalcost");
var months_cost = JSON.parse(month_costs);
var totals_by_month_costs = httpGet("http://127.0.0.1:5000/api/totalsbymonth");
var months = httpGet("http://127.0.0.1:5000/api/months");
var months = JSON.parse(months);
var length_months = months.length;
var totals_by_month_cost = JSON.parse(totals_by_month_costs);

var getbudget = httpGet("http://127.0.0.1:5000/api/getbudgets");
var getbudgetobj = JSON.parse(getbudget);

var jan = "";
var feb = "";
var mar = "";
var apr = "";
var may = "";
var june = "";
var july = "";
var aug = "";
var sept = "";
var oct = "";
var nov = "";
var dec = "";
var yearly = "";

var buget_months_list = [];

for (var i in getbudgetobj) {
    var buget_insert_months = [];
    var id = getbudgetobj[i][0].toString();
    var year = id.substring(0, 4);
    var id_length = id.length;
    var year = id.substring(0, 4);
    var month = id.substring(4, id_length);
    var buget_month = "";
    var budget = getbudgetobj[i][2].toString();

    if ( month.length < 2 && month != "0"){
        buget_month = year + "-" + "0" + month + "-01";
        buget_insert_months.push(buget_month);
        buget_insert_months.push(budget);
        buget_months_list.push(buget_insert_months);
    }else{
        if ( month != "0"){
            buget_month = year + "-" + month + "-01";
            buget_insert_months.push(buget_month);
            buget_insert_months.push(budget);
            buget_months_list.push(buget_insert_months);
        }
    }

    if ( month == "1" ){
        jan = budget;
        $("#janbudget").val(jan);
    }
    if ( month == "2" ){
        feb = budget;
        $("#febbudget").val(feb);
    }
    if ( month == "3" ){
        mar = budget;
        $("#marbudget").val(mar);
    }
    if ( month == "4" ){
        apr = budget;
        $("#aprbudget").val(apr);
    }
    if ( month == "5" ){
        may = budget;
        $("#maybudget").val(may);
    }
    if ( month == "6" ){
        june = budget;
        $("#junebudget").val(june);
    }
    if ( month == "7" ){
        july = budget;
        $("#julybudget").val(july);
    }
    if ( month == "8" ){
        aug = budget;
        $("#augbudget").val(aug);
    }
    if ( month == "9" ){
        sept = budget;
        $("#septbudget").val(sept);
    }
    if ( month == "10" ){
        oct = budget;
        $("#octbudget").val(oct);
    }
    if ( month == "11" ){
        nov = budget;
        $("#novbudget").val(nov);
    }
    if ( month == "12" ){
        dec = budget;
        $("#decbudget").val(dec);
    }
    if ( month == "0" ){
        yearly = budget;
        $("#yearlybudget").val(yearly);

    }
}

var balance_data_len = Math.abs(buget_months_list.length - months.length + 1);
var new_length_of_budget_months = Math.abs(months.length - balance_data_len);
var months = months.slice(0, new_length_of_budget_months);
var projected_costs = [];
var budget_chart_object = {};

for (var i in buget_months_list) {
    var month = buget_months_list[i][0];
    var budget = buget_months_list[i][1];
    budget_chart_object[month] = {"budget":budget};
}
var cumulative_list = [];
for (var i in months) {
    if ( !(months[i] in budget_chart_object) ){
        budget_chart_object[months[i]] = {};
        budget_chart_object[months[i]] = {"budget":"0"};
        projected_costs.push("0");
        cumulative_list.push(0.00);
    }
}
console.log(cumulative_list);

var cumulative_total = 0.00;
var current_index = 0;
for (var i in buget_months_list) {
    var month = buget_months_list[i][0];
    var budget = buget_months_list[i][1];
    projected_costs.push(budget);

    if (current_index == 0){
        cumulative_total = parseFloat(budget);
        console.log(cumulative_total);
        cumulative_list.push(cumulative_total);
        current_index = 1;
        continue
    }
    if (current_index > 0){
        cumulative_total = parseFloat(cumulative_total) + parseFloat(budget);
        console.log(cumulative_total);
        cumulative_list.push(cumulative_total);
        current_index = current_index + 1;
        continue
    }
}

var ctx = document.getElementById("chartjs-intro-myChart");
var myChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: months,
    datasets: [
      { 
        data: months_cost,
        label: "Actual Monthly Cost",
        borderColor: "#3e95cd",
        fill: true
      },
      {
        data: totals_by_month_cost,
        label: "Cumulative Total by Month",
        borderColor: "#d9f441",
        fill: true
      },
      {
        data: projected_costs,
        label: "Budget by Month",
        borderColor: "#03a84a",
        fill: true
      },
      {
        data: cumulative_list,
        label: "Cumulative Projected Budget",
        borderColor: "#f44242",
        fill: true
      }
    ]
  }
});

var ctx = document.getElementById("chartjs-intro-donought");
var cost_by_service = httpGet("http://127.0.0.1:5000/api/getcostby_service");
var cost_by_service_list = JSON.parse(cost_by_service);

var service_names = [];
var service_costs = [];

for (var i in cost_by_service_list) {
  var service_name = cost_by_service_list[i][0];
  var service_cost = cost_by_service_list[i][1];
  service_names.push(service_name);
  service_costs.push(service_cost);
}

var myDoughnutChart = new Chart(ctx, {
    type: 'doughnut',
      data: {
        labels: service_names,
        datasets: [
          {
            data: service_costs,
            label: "Cost By Service",
            borderColor: "#3e95cd",
            backgroundColor: [
                "#FF6384",
                "#d9f441",
                "#3e95cd",
                "#8463FF",
                "#6384FF",
                "#f44242",
                "#3e95cd",
                "#d9f441",
                "#63FF84",
                "#1a8e0b",
                "#072784",
                "#02b59a",
                "#2a03b5",
                "#02b59a",
                "#67b502",
                "#b75d03",
                "#2a03b5"
            ],
            fill: true
          }
        ]
      }
});



var ctx = document.getElementById("chartjs-intro-bar");
var cost_by_service = httpGet("http://127.0.0.1:5000/api/costpredictions");
var cost_by_service_object = JSON.parse(cost_by_service);
var labels = [];
var costs = [];

for (var i in cost_by_service_object) {
  labels.push(i);
  costs.push(cost_by_service_object[i]);
}

var myBarChart = new Chart(ctx, {
    type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            data: costs,
            label: "Cost Predictions",
            borderColor: "#3e95cd",
            backgroundColor: [
                "#FF6384",
                "#d9f441",
                "#3e95cd",
                "#8463FF",
                "#6384FF",
                "#f44242",
                "#3e95cd",
                "#d9f441",
                "#63FF84",
                "#1a8e0b",
                "#072784",
                "#2a03b5",
                "#2a03b5",
                "#02b59a",
                "#67b502",
                "#b75d03",
                "#02b59a"
            ],
            fill: true
          }
        ]
      }
});

function postBudget(){
    jan = $("#janbudget").val();
    feb = $("#febbudget").val();
    mar = $("#marbudget").val();
    apr = $("#aprbudget").val();
    may = $("#maybudget").val();
    june = $("#junebudget").val();
    july = $("#julybudget").val();
    aug = $("#augbudget").val();
    sept = $("#septbudget").val();
    oct = $("#octbudget").val();
    nov = $("#novbudget").val();
    dec = $("#decbudget").val();
    yearly = $("#yearlybudget").val();

    post_data = {
        "jan": jan,
        "feb": feb,
        "mar": mar,
        "apr": apr,
        "may": may,
        "june": june,
        "july": july,
        "aug": aug,
        "sept": sept,
        "oct": oct,
        "nov": nov,
        "dec": dec,
        "yearly": yearly,
    }
    console.log(post_data);
    $.post( "http://127.0.0.1:5000/api/savebudget", post_data, function( data ) {
      //$( ".result" ).html( data );
      console.log(data);
    });
}
