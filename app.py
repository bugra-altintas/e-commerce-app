from flask import Flask, render_template, request, url_for, redirect, flash, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import json


app = Flask(__name__)

username = "bugraltintas"
password = "9B9mtXOpGtSx6FWa"

client = MongoClient("mongodb+srv://{}:{}@cluster0.mcjm34k.mongodb.net/?retryWrites=true&w=majority".format(username,password))

db = client.flask_db
todos = db.todos
users = db.users

app.secret_key = "secret"

def clear_all_ratings():
    # update all users' avg_rating field to 0 and ratings field to empty list
    users.update_many({},{'$set':{"ratings":[],"avg_rating":0.0}})
    # update all items' avg_rating field to 0 and rating field to empty list
    db.items.update_many({},{'$set':{"rating":[],"avg_rating":0.0}})

def clear_all_reviews():
    # update all users' reviews field to empty list
    users.update_many({},{'$set':{"reviews":[]}})
    # update all items' reviews field to empty list
    db.items.update_many({},{'$set':{"reviews":[]}})

def clear_all_users():
    # delete all users except admin
    users.delete_many({"username":{"$ne":"bugra"}})

def clear_all_items():
    db.items.delete_many({})


#endpoint for index page
@app.route('/', methods=('GET', 'POST'))
def index():
    all_items = db.items.find()
    return render_template('index.html',items=all_items)

#endpoint for login page
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username'] 
        record = users.find_one({'username': username})
        if record:
            #admin authentication
            if record['is_admin']:
                if record['password'] != request.form['password']:
                    return render_template('login.html')

            user = {
                "username":record['username'],
                "role":'admin' if record['is_admin'] else 'user',
                "_id":str(record['_id'])
            }
            session['user'] = user
            return redirect(url_for('index'))
        else:
            redirect(url_for('login'))
    return render_template('login.html')

#endpoint for logout
@app.route('/logout', methods=('GET', 'POST'))
def logout():
    session.pop('user',None)
    return redirect(url_for('index'))

#endpoint for category filtering
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
        # check if user is logged in
        if 'user' not in session:
            print("you are not logged in")
            return redirect(url_for('login'))
        
        user = db.users.find_one({"username":session['user']['username']})
        if 'review' in request.form:
            username = user['username'] # TODO: get username from session
            review = {
                "reviewer":username,
                "review":request.form['review'],
            }

            # if user has already reviewed this item, update review
            if username in [r['reviewer'] for r in item['reviews']]:
                db.items.update_one({"_id":ObjectId(item_id),"reviews.reviewer":username},{'$set':{"reviews.$.review":request.form['review']}})
                return redirect(url_for('item',item_id=item_id))
            # else add review
            else:
                db.items.update_one({"_id":ObjectId(item_id)},{'$push':{"reviews":review}})            
                return redirect(url_for('item',item_id=item_id))

            
        if 'rate' in request.form:
            username = user['username'] # TODO: get username from session
            star = float(request.form['rate'])
            rate = {
                "rater":username,
                "rate":star,
            }

            # if user has already rated this item, update rating
            if username in [r['rater'] for r in item['ratings']]:

                #get old rating,
                total = 0
                old_rating = 0
                for r in item['ratings']:
                    if r['rater'] == username:
                        old_rating = r['rate']
                    total += r['rate']
                avg = (total-old_rating+star) / (len(item['ratings']))
                
                db.items.update_one({"_id":ObjectId(item_id),"ratings.rater":username},{'$set':{"ratings.$.rate":star,"avg_rating":avg}})
                return redirect(url_for('item',item_id=item_id))
            # else add rating
            else:
                #update avg_rating of item
                total = 0
                for r in item['ratings']:
                    total += r['rate']
                total+=star
                avg = total / (len(item['ratings'])+1)
                db.items.update_one({"_id":ObjectId(item_id)},{'$push':{"ratings":rate},'$set':{"avg_rating":avg}})
                return redirect(url_for('item',item_id=item_id))
    return render_template('item.html',item = item)

#endpoint for adding item
@app.route('/add_item', methods=['GET','POST'])
def add_item():
    # check if user is logged in
    if 'user' not in session:
        print("you are not logged in")
        return redirect(url_for('login'))
    
    # check if user is admin
    if session['user']['role'] == 'user':
        print("you are not admin")
        return redirect(url_for('index'))

    if request.method == 'POST':
        category = request.form['item_category']
        item = None
        # if category is clothing, add size
        if category == "Clothing":
            item = {
                "name":request.form['item_name'],
                "description":request.form['item_desc'],
                "category":request.form['item_category'],
                "price":int(request.form['item_price']),
                "seller": request.form['item_seller'],
                "image":"",
                "size":request.form['item_size'],
                "color":request.form['item_color'],
                "ratings":[],
                "avg_rating":0.0,
                "reviews":[],
            }
        # if category is monitor, add spec
        elif category == "Monitor" or category == "Computer Components":
            item = {
                "name":request.form['item_name'],
                "description":request.form['item_desc'],
                "category":request.form['item_category'],
                "price":int(request.form['item_price']),
                "seller": request.form['item_seller'],
                "image":"",
                "spec":request.form['item_spec'],
                "ratings":[],
                "avg_rating":0.0,
                "reviews":[],
            }
        else:
            item = {
                "name":request.form['item_name'],
                "description":request.form['item_desc'],
                "category":request.form['item_category'],
                "price":int(request.form['item_price']),
                "seller": request.form['item_seller'],
                "image":"",
                "ratings":[],
                "avg_rating":0.0,
                "reviews":[],
            }
        
        db.items.insert_one(item)
    
        return redirect(url_for('index'))
    return render_template('add_item.html')

#endpoint for adding user
@app.route('/add_user', methods=['GET','POST'])
def add_user():
    if 'user' not in session:
        print("you are not logged in")
        return redirect(url_for('login'))
    
    # check if user is admin
    if session['user']['role'] == 'user':
        print("you are not admin")
        return redirect(url_for('index'))
    if request.method == 'POST':
        if db.users.find_one({"username":request.form['username']}):
            print("username already exists")
            return redirect(url_for('add_user'))
        admin = True if request.form['admin'] == 'true' else False
        user = {
            "username":request.form['username'],
            "password":request.form['password'] if admin else "",
            "is_admin":admin,
        }
        db.users.insert_one(user)
        return redirect(url_for('index'))
    return render_template('add_user.html')

#endpoint for removing item
@app.route('/remove_item',methods=['GET','POST'])
def remove_item():
    # check if user is logged in
    if 'user' not in session:
        print("you are not logged in")
        return redirect(url_for('login'))
    
    # check if user is admin
    if session['user']['role'] == 'user':
        print("you are not admin")
        return redirect(url_for('index'))

    items = db.items.find()

    if request.method == 'POST':
        if 'to_remove' in request.form:
            for item_id in request.form.getlist('to_remove'):
                # remove item
                db.items.delete_one({"_id":ObjectId(item_id)})
            return redirect(url_for('remove_item'))


    return render_template('remove_item.html',items=items)

#endpoint for removing user
@app.route('/remove_user',methods=['GET','POST'])
def remove_user():
    # check if user is logged in
    if 'user' not in session:
        print("you are not logged in")
        return redirect(url_for('login'))

    # check if user is admin
    if session['user']['role'] == 'user':
        print("you are not admin")
        return redirect(url_for('index'))

    users = db.users.find()

    if request.method == 'POST':
        for user_id in request.form.getlist('to_remove'):
            # check user is an admin
            user = db.users.find_one({"_id":ObjectId(user_id)})
            if user['is_admin'] == True:
                print("cannot remove admin")
                return redirect(url_for('remove_user'))

            # remove user from item's reviews and ratings
            items = db.items.find()
            for item in items:
                for review in item['reviews']:
                    if review['reviewer'] == user['username']:
                        db.items.update_one({"_id":ObjectId(item['_id'])},{'$pull':{"reviews":{"reviewer":user['username']}}})
                for rating in item['ratings']:
                    if rating['rater'] == user['username']:
                        #recalculate avg rating
                        old_rating = rating['rate']
                        total = 0
                        for rating in item['ratings']:
                            total += rating['rate']
                        avg = (total-old_rating) / (len(item['ratings'])-1) if len(item['ratings']) > 1 else 0.0
                        db.items.update_one({"_id":ObjectId(item['_id'])},{'$pull':{"ratings":{"rater":user['username']}},'$set':{"avg_rating":avg}})

            db.users.delete_one({"_id":ObjectId(user_id)})
        return redirect(url_for('remove_user'))

    return render_template('remove_user.html',users=users)

#endpoint for user page
@app.route('/user/<user_id>', methods=['GET'])
def user(user_id):
    # check if user is logged in
    if 'user' not in session:
        print("you are not logged in")
        return redirect(url_for('login'))

    user = db.users.find_one({"_id":ObjectId(user_id)})
    
    # find reviews of user
    reviews = []
    ratings = []
    total = 0.0
    ratings_count = 0
    items = db.items.find()
    for item in items:
        for review in item['reviews']:
            if review['reviewer'] == user['username']:
                review['item'] = item
                reviews.append(review)
        for rating in item['ratings']:
            if rating['rater'] == user['username']:
                total += rating['rate']
                ratings_count += 1
                #rating['item_id'] = str(item['_id'])
                #ratings.append(rating)
    avg_rating = total / ratings_count if ratings_count > 0 else 0.0
    return render_template('user.html',user=user,reviews=reviews,avg_rating=avg_rating)