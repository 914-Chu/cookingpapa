from pymongo import MongoClient

client = MongoClient("mongodb+srv://cookingpapaAdmin:cookingpapa@cluster0.amfe5.mongodb.net/cookingpapa?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
db = client.cookingpapa
recipes=db.recipes

result = recipes.aggregate([
        {"$unwind":"$tags"},
        {"$project":{"_id":0, "tags.name":1}}
    ])
tagList = [i['tags']['name'] for i in result] 
uniqueTags = set(tagList)
print(uniqueTags)