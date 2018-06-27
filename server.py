from flask import Flask,jsonify
from flask_cors import cross_origin, CORS
import boto3
import datetime
import calendar
from dateutil.relativedelta import relativedelta
import collections

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

def get_aws_data(first_date, current_date):
    client = boto3.client('ce')
    Dimensions = client.get_dimension_values(
        TimePeriod={
            'Start': first_date,
            'End': current_date
        },
        Dimension='SERVICE',
        Context='COST_AND_USAGE'
    )
    cost_dict = {}
    for dimension in Dimensions["DimensionValues"]:
        dimension_to_search = str(dimension["Value"])
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': first_date,
                'End': current_date
            },
            Granularity='MONTHLY',
            Filter={"Dimensions": {
                    "Key": "SERVICE",
                    "Values": [
                        dimension_to_search
                    ]
            }},
            Metrics=[
                'BlendedCost',
                'UnblendedCost',
                'UsageQuantity',
            ],
            GroupBy=[
                {
                    "Type": "DIMENSION",
                    "Key": "SERVICE"
                },
            ]
        )
        for result in response["ResultsByTime"]:
            for cost in result["Groups"]:
                if cost["Metrics"]["BlendedCost"]["Amount"] > 0 or cost["Metrics"]["UnblendedCost"]["Amount"] > 0:
                    if cost_dict.has_key(cost["Keys"][0]):
                        cost_dict[cost["Keys"][0]]["BlendedCost"] = float(cost["Metrics"]["BlendedCost"]["Amount"]) + float(cost_dict[cost["Keys"][0]]["BlendedCost"])
                        cost_dict[cost["Keys"][0]]["UnblendedCost"] = float(cost["Metrics"]["UnblendedCost"]["Amount"]) + float(cost_dict[cost["Keys"][0]]["UnblendedCost"])
                        cost_dict[cost["Keys"][0]]["Usage"] = float(cost["Metrics"]["UsageQuantity"]["Amount"]) + float(cost_dict[cost["Keys"][0]]["Usage"])
                    else:
                        cost_dict[cost["Keys"][0]] = {}
                        cost_dict[cost["Keys"][0]]["BlendedCost"] = {}
                        cost_dict[cost["Keys"][0]]["UnblendedCost"] = {}
                        cost_dict[cost["Keys"][0]]["Usage"] = {}
                        cost_dict[cost["Keys"][0]]["BlendedCost"] = float(cost["Metrics"]["BlendedCost"]["Amount"])
                        cost_dict[cost["Keys"][0]]["UnblendedCost"] = float(cost["Metrics"]["UnblendedCost"]["Amount"])
                        cost_dict[cost["Keys"][0]]["Usage"] = float(cost["Metrics"]["UsageQuantity"]["Amount"])
    return cost_dict

def generate_months(months):
    dates_dict = collections.OrderedDict()
    starting_and_end_days = []
    months = int(months)
    for month_count in range(months,0,-1):
        six_months = datetime.datetime.today() + relativedelta(months=-month_count)
        last_day_of_month = calendar.monthrange(six_months.year, six_months.month)[1]
        six_month = six_months.month
        if six_month != 10 and six_month != 11 and six_month != 12:
            six_month = "0" + str(six_month)
        sixth_months_first = str(six_months.year) + "-" + str(six_month) + "-" + "01"
        sixth_months_last = str(six_months.year) + "-" + str(six_month) + "-" + str(last_day_of_month)
        starting_and_end_days.append((sixth_months_first, sixth_months_last))
    months_dict = collections.OrderedDict()
    last_month_total = 0
    months_list = []
    for first_day, last_day in starting_and_end_days:
        old_month = int(last_day.split("-")[1]) - 1
        if len(str(old_month)) < 2:
            old_month = "0" + str(old_month)
        one_month_forward = int(last_day.split("-")[1]) + 1
        if len(str(one_month_forward)) < 2:
            one_month_forward = "0" + str(one_month_forward)
        year = last_day.split("-")[0]
        if str(one_month_forward) == "01":
            year = int(year) + 1
            year = str(year)
        last_day = year + "-" + one_month_forward + "-01"
        cost_dict = get_aws_data(first_day, last_day)
        total_cost = 0.0
        time_frame = str(first_day) + ":" + str(last_day)
        months_list.append(first_day)
    return months_list

def generate_monthly_cost_report(months):
    dates_dict = collections.OrderedDict()
    starting_and_end_days = []
    months = int(months)
    for month_count in range(months,0,-1):
        six_months = datetime.datetime.today() + relativedelta(months=-month_count)
        last_day_of_month = calendar.monthrange(six_months.year, six_months.month)[1]
        six_month = six_months.month
        if six_month != 10 and six_month != 11 and six_month != 12:
            six_month = "0" + str(six_month)
        sixth_months_first = str(six_months.year) + "-" + str(six_month) + "-" + "01"
        sixth_months_last = str(six_months.year) + "-" + str(six_month) + "-" + str(last_day_of_month)
        starting_and_end_days.append((sixth_months_first, sixth_months_last))
    months_dict = collections.OrderedDict()
    last_month_total = 0
    for first_day, last_day in starting_and_end_days:
        old_month = int(last_day.split("-")[1]) - 1
        if len(str(old_month)) < 2:
            old_month = "0" + str(old_month)
        one_month_forward = int(last_day.split("-")[1]) + 1
        if len(str(one_month_forward)) < 2:
            one_month_forward = "0" + str(one_month_forward)
        year = last_day.split("-")[0]
        if str(one_month_forward) == "01":
            year = int(year) + 1
            year = str(year)
        last_day = year + "-" + one_month_forward + "-01"
        cost_dict = get_aws_data(first_day, last_day)
        total_cost = 0.0
        time_frame = str(first_day) + ":" + str(last_day)
        if time_frame not in months_dict.keys():
            months_dict[time_frame] = {}
        for cost in cost_dict:
            if cost_dict[cost]["UnblendedCost"] >= 0.1:
                total_cost = cost_dict[cost]["UnblendedCost"] + total_cost
                last_month_total = total_cost
        dates_dict[first_day] = total_cost
        days = int(str(last_day).split("-")[2]) - int(str(first_day).split("-")[2]) + 1
        average_by_day = total_cost / float(days)
        months_dict[time_frame]["cost"] = {}
        months_dict[time_frame]["cost"] = cost_dict
        months_dict[time_frame]["total"] = {}
        months_dict[time_frame]["total"] = total_cost
        months_dict[time_frame]["average"] = {}
        months_dict[time_frame]["average"] = str(average_by_day)
    return dates_dict, months_dict, round(last_month_total, 2)

def generate_month_cost_report():
    todays_date = datetime.datetime.now()
    day = todays_date.day
    year = todays_date.year
    month = todays_date.month
    first_day = "01"
    if month != "10" and month != "11" and month != "12":
        first_date = str(year) + "-0" + str(month) + "-" + str(first_day)
        if len(str(day)) < 2:
            day = "0" + str(day)
        current_date = str(year) + "-0" + str(month) + "-" + str(day)
    else:
        first_date = str(year) + "-" + str(month) + "-" + str(first_day)
        if len(str(day)) < 2:
            day = "0" + str(day)
        current_date = str(year) + "-" + str(month) + "-" + str(day)
    cost_dict = get_aws_data(first_date, current_date)
    time_frame = str(first_date) + ":" + str(current_date)
    total_cost = 0.0
    for cost in cost_dict:
        if cost_dict[cost]["UnblendedCost"] >= 0.1:
            total_cost = cost_dict[cost]["UnblendedCost"] + total_cost
    average_by_day = total_cost / float(day)
    last_day_of_month = calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]
    number_of_days_left_in_month = last_day_of_month - datetime.datetime.now().day
    total_left_for_month = average_by_day * number_of_days_left_in_month
    return cost_dict, total_left_for_month, total_cost, first_date, time_frame, average_by_day

@app.route('/api/getmonthtotalcost/<months>')
@cross_origin()
def getmonthtotalcost(months):
    number_of_months = months
    number_of_months = str(number_of_months).strip()
    number_of_months = int(number_of_months)
    dates_dict, months_dict, last_month_total = generate_monthly_cost_report(number_of_months)
    months_total = []
    for item in months_dict:
        month_total = months_dict[item]["total"]
        months_total.append(round(month_total,2))
    return jsonify(months_total)

@app.route('/api/getcostby_service')
@cross_origin()
def generatecost():
    number_of_months = 1
    cost_dict, total_left_for_month, total_cost, first_date, time_frame_this_month, average_by_day = generate_month_cost_report()
    new_cost_dict = []
    for cost in cost_dict:
        new_cost_dict.append((cost, round(cost_dict[cost]["UnblendedCost"], 2)))
    return jsonify(new_cost_dict)

@app.route('/api/totalsbymonth/<months>')
@cross_origin()
def totalsbymonth(months):
    number_of_months = months
    number_of_months = str(number_of_months).strip()
    number_of_months = int(number_of_months)
    dates_dict, months_dict, last_month_total = generate_monthly_cost_report(number_of_months)
    months_total = []
    count = -1
    for item in months_dict:
        month_total = months_dict[item]["total"]
        if count != -1:
            last_month_total = months_total[count]
            current_total = round(month_total,2) + last_month_total
            months_total.append(round(current_total,2))
            count += 1
        else:
            months_total.append(round(month_total,2))
            count += 1
    return jsonify(months_total)

@app.route('/api/costpredictions/<months>')
@cross_origin()
def costpredictions(months):
    number_of_months = months
    cost_predictions_dict = {}
    cost_dict, total_left_for_month, total_cost, first_date, time_frame_this_month, average_by_day = generate_month_cost_report()
    cost_predictions_dict["Predicted Remaining Monthly Cost"] = round(total_left_for_month,2)
    cost_predictions_dict["Average Cost by Day"] = round(average_by_day,2)
    cost_predictions_dict["Current Total Cost"] = round(total_cost,2)
    cost_predictions_dict["Predicted Total Cost"] = round(total_cost, 2) + round(total_left_for_month,2)
    return jsonify(cost_predictions_dict)

@app.route('/api/months/<months>')
@cross_origin()
def getMonths(months):
    number_of_months = months
    months = generate_months(number_of_months)
    return jsonify(months)

if __name__ == '__main__':
    app.run()