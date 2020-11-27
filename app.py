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

@app.route("/findRecipes", methods=['GET', 'POST'])
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
        {"$group": {"_id": "$_id", "id":{"$first":"$id"}, "name":{"$first":"$name"},"thumbnail_url":{"$first":"$thumbnail_url"}, "countMatch": {"$sum": {"$cond":[{"$in": ["$sections.components.ingredient.id", usersIngredients]},1,0]}},"countTotal": {"$sum": 1}}},
        {"$project": {"_id": 1, "id":1,"name":1, "thumbnail_url":1, "countMatch": 1, "countTotal": 1, "score":{"$round":[{"$divide": [{"$multiply":["$countMatch",100]}, "$countTotal"]}, 1]}}},
        {"$sort": {"score": -1}},
        {"$limit": 20}
        ])
    cookableRecipesList = list(canCookRecipes)
    return render_template('findRecipes.html', cookableRecipesList=cookableRecipesList, len=len(cookableRecipesList))

@app.route("/findRecipesPreferences", methods=['GET', 'POST'])
def findRecipesPreferences():
    tagList = ['almond_joy', 'mccormick_seasoned_pro', '3_musketeers', 'vegetarian', 'summer', 'mexican', 'dutch_oven', 'meal_prep', 'baking_cups', 'strainer', 'chop_champ', 'bread_pan', 'tasty_s_5th_birthday_savory', 'tasty_ewd_fifteen', 'tupperware', 'italian', 'mccormick_easy_dinner', 'german', 'pressure_cooker', 'tongs', 'pescatarian', 'one_top_app_steak', 'holiday_treats', 'parchment_paper', 'cooking_kit', 'african', 'rolling_pin', 'snickers', 'game_day', 'chinese', 'korean', 'cupcake_pan', 'snacks', 'food_processor', 'one_top_app_seafood', 'qfp_recipes', 'breakfast', 'gluten_free', 'paper_bowls', 'eko_video', 'hershey_s', 'pie_dish', 'latin_american', 'ice_cream_scoop', 'contains_alcohol', 'tasty_dinner_kits', 'every_occasion', 'bakery_goods', 'dairy_free', 'steam', 'under_30_minutes', 'beyond_red_blend', 'appetizers', 'instant_pot', 'fish_spatula', 'sides', 'caribbean', 'one_top_app_sauces', 'kid_friendly', 'cooling_rack', 'liquid_measuring_cup', 'winter', 'hispanic_heritage_month', 'oh_so_rose', 'one_top_app_dessert', 'epoca_walmart', 'one_top_app_sides', 'grill', 'bake', 'tasty_s_5th_birthday_recipe', 'wok', 'drinks', 'thanksgiving', 'sponsored_recipe', 'date_night', 'licensed_video', 'sauce_pan', 'easter', 'ice_cube_tray', 'pyrex', 'tasty_ewd_tips', 'cutting_board', 'walmart_holiday_bundle', 'lunch', 'spatula', 'wax_paper', 'light_bites', 'best_of_tasty', 'one_top_app_eggs', 'american', 'party', 'fusion', 'thai', 'casual_party', 'offset_spatula', 'greek', 'mccormick_game_day', 'club_house_seasoned_pro', 'spider', 'cheese_grater', 'one_pot_or_pan', 'hand_mixer', 'freezer', 'one_top_friendly', 'desserts', 'paper_napkins', 'saute_pan', 'microplane', 'indian', 'sieve', 'stuffed', 'tasty_s_5th_birthday_sweet', 'tastyjunior', 'peeler', 'baking_kit', 'comfort_food', 'asian_pacific_american_heritage_month', 'colander', 'holiday_cookie_recipe', 'spring', 'paper_plates', 'tasty_ewd_fall', 'healthy', 'tasty_junior_cookbook', 'wooden_spoon', 'one_top_app_grains', 'peppermint_pattie', 'mixing_bowl', 'zipper_storage_bags', 'no_bake_desserts', 'plastic_wrap', 'deep_fry', 'cake_pan', 'vietnamese', 'ice_cream_social', 'fall', 'oven', 'seafood', 'paper_cups', 'holiday_cookie_howto', 'slow_cooker', 'stove_top', 'tasty_ewd_healthy', '5_ingredients_or_less', 'baking_pan', 'lollipop_sticks', 'black_history_month', 'easy', 'broiler', 'plastic_utensils', 'indulgent_sweets', 'qfp_baking', 'fourth_of_july', 'big_batch', 'schwartz_seasoned_pro', 'whisk', 'british', 'cast_iron_pan', 'japanese', 'weeknight', 'valentines_day', 'brunch', 'tasty_cookbook', 'vegan', 'microwave', 'dry_measuring_cups', 'brazilian', 'pizza_kit', 'dinner', 'measuring_spoons', 'special_occasion', 'french', 'one_top_app_meat', 'mashup', 'one_top_app_veggies', 'low_carb', 'happy_hour', 'christmas', 'oven_mitts', 'bbq', 'kitchen_shears', 'blender', 'srsly_sauv_blanc', 'halloween', 'chefs_knife', 'pride_month', 'zipper_freezer_bags', 'middle_eastern', 'pan_fry', 'picnic', 'one_top_app_main_feed']
    numberList = []
    for i in range(0, len(tagList)):
        numberList.append(i)
    tagDict = {tagList[i]: numberList[i] for i in range(len(tagList))}

    #create user profile
    userProfile = [0] * len(tagList)

    cursor = mysql.connection.cursor()
    query = """SELECT Favorites.recipe_id
                FROM Favorites
                WHERE Favorites.user_id = {}""".format(session['userId'])
    cursor.execute(query)
    result = cursor.fetchall()
    usersFavorites = [i['recipe_id'] for i in result]

    for recipe_id in usersFavorites:
        tagResult = recipes.aggregate([
            {"$match":{"id":recipe_id}},
            {"$limit":1},
            {"$unwind":"$tags"},
            {"$project":{"_id":0, "tags":1}}
            ])
        recipeTags = [i['tags']['name'] for i in tagResult] 
        for tag in recipeTags:
            if tag in tagList:
                userProfile[tagDict[tag]] += 1

    cursor = mysql.connection.cursor()
    query = """SELECT Dislikes.recipe_id
                FROM Dislikes
                WHERE Dislikes.user_id = {}""".format(session['userId'])
    cursor.execute(query)
    result = cursor.fetchall()
    usersDislikes = [i['recipe_id'] for i in result]

    for recipe_id in usersDislikes:
        tagResult = recipes.aggregate([
            {"$match":{"id":recipe_id}},
            {"$limit":1},
            {"$unwind":"$tags"},
            {"$project":{"_id":0, "tags":1}}
            ])
        recipeTags = [i['tags']['name'] for i in tagResult] 
        for tag in recipeTags:
            if tag in tagList:
                userProfile[tagDict[tag]] -= 1

    allRecipes = list(db.recipes.find({"$and":[{"id":{"$nin": usersFavorites}},{"id":{"$nin": usersDislikes}}]},{"_id":0, "id":1, "tags":1}))

    recipeScores = {}                          #key: recipe id, value:score
    for item in allRecipes:
        tagArr = [0] * len(tagList)
        if 'tags' in item.keys():
            for tag in item['tags']:
                tagArr[tagDict[tag['name']]] += 1
            if 'id' in item.keys():
                recipeScores[item['id']] = sum(i[0] * i[1] for i in zip(tagArr, userProfile))

    recipeIdandScore = sorted(recipeScores.items(), key=lambda x:x[1], reverse=True)
    recipesIdToRec = [recipeIdandScore[i][0] for i in range(0,20)]

    recipesToRec = list(recipes.find({"id":{"$in": recipesIdToRec}}))
    return render_template('findRecipesPreferences.html', recipesToRec=recipesToRec, len=len(recipesToRec))

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

@app.route("/pantry/addDislike/<string:recipeId>", methods=['GET', 'POST'])
def addDislike(recipeId):
    msg = ""
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        # query = "ALTER TABLE userAccount AUTO_INCREMENT = {}".format(lastId)
        query = """SELECT *
                   FROM Dislikes
                   WHERE user_id = {} 
                   AND recipe_id = {}""".format(session['userId'], recipeId)
        cursor.execute(query)
        output = cursor.fetchall()
        if len(output) != 0:
            msg = "Recipe already added"
            return redirect(url_for('findRecipesPreferences', msg=msg))
        else:
            query = """INSERT INTO Dislikes (recipe_id, user_id)
                       VALUES ({}, {})""".format(recipeId, session['userId'])
            cursor.execute(query)
            mysql.connection.commit()
            msg = "Add success"
            return redirect(url_for('findRecipesPreferences', msg=msg))
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
   
@app.route("/recipeDetails", methods=['GET'])
def showRecipeDetails():
    recipe = {}
    recipe['name'] = 'Skinny Oatmeal'
    recipe['beauty_url'] = 'https://www.eatyourselfskinny.com/wp-content/uploads/2016/01/blueberry-oatmeal-33.jpg'
    recipe['tags'] = [{'type':'Lifestyle','display_name':'Weight loss'},{'type':'Dietary','display_name':'Vegan'}]
    recipe['description'] = 'Whether you are getting in shape during quarantine or just plain bored, Skinny Oatmeal is the perfect breakfast food to kick start your metabolism'
    recipe['ingredients'] = [{'name':'Old fashioned rolled oats','quantity':'0.5 cup'},{'name':'Almond milk', 'quantity':'1 cup'},{'name':'Bananas', 'quantity':'0.5'}]
    recipe['instructions'] = [{'display_text':'Heat almond milk on stove top to boiling point'},{'display_text':'Turn heat down to simmer and add the oats'},{'display_text':'When oats turn fluffy, add mashed banana'},{'display_text':'Remove into a bowl and serve immediately.'}]
    return render_template("recipeDetails.html", recipe=recipe)
