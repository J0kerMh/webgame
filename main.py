from app import app, mongo, day, weight, package_limit
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import jsonify, request,redirect, url_for, session, escape, flash
from werkzeug.security import generate_password_hash, check_password_hash
import time
import datetime
import silly
import random
from utils import weighted_random
from operator import methodcaller
#TODO checkout session

def check_package_is_full(name):
    package = mongo.db.package.find_one({'name': name})
    item_list = package['item']
    item_num = len(package['item'])
    if item_num == package_limit:
        new_item_list = sorted(item_list, key = lambda k: k['quality'])
        for item in package['item']:
            if not item['on_sale']:
                package['item'].remove(item)
                return  package
    return {}



@app.route('/')
def index():
    if 'name' in session:
        return 'Logged in as %s' % escape(session['name'])
    return 'You are not logged in'

@app.route('/signup', methods=['POST'])
def add_user():
    json = request.json
    name = json['name']
    F_pwd = json['F_pwd']
    S_pwd = json['S_pwd']
    if F_pwd != S_pwd:
        return jsonify("Inconsistent passwords!")
    if name and F_pwd and S_pwd and request.method == 'POST':
        if mongo.db.user.find_one({'name': name}):
            return  jsonify("User name id existed!")
        hashed_pwd = generate_password_hash(F_pwd)
        mongo.db.user.insert_one({'name': name, 'pwd': hashed_pwd, 'gold': 0, 'decoration':[], 'tool': [],
                                       'luck': 0, 'strength': 1})
        mongo.db.package.insert_one({'name':name, 'item': []})
        resp = jsonify('User added successfully!')
        resp.status_code = 200
        return resp
    else:
        return not_found()

@app.route('/login', methods=['POST'])
def login():
    json = request.json
    name = json['name']
    pwd = json['pwd']
    if name and pwd and request.method == 'POST':
        user = mongo.db.user.find_one({'name': name})
        if user is None:
            ret = 'Invalid username!'
        elif not check_password_hash(user['pwd'], pwd):
            ret = 'Invalid password!'
        else:
            session['name'] = name
            ret = 'Login successfully!'
            resp = jsonify(ret)
            resp.status_code = 200
            return resp
    else:
        return not_found()

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    # session.popitem('name')
    session.pop('name', None)
    ret = 'You have logout !'
    resp = jsonify(ret)
    resp.status_code = 200
    redirect(url_for('login'))
    return resp



@app.route('/user')
# name = escape(session['name'])
def user_info():
    name = escape(session['name'])
    user = mongo.db.user.find_one({'name': name})
    resp = dumps(user)
    return resp

@app.route('/user/<opts>/<args1>')
def do_opts(opts,args1):
    #work
    #treasure_hunt
    #show_package
    #open_market
    #show_info
    #adorn_tool
    #adorn_decoration
    #take_off_tool
    #take_off_decoration

    name = escape(session['name'])
    def show_info(args1):
        return user_info()

    def show_package(args1):
        package = mongo.db.package.find_one({'name': name})
        resp = dumps(package)
        return  resp

    def open_market(args1):
        return redirect(url_for('/market'))

    def work(args1):
        his = mongo.db.workHistory.find_one({'name': name}, sort=[('timestamp', -1)])
        user = mongo.db.user.find_one({'name': name})

        if not his: #history is empty
            mongo.db.workHistory.insert({'name': name, 'timestamp': time.time()})
            user['gold'] = user['gold']+user['strength']
            mongo.db.user.update({'name': name}, user)
            ret = 'You earned %d yuan today!' %(user['strength'])
        elif time.time()-his['timestamp'] > day:
            mongo.db.workHistory.insert({'name': name, 'timestamp': time.time()})
            user['gold'] = user['gold'] + user['strength']
            mongo.db.user.update({'name': name}, user)
            ret = 'You earned %d yuan today!' % (user['strength'])
        else:
            ret = 'You can only hunt for treasure once a day!'
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def random_item():
        item_name = silly.name()
        if (random.randint(0, 9) % 2):
            category = 'tool'
        else:
            category = 'decoration'
        luck = mongo.db.user.find_one({'name': name})['luck']
        from app import weight
        weight = [j + (2 ** luck) for j in weight]
        quality = weighted_random(tuple(zip(reversed(range(1, 6)), weight)))
        # quality = weighted_random(weighted_item)
        return {'item_name': item_name, 'category': category, 'quality': quality, 'on_sale': False}


    def treasure_hunt(args1):
        #TODO checkout the package is full
        his = mongo.db.treasureHuntHistory.find_one({'name': name},sort=[('timestamp', -1)])
        package = mongo.db.package.find_one({'name': name})
        if not his:  # history is empty
            ritem = random_item()
            package['item'].append(ritem)
            # print(package)
            mongo.db.package.update({'name': name}, package)
            mongo.db.treasureHuntHistory.insert({'name': name, 'timestamp': time.time()})
            ret = 'You got a %s called %s with %d quality!' % (ritem['category'], ritem['item_name'], ritem['quality'])
        elif time.time()-his['timestamp'] > day:
            mongo.db.treasureHuntHistory.insert({'name': name, 'timestamp': time.time()})
            ritem = random_item()
            package['item'].append(ritem)
            mongo.db.package.update({'name': name}, package)
            ret = 'You got a %s called %s with %d quality!' % (ritem['category'], ritem['item_name'], ritem['quality'])
        else:

            ret = 'You can only hunt for treasure once a day!'
            # return(jsonify(time.time()-his['timestamp']))
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def adorn_tool(item_name):
        tool = mongo.db.package.find_one({'name': name}, {'_id': 0, 'item': {"$elemMatch": {'item_name':item_name}}})
        user = mongo.db.user.find_one({'name': name})
        package = mongo.db.package.find_one({'name':name})
        # return dumps(tool)
        if not tool:
            ret = 'This tool is not existed!'
        else:
            tool = tool['item'][0]
            if tool['on_sale']:
                ret = 'This item is on sale, you can not adorn it!'
            else:
                if tool['category']=='tool':
                    if not user['tool']: #tool is empyt
                        user['tool'].append(tool)
                        mongo.db.user.update({'name': name}, user)
                        package['item'].remove(tool)
                        mongo.db.package.update({'name': name}, package)
                        ret = 'You adorn this tool successfully!'
                    else:
                        ret = 'You must take off your tool!'
                else:
                    ret = 'This is not a tool!'
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def adorn_decoration(item_name):
        decoration = mongo.db.package.find_one({'name': name}, {'_id': 0, 'item': {"$elemMatch": {'item_name':item_name}}})
        user = mongo.db.user.find_one({'name': name})
        package = mongo.db.package.find_one({'name': name})
        if not decoration:
            ret = 'This decoration is not existed!'
        else:
            decoration = decoration['item'][0]
            if decoration['on_sale']:
                ret = 'This item is on sale, you can not adorn it!'
            else:
                if decoration['category']=='decoration':
                    if not user['decoration']: #tool is empyt #TODO limit number of decoration
                        user['decoration'].append(decoration)
                        mongo.db.user.update({'name': name}, user)
                        package['item'].remove(decoration)
                        mongo.db.package.update({'name': name}, package)
                        ret = 'You adorn this decoration successfully!'
                    else:
                        ret = 'You must take off your decoration!'
                else:
                    ret = 'This is not a decoration!'
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def take_off_tool(item_name):
        user = mongo.db.user.find_one({'name': name})
        package = mongo.db.package.find_one({'name': name})
        tool = user['tool'][0]#TODO type of tool set to dict instead of list
        if item_name == tool['item_name']:
            user['tool'].remove(tool)
            mongo.db.user.update({'name': name}, user)
            package['item'].append(tool)
            #TODO if the package is full
            mongo.db.package.update({'name': name}, package)
            ret = 'You take off this tool successfully!'
        else:
            ret = 'This tool is not existed!'
        resp = jsonify(ret)
        resp.status_code = 200
        return  resp

    def take_off_decoration(item_name):
        user = mongo.db.user.find_one({'name': name})
        package = mongo.db.package.find_one({'name': name})
        # return dumps(user)
        decoration = user['decoration'][0]#TODO find by item_name
        if item_name == decoration['item_name']:
            user['decoration'].remove(decoration)
            mongo.db.user.update({'name': name}, user)
            package['item'].append(decoration)
            # TODO if the package is full
            mongo.db.package.update({'name': name}, package)
            ret = 'You take off this decoration successfully!'
        else:
            ret = 'This decoration is not existed!'
        resp = jsonify(ret)
        resp.status_code = 200
        return  resp

    #do options
    return eval(opts)(args1)

@app.route('/market/<opts>/<args1>/<args2>')
def do_opts(opts,args1,args2):
    #sale_item
    #buy_item
    #cancel_sale
    #sale_list
    #change_sale
    name = escape(session['name'])
    def sale_item(item_name, price):
        item = mongo.db.package.find_one({'name': name}, {'_id': 0, 'item': {"$elemMatch": {'item_name':item_name}}})
        package = mongo.db.package.find_one({'name': name})

        if not item:
            ret = 'This item is not existed!'
        else:
            item = item['item'][0]
            if item['on_sale']:
                ret = 'This item is on sale!'
            else:
                mongo.db.market.insert({'seller': name, 'item_name':item['item_name'],
                                        'category': item['category'], 'quality':item['quality'],
                                        'price':price})
                package['item'].remove(item)
                item['on_sale']= True
                package['item'].append(item)
                mongo.db.package.update_one({'name': name}, package)
                ret = 'This item is on shelf!'
        resp = jsonify(ret)
        resp.status_code = 200
        return  resp

    def buy_item(item_name, args2):
        item = mongo.db.market.find_one({'item_name':item_name})
        user = mongo.db.user.find_one({'name': name})
        package = mongo.db.package.find_one({'name': name})
        if not item:
            ret = 'This item is not existed!'
        else:
            if user['gold']>=item['price']:
                seller = mongo.db.user.find_one({'name':item['seller']})
                seller['gold'] = seller['gold'] + item['price']
                user['gold'] = user['gold'] - item['price']
                package['item'].append({'item_name': item['item_name'], 'category': item['category']
                                        , 'quality': item['quality'], 'on_sale': False})
                mongo.db.user.update_one({'name': seller['name']}, seller)
                mongo.db.user.update_one({'name': name}, user)
                mongo.db.package.update_one({'name': name}, package)
                mongo.db.market.delete_one({'item_name':item_name})
                ret = 'You buy this item!'
            else:
                ret = 'You do not have enough gold.'
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def cancel_sale(item_name, args2):
        user = mongo.db.user.find_one({'name':name})
        package = mongo.db.package.find_one({'name': name})
        item = mongo.db.market.find_one({'item_name':item_name})
        if not item:
            ret = 'This item is not existed!'
        else:
            #TODO The package is full
            user['gold'] = user['gold'] + item['price']
            package['item'].append({'item_name':item_name,'category':item['category'],
                                    'quality':item['quality'],'on_sale':False})
            mongo.db.user.update_one({'name':name}, user)
            mongo.db.package.update_one({'name':name}, package)
            mongo.db.market.delete_one({'item_name':item_name})
            ret = 'You successfully cancelled the sale of this item!'
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def change_sale(item_name, new_price):
        item = mongo.db.market.find_one({'item_name': item_name})
        if not item:
            ret = 'This item is not existed!'
        else:
            item['price'] = new_price
            mongo.db.market.update_one({'item_name': item_name}, item)
            ret = 'You change the price of item to %d!'%(new_price)
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def my_sale_list(args1, args2):
        item_list = mongo.db.find({'seller': name})
        return dumps(item_list)

    def sale_list(args1, args2):
        # Excluding current user
        item_list = mongo.db.find({'seller':{"$ne":name}})
        return dumps(item_list)


    # do options
    return eval(opts)(args1,args2)

@app.route('/users')
def users():
    users = mongo.db.user.find()
    resp = dumps(users)
    return resp


@app.route('/user/<id>')
def user(id):
    user = mongo.db.user.find_one({'_id': ObjectId(id)})
    resp = dumps(user)
    return resp


@app.route('/update', methods=['PUT'])
def update_user():
    _json = request.json
    _id = _json['_id']
    _name = _json['name']
    _email = _json['email']
    _password = _json['pwd']
    # validate the received values
    if _name and _email and _password and _id and request.method == 'PUT':
        # do not save password as a plain text
        _hashed_password = generate_password_hash(_password)
        # save edits
        mongo.db.user.update_one({'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},
                                 {'$set': {'name': _name, 'email': _email, 'pwd': _hashed_password}})
        resp = jsonify('User updated successfully!')
        resp.status_code = 200
        return resp
    else:
        return not_found()


@app.route('/delete/<id>', methods=['DELETE'])
def delete_user(id):
    mongo.db.user.delete_one({'_id': ObjectId(id)})
    resp = jsonify('User deleted successfully!')
    resp.status_code = 200
    return resp


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


if __name__ == "__main__":
    app.run()
