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

if __name__ == '__main__':
    db.create_all()
    app.run(host='localhost', port=8004, debug=True)