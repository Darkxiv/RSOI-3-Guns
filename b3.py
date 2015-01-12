# coding: utf-8

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

class WeaponType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True)

class Weapon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True)
    type = db.Column(db.Integer, db.ForeignKey(WeaponType.id))
    weapontype = db.relationship('WeaponType')
    cost = db.Column(db.Integer)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    pas = db.Column(db.String(40), unique=False)
    mail = db.Column(db.String(60), unique=True)
    telnum = db.Column(db.String(20), unique=True)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    gun_id = db.Column(db.Integer, db.ForeignKey(Weapon.id))


@app.route('/api/favorites', methods=['GET', 'POST'])
def show_favorites():
    if request.method == 'GET':
        user_id = request.args.get('user_id', '')
        pp = int(request.args.get('pp', 10))
        p = int(request.args.get('p', 1))
        
        if user_id:
            count = db.session.query(Favorite).filter_by(user_id=user_id).count()
        else:
            count = db.session.query(Favorite).count()
        
        if pp <= 0:
            pp = count
            max_page = 1
        else:
            max_page = int(math.ceil(count * 1.0 / pp))
            
        if (p < 1) or (p > max_page):
            p = max_page
        
        array = []
        if user_id:
            fav = Favorite.query.filter_by(user_id=user_id).offset((p-1)*pp).limit(pp).all()
        else:
            fav = Favorite.query.offset((p-1)*pp).limit(pp).all()
        #set paging
        for f in fav:
            key = {'id': f.id, 'gun_id': f.gun_id}
            array.append(key)
        output = {'elements': array, 'page': p, 'max_page': max_page, 'count': count}
        return json.dumps(output)
    if request.method == 'POST':
        user_id = request.args.get('user_id', '')
        gun_id = request.args.get('gun_id', '')
        f = Favorite.query.filter_by(user_id=user_id, gun_id=gun_id).first()
        if not f:
            f = Favorite(user_id=user_id, gun_id=gun_id)
            db.session.add(f)
            db.session.commit()
            return jsonify(id=f.id, user_id=f.user_id, gun_id=f.gun_id)
    return jsonify(error='1')

@app.route('/api/favorites/<int:fid>', methods=['GET', 'PUT', 'DELETE'])
def show_favorite(fid):
    if request.method == 'GET':
        f = Favorite.query.filter_by(id=fid).first()
        if f:
            return jsonify(id=f.id, user_id=f.user_id, gun_id=f.gun_id)
    if request.method == 'PUT':
        f = Favorite.query.filter_by(id=fid).first()
        if f:
            user_id = request.args.get('user_id', '')
            gun_id = request.args.get('gun_id', '')
            if user_id:
                Favorite.query.filter_by(id=fid).update({'user_id': user_id})
            if gun_id:
                Favorite.query.filter_by(id=fid).update({'gun_id': gun_id})
            db.session.commit()
            f = Favorite.query.filter_by(id=fid).first()
            return jsonify(id=f.id, user_id=f.user_id, gun_id=f.gun_id)
    if request.method == 'DELETE':
        f = Favorite.query.filter_by(id=fid).first()
        if f:
            f = Favorite.query.filter_by(id=fid).delete()
            db.session.commit()
            return jsonify(answer='Success')
    return jsonify(error='1')


@app.route('/api/favorites_by_user_gun', methods=['GET', 'POST'])
def favorite_by_user_gun():
    user_id = request.args.get('user_id', '')
    gun_id = request.args.get('gun_id', '')
    f = Favorite.query.filter_by(user_id=user_id, gun_id=gun_id).first()
    if f:
        return jsonify(id=f.id, user_id=f.user_id, gun_id=f.gun_id)
    return jsonify(error='1')

if __name__ == '__main__':
    db.create_all()
    app.run(host='localhost', port=8005, debug=True)
