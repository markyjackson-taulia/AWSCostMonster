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
var projected_costs = [1012,2071,3200,4336,5493];

//months = ["January 1 2018","Febuary 1 2018","March 1 2018","April 1 2018","May 1 2018","June 1 2018","July 1 2018","August 1 2018","September 1 2018","October 1 2018","November 1 2018","December 1 2018"];

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
        label: "Total by Month",
        borderColor: "#d9f441",
        fill: true
      },
      {
        data: projected_costs,
        label: "Projected Totals by Month",
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
    data = $( "#budgetForm" ).serialize();
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
