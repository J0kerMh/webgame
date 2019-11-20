from flask import (
    Blueprint, flash, g, redirect, escape, request, session, url_for,jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import Model
import app_sql  as app
db = app.db
User= app.User
bp = Blueprint('auth', __name__)
@bp.route('/')
def index():
    if 'name' in session:
        return 'Logged in as %s' % escape(session['name'])
    return 'You are not logged in'

@bp.route('/signup', methods=['POST'])
def add_user():
    json = request.form
    name = json['name']
    F_pwd = json['F_pwd']
    S_pwd = json['S_pwd']
    if F_pwd != S_pwd:
        return jsonify("Inconsistent passwords!")
    if name and F_pwd and S_pwd and request.method == 'POST':
        if User.query.filter_by(name = name).first():
            return  jsonify("User name is existed!")
        hashed_pwd = generate_password_hash(F_pwd)
        new_user = User(name,hashed_pwd,0,1,1)
        db.session.add(new_user)
        db.session.commit()
        resp = jsonify('User added successfully!')
        resp.status_code = 200
        return resp
    else:
        return jsonify("Post can not be empty!")


@bp.route('/login', methods=['POST'])
def login():
    json = request.form
    name = json['name']
    pwd = json['pwd']
    if name and pwd and request.method == 'POST':
        user = User.query.filter_by(name = name).first()
        if user is None:
            return 'Invalid username!'
        elif not check_password_hash(user.pwd, pwd):
            return 'Invalid password!'
        else:
            session['name'] = name
            ret = 'Login successfully!'
            resp = jsonify(ret)
            resp.status_code = 200
            return resp
    else:
        return jsonify("Post can not be empty!")


# @bp.errorhandler(404)
# def not_found(error=None):
#     message = {
#         'status': 404,
#         'message': 'Not Found: ' + request.url,
#     }
#     resp = jsonify(message)
#     resp.status_code = 404
#
#     return resp


@bp.route('/logout')
def logout():
    # remove the username from the session if it's there
    # session.popitem('name')
    session.pop('name', None)
    ret = 'You have logout !'
    resp = jsonify(ret)
    resp.status_code = 200
    # redirect(url_for('login'))
    return resp


