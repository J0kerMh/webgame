import functools

from flask import (
    Blueprint, flash, g, redirect, escape, request, session, url_for,jsonify
)
from flask_sqlalchemy import Model
from json import dumps
import time
import silly
import random
from app_sql.utils import *
import app_sql  as app
db = app.db
User = app.User
Item = app.Item
WorkHistory= app.WorkHistory
TreasureHuntHistory = app.TreasureHuntHistory
bp = Blueprint('user', __name__)


@bp.route('/user')
# name = escape(session['name'])
def user_info():
    name = escape(session['name'])
    user = User.query.filter_by(name = name).first()
    package = []
    for item in user.item:
        package.append(item.to_list())
    var = {'name': user.name, 'package': package, 'luck': user.luck, 'strength': user.strength, 'gold': user.gold}
    return var
@bp.route('/user/opts', methods =['POST'])
def do_opts():
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
    json = request.form
    opts = json['opts']
    args = json['args']
    def show_info(args1):
        return user_info()

    def show_package(args1):
        user = User.query.filter_by(name=name).first()
        package = []
        for item in user.item:
            package.append(item.to_list())
        return package

    def open_market(args1):
        return redirect(url_for('/market'))

    def work(args1):
        his = WorkHistory.query.order_by(WorkHistory.timestamp.desc()).first()
        user = User.query.filter_by(name = name).first()

        if not his: #history is empty
            print('in here')
            db.session.add(WorkHistory(name,time.time()))
            user.gold=user.gold+user.strength
            db.session.commit()
            ret = 'You earned %d yuan today!' %(user.strength)
        elif time.time()-his.timestamp > day:
            print(time.time()-his.timestamp)
            db.session.add(WorkHistory(name,time.time()))
            user.gold=user.gold+user.strength
            db.session.commit()
            ret = 'You earned %d yuan today!' % (user.strength)
        else:
            ret = 'You can only work once a day!'
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def random_item(name):
        item_name = silly.name()
        if (random.randint(0, 9) % 2):
            category = 'tool'
        else:
            category = 'decoration'
        luck = User.query.filter_by(name = name ).first().luck
        from app_sql.utils import weight
        weight = [j + (2 ** luck) for j in weight]
        quality = weighted_random(tuple(zip(reversed(range(1, 6)), weight)))
        # quality = weighted_random(weighted_item)
        return Item(name,item_name,category,quality,False,False)


    def treasure_hunt(args1):
        #TODO checkout the package is full
        his = TreasureHuntHistory.query.order_by(TreasureHuntHistory.timestamp.desc()).first()
        user = User.query.filter_by(name=name).first()
        if check_package_is_full(name):
            ret = 'Failed! Your package is full!'
        else:
            if not his:  # history is empty
                new_item = random_item(name)
                db.session.add(new_item)
                db.session.add(TreasureHuntHistory(name, time.time()))
                db.session.commit()
                ret = 'You got a %s called %s with %d quality!' % (new_item.category,new_item.item_name,new_item.quality)
            elif time.time()-his.timestamp > day:
                new_item = random_item(name)

                db.session.add(new_item)
                db.session.add(TreasureHuntHistory(name, time.time()))
                db.session.commit()
                ret = 'You got a %s called %s with %d quality!' % (new_item.category, new_item.item_name, new_item.quality)
            else:

                ret = 'You can only hunt for treasure once a day!'
            # return(jsonify(time.time()-his['timestamp']))
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def adorn_tool(item_name):
        tool = Item.query.filter_by(owner = name, item_name = item_name, is_used= False).first()
        full = Item.query.filter_by(owner = name, item_name = item_name, is_used= True, category = 'tool').count() >= tool_limit
        user = User.query.filter_by(name=name).first()
        if not tool:
            ret = 'This tool is not existed!'
        else:
            if tool.on_sale:
                ret = 'This item is on sale, you can not adorn it!'
            else:
                if tool.category=='tool':
                    if not full: #tool is empyt
                        user.strength = user.strength + tool.quality
                        tool.is_used = True
                        db.session.commit()
                        ret = 'You adorn this tool successfully!'
                    else:
                        ret = 'You must take off your tool!'
                else:
                    ret = 'This is not a tool!'
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def adorn_decoration(item_name):
        decoration = Item.query.filter_by(owner=name, item_name=item_name, is_used=False).first()
        full = Item.query.filter_by(owner=name, item_name=item_name, is_used=True, category='decoration').count() >= decoration_limit
        user = User.query.filter_by(name=name).first()
        if not decoration:
            ret = 'This decoration is not existed!'
        else:
            if decoration.on_sale:
                ret = 'This item is on sale, you can not adorn it!'
            else:
                if decoration.category=='decoration':
                    if not full: #tool is empyt #TODO limit number of decoration
                        user.luck = user.luck + decoration.quality
                        decoration.is_used = True
                        db.session.commit()
                        ret = 'You adorn this decoration successfully!'
                    else:
                        ret = 'You must take off your decoration!'
                else:
                    ret = 'This is not a decoration!'
        resp = jsonify(ret)
        resp.status_code = 200
        return resp

    def take_off_tool(item_name):
        tool = Item.query.filter_by(owner=name, item_name=item_name, is_used=False, category='tool').first()
        full = Item.query.filter_by(owner=name, item_name=item_name, is_used=True, category='tool').count() >= tool_limit
        user = User.query.filter_by(name=name).first()

        if tool:
            tool.is_used=False
            user.strength = user.strength - tool.quality
            db.session.commit()
            ret = 'You take off this tool successfully!'
        else:
            ret = 'This tool is not existed!'
        resp = jsonify(ret)
        resp.status_code = 200
        return  resp

    def take_off_decoration(item_name):
        decoration = Item.query.filter_by(owner=name, item_name=item_name, is_used=False, category='decoration').first()
        user = User.query.filter_by(name=name).first()

        if decoration:
            decoration.is_used = False
            user.luck = user.luck - decoration.quality
            ret = 'You take off this decoration successfully!'
        else:
            ret = 'This decoration is not existed!'
        resp = jsonify(ret)
        resp.status_code = 200
        return  resp

    #do options
    return eval(opts)(args)