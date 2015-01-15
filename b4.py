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

class UserPas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    pas = db.Column(db.String(40), unique=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(UserPas.id))
    mail = db.Column(db.String(60), unique=True)
    telnum = db.Column(db.String(20), unique=True)

#REST
@app.route('/api/rest_user',  methods=['GET', 'POST', 'PUT', 'DELETE'])
def rest_user():
    if request.method == 'GET':
        user_id = request.args.get('user_id', '')
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            return jsonify(telnum=user.telnum, mail=user.mail)
    if request.method == 'POST':
        username = request.args.get('username', '')
        pas = request.args.get('pas', '')
        telnum = request.args.get('telnum', '')
        mail = request.args.get('mail', '')
        
        user = UserPas.query.filter_by(username=username).first()
        testn = User.query.filter_by(telnum=telnum).first()
        testm = User.query.filter_by(mail=mail).first()
        if not (user or testn or testm):
            up = UserPas(username=username, pas=pas)
            db.session.add(up)
            db.session.commit()
            user = User(user_id=up.id, telnum=telnum, mail=mail)
            db.session.add(user)
            db.session.commit()
            return jsonify(telnum=user.telnum, mail=user.mail)
    if request.method == 'PUT':
        user_id = request.args.get('user_id', '')
        telnum = request.args.get('telnum', '')
        mail = request.args.get('mail', '')
        user = User.query.filter_by(user_id=user_id).first()
        #update
        if user:
            testn = User.query.filter_by(telnum=telnum).first()
            testm = User.query.filter_by(mail=mail).first()
            if telnum and (not testn):
                User.query.filter_by(user_id=user_id).update({'telnum': telnum})
            if mail and (not testm):
                User.query.filter_by(user_id=user_id).update({'mail': mail})
            db.session.commit()
            user = User.query.filter_by(user_id=user_id).first()
            return jsonify(telnum=user.telnum, mail=user.mail)
    if request.method == 'DELETE':
        user_id = request.args.get('user_id', '')
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            a = User.query.filter_by(user_id=user_id).delete()
            b = UserPas.query.filter_by(id=user_id).delete()
            db.session.commit()
            return jsonify(answer='Success')
    return jsonify(error='1')


if __name__ == '__main__':
    db.create_all()
    app.run(host='localhost', port=8006, debug=True)
    