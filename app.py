from flask import Flask, render_template, request, redirect, url_for, session, jsonify
#from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import json
import datetime

app = Flask(__name__)
app.secret_key = 'cookingpapa'
app.config['MYSQL_HOST'] = 'jank56-cookingpapa.cnm9qamwzhhp.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'cookingpapaAdmin'
app.config['MYSQL_PASSWORD'] = 'cookingpapa'
app.config['MYSQL_DB'] = 'cookingpapaDB'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/register", methods=['GET','POST'])
def register():
    msg = ''
    userName = ''
    pwd = ''
    if request.method == 'POST' and 'userName' in request.form and 'pwd' in request.form:
        userName = request.form['userName']
        pwd = request.form['pwd']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM userAccount WHERE userName = %s", (userName,))
        account = cursor.fetchone()
        #print(account)
        if account:
            msg = 'USERNAME EXISTS!'
        elif not re.match(r'^[A-Za-z]+$', userName):
            msg = 'INVALID USER NAME'
        elif bool(re.search(r"\s", pwd)):
            msg = 'INVALID PASSWORD WITH SPACE'
        else:
            #auto increment adjustment
            cursor.execute("SELECT COUNT(userId) AS cnt FROM userAccount")
            res = cursor.fetchone()
            count = res['cnt']
            if count == 0:
                cursor.execute("ALTER TABLE userAccount AUTO_INCREMENT = 1")
                mysql.connection.commit()

            cursor.execute("INSERT INTO userAccount VALUES(NULL, %s, %s)", (userName, pwd))
            mysql.connection.commit()
            msg = 'REGISTER SUCCESS!'
    elif request.method == 'POST':
        msg = 'EMTPY ENTRY'
    
    return render_template("register.html", msg=msg)

@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    userName = ''
    pwd = ''
    if request.method == 'POST' and 'userName' in request.form and 'pwd' in request.form:
        userName = request.form['userName']
        pwd = request.form['pwd']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM userAccount WHERE userName = %s AND pwd = %s', (userName, pwd))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['userId'] = account['userId']
            session['userName'] = account['userName']

            return redirect(url_for('home'))
        else:
            msg = "INCORRECT USERNAME OR PASSWORD!"

    return render_template('login.html', msg=msg)

@app.route("/login/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('userId', None)
    session.pop('userName', None)

    return redirect(url_for('login'))


@app.route("/login/home")
def home():
    if 'loggedin' in session:
        return render_template('home.html', userName = session['userName'])
    else:
        return redirect(url_for('login'))

@app.route("/login/pantry")
def pantry():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        # query = "ALTER TABLE userAccount AUTO_INCREMENT = {}".format(lastId)
        query = """SELECT Ingredient.name AS name, Pantry.qty AS qty, Pantry.unit AS unit, Pantry.purchDate AS pdate, Pantry.expDate AS edate, Pantry.pantryId AS pantryId
                          FROM Pantry JOIN Ingredient ON Pantry.ingId = Ingredient.ingId
                          WHERE Pantry.userId = {}""".format(session['userId'])
        cursor.execute(query)
        output = cursor.fetchall()
        return render_template('pantry.html', userName = session['userName'], output=output)
    else:
        return redirect(url_for('login'))

@app.route("/login/pantry/add", methods=['GET', 'POST'])
def pantryadd():
    msg = ''
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT name FROM Ingredient")
    ings=[item['name'] for item in cursor.fetchall()]

    if 'loggedin' in session:
        if request.method == 'POST' and 'ingName1' in request.form and 'qty1' in request.form  and 'unit1' in request.form  and 'pdate1' in request.form  and 'edate1' in request.form:
            ingName = ''
            qty = ''
            unit = ''
            pdate = ''
            edate = ''
            invalid=[]
            uId = str(session['userId'])
            
            # cursor = mysql.connection.cursor()
            # cursor.execute()
            #print(request.form)
            for i in range(1, (len(request.form)//5)+1):
                
                #print(request.form['ingName{}'.format(i)])
                ingName = request.form['ingName{}'.format(i)]
                qty = request.form['qty{}'.format(i)]
                unit = request.form['unit{}'.format(i)]
                pdate = request.form['pdate{}'.format(i)]
                edate = request.form['edate{}'.format(i)]

                cursor.execute("SELECT ingId FROM Ingredient WHERE name = %s", (ingName,))
                res = cursor.fetchone()
                # print(bool(cursor.fetchone()))
                # #ingId = str(cursor.fetchone()['ingId'])
                # #ingId=NULL
                # print(type(ingId))
                if bool(res):
                    ingId = res['ingId']
                    cursor.execute("SELECT COUNT(pantryId) AS cnt FROM Pantry")
                    res = cursor.fetchone()
                    count = res['cnt']
                    if count == 0:
                        cursor.execute("ALTER TABLE Pantry AUTO_INCREMENT = 1")
                        mysql.connection.commit()

                    cursor.execute("INSERT INTO Pantry (pantryId, ingId, userId, qty, unit, purchDate, expDate) VALUES(NULL, %s, %s, %s, %s, %s, %s)", (ingId, uId, qty, unit, pdate, edate))
                    mysql.connection.commit()
                    msg = 'INSERT SUCCESS!'
                else:
                    invalid.append(ingName)

            if len(invalid) > 0:
                for item in invalid:
                    msg += item + ', ' 
                
                msg = msg[0:len(msg)-2]
                if len(invalid) == 1:
                    msg += ' IS AN INVALID INGREDIENT!'   
                else:
                    msg += ' ARE INVALID INGREDIENTS!'   

        elif request.method == 'POST':
            msg = 'EMTPY ENTRY'
        
        return render_template("pantryadd.html", msg=msg, ings=ings)
    else:
        return redirect(url_for('login'))

@app.route("/login/pantry/update/<item>", methods=['GET', 'POST'])
def updatePantry(item):
    p = re.compile('(?<!\\\\)\'')
    item = p.sub('\"', item)
    itemdict = json.loads(re.sub(r'datetime\.date\(([^)]*)\)', r'[\1]', item))
    pstr = datetime.date(itemdict['pdate'][0], itemdict['pdate'][1], itemdict['pdate'][2])
    estr = datetime.date(itemdict['edate'][0], itemdict['edate'][1], itemdict['edate'][2])
    itemdict['pdate'] = pstr.strftime('%Y-%m-%d')
    itemdict['edate'] = estr.strftime('%Y-%m-%d')

    msg=''
    qty=''
    unit=''
    pdate=''
    edate=''

    if 'loggedin' in session:
        if bool(itemdict):
            if request.method == 'POST' and 'qty' in request.form  and 'unit' in request.form  and 'pdate' in request.form  and 'edate' in request.form:
                cursor = mysql.connection.cursor()

                qty = request.form['qty']
                unit = request.form['unit']
                pdate = request.form['pdate']
                edate = request.form['edate']
                pantryId = str(itemdict['pantryId'])
                cursor.execute("UPDATE Pantry SET qty = %s, unit = %s, purchDate = %s, expDate = %s WHERE pantryId = %s", (qty, unit, pdate, edate, pantryId))
                mysql.connection.commit()
                msg = 'UPDATE SUCCESS!'
        else:
            msg='ERROR FETCHING ENTRY!'

        return render_template("updatePantry.html", msg=msg, item=itemdict)
    else:
        return redirect(url_for('login'))

@app.route("/login/pantry/delete/<item>", methods=['GET', 'POST'])
def deletePantry(item):
    p = re.compile('(?<!\\\\)\'')
    item = p.sub('\"', item)
    itemdict = json.loads(re.sub(r'datetime\.date\(([^)]*)\)', r'[\1]', item))
    pstr = datetime.date(itemdict['pdate'][0], itemdict['pdate'][1], itemdict['pdate'][2])
    estr = datetime.date(itemdict['edate'][0], itemdict['edate'][1], itemdict['edate'][2])
    itemdict['pdate'] = pstr.strftime('%Y-%m-%d')
    itemdict['edate'] = estr.strftime('%Y-%m-%d')
    msg = ''
    pantryId = str(itemdict['pantryId'])
    print(type(pantryId))
    if bool(itemdict):
        if request.method == 'GET':
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM Pantry WHERE pantryId = %s", (pantryId,))
            entry = cursor.fetchone()

            if not entry:
                msg = 'INGREDIENT IN PANTRY DOES NOT EXISTS!'
            else:
                cursor.execute("DELETE FROM Pantry WHERE pantryId = %s", (pantryId,))

                #auto increment adjustment
                lastId = str(cursor.execute("SELECT MAX(pantryId) FROM Pantry"))       
                cursor.execute("UPDATE Pantry SET pantryId = pantryId-1 WHERE pantryId > %s", (pantryId,))
                query = "ALTER TABLE Pantry AUTO_INCREMENT = {}".format(lastId)
                cursor.execute(query)

                mysql.connection.commit()
                msg = 'DELETE SUCCESS!'
    else:
        msg = 'NO PANTRYID'
    
    return render_template("deletePantry.html", msg=msg, item=itemdict)


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
    userName = ''
    pwd = ''
    if userId:
        if request.method == 'POST' and 'userName' in request.form and 'pwd' in request.form:
            userName = request.form['userName']
            pwd = request.form['pwd']

            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM userAccount WHERE userId = %s", (userId))
            account = cursor.fetchone()
            #print(account)
            if not account:
                msg = 'ACCOUNT DOES NOT EXISTS!'
            elif not re.match(r'^[A-Za-z]+$', userName):
                msg = 'INVALID USER NAME'
            elif bool(re.search(r"\s", pwd)):
                msg = 'INVALID PASSWORD WITH SPACE'
            else:
                cursor.execute("UPDATE userAccount SET userName = %s, pwd = %s WHERE userId = %s", (userName, pwd, userId))
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

                # auto increment adjustment
                # lastId = str(cursor.execute("SELECT MAX(userId) FROM userAccount"))
                # count = str(cursor.execute("SELECT COUNT(userId) FROM userAccount"))
                #print('lastId: '+ lastId)
                #print('count: ' + count)
                
                # cursor.execute("UPDATE userAccount SET userId = userId-1 WHERE userId > %s", (userId))
                # query = "ALTER TABLE userAccount AUTO_INCREMENT = {}".format(lastId)
                # cursor.execute(query)

                mysql.connection.commit()
                msg = 'DELETE SUCCESS!'
    else:
        msg = 'NO USERID'
    
    return render_template("delete.html", msg=msg, account=account)
'''
#live-search
@app.route("/live-search-box")
def live_search_box():
    return render_template("pantryadd.html")
'''
@app.route("/live-search",methods=["GET","POST"])
def live_search():
    searchbox = request.form.get("text")
    cursor = mysql.connection.cursor()
    query = "SELECT name FROM Ingredient WHERE name LIKE '%{}%' ORDER BY name".format(searchbox)
    cursor.execute(query)
    result = cursor.fetchall()
    return jsonify(result)

@app.route("/live-search-insert",methods=["POST"])
def live_search_insert():
    ingredient = request.form["ingredient"]

    # Find ingredient name in Ingredient table
    # Insert the ingredient_id from result to Pantry

    if ingredient:
        return jsonify({'name': 'Inserted '+ingredient})
    return jsonify({'error': 'Missing Data!'})
