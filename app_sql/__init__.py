import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()
def create_app(test_config=None):
    application = Flask(__name__)
    application.config.from_mapping(
        SECRET_KEY='yhma',
        # MONGO_URI ='mongodb://localhost:27017/webgame',
        SQLALCHEMY_DATABASE_URI = 'mysql://root:joker@127.0.0.1/webgame',
        SQLALCHEMY_TRACK_MODIFICATIONS = 'False'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        application.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        application.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(application.instance_path)
    except OSError:
        pass



    db.init_app(application)


    @application.route('/hello')
    def hello():
        db.create_all()
        return 'Hello, World!'


    # apply the blueprints to the application
    from app_sql import user, market, auth
    application.register_blueprint(user.bp)
    application.register_blueprint(auth.bp)
    # application.register_blueprint(market.bp)


    return application

class User(db.Model):
    __tablename__ = 'user'
    name = db.Column(db.String(30), unique=True, primary_key=True)
    pwd = db.Column(db.String(100), nullable=False)
    gold = db.Column(db.Integer, default=0)
    luck = db.Column(db.Integer, default=0)
    strength = db.Column(db.Integer, default=0)
    item = db.relationship('Item', backref='user', lazy=True)
    treasureHuntHistory = db.relationship('TreasureHuntHistory', backref='user', lazy = True)
    workHistory = db.relationship('WorkHistory', backref='user', lazy = True)
    my_sale = db.relationship('Market', backref = 'user', lazy = True)
    def __init__(self, name, pwd, gold, luck, strength):
        self.name = name
        self.pwd = pwd
        self.gold = gold
        self.luck = luck
        self.strength = strength

class Item(db.Model):
    __tablename__ = 'item'
    owner = db.Column(db.String(30), db.ForeignKey('user.name'))
    item_name = db.Column(db.String(30), unique=True, primary_key=True)
    category = db.Column(db.String(10), nullable=False)
    quality = db.Column(db.Integer, nullable=False)
    on_sale = db.Column(db.Boolean, default=False)
    is_used = db.Column(db.Boolean, default=False)
    def __init__(self, owner,item_name, category, quality, on_sale,is_used):
        self.item_name = item_name
        self.owner = owner
        self.category = category
        self.quality = quality
        self.on_sale = on_sale
        self.is_used = is_used
    def to_list(self):
        return [self.owner, self.item_name, self.category, self.quality, self.on_sale, self.is_used]
class TreasureHuntHistory(db.Model):
    __tablename__ = 'treasureHuntHistory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30),db.ForeignKey('user.name'))
    timestamp = db.Column(db.Float(2), nullable=False)
    def __init__(self, name , timestamp):
        self.name = name
        self.timestamp = timestamp

class WorkHistory(db.Model):
    __tablename__ = 'workHistory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30),db.ForeignKey('user.name'))
    timestamp = db.Column(db.Float(2), nullable=False)
    def __init__(self, name , timestamp):
        self.name = name
        self.timestamp = timestamp

class Market(db.Model):
    __tablename__ = 'market'
    pid = db.Column(db.Integer, primary_key=True)
    seller = db.Column(db.String(30),db.ForeignKey('user.name'), nullable=False)
    item_name = db.Column(db.String(30),db.ForeignKey('item.item_name'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    def __init__(self,  seller, item_name, price,quality):
        self.seller = seller
        self.item_name = item_name
        self.price = price



