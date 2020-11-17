from flask import Flask, render_template, request, redirect
#import pymysql
from flask_mysqldb import MySQL
import MySQLdb.cursors
from pymongo import MongoClient
# import re

client = MongoClient("mongodb+srv://cookingpapaAdmin:cookingpapa@cluster0.amfe5.mongodb.net/cookingpapa?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
db = client.cookingpapa
serverStatusResult=db.command("serverStatus")
print(serverStatusResult)
recipes=db.recipes
print(recipes.find_one({"name":"cereal with milk"}))

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'jank56-cookingpapa.cnm9qamwzhhp.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'cookingpapaAdmin'
app.config['MYSQL_PASSWORD'] = 'cookingpapa'
app.config['MYSQL_DB'] = 'cookingpapaDB'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

#db = pymysql.connect('jank56-cookingpapa.cnm9qamwzhhp.us-east-2.rds.amazonaws.com', 'cookingpapaAdmin', 'cookingpapa')

@app.route("/")
def crud():

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM userAccount")
    datas = cursor.fetchall()
    print(datas)

    # return datas[0]
    return render_template("test.html", datas=datas)

# if __name__ == '__main__':
#     app.run()