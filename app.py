from flask import Flask, render_template, request, redirect, url_for, session, jsonify, json
#from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_paginate import Pagination, get_page_parameter, get_page_args
import MySQLdb.cursors
from pymongo import MongoClient
import re
import re
import json
import datetime
from collections import OrderedDict

client = MongoClient("mongodb+srv://cookingpapaAdmin:cookingpapa@cluster0.amfe5.mongodb.net/cookingpapa?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
db = client.cookingpapa
#serverStatusResult=db.command("serverStatus")
#print(serverStatusResult)
recipes=db.recipes
#print(recipes.find_one({"name":"cereal with milk"}))

app = Flask(__name__)
app.secret_key = 'cookingpapa'
app.config['MYSQL_HOST'] = 'jank56-cookingpapa.cnm9qamwzhhp.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'cookingpapaAdmin'
app.config['MYSQL_PASSWORD'] = 'cookingpapa'
app.config['MYSQL_DB'] = 'cookingpapaDB'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

unitConversions = {'g-mg': 1000.0, 'mg-g': 0.001,
                   'l-ml:': 1000.0, 'ml-l': 0.001,
                   }


@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/frontpage")
def frontpage():
    return render_template("frontpage.html")

@app.route("/findRecipes")
def findRecipes():
    cursor = mysql.connection.cursor()
    query = """SELECT Pantry.ingId
                FROM Pantry
                WHERE Pantry.userId = {}""".format(session['userId'])
    cursor.execute(query)
    result = cursor.fetchall()
    usersIngredients = [i['ingId'] for i in result]     #list of ingredient ids that the user has
    canCookRecipes = db.recipes.aggregate([
        {"$unwind": "$sections"},
        {"$unwind": "$sections.components"},
        {"$group": {"_id": "$id", "countMatch": {"$sum": {"$cond":[{"$in": ["$sections.components.ingredient.id", usersIngredients]},1,0]}},"countTotal": {"$sum": 1}}},
        {"$project": {"_id": 0, "id":"$_id", "countMatch": 1, "countTotal": 1, "score":{"$divide": ["$countMatch", "$countTotal"]}}},
        {"$sort": {"score": -1}},
        {"$limit": 5},
        ])
    #print(list(canCookRecipes))
    recipeIds = []
    for dic in list(canCookRecipes):
        recipeIds.append(int(dic['id']))
    
    recipeList = list(db.recipes.find( {"id": {"$in": recipeIds} }, {"_id":0, "name":1, "thumbnail_url":1, "id":1} ))

    return render_template('findRecipes.html', recipes=recipeList)

@app.route("/register", methods=['GET','POST'])
def register():
    msg = ''
    userName = ''
    pwd = ''
    if request.method == 'POST' and 'userName' in request.form and 'pwd' in request.form:
        userName = request.form['userName']
        pwd = request.form['pwd']

        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT * FROM userAccount WHERE userName = %s", (userName,))
        account = cursor.fetchone()
        # print(account)
        if account:
            msg = 'USERNAME EXISTS!'
        elif not re.match(r'^[A-Za-z]+$', userName):
            msg = 'INVALID USER NAME'
        elif bool(re.search(r"\s", pwd)):
            msg = 'INVALID PASSWORD WITH SPACE'
        else:
            # auto increment adjustment
            cursor.execute("SELECT COUNT(userId) AS cnt FROM userAccount")
            res = cursor.fetchone()
            count = res['cnt']
            if count == 0:
                cursor.execute("ALTER TABLE userAccount AUTO_INCREMENT = 1")
                mysql.connection.commit()

            cursor.execute(
                "INSERT INTO userAccount VALUES(NULL, %s, %s)", (userName, pwd))
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
        cursor.execute(
            'SELECT * FROM userAccount WHERE userName = %s AND pwd = %s', (userName, pwd))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['userId'] = account['userId']
            session['userName'] = account['userName']

            return redirect(url_for('pantry'))
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
        return render_template('home.html', userName=session['userName'])
    else:
        return redirect(url_for('login'))


@app.route("/login/pantry")
def pantry():
    if 'loggedin' in session:
        '''cursor = mysql.connection.cursor()
        # query = "ALTER TABLE userAccount AUTO_INCREMENT = {}".format(lastId)
        query = """SELECT Ingredient.name AS name, Pantry.qty AS qty, Pantry.unit AS unit, Pantry.purchDate AS pdate, Pantry.expDate AS edate, Pantry.pantryId AS pantryId
                          FROM Pantry JOIN Ingredient ON Pantry.ingId = Ingredient.ingId
                          WHERE Pantry.userId = {}""".format(session['userId'])
        cursor.execute(query)
        output = cursor.fetchall()'''
        # Below function call to replace line 102-108
        return prettyPantryDescription()  # ADVANCED SQL QUERY #1
        '''return render_template('pantry.html', userName = session['userName'], output=output)'''
    else:
        return redirect(url_for('login'))

# ADVANCED SQL QUERY #1
# NOTES: Use stored procedures to convert units to standardized units so no conversion
# Need to be called by pantry()
# parameter pantryRecords


def prettyPantryDescription():
    cursor = mysql.connection.cursor()
    query = """SELECT Ingredient.name AS name, Pantry.unit AS unit, SUM(Pantry.qty) AS qty
                            FROM Pantry JOIN Ingredient ON Pantry.ingId = Ingredient.ingId
                            WHERE Pantry.userId = {}
                            GROUP BY Ingredient.name, Pantry.unit
                            ORDER BY Ingredient.name, Pantry.unit""".format(session['userId'])
    cursor.execute(query)
    output = cursor.fetchall()
    return render_template('pantry.html', userName=session['userName'], output=output)


@app.route("/login/pantry/add", methods=['GET', 'POST'])
def pantryadd():
    msg = ''
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT name FROM Ingredient")
    ings = [item['name'] for item in cursor.fetchall()]

    if 'loggedin' in session:
        if request.method == 'POST' and 'ingName1' in request.form and 'qty1' in request.form and 'unit1' in request.form and 'pdate1' in request.form and 'edate1' in request.form:
            ingName = ''
            qty = ''
            unit = ''
            pdate = ''
            edate = ''
            invalid = []
            uId = str(session['userId'])

            # cursor = mysql.connection.cursor()
            # cursor.execute()
            # print(request.form)
            for i in range(1, (len(request.form)//5)+1):

                # print(request.form['ingName{}'.format(i)])
                ingName = request.form['ingName{}'.format(i)]
                qty = request.form['qty{}'.format(i)]
                unit = request.form['unit{}'.format(i)]
                pdate = request.form['pdate{}'.format(i)]
                edate = request.form['edate{}'.format(i)]

                cursor.execute(
                    "SELECT ingId FROM Ingredient WHERE name = %s", (ingName,))
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

                    cursor.execute("INSERT INTO Pantry (pantryId, ingId, userId, qty, unit, purchDate, expDate) VALUES(NULL, %s, %s, %s, %s, %s, %s)", (
                        ingId, uId, qty, unit, pdate, edate))
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
    pstr = datetime.date(itemdict['pdate'][0],
                         itemdict['pdate'][1], itemdict['pdate'][2])
    estr = datetime.date(itemdict['edate'][0],
                         itemdict['edate'][1], itemdict['edate'][2])
    itemdict['pdate'] = pstr.strftime('%Y-%m-%d')
    itemdict['edate'] = estr.strftime('%Y-%m-%d')

    msg = ''
    qty = ''
    unit = ''
    pdate = ''
    edate = ''

    if 'loggedin' in session:
        if bool(itemdict):
            if request.method == 'POST' and 'qty' in request.form and 'unit' in request.form and 'pdate' in request.form and 'edate' in request.form:
                cursor = mysql.connection.cursor()

                qty = request.form['qty']
                unit = request.form['unit']
                pdate = request.form['pdate']
                edate = request.form['edate']
                pantryId = str(itemdict['pantryId'])
                cursor.execute("UPDATE Pantry SET qty = %s, unit = %s, purchDate = %s, expDate = %s WHERE pantryId = %s", (
                    qty, unit, pdate, edate, pantryId))
                mysql.connection.commit()
                msg = 'UPDATE SUCCESS!'
        else:
            msg = 'ERROR FETCHING ENTRY!'

        return render_template("updatePantry.html", msg=msg, item=itemdict)
    else:
        return redirect(url_for('login'))


@app.route("/login/pantry/delete/<item>", methods=['GET', 'POST'])
def deletePantry(item):
    p = re.compile('(?<!\\\\)\'')
    item = p.sub('\"', item)
    itemdict = json.loads(re.sub(r'datetime\.date\(([^)]*)\)', r'[\1]', item))
    pstr = datetime.date(itemdict['pdate'][0],
                         itemdict['pdate'][1], itemdict['pdate'][2])
    estr = datetime.date(itemdict['edate'][0],
                         itemdict['edate'][1], itemdict['edate'][2])
    itemdict['pdate'] = pstr.strftime('%Y-%m-%d')
    itemdict['edate'] = estr.strftime('%Y-%m-%d')
    msg = ''
    pantryId = str(itemdict['pantryId'])
    print(type(pantryId))
    if bool(itemdict):
        if request.method == 'GET':
            cursor = mysql.connection.cursor()
            cursor.execute(
                "SELECT * FROM Pantry WHERE pantryId = %s", (pantryId,))
            entry = cursor.fetchone()

            if not entry:
                msg = 'INGREDIENT IN PANTRY DOES NOT EXISTS!'
            else:
                cursor.execute(
                    "DELETE FROM Pantry WHERE pantryId = %s", (pantryId,))

                # auto increment adjustment
                lastId = str(cursor.execute(
                    "SELECT MAX(pantryId) FROM Pantry"))
                cursor.execute(
                    "UPDATE Pantry SET pantryId = pantryId-1 WHERE pantryId > %s", (pantryId,))
                query = "ALTER TABLE Pantry AUTO_INCREMENT = {}".format(lastId)
                cursor.execute(query)

                mysql.connection.commit()
                msg = 'DELETE SUCCESS!'
    else:
        msg = 'NO PANTRYID'

    return render_template("deletePantry.html", msg=msg, item=itemdict)


@app.route('/login/pantry/checkDate', methods=['GET', 'POST'])
def checkDate():
    expInterval = "2"

    if 'loggedin' in session:
        if request.method == "POST" and 'day' in request.form and int(request.form['day']) > 0:
            expInterval = request.form['day']

        cursor = mysql.connection.cursor()
        # EXPIRED IN ? DAYS
        query = """SELECT Pantry.pantryId AS pantryId, Ingredient.name AS name, Pantry.qty AS qty, Pantry.unit AS unit, Pantry.expDate AS edate
                          FROM Pantry JOIN Ingredient ON Pantry.ingId = Ingredient.ingId
                          WHERE Pantry.userId = {}
                          AND Pantry.expDate <= DATE_ADD(CURDATE(), INTERVAL {} DAY)
                          AND Pantry.expDate >= CURDATE()""".format(session['userId'], expInterval)
        # ALREADY EXPIRED
        query2 = """SELECT Pantry.pantryId AS pantryId, Ingredient.name AS name, Pantry.qty AS qty, Pantry.unit AS unit, Pantry.expDate AS edate
                          FROM Pantry JOIN Ingredient ON Pantry.ingId = Ingredient.ingId
                          WHERE Pantry.userId = {}
                          AND Pantry.expDate <= DATE_ADD(CURDATE(), INTERVAL {} DAY)
                          AND Pantry.expDate < CURDATE()""".format(session['userId'], expInterval)
        cursor.execute(query)
        expiredSoon = cursor.fetchall()
        cursor.execute(query2)
        expired = cursor.fetchall()

        return render_template('checkDate.html', expInterval=expInterval, expiredSoon=expiredSoon, expired=expired)
    else:
        return redirect(url_for('login'))

@app.route("/login/pantry/explore", methods=['GET', 'POST'])
def explore():
    if 'loggedin' in session:
        search = False
        q = request.args.get('q')
        if q:
            search = True

        page, per_page, offset = get_page_args()
        cond = re.compile(r'recipe', re.I)
        display = recipes.find({"canonical_id":{'$regex': cond}}, {"_id":0, "name":1, "thumbnail_url":1, "id":1})
        displaypage = recipes.find({"canonical_id":{'$regex': cond}}, {"_id":0, "name":1, "thumbnail_url":1, "id":1}).limit(per_page).skip(offset)
        pagination = Pagination(page=page, total=display.count(), search=search, record_name='display', per_page=per_page, offset=offset)
        return render_template('explore.html', display=displaypage, pagination=pagination)
    else:
        return redirect(url_for('login'))

@app.route("/login/pantry/recipe/<string:recipeId>", methods=['GET', 'POST'])
def recipe(recipeId):
    if 'loggedin' in session:
        search = False
        q = request.args.get('q')
        if q:
            search = True

        page, per_page, offset = get_page_args()
        display = recipes.find({"id":recipedId}, {"_id":0, "name":1, "thumbnail_url":1, "id":1, "sections":1, "description":1, "instructions":1, "tags":1})

        #TODO CHANGE html page
        return render_template('explore.html', display=display)
    else:
        return redirect(url_for('login'))

@app.route("/pantry/favorite", methods=['GET', 'POST'])
def favorite():
    msg=''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        query = """SELECT recipe_id
                   FROM Favorites
                   WHERE user_id = {}""".format(session['userId'])
        cursor.execute(query)
        output = cursor.fetchall()
        res = []
        for x in output:
            # s = "recipe:" + str(x.get('recipe_id'))
            res.append(x.get('recipe_id'))
        
        print(res)

        search = False
        q = request.args.get('q')
        if q:
            search = True

        page, per_page, offset = get_page_args()
        display = recipes.find({"id":{'$in': res}}, {"_id":0, "name":1, "thumbnail_url":1, "id":1})
        displaypage = recipes.find({"id":{'$in': res}}, {"_id":0, "name":1, "thumbnail_url":1, "id":1}).limit(per_page).skip(offset)
        pagination = Pagination(page=page, total=display.count(), search=search, record_name='display', per_page=per_page, offset=offset)
        return render_template('favorite.html', display=displaypage, pagination=pagination, msg=msg)
    else:
        return redirect(url_for('login'))

@app.route("/pantry/addfavorite/<string:recipeId>", methods=['GET', 'POST'])
def addfavorite(recipeId):
    msg = ""
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        # query = "ALTER TABLE userAccount AUTO_INCREMENT = {}".format(lastId)
        query = """SELECT *
                   FROM Favorites
                   WHERE user_id = {} 
                   AND recipe_id = {}""".format(session['userId'], recipeId)
        cursor.execute(query)
        output = cursor.fetchall()
        if len(output) != 0:
            msg = "Recipe already added"
            return redirect(url_for('favorite', msg=msg))
        else:
            query = """INSERT INTO Favorites (recipe_id, user_id)
                       VALUES ({}, {})""".format(recipeId, session['userId'])
            cursor.execute(query)
            mysql.connection.commit()
            msg = "Add success"
            return redirect(url_for('favorite', msg=msg))
    else:
        return redirect(url_for('login'))

@app.route("/pantry/deletefavorite/<string:recipeId>", methods=['GET', 'POST'])
def deletefavorite(recipeId):
    msg = ""
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        query = """SELECT *
                   FROM Favorites
                   WHERE user_id = {} 
                   AND recipe_id = {}""".format(session['userId'], recipeId)
        cursor.execute(query)
        output = cursor.fetchall()
        if len(output) != 1:
            msg = "Delete Failed"
            return redirect(url_for('favorite', msg=msg))
        else:
            query = """DELETE FROM Favorites 
                       WHERE user_id = {} 
                       AND recipe_id = {}""".format(session['userId'], recipeId)
            cursor.execute(query)
            mysql.connection.commit()
            msg= "Delete Success"
            return redirect(url_for('favorite', msg=msg))
    else:
        return redirect(url_for('login'))

@app.route("/read", methods=['GET', 'POST'])
def read():

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM userAccount")
    datas = cursor.fetchall()

    return render_template("read.html", output=datas)


@app.route("/update/<string:userId>", methods=['GET', 'POST'])
def update(userId):
    msg = ''
    userName = ''
    pwd = ''
    if userId:
        if request.method == 'POST' and 'userName' in request.form and 'pwd' in request.form:
            userName = request.form['userName']
            pwd = request.form['pwd']

            cursor = mysql.connection.cursor()
            cursor.execute(
                "SELECT * FROM userAccount WHERE userId = %s", (userId))
            account = cursor.fetchone()
            # print(account)
            if not account:
                msg = 'ACCOUNT DOES NOT EXISTS!'
            elif not re.match(r'^[A-Za-z]+$', userName):
                msg = 'INVALID USER NAME'
            elif bool(re.search(r"\s", pwd)):
                msg = 'INVALID PASSWORD WITH SPACE'
            else:
                cursor.execute(
                    "UPDATE userAccount SET userName = %s, pwd = %s WHERE userId = %s", (userName, pwd, userId))
                mysql.connection.commit()
                msg = 'UPDATE SUCCESS!'
        elif request.method == 'POST':
            msg = 'EMTPY ENTRY'
    else:
        msg = 'NO USERID'
    return render_template("update.html", userId=userId, msg=msg)


@app.route("/delete/<string:userId>", methods=['GET', 'POST'])
def delete(userId):
    msg = ''
    account = {}
    if userId:
        if request.method == 'GET':
            cursor = mysql.connection.cursor()
            cursor.execute(
                "SELECT * FROM userAccount WHERE userId = %s", (userId))
            account = cursor.fetchone()

            if not account:
                msg = 'ACCOUNT DOES NOT EXISTS!'
            else:
                cursor.execute(
                    "DELETE FROM userAccount WHERE userId = %s", (userId))

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
   
@app.route("/recipeDetails/<int:recipeId>", methods=['GET'])
def showRecipeDetails(recipeId):
    if not recipeId:
        recipeId = 6908
    
    '''
    recipe = list(recipes.aggregate([
        { "$match": {"id":recipeId} },
        { "$project": {"_id":0, "id":1, "name":1, "thumbnail_url":1, "tags":1, "total_time_minutes":1, "description":1, "num_servings":1, 
                        "component":"$sections.name", "ingredients": "$sections.components.ingredient", "measurements":"$sections.components.measurements", "instructions":1} }
    ]))
    '''

    recipe = list(recipes.aggregate([
        { "$match": {"id":recipeId} },
        { "$project": {"_id":0, "id":1, "name":1, "thumbnail_url":1, "tags":1, "total_time_minutes":1, "description":1, "num_servings":1, 
                        "component":"$sections.name", "ingredients": "$sections.components", "instructions":1} }
    ]))
    return render_template("recipeDetails.html", recipe=recipe[0])
