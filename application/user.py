import functools

from flask import (
    Blueprint, flash, g, redirect, escape, request, session, url_for,jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
# from application.__init__ import  mongo
from bson.json_util import dumps
import time
import silly
import random
from application.utils import *
from application import mongo


bp = Blueprint('user', __name__)

# @bp.before_app_request
# def load_logged_in_user():
#     if 'name' not in session:
#         # return 'Logged in as %s' % escape(session['name'])
#         return 'You are not logged in'

    # name = session.get('name')
    #
    # if name is None:
    #     g.name = None
    # else:
    #     g.name = name

@bp.route('/user')
# name = escape(session['name'])
def user_info():
    name = escape(session['name'])
    user = mongo.db.user.find_one({'name': name})
    resp = dumps(user)
    return resp

@bp.route('/user/<opts>/<args1>')
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
        from application.utils import weight
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
            new_package = check_package_is_full(name)
            if new_package:
                mongo.db.package.update({'name': name},new_package )
                package = new_package
            package['item'].append(ritem)
            # print(package)
            mongo.db.package.update({'name': name}, package)
            mongo.db.treasureHuntHistory.insert({'name': name, 'timestamp': time.time()})
            ret = 'You got a %s called %s with %d quality!' % (ritem['category'], ritem['item_name'], ritem['quality'])
        elif time.time()-his['timestamp'] > day:
            mongo.db.treasureHuntHistory.insert({'name': name, 'timestamp': time.time()})
            ritem = random_item()
            new_package = check_package_is_full(name)
            if new_package:
                mongo.db.package.update({'name': name}, new_package)
                package = new_package

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
            new_package = check_package_is_full(name)
            if new_package:
                mongo.db.package.update({'name': name}, new_package)
                package = new_package
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
            new_package = check_package_is_full(name)
            if new_package:
                mongo.db.package.update({'name': name}, new_package)
                package = new_package
            package['item'].append(decoration)
            mongo.db.package.update({'name': name}, package)
            ret = 'You take off this decoration successfully!'
        else:
            ret = 'This decoration is not existed!'
        resp = jsonify(ret)
        resp.status_code = 200
        return  resp

    #do options
    return eval(opts)(args1)
