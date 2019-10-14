from flask import (
    Blueprint, flash, g, redirect, escape, request, session, url_for,jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from bson.json_util import dumps
import time
import silly
import random
from application.utils import *
import application
mongo = application.mongo


bp = Blueprint('auth', __name__)
@bp.route('/')
def index():
    if 'name' in session:
        return 'Logged in as %s' % escape(session['name'])
    return 'You are not logged in'

@bp.route('/signup', methods=['POST'])
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

@bp.route('/login', methods=['POST'])
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


@bp.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


@bp.route('/logout')
def logout():
    # remove the username from the session if it's there
    # session.popitem('name')
    session.pop('name', None)
    ret = 'You have logout !'
    resp = jsonify(ret)
    resp.status_code = 200
    redirect(url_for('login'))
    return resp


