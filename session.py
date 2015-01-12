# coding: utf-8
# need to return error by try catch
# cascade delete to all table
from datetime import datetime, timedelta
from flask import Flask
from flask import session, request
from flask import render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth2Provider
import json, math

app = Flask(__name__, template_folder='templates')
app.debug = True
app.secret_key = 'secret'
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
})
db = SQLAlchemy(app)

SALT_LENGTH = 3
SESSION_EXPIRES = 100

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    pas = db.Column(db.String(40), unique=False)
    mail = db.Column(db.String(60), unique=True)
    telnum = db.Column(db.String(20), unique=True)


class Access(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id')
    )
    user = db.relationship('User')
    access_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)

    
#REST
@app.route('/api/rest_session',  methods=['GET', 'PUT', 'POST', 'DELETE'])
def reg_session():
    if request.method == 'GET':
        sid = request.args.get('sid', '')
        a = Access.query.filter_by(access_token=sid).first()
        if a:
            return jsonify(id=a.user_id, sid=a.access_token, expires=a.expires)
    if request.method == 'PUT':
        sid = request.args.get('sid', '')
        s = Access.query.filter_by(access_token=sid).first()
        if s:
            a = Access.query.filter_by(access_token=sid).update({'expires': datetime.utcnow() + timedelta(seconds=SESSION_EXPIRES)})
            db.session.commit()
            a = Access.query.filter_by(access_token=sid).first()
            return jsonify(id=a.user_id, sid=a.access_token, expires=a.expires)
    if request.method == 'POST':
        user_id = request.args.get('user_id', '')
        u = User.query.filter_by(id=user_id).first()
        if u:
            a = Access(user_id=u.id, access_token=gen_salt(SALT_LENGTH), expires=datetime.utcnow() + timedelta(seconds=SESSION_EXPIRES))
            db.session.add(a)
            db.session.commit()
            return jsonify(id=a.user_id, sid=a.access_token)
    if request.method == 'DELETE':
        sid = request.args.get('sid', '')
        s = Access.query.filter_by(access_token=sid).first()
        if s:
            Access.query.filter_by(access_token=sid).delete()
            db.session.commit()
            return jsonify(answer='Success')
    return jsonify(error='1')

if __name__ == '__main__':
    db.create_all()
    app.run(host='localhost', port=8002, debug=True)
    
