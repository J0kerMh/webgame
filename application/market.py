from flask import (
    Blueprint, flash, g, redirect, escape, request, session, url_for,jsonify
)

from bson.json_util import dumps
from application.utils import *
from application import mongo

bp = Blueprint('market', __name__)
@bp.route('/market/<opts>/<args1>/<args2>')
def do_opts1(opts,args1,args2):
    #sale_item
    #buy_item
    #cancel_sale
    #sale_list
    #change_sale
    #my_sale_list
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
                mongo.db.market.insert_one({'seller': name, 'item_name':item['item_name'],
                                        'category': item['category'], 'quality':item['quality'],
                                        'price':price})
                package['item'].remove(item)
                item['on_sale']= True
                package['item'].append(item)
                mongo.db.package.update({'name': name}, package)
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
                mongo.db.user.update({'name': seller['name']}, seller)
                mongo.db.user.update({'name': name}, user)
                mongo.db.package.update({'name': name}, package)
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
            new_package = check_package_is_full(name)
            if new_package:
                mongo.db.package.update({'name': name}, new_package)
                package = new_package
            package['item'].append({'item_name':item_name,'category':item['category'],
                                    'quality':item['quality'],'on_sale':False})
            mongo.db.user.update({'name':name}, user)
            mongo.db.package.update({'name':name}, package)
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
            mongo.db.market.update({'item_name': item_name}, item)
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
