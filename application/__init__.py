import os
from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()
def create_app(test_config=None):
    application = Flask(__name__)
    application.config.from_mapping(
        SECRET_KEY='yhma',
        MONGO_URI ='mongodb://localhost:27017/webgame'
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

    mongo.init_app(application)


    @application.route('/hello')
    def hello():
        return 'Hello, World!'


    # apply the blueprints to the application
    from application import user, market, auth
    application.register_blueprint(user.bp)
    application.register_blueprint(auth.bp)
    application.register_blueprint(market.bp)


    return application

