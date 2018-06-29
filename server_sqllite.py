from flask import Flask, jsonify, request
from flask_cors import cross_origin, CORS
import sqlite3
from sqlite3 import Error
import json
import datetime
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


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

def save_or_update_budget(month, budget, id, conn, cur):
    try:
        does_entry_exist = select_by_id(conn, id, "budget")
        if not does_entry_exist:
            insert_statement = "INSERT INTO budget VALUES(" + str(id) + ", '" + str(month) + "', " + str(budget) + ", 'cost');"
            print insert_statement
            cur.execute(insert_statement)
            conn.commit()
        else:
            update_statement = "UPDATE budget SET month = " + str(month) + ", budget = " + str(budget) + ", name = 'cost' WHERE id=" + id +";"
            print update_statement
            cur.execute(update_statement)
            conn.commit()
    except Exception as e:
        print e

@app.route('/api/getmonthtotalcost')
@cross_origin()
def getmonthtotalcost():
    database = "pythonsqlite.db"
    conn = create_connection(database)
    monthly_totals = select_all_tasks(conn, "montly_totals")
    montly_tt_list = []
    for total in monthly_totals:
        montly_tt_list.append(total[1])
    conn.close()
    return jsonify(montly_tt_list)

@app.route('/api/getcostby_service')
@cross_origin()
def generatecost():
    database = "pythonsqlite.db"
    conn = create_connection(database)
    service_totals = select_all_tasks(conn, "cost_by_service")
    cost_by_service = []
    for id,cost,name in service_totals:
        cost_by_service.append((name,cost))
    conn.close()
    return jsonify(cost_by_service)

@app.route('/api/totalsbymonth')
@cross_origin()
def totalsbymonth():
    database = "pythonsqlite.db"
    conn = create_connection(database)
    monthly_totals = select_all_tasks(conn, "culmulative_montly_totals")
    montly_tt_list = []
    for total in monthly_totals:
        montly_tt_list.append(total[1])
    conn.close()
    return jsonify(montly_tt_list)

@app.route('/api/costpredictions')
@cross_origin()
def costpredictions():
    database = "pythonsqlite.db"
    conn = create_connection(database)
    costs = select_all_tasks(conn, "costs")
    cost_predictions_dict = {}

    for total in costs:
        cost_predictions_dict["Predicted Remaining Monthly Cost"] = total[1]
        cost_predictions_dict["Average Cost by Day"] = total[2]
        cost_predictions_dict["Current Total Cost"] = total[3]
        cost_predictions_dict["Predicted Total Cost"] = total[4]

    conn.close()
    return jsonify(cost_predictions_dict)

@app.route('/api/months')
@cross_origin()
def getMonths():
    database = "pythonsqlite.db"
    conn = create_connection(database)
    months_db = select_all_tasks(conn, "months")
    months = []
    for month in months_db:
        print month
        months.append(month[1])
    conn.close()
    return jsonify(months)

@app.route('/api/savebudget', methods=['POST'])
@cross_origin()
def saveBudget():
    database = "pythonsqlite.db"
    conn = create_connection(database)
    cur = conn.cursor()

    year = str(datetime.datetime.now().year)

    jan = request.form.get('jan')
    jan_month = year + "-01-01"
    jan_id = year + "1"
    save_or_update_budget(jan_month, jan, jan_id, conn, cur)

    feb = request.form.get('feb')
    feb_month = year + "-02-01"
    feb_id = year + "2"
    save_or_update_budget(feb_month, feb, feb_id, conn, cur)

    mar = request.form.get('mar')
    mar_month = year + "-03-01"
    mar_id = year + "3"
    save_or_update_budget(mar_month, mar, mar_id, conn, cur)

    apr = request.form.get('apr')
    apr_month = year + "-04-01"
    apr_id = year + "4"
    save_or_update_budget(apr_month, apr, apr_id, conn, cur)

    may = request.form.get('may')
    may_month = year + "-05-01"
    may_id = year + "5"
    save_or_update_budget(may_month, may, may_id, conn, cur)

    june = request.form.get('june')
    june_month = year + "-06-01"
    june_id = year + "6"
    save_or_update_budget(june_month, june, june_id, conn, cur)

    july = request.form.get('july')
    july_month = year + "-07-01"
    july_id = year + "7"
    save_or_update_budget(july_month, july, july_id, conn, cur)

    aug = request.form.get('aug')
    aug_month = year + "-08-01"
    aug_id = year + "8"
    save_or_update_budget(aug_month, aug, aug_id, conn, cur)

    sept = request.form.get('sept')
    sept_month = year + "-9-01"
    sept_id = year + "9"
    save_or_update_budget(sept_month, sept, sept_id, conn, cur)

    oct = request.form.get('oct')
    oct_month = year + "-10-01"
    oct_id = year + "10"
    save_or_update_budget(oct_month, oct, oct_id, conn, cur)

    nov = request.form.get('nov')
    nov_month = year + "-11-01"
    nov_id = year + "11"
    save_or_update_budget(nov_month, nov, nov_id, conn, cur)

    dec = request.form.get('dec')
    dec_month = year + "-12-01"
    dec_id = year + "12"
    save_or_update_budget(dec_month, dec, dec_id, conn, cur)

    yearly = request.form.get('yearly')
    yearly_month = "0"
    yearly_id = year + "0"
    save_or_update_budget(yearly_month, yearly, yearly_id, conn, cur)

    conn.close()

    return str("saved")
    #dataDict = json.loads(data)
    #database = "pythonsqlite.db"
    #conn = create_connection(database)
    #months_db = select_all_tasks(conn, "months")
    #months = []
    #for month in months_db:
    #    print month
    #    months.append(month[1])
    #conn.close()
    #return jsonify(months)

@app.route('/api/getbudgets')
@cross_origin()
def getbudgets():
    database = "pythonsqlite.db"
    conn = create_connection(database)
    monthly_totals = select_all_tasks(conn, "budget")
    montly_tt_list = []
    for total in monthly_totals:
        montly_tt_list.append(total)
    conn.close()
    return jsonify(montly_tt_list)

if __name__ == '__main__':
    database = "pythonsqlite.db"
    conn = create_connection(database)
    cur = conn.cursor()
    try:
        # print("""CREATE TABLE months(ID INT, month TEXT, name TEXT)""")
        cur.execute("""CREATE TABLE budget(ID INT, month TEXT, budget REAL, name TEXT)""")
    except:
        print ""

    app.run()