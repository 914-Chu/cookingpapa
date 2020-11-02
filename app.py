from flask import Flask, render_template, request, redirect, url_for, session
#from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'jank56-cookingpapa.cnm9qamwzhhp.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'cookingpapaAdmin'
app.config['MYSQL_PASSWORD'] = 'cookingpapa'
app.config['MYSQL_DB'] = 'cookingpapaDB'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

#datas = [] 
# @app.route("/home", methods=['GET','POST'])
# def crud():
    
#     cursor = mysql.connection.cursor()
#     cursor.execute("SELECT * FROM userAccount")
#     datas = cursor.fetchall()
#     print(datas)

#     #return datas[0]
#     return render_template("test.html", output=datas)

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/create", methods=['GET','POST'])
def create():
    msg = ''
    firstName = ''
    lastName = ''
    pwd = ''
    if request.method == 'POST' and 'firstName' in request.form and 'lastName' in request.form and 'pwd' in request.form:
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        pwd = request.form['pwd']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM userAccount WHERE firstName = %s AND lastName = %s", (firstName, lastName))
        account = cursor.fetchone()
        #print(account)
        if account:
            msg = 'ACCOUNT EXISTS!'
        elif not re.match(r'^[A-Za-z]+$', firstName):
            msg = 'INVALID FIRST NAME'
        elif not re.match(r'^[A-Za-z]+$', lastName):
            msg = 'INVALID LAST NAME'
        elif bool(re.search(r"\s", pwd)):
            msg = 'INVALID PASSWORD WITH SPACE'
        else:
            count = str(cursor.execute("SELECT COUNT(userId) FROM userAccount"))
            if count == 0:
                cursor.execute("ALTER TABLE userAccount AUTO_INCREMENT = 1")
                mysql.connection.commit()

            cursor.execute("INSERT INTO userAccount VALUES(NULL, %s, %s, %s)", (firstName, lastName, pwd))
            mysql.connection.commit()
            msg = 'CREATE SUCCESS!'
    elif request.method == 'POST':
        msg = 'EMTPY ENTRY'
    
    return render_template("create.html", msg=msg)
    #print(datas)
    
@app.route("/read", methods=['GET','POST'])
def read():
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM userAccount")
    datas = cursor.fetchall()
    #print(datas)
    #return datas[0]

    return render_template("read.html", output=datas)

@app.route("/update/<string:userId>", methods=['GET', 'POST'])
def update(userId):
    msg= ''
    firstName = ''
    lastName = ''
    pwd = ''
    if userId:
        if request.method == 'POST' and 'firstName' in request.form and 'lastName' in request.form and 'pwd' in request.form:
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            pwd = request.form['pwd']

            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM userAccount WHERE userId = %s", (userId))
            account = cursor.fetchone()
            #print(account)
            if not account:
                msg = 'ACCOUNT DOES NOT EXISTS!'
            elif not re.match(r'^[A-Za-z]+$', firstName):
                msg = 'INVALID FIRST NAME'
            elif not re.match(r'^[A-Za-z]+$', lastName):
                msg = 'INVALID LAST NAME'
            elif bool(re.search(r"\s", pwd)):
                msg = 'INVALID PASSWORD WITH SPACE'
            else:
                cursor.execute("UPDATE userAccount SET firstName = %s, lastName = %s, pwd = %s WHERE userId = %s", (firstName, lastName, pwd, userId))
                mysql.connection.commit()
                msg = 'UPDATE SUCCESS!'
        elif request.method == 'POST':
            msg = 'EMTPY ENTRY'
    else:
        msg= 'NO USERID'
    return render_template("update.html", userId=userId, msg=msg)

@app.route("/delete/<string:userId>", methods=['GET', 'POST'])
def delete(userId):
    msg = ''
    account = {}
    if userId:
        if request.method == 'GET':
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM userAccount WHERE userId = %s", (userId))
            account = cursor.fetchone()

            if not account:
                msg = 'ACCOUNT DOES NOT EXISTS!'
            else:
                cursor.execute("DELETE FROM userAccount WHERE userId = %s", (userId))
                #mysql.connection.commit()
                lastId = str(cursor.execute("SELECT MAX(userId) FROM userAccount"))
                count = str(cursor.execute("SELECT COUNT(userId) FROM userAccount"))
                #print('lastId: '+ lastId)
                #print('count: ' + count)
                
                cursor.execute("UPDATE userAccount SET userId = userId-1 WHERE userId > %s", (userId))
                query = "ALTER TABLE userAccount AUTO_INCREMENT = {}".format(lastId)
                cursor.execute(query)
                mysql.connection.commit()
                msg = 'DELETE SUCCESS!'
    else:
        msg = 'NO USERID'
    
    return render_template("delete.html", msg=msg, account=account)

# if __name__ == '__main__':
#     app.run()