from flask import Flask,jsonify
from flask_cors import cross_origin, CORS
import boto3
import datetime
import calendar
from dateutil.relativedelta import relativedelta
import collections
import sqlite3
from sqlite3 import Error


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
    return jsonify(months)

if __name__ == '__main__':
    app.run()