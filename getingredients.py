import requests
import json
import mysql.connector


url = "https://tasty.p.rapidapi.com/recipes/list"

querystring = {"from":"0","size":"40","tags":"under_30_minutes"}

headers = {
    'x-rapidapi-key': "3f794b9ea4mshd6b61d22b11ccb2p1c4375jsnb2d1f87a2f0a",
    'x-rapidapi-host': "tasty.p.rapidapi.com"
    }

response = requests.request("GET", url, headers=headers, params=querystring)
response_dict = json.loads(response.text)

mydb = mysql.connector.connect(
  host="jank56-cookingpapa.cnm9qamwzhhp.us-east-2.rds.amazonaws.com",
  user="cookingpapaAdmin",
  password="cookingpapa",
  database="cookingpapaDB"
)
mycursor = mydb.cursor()
#with open('ingredients.csv', mode = 'w') as ingredients:
    #ingredient_writer = csv.writer(ingredients, delimiter=',', quotechar = '"', quoting=csv.QUOTE_MINIMAL)
for recipe in response_dict['results']:
    if not 'sections' in recipe:
        continue
    for section in recipe['sections']:
        for component in section['components']:
            ingredient = component['ingredient']['name']
            ing_id = component['ingredient']['id']
            tup = (ing_id, ingredient)
            sql = "INSERT INTO cookingpapaDB.Ingredient (ingId, name) VALUES (%s, %s)"
            val = tup
            mycursor.execute(sql, val)
            #ingredient_writer.writerow(tup)

mydb.commit()

print(mycursor.rowcount, "record inserted.")
