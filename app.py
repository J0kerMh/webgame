from flask import Flask
from flask_pymongo import PyMongo
import time
app = Flask(__name__)
app.secret_key = "secret key"
app.config["MONGO_URI"] = "mongodb://localhost:27017/webgame"
mongo = PyMongo(app)
day = 600
package_limit = 10
# mongo.db.treasureHuntHistory.insert({'name': 'yhma', 'timestamp': time.time()})
# mongo.db.package.insert({''})
weight = []
w = 1
for i in range(5):
    w*=3
    weight.append(w)
