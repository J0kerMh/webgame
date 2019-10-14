import application
import os
from flask import Flask
from flask_pymongo import PyMongo


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='yhma',
        MONGO_URI ='mongodb://localhost:27017/webgame'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # mongo.init_app(application)


    @app.route('/hello')
    def hello():
        return 'Hello, World!'


    # apply the blueprints to the application
    from application import user, market, auth
    # app.register_blueprint(user.bp)
    app.register_blueprint(auth.bp)
    # application.register_blueprint(market.bp)


    return app

def create_mongo(app):
    return PyMongo(app)

app = create_app()

# bind to application package
application.app = app
application.mongo = create_mongo(app)