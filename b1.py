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

@app.route('/api/types', methods=['GET', 'POST'])
def show_guns_by_type():
    if request.method == 'GET':
        pp = int(request.args.get('pp', 10))
        p = int(request.args.get('p', 1))
        
        count = db.session.query(WeaponType).count()

        if pp <= 0:
            pp = count
            max_page = 1
        else:
            max_page = int(math.ceil(count * 1.0 / pp))
            
        if (p < 1) or (p > max_page):
            p = max_page
        
        array = []
        types = WeaponType.query.offset((p-1)*pp).limit(pp).all()
        
        for t in types:
            key = {'id': t.id, 'name': t.name}
            array.append(key)
        output = {'elements': array, 'page': p, 'max_page': max_page, 'count': count}
        return json.dumps(output)
    if request.method == 'POST':
        name = request.args.get('name', '')
        wt = WeaponType.query.filter_by(name=name).first()
        if not wt:
            wt = WeaponType(name=name)
            db.session.add(wt)
            db.session.commit()
            return jsonify(id=wt.id, name=wt.name)
    return jsonify(error='1')

@app.route('/api/types/<int:type_id>', methods=['GET', 'PUT', 'DELETE'])
def show_type(type_id):
    if request.method == 'GET':
        wt = WeaponType.query.filter_by(id=type_id).first()
        if wt:
            return jsonify(id=wt.id, name = wt.name)
        return jsonify(error='not found :P')
    if request.method == 'PUT':
        wt = WeaponType.query.filter_by(id=type_id).first()
        if wt:
            name = request.args.get('name', '')
            testn = WeaponType.query.filter_by(name=name).first()
            if name and (not testn):
                WeaponType.query.filter_by(id=type_id).update({'name': name})
            db.session.commit()
            wt = WeaponType.query.filter_by(id=type_id).first()
            return jsonify(id=wt.id, name = wt.name)
    if request.method == 'DELETE':
        wt = WeaponType.query.filter_by(id=type_id).first()
        if wt:
            WeaponType.query.filter_by(id=type_id).delete()
            db.session.commit()
            return jsonify(answer='Success')
    return jsonify(error='1')
    
@app.route('/api/guns', methods=['GET', 'POST'])
def show_guns():
    if request.method == 'GET':
        pp = int(request.args.get('pp', 10))
        p = int(request.args.get('p', 1))
        
        count = db.session.query(Weapon).count()
        
        if pp <= 0:
            pp = count
            max_page = 1
        else:
            max_page = int(math.ceil(count * 1.0 / pp))
            
        if (p < 1) or (p > max_page):
            p = max_page
        
        array = []
        guns = Weapon.query.offset((p-1)*pp).limit(pp).all()
        #set paging
        for g in guns:
            key = {'id': g.id, 'name': g.name, 'type': g.type}
            array.append(key)
        output = {'elements': array, 'page': p, 'max_page': max_page, 'count': count}
        return json.dumps(output)
    if request.method == 'POST':
        name = request.args.get('name', '')
        type = int(request.args.get('type', ''))
        cost = int(request.args.get('cost', ''))
        w = Weapon.query.filter_by(name=name).first()
        if not w:
            w = Weapon(name=name, type=type, cost=cost)
            db.session.add(w)
            db.session.commit()
            return jsonify(id=w.id, name=w.name, type=w.type, cost=w.cost)
        
    return jsonify(error='1')

@app.route('/api/guns/<int:gun_id>', methods=['GET', 'PUT', 'DELETE'])
def show_gun(gun_id):
    if request.method == 'GET':
        g = Weapon.query.filter_by(id=gun_id).first()
        if g:
            return jsonify(id=g.id, name=g.name, type=g.type, cost=g.cost)
    if request.method == 'PUT':
        g = Weapon.query.filter_by(id=gun_id).first()
        if g:
            name = request.args.get('name', '')
            type = request.args.get('type', '')
            cost = request.args.get('cost', '')
            testn = Weapon.query.filter_by(name=name).first()
            if name and (not testn):
                Weapon.query.filter_by(id=gun_id).update({'name': name})
            if type:
                Weapon.query.filter_by(id=gun_id).update({'type': type})
            if cost:
                Weapon.query.filter_by(id=gun_id).update({'cost': cost})
            db.session.commit()
            g = Weapon.query.filter_by(id=gun_id).first()
            return jsonify(id=g.id, name=g.name, type=g.type, cost=g.cost)
    if request.method == 'DELETE':
        g = Weapon.query.filter_by(id=gun_id).first()
        if g:
            Weapon.query.filter_by(id=gun_id).delete()
            db.session.commit()
            return jsonify(answer='Success')
    return jsonify(error='1')


@app.route('/api/status',  methods=['GET', 'POST'])
def status():
    count = db.session.query(Weapon).count()
    answer = {'Guns count': count}
    return jsonify(answer)


@app.route('/load_some_data', methods=['GET', 'POST'])
def load_some_data():
    try:
        t1 = WeaponType(name='pistol')
        t2 = WeaponType(name='rifle')
        db.session.add(t1)
        db.session.commit()
        db.session.add(t2)
        db.session.commit()
        pid = WeaponType.query.filter_by(name='pistol').first()
        rid = WeaponType.query.filter_by(name='rifle').first()

        for i in range(1, 6):
            n = "Colt " + str(i*2) + "'"
            w = Weapon(name=n, type=pid.id, cost = i * 1000)
            db.session.add(w)
            db.session.commit()
        
        for i in range(2, 8):
            n = "A Gun " + str(i) + "'"
            w = Weapon(name=n, type=pid.id, cost = i * 100)
            db.session.add(w)
            db.session.commit()

        for i in range(4, 10):
            n = "Desert Eagle " + str(i*5) + "'"
            w = Weapon(name=n, type=pid.id, cost = i * 1500)
            db.session.add(w)
            db.session.commit()
        
        for i in range(7, 12):
            n = "Smoked barrel " + str(i*3) + "'"
            w = Weapon(name=n, type=rid.id, cost = i * 800)
            db.session.add(w)
            db.session.commit()
            
        for i in range(9, 12):
            n = "Snipers rifle " + str(i*4) + "'"
            w = Weapon(name=n, type=rid.id, cost = i * 2000)
            db.session.add(w)
            db.session.commit()
    except:
        return 'Already loaded'
    return 'Success'


if __name__ == '__main__':
    db.create_all()
    app.run(host='localhost', port=8003, debug=True)
'''    
GET - получение модельки
POST - добавление модельки
PUT - обновление
DELETE - удаление

GET /guns?id=1
GET /guns?idlist=1;2;3;4;5;6;

request.args.get('idlist').split(';')
GET - получить список
POST - добавление
PUT - обновление
DELETE - удаление

Добавить Favorite
'''