from flask import Flask, render_template, request, url_for, redirect, flash
from pymongo import MongoClient
from User import User
from bson.objectid import ObjectId
import json


app = Flask(__name__)

username = "bugraltintas"
password = "9B9mtXOpGtSx6FWa"

client = MongoClient("mongodb+srv://{}:{}@cluster0.mcjm34k.mongodb.net/?retryWrites=true&w=majority".format(username,password))

db = client.flask_db
todos = db.todos
users = db.users


def clear_all_ratings():
    # update all users' avg_rating field to 0 and ratings field to empty list
    users.update_many({},{'$set':{"ratings":[],"avg_rating":0.0}})
    # update all items' avg_rating field to 0 and rating field to empty list
    db.items.update_many({},{'$set':{"rating":[],"avg_rating":0.0}})

def clear_all_reviews():
    # update all users' reviews field to empty list
    users.update_many({},{'$set':{"reviews":[]}})
    # update all items' reviews field to empty list and num_of_reviewers field to 0
    db.items.update_many({},{'$set':{"reviews":[],"num_of_reviewers":0}})

@app.route('/', methods=('GET', 'POST'))
def index():
    all_items = db.items.find()
    return render_template('index.html',items=all_items)

# login page
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username'] 
        record = users.find_one({'username': username})
        if record:
            return redirect(url_for('index'))
        else:
            print('Username or password is incorrect.')
            render_template('login.html')
    return render_template('login.html')

#endpoint for category get request
@app.route('/category', methods=['GET'])
def category():
    print(request.args)
    category = request.args.get('category')
    if category == "All":
        items = db.items.find()
    else:
        items = db.items.find({"category":category})
    return render_template('index.html',items=items)


#endpoint for item
@app.route('/item/<item_id>', methods=('GET', 'POST'))
def item(item_id):
    item = db.items.find_one({"_id":ObjectId(item_id)})
    if request.method == 'POST':
        user = db.users.find_one({"username":"ayberk"})
        print(request.form)
        if 'review' in request.form:
            username = "ayberk" # TODO: get username from session
            review = {
                "reviewer":username,
                "review":request.form['review'],
            }

            db.items.update_one({"_id":ObjectId(item_id)},{'$push':{"reviews":review},'$inc':{"num_of_reviewers":1}})            
            # update user's reviews

            db.users.update_one({"username":username},{'$push':{"reviews":item_id}})
            return redirect(url_for('item',item_id=item_id))

            
        if 'rate' in request.form:
            print("rate request")
            username = "ayberk" # TODO: get username from session
            star = int(request.form['rate'])
            rate = {
                "rater":username,
                "rate":star,
            }
            
            # update item's ratings
            new_avg_rate = (item['avg_rating']*len(item['rating']) + star)/(len(item['rating'])+1)
            db.items.update_one({"_id":ObjectId(item_id)},{'$set':{"avg_rating":new_avg_rate},'$push':{"rating":rate}})

            # update user's ratings
            new_avg_rate_user = (user['avg_rating']*len(user['ratings']) + star)/(len(user['ratings']) + 1)
            db.users.update_one({"username":username},{'$set':{"avg_rating":new_avg_rate_user},'$push':{"ratings":item_id}})

            return redirect(url_for('item',item_id=item_id))

    return render_template('item.html',item = item)

#endpoint for adding item
@app.route('/add_item', methods=['GET','POST'])
def add_item():
    if request.method == 'POST':
        item = {
            "name":request.form['item_name'],
            "description":request.form['item_desc'],
            "category":request.form['item_category'],
            "price":int(request.form['item_price']),
            "seller": "bugra",
            "image":"",
            "size":"",
            "colour":"",
            "spec":"",
            "rating":[],
            "avg_rating":0.0,
            "reviews":[],
            "num_of_reviewers":0,
        }
        print(item)
        db.items.insert_one(item)
        return redirect(url_for('index'))
    return render_template('add_item.html')

@app.route('/add_user', methods=['GET','POST'])
def add_user():
    if request.method == 'POST':
        admin = None
        if 'admin_yes' in request.form:
            admin = True
        else:
            admin = False
        user = {
            "username":request.form['username'],
            "ratings":[],
            "avg_rating":0.0,
            "reviews":[],
            "admin":admin,
        }
        db.users.insert_one(user)
        return redirect(url_for('index'))
    return render_template('add_user.html')
