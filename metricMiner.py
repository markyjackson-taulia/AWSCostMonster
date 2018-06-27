import boto3
import datetime
import calendar
from dateutil.relativedelta import relativedelta
import collections
import time
import sqlite3
from sqlite3 import Error

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

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None

def select_all_tasks(conn, table):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + table)

    rows = cur.fetchall()
    return rows

def select_by_id(conn, id, table):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM "+table+" WHERE ID=?", (id,))

        rows = cur.fetchall()
        return rows
    except Exception as e:
        return e

def main():
    while True:
        database = "pythonsqlite.db"
        conn = create_connection(database)
        with conn:

            cost_dict, total_left_for_month, total_cost, first_date, time_frame_this_month, average_by_day = generate_month_cost_report()

            number_of_months = 4
            number_of_months = str(number_of_months).strip()
            number_of_months = int(number_of_months)

            dates_dict, months_dict, last_month_total = generate_monthly_cost_report(number_of_months)

            #Totals by the current number of months
            months_totals = []
            for item in months_dict:
                month_total = months_dict[item]["total"]
                months_totals.append(round(month_total,2))

            #cost by service
            number_of_months = 1
            new_cost_dict = []
            for cost in cost_dict:
                new_cost_dict.append((cost, round(cost_dict[cost]["UnblendedCost"], 2)))

            #total of all months
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

            cost_predictions_dict = {}
            cost_predictions_dict["Predicted Remaining Monthly Cost"] = round(total_left_for_month,2)
            cost_predictions_dict["Average Cost by Day"] = round(average_by_day,2)
            cost_predictions_dict["Current Total Cost"] = round(total_cost,2)
            cost_predictions_dict["Predicted Total Cost"] = round(total_cost, 2) + round(total_left_for_month,2)
            cost_predictions_dict["Cummulative Months Total"] =  months_total
            cost_predictions_dict["Totals by Month"] =  months_totals
            cost_predictions_dict["Cost By Service"] =  new_cost_dict
            cost_predictions_dict["Months"] =  generate_months(4)
            cost_predictions_dict["Number of Months"] =  4

            cur = conn.cursor()
            try:
                #print ("""CREATE TABLE costs(ID INT, predicted_remaining_montly_cost REAL, average_cost_by_day REAL, current_total_cost REAL, predicted_total_cost REAL, number_of_months INT, name TEXT)""")
                cur.execute("""CREATE TABLE costs(ID INT, predicted_remaining_montly_cost REAL, average_cost_by_day REAL, current_total_cost REAL, predicted_total_cost REAL, number_of_months INT, name TEXT)""")
            except:
                print ""

            try:
                #print ("""CREATE TABLE culmulative_montly_totals(ID INT, total REAL, month INT, name TEXT)""")
                cur.execute("""CREATE TABLE culmulative_montly_totals(ID INT, total REAL, month INT, name TEXT)""")
            except:
                print ""

            try:
                #print ("""CREATE TABLE culmulative_montly_totals(ID INT, total REAL, month INT, name TEXT)""")
                cur.execute("""CREATE TABLE cost_by_service(ID INT, total REAL, name TEXT)""")
            except:
                print ""

            try:
                #print ("""CREATE TABLE montly_totals(ID INT, total REAL, month INT, name TEXT)""")
                cur.execute("""CREATE TABLE montly_totals(ID INT, total REAL, month INT, name TEXT)""")
            except:
                print ""

            try:
                #print("""CREATE TABLE months(ID INT, month TEXT, name TEXT)""")
                cur.execute("""CREATE TABLE months(ID INT, month TEXT, name TEXT)""")
            except:
                print ""

            try:
                does_entry_exist = select_by_id(conn, "1", "costs")
                if not does_entry_exist:
                    insert_statement = "INSERT INTO costs VALUES( 1, " + \
                                                                     str(round(total_left_for_month,2)) + \
                                                                     ", " + str(round(average_by_day,2)) + \
                                                                     ", " + str(round(total_cost,2)) + \
                                                                     ", " + str(round(total_cost, 2) + round(total_left_for_month,2)) + \
                                                                     ", " + str(number_of_months) + \
                                                                     ", '" + "cost" + "')"
                    print insert_statement
                    cur.execute(insert_statement)
                    conn.commit()
                else:
                    update_statement = "UPDATE costs SET predicted_remaining_montly_cost = "+str(round(total_left_for_month,2)) + \
                                       ", average_cost_by_day = "+ str(round(average_by_day,2)) + \
                                       ", current_total_cost = " + str(round(total_cost,2)) + \
                                       ", predicted_total_cost = " + str((round(total_cost, 2) + round(total_left_for_month,2))) + \
                                       ", number_of_months = " + str(number_of_months) + \
                                       ", name = 'cost'" + \
                                       " WHERE id=1;"
                    print update_statement
                    cur.execute(update_statement)
                    conn.commit()
            except Exception as e:
                print e

            try:
                index = 0
                for name, month_t in new_cost_dict:
                    does_entry_exist = select_by_id(conn, index, "cost_by_service")
                    if not does_entry_exist:
                        insert_statement = "INSERT INTO cost_by_service VALUES(" + str(index) + "," + str(month_t) + ", '" + str(name) + "')"
                        index = index + 1
                        print insert_statement
                        cur.execute(insert_statement)
                        conn.commit()
                    else:
                        update_statement = "UPDATE cost_by_service SET total = "+str(month_t)+" WHERE name='"+str(name)+"';"
                        index = index + 1
                        print update_statement
                        cur.execute(update_statement)
                        conn.commit()
            except Exception as e:
                print e


            try:
                for index, month_t in enumerate(months_total):
                    mon_list = generate_months(4)

                    month = mon_list[index]
                    month_id = month.split("-")[1]
                    if "0" in month_id and month_id != "10":
                        month_id = month_id.replace("0", "")

                    does_entry_exist = select_by_id(conn, month_id, "culmulative_montly_totals")
                    if not does_entry_exist:
                        insert_statement = "INSERT INTO culmulative_montly_totals VALUES(" + str(month_id) + "," + str(month_t) + ",'" + str(month) + "', '" + "cost" + "')"
                        print insert_statement
                        cur.execute(insert_statement)
                        conn.commit()
                    else:
                        update_statement = "UPDATE culmulative_montly_totals SET total = "+str(month_t)+" WHERE id="+str(month_id)+";"
                        print update_statement
                        cur.execute(update_statement)
                        conn.commit()
            except Exception as e:
                print e

            try:
                for index, month_tt in enumerate(months_totals):
                    mon_list = generate_months(4)

                    month = mon_list[index]
                    month_id = month.split("-")[1]
                    if "0" in month_id and month_id != "10":
                        month_id = month_id.replace("0", "")

                    does_entry_exist = select_by_id(conn, month_id, "montly_totals")
                    if not does_entry_exist:
                        insert_statement = "INSERT INTO montly_totals VALUES(" + str(month_id) + "," + str(month_tt) + ", '" + str(month) + "', '" + "cost" + "')"
                        print insert_statement
                        cur.execute(insert_statement)
                        conn.commit()
                    else:
                        update_statement = "UPDATE montly_totals SET total = "+str(month_tt)+" WHERE id="+str(month_id)+";"
                        print update_statement
                        cur.execute(update_statement)
                        conn.commit()
            except Exception as e:
                print e

            try:
                for index, month_ss in enumerate(generate_months(4)):
                    mon_list = generate_months(4)

                    month = mon_list[index]
                    month_id = month.split("-")[1]
                    if "0" in month_id and month_id != "10":
                        month_id = month_id.replace("0", "")

                    does_entry_exist = select_by_id(conn, month_id, "months")
                    if not does_entry_exist:
                        insert_statement = "INSERT INTO months VALUES(" + str(month_id) + ",'" + str(month_ss) + "', '" + "cost" + "')"
                        print insert_statement
                        cur.execute(insert_statement)
                        conn.commit()
                    else:
                        update_statement = "UPDATE months SET month = '"+str(month_ss)+"' WHERE id="+str(month_id)+";"
                        print update_statement
                        cur.execute(update_statement)
                        conn.commit()
            except Exception as e:
                print e

            try:
                if "0" in first_date and first_date != "10":
                    month_id = first_date.split("-")[1].replace("0","")
                else:
                    month_id = first_date.split("-")[1]

                all_current_totals = select_all_tasks(conn, "culmulative_montly_totals")
                does_entry_exist = select_by_id(conn, month_id, "culmulative_montly_totals")
                if not does_entry_exist:
                    max_total = 0.00
                    for total in all_current_totals:
                        total = total[1]
                    max_total = float(total)

                    final_culm_total = max_total + (round(total_cost, 2) + round(total_left_for_month,2))
                    insert_statement = "INSERT INTO culmulative_montly_totals VALUES(" + str(month_id) + "," + str(final_culm_total) + ", '" + str(first_date) + "', '" + "cost" + "')"
                    print insert_statement
                    cur.execute(insert_statement)
                    conn.commit()
                else:
                    max_total = 0.00
                    for total_c in all_current_totals:
                        if str(total_c[0]) != str(month_id):
                            total = total_c[1]
                    max_total = float(total)
                    final_culm_total = max_total + (round(total_cost, 2) + round(total_left_for_month,2))
                    update_statement = "UPDATE culmulative_montly_totals SET total = "+ str(final_culm_total)+" WHERE id="+str(month_id)+";"
                    print update_statement
                    cur.execute(update_statement)
                    conn.commit()
            except Exception as e:
                print e

            try:
                if "0" in first_date and first_date != "10":
                    month_id = first_date.split("-")[1].replace("0","")
                else:
                    month_id = first_date.split("-")[1]

                does_entry_exist = select_by_id(conn, month_id, "montly_totals")
                if not does_entry_exist:
                    insert_statement = "INSERT INTO montly_totals VALUES(" + str(month_id) + "," +  str((round(total_cost, 2) + round(total_left_for_month,2))) + ", '" + str(first_date) + "', '" + "cost" + "')"
                    print insert_statement
                    cur.execute(insert_statement)
                    conn.commit()
                else:
                    update_statement = "UPDATE montly_totals SET total = "+ str((round(total_cost, 2) + round(total_left_for_month,2)))+" WHERE id="+str(month_id)+";"
                    print update_statement
                    cur.execute(update_statement)
                    conn.commit()
            except Exception as e:
                print e

            try:
                if "0" in first_date and first_date != "10":
                    month_id = first_date.split("-")[1].replace("0","")
                else:
                    month_id = first_date.split("-")[1]

                does_entry_exist = select_by_id(conn, month_id, "months")
                if not does_entry_exist:
                    insert_statement = "INSERT INTO months VALUES(" + str(month_id) + ",'" + str(first_date) + "', '" + "cost" + "')"
                    print insert_statement
                    cur.execute(insert_statement)
                    conn.commit()
                else:
                    update_statement = "UPDATE months SET month = '"+str(first_date)+"' WHERE id="+str(month_id)+";"
                    print update_statement
                    cur.execute(update_statement)
                    conn.commit()
            except Exception as e:
                print e

            print cost_predictions_dict
        conn.close()
        time.sleep(7200)

if __name__ == '__main__':
    main()