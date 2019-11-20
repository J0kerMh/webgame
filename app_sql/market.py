from flask import (
    Blueprint, flash, g, redirect, escape, request, session, url_for,jsonify
)

from bson.json_util import dumps
from app_sql.utils import *
import app_sql  as app
db = app.db
User = app.User
Item = app.Item
WorkHistory= app.WorkHistory
TreasureHuntHistory = app.TreasureHuntHistory
Market = app.Market
bp = Blueprint('market', __name__)
@bp.route('/market', methods = ['POST'])
def do_opts1():
    #sale_item
    #sale_item
    #buy_item
    #cancel_sale
    #sale_list
    #change_sale
    #my_sale_list
    name = escape(session['name'])
    json = request.json
    opts = json['opts']
    args1 = json['args1']
    args2 = json['args2']

    def sale_item(item_name, price):
        item = Item.query.filter_by(owner = name, item_name = item_name).first()

        if not item:
            ret = 'This item is not existed!'
        else:
            if item.is_used:
                ret = 'This item is used!'
            else:
                if item.on_sale:
                    ret = 'This item is on sale!'
                else:
                    db.session.add(Market(name,item_name,price))
                    item.on_sale=True
                    db.session.commit()
                    ret = 'This item is on shelf!'
        resp = jsonify(ret)
        resp.status_code = 200
        return  resp

    def buy_item(item_name, args2):
        market = Market.query.filter_by(item_name=item_name).first()
        item = Item.query.filter_by(item_name=item_name,on_sale = True).first()
        user = User.query.filter_by(name = name).first()
        if not market:
            ret = 'This item is not existed!'
        else:
            if check_package_is_full(name):
                ret = 'Failed! Your package is full!'
            else:
                if user.gold>=market.price:
                    seller = User.query.filter_by(name = market.seller).first()
                    seller.gold = seller.gold + market.price
                    user.gold = user.gold - market.price
                    item.on_sale= False
                    item.owner= name
                    db.session.delete(market)
                    db.session.commit()
                    ret = 'You buy this item!'
                else:
                    ret = 'You do not have enough gold.'
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def cancel_sale(item_name, args2):
        user = User.query.filter_by(name = name).first()
        market = Market.query.filter_by(item_name= item_name).first()
        if not market:
            ret = 'This item is not existed!'
        else:
            #TODO The package is full
            if check_package_is_full(name):
                ret = 'Failed! Your package is full!'
            else:
                user.gold = user.gold + market.price
                item = Item.query.filter_by(item_name = item_name).first()
                item.on_sale=False
                db.session.delete(market)
                db.session.commit()
                ret = 'You successfully cancelled the sale of this item!'
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def change_sale(item_name, new_price):
        market = Market.query.filter_by(item_name = item_name).first()
        if not market:
            ret = 'This item is not existed!'
        else:
            market.price = int(new_price)
            db.session.commit()
            ret = 'You change the price of item to %d!'%(new_price)
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def my_sale_list(args1, args2):
        item_list = User.query.filter_by(name = name).first().my_sale

        return dumps(item_list)

    def sale_list(args1, args2):
        # Excluding current user
        item_list = Market.query.filter(Market.seller!=name).all()
        return dumps(item_list)


    # do options
    return eval(opts)(args1,args2)
