from datetime import datetime, timedelta
from flask import Flask
from flask import session, request
from flask import render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth2Provider
import urllib, urllib2, base64, json
import json, math

app = Flask(__name__)
app.debug = True

#
#   WORK WITH SESSION
#
# NEED TO MAKE GETTING OF USER_ID BY COOKIE (SID)

#
#   REST SESSION
#

def getJSONdata(url, method):
    if method == 'GET':
        req = urllib2.Request(url)
        resp = urllib2.urlopen(req)
        answ = json.loads(resp.read())
    else:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(url)
        req.get_method = lambda: method
        resp = opener.open(req)
        answ = json.loads(resp.read())
    if not ('error' in answ):
        return answ
    return None

def get_session(sid):
    url = 'http://localhost:8002/api/rest_session?sid=' + sid
    return getJSONdata(url, 'GET')

def reg_session(user_id):
    url = 'http://localhost:8002/api/rest_session?user_id=' + str(user_id)
    return getJSONdata(url, 'POST')

def update_session(sid):
    url = 'http://localhost:8002/api/rest_session?sid=' + sid
    return getJSONdata(url, 'PUT')

def delete_session(sid):
    url = 'http://localhost:8002/api/rest_session?sid=' + sid
    return getJSONdata(url, 'DELETE')


@app.route('/api/rest_session', methods=['GET', 'POST', 'PUT', 'DELETE'])
def rest_session():
    if request.method == 'GET':
        sid = request.args.get('sid', '')
        a = get_session(sid)
        if a:
            return jsonify(a)
    if request.method == 'POST':
        user_id = request.args.get('user_id', '')
        a = reg_session(user_id)
        if a:
            return jsonify(a)
    if request.method == 'PUT':
        sid = request.args.get('sid', '')
        a = update_session(sid)
        if a:
            return jsonify(a)
    if request.method == 'DELETE':
        sid = request.args.get('sid', '')
        a = delete_session(sid)
        if a:
            return jsonify(a)
    return jsonify(error='1')

#
#   REST USER
#

def get_user(user_id):
    url = 'http://localhost:8006/api/rest_user?user_id=' + str(user_id)
    return getJSONdata(url, 'GET')

def reg_user(username, pas, telnum, mail):
    url = 'http://localhost:8006/api/rest_user?username=' + username + '&pas=' + pas + '&telnum=' + telnum + '&mail=' + mail
    return getJSONdata(url, 'POST')

def update_user(user_id, telnum, mail):
    url = 'http://localhost:8006/api/rest_user?user_id=' + str(user_id) + '&telnum=' + telnum + '&mail=' + mail
    return getJSONdata(url, 'PUT')

def delete_user(user_id):
    url = 'http://localhost:8006/api/rest_user?user_id=' + str(user_id)
    return getJSONdata(url, 'DELETE')

#
# NEED TO MAKE PRIVATE METHODS FOR LOGIN (and POST)
#

def get_user_id(request):
    sid = request.args.get('sid', '')
    access = get_session(sid)
    if access:
        expires = datetime.strptime(access['expires'], "%a, %d %b %Y %H:%M:%S %Z")
        if expires > datetime.utcnow():
            access = update_session(sid)
            if access:
                return access['id'], sid
    return (None, None)


@app.route('/api/rest_user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def rest_user():
    if request.method != 'POST':
        user_id, sid = get_user_id(request)
        if not user_id:
            return jsonify(error='0')
    if request.method == 'GET':
        u = get_user(user_id)
        if u:
            return jsonify(u)
    if request.method == 'POST':
        username = request.args.get('username', '')
        pas = request.args.get('pas', '')
        telnum = request.args.get('telnum', '')
        mail = request.args.get('mail', '')
        u = reg_user(username, pas, telnum, mail)
        if u:
            return jsonify(u)
    if request.method == 'PUT':
        telnum = request.args.get('telnum', '')
        mail = request.args.get('mail', '')
        u = update_user(user_id, telnum, mail)
        if u:
            return jsonify(u)
    if request.method == 'DELETE':
        a = delete_user(user_id)
        if a:
            a = delete_session(sid)
            if a:
                return jsonify(a)
    return jsonify(error='1')
    
#
#   BACKEND I
#

@app.route('/api/status',  methods=['GET', 'POST'])
def status():
    url = 'http://localhost:8003/api/status'
    req = urllib2.Request(url)
    resp = urllib2.urlopen(req)
    return resp.read()

#
#   REST WEAPON
#


def get_weapon(gun_id):
    url = 'http://localhost:8003/api/guns/' + str(gun_id)
    return getJSONdata(url, 'GET')

def get_weapons(p, pp):
    url = 'http://localhost:8003/api/guns?pp=' + str(pp) + '&p=' + str(p)
    return getJSONdata(url, 'GET')

def reg_weapon(name, type, cost):
    url = 'http://localhost:8003/api/guns?name=' + name + '&type=' + str(type) + '&cost=' + str(cost)
    return getJSONdata(url, 'POST')

def update_weapon(gun_id, name, type, cost):
    url = 'http://localhost:8003/api/guns/' + str(gun_id) + '?name=' + name + '&type=' + str(type) + '&cost=' + str(cost)
    return getJSONdata(url, 'PUT')

def delete_weapon(gun_id):
    url = 'http://localhost:8003/api/guns/' + str(gun_id)
    return getJSONdata(url, 'DELETE')


@app.route('/api/guns', methods=['GET', 'POST'])
def show_guns():
    user_id, sid = get_user_id(request)
    if not user_id:
        return jsonify(error='0')
    if request.method == 'GET':
        p = request.args.get('p','1')
        pp = request.args.get('pp','10')
        ws = get_weapons(p, pp)
        if ws:
            ws['elements'] = parse_weapons(user_id, ws['elements'])
            return jsonify(ws)
    if request.method == 'POST':
        name = request.args.get('name','')
        type = request.args.get('type','1')
        cost = request.args.get('cost','')
        w = reg_weapon(name, type, cost)
        if w:        
            return jsonify(w)
    return jsonify(error='1')

@app.route('/api/guns/<int:gun_id>', methods=['GET', 'PUT', 'DELETE'])
def show_gun(gun_id):
    user_id, sid = get_user_id(request)
    if not user_id:
        return jsonify(error='0')
    if request.method == 'GET':
        w = get_weapon(gun_id)
        if w:
            w = parse_weapon(w)
            return jsonify(w)        
    if request.method == 'PUT':
        name = request.args.get('name','')
        type = request.args.get('type','')
        cost = request.args.get('cost','')
        w = update_weapon(gun_id, name, type, cost)
        if w:
            return jsonify(w)
    if request.method == 'DELETE':
        a = delete_weapon(gun_id)
        if a:
            return jsonify(a)
    return jsonify(error='1')

#
#   REST WEAPON TYPE
#


def get_weapon_type(types_id):
    url = 'http://localhost:8004/api/types/' + str(types_id)
    return getJSONdata(url, 'GET')

def get_weapon_types(p, pp):
    url = 'http://localhost:8004/api/types?pp=' + str(pp) + '&p=' + str(p)
    return getJSONdata(url, 'GET')

def reg_weapon_type(name):
    url = 'http://localhost:8004/api/types?name=' + name
    return getJSONdata(url, 'POST')

def update_weapon_type(types_id, name):
    url = 'http://localhost:8004/api/types/' + str(types_id) + '?name=' + name
    return getJSONdata(url, 'PUT')

def delete_weapon_type(types_id):
    url = 'http://localhost:8004/api/types/' + str(types_id)
    return getJSONdata(url, 'DELETE')


#
# NEED TO ADD COUNT OF WEAPON
#

@app.route('/api/types', methods=['GET', 'POST'])
def show_types():
    user_id, sid = get_user_id(request)
    if not user_id:
        return jsonify(error='0')
    if request.method == 'GET':
        p = request.args.get('p','1')
        pp = request.args.get('pp','10')
        wts = get_weapon_types(p, pp)
        if wts:        
            return jsonify(wts)
    if request.method == 'POST':
        name = request.args.get('name','')
        wt = reg_weapon_type(name)
        if wt:        
            return jsonify(wt)
    return jsonify(error='1')

@app.route('/api/types/<int:types_id>', methods=['GET', 'PUT', 'DELETE'])
def show_type(types_id):
    user_id, sid = get_user_id(request)
    if not user_id:
        return jsonify(error='0')
    if request.method == 'GET':
        wt = get_weapon_type(types_id)
        if wt:
            return jsonify(wt)        
    if request.method == 'PUT':
        name = request.args.get('name','')
        wt = update_weapon_type(types_id, name)
        if wt:
            return jsonify(wt)
    if request.method == 'DELETE':
        a = delete_weapon_type(types_id)
        if a:
            return jsonify(a)
    return jsonify(error='1')


#
#   REST FAVORITE
#

def get_favorite(fid):
    url = 'http://localhost:8005/api/favorites/' + str(fid)
    return getJSONdata(url, 'GET')

def get_favorite_by_user_gun(user_id, gun_id):
    url = 'http://localhost:8005/api/favorites_by_user_gun?user_id=' + str(user_id) + '&gun_id=' + str(gun_id)
    return getJSONdata(url, 'GET')

def get_favorites(user_id, p, pp):
    url = 'http://localhost:8005/api/favorites?pp=' + str(pp) + '&p=' + str(p) + '&user_id=' + str(user_id)
    return getJSONdata(url, 'GET')

def reg_favorite(user_id, gun_id):
    url = 'http://localhost:8005/api/favorites?user_id=' + str(user_id) + '&gun_id=' + str(gun_id)
    return getJSONdata(url, 'POST')

def update_favorite(fid, user_id, gun_id):
    url = 'http://localhost:8005/api/favorites/' + str(fid) + '&user_id=' + str(user_id) + '&gun_id=' + str(gun_id)
    return getJSONdata(url, 'PUT')

def delete_favorite(fid):
    url = 'http://localhost:8005/api/favorites/' + str(fid)
    return getJSONdata(url, 'DELETE')

#
# NEED TO CONVERT USER_ID AND GUN_ID TO 
#

@app.route('/api/favorites', methods=['GET', 'POST', 'DELETE'])
def show_favorites():
    user_id, sid = get_user_id(request)
    if not user_id:
        return jsonify(error='0')
    if request.method == 'GET':
        p = request.args.get('p','1')
        pp = request.args.get('pp','10')
        fs = get_favorites(user_id, p, pp)
        if fs:  
            fs['elements'] = parse_favorites(fs['elements'])
            return jsonify(fs)
    if request.method == 'POST':
        gun_id = request.args.get('gun_id','')
        f = reg_favorite(user_id, gun_id)
        if f:        
            return jsonify(f)
    if request.method == 'DELETE':
        gun_id = request.args.get('gun_id','')
        f = get_favorite_by_user_gun(user_id, gun_id)
        if f:
            fid = f['id']
            a = delete_favorite(fid)
            if a:
                return jsonify(a)
    return jsonify(error='1')

@app.route('/api/favorites/<int:fid>', methods=['GET', 'PUT', 'DELETE'])
def show_favorite(fid):
    user_id, sid = get_user_id(request)
    if not user_id:
        return jsonify(error='0')
    if request.method == 'GET':
        f = get_favorite(fid)
        if f:
            if f['user_id'] == user_id:
                return jsonify(f)        
    if request.method == 'PUT':
        gun_id = request.args.get('gun_id','')
        f = update_favorite(fid, user_id, gun_id)
        if f:
            return jsonify(f)
    if request.method == 'DELETE':
        f = get_favorite(fid)
        if f:
            if f['user_id'] == user_id:
                a = delete_favorite(fid)
                if a:
                    return jsonify(a)
    return jsonify(error='1')

#
#   OTHER METHODS
#

def get_user_by_login(username, pas):
    url = 'http://localhost:8006/api/user_by_login?username=' + username + '&pas=' + pas
    return getJSONdata(url, 'GET')

@app.route('/api/login')
def login():
    username = request.args.get('username', '')
    pas = request.args.get('pas', '')
    user = get_user_by_login(username, pas)
    if user:
        a = reg_session(user['id'])
        return jsonify(a)
    return jsonify(error='1')

def parse_weapon(w):
    wt = get_weapon_type(w['type'])
    if wt:
        w['type'] = wt['name']
    else:
        w['type'] = 'unknown'
    return w

def parse_weapons(user_id, ws):
    wts = get_weapon_types(1, -1)
    if wts:
        ewts = wts['elements']
        for w in ws:
            type = w['type']
            w['type'] = 'unknown'
            for wt in ewts:
                if wt['id'] == type:
                    w['type'] = wt['name']
                    break
            data = get_favorite_by_user_gun(user_id, w['id'])
            if data:
                w['favorite'] = True
            else:
                w['favorite'] = False
        return ws
    return jsonify(error='1')

def parse_favorites(fs):
    for f in fs:
        w = get_weapon(f['gun_id'])
        if w:
            w = parse_weapon(w)
            f['gun_name'] = w['name']
            f['gun_type'] = w['type']
        else:
            f['gun_name'] = 'unknown'
            f['gun_type'] = 'unknown'
    return fs

if __name__ == '__main__':
    app.run(host='localhost', port=8001, debug=True)
