from datetime import datetime, timedelta
from flask import Flask
from flask import session, request, url_for
from flask import render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth2Provider
import urllib, urllib2, base64, json
import json, math

app = Flask(__name__)
app.debug = True
app.secret_key = 'AdventureTime'

def error_handler(msg):  
    if msg['error'] == '0':
        if 'sid' in session:
            delete_session(session['sid'])
            session.clear()
        return 'Authorization error. Your session will be cleared.'
    if msg['error'] == '1':
        return 'Internal service error'
    return 'Unknow error'


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
    return answ

def delete_session(sid):
    url = 'http://localhost:8001/api/rest_session?sid=' + sid
    answ = getJSONdata(url, 'DELETE')
    if 'error' in answ:
        return (error_handler(answ), 1)
    return (answ, 0)

def get_user(sid):
    url = 'http://localhost:8001/api/rest_user?sid=' + sid
    answ = getJSONdata(url, 'GET')
    if 'error' in answ:
        return (error_handler(answ), 1)
    return (answ, 0)

def get_gun(id, sid):
    url = 'http://localhost:8001/api/guns/' + str(id) + '?sid=' + sid
    answ = getJSONdata(url, 'GET')
    if 'error' in answ:
        return (error_handler(answ), 1)
    return (answ, 0)

def get_guns(sid, p, pp):
    url = 'http://localhost:8001/api/guns?sid=' + sid + '&p=' + str(p) + '&pp=' + str(pp)
    answ = getJSONdata(url, 'GET')
    if 'error' in answ:
        return (error_handler(answ), 1)
    return (answ, 0)

def get_type(id, sid):
    url = 'http://localhost:8001/api/types/' + str(id) + '?sid=' + sid
    answ = getJSONdata(url, 'GET')
    if 'error' in answ:
        return (error_handler(answ), 1)
    return (answ, 0)

def get_types(sid, p, pp):
    url = 'http://localhost:8001/api/types?sid=' + sid + '&p=' + str(p) + '&pp=' + str(pp)
    answ = getJSONdata(url, 'GET')
    if 'error' in answ:
        return (error_handler(answ), 1)
    return (answ, 0)

def get_favorites(sid, p, pp):
    url = 'http://localhost:8001/api/favorites?sid=' + sid + '&p=' + str(p) + '&pp=' + str(pp)
    answ = getJSONdata(url, 'GET')
    if 'error' in answ:
        return (error_handler(answ), 1)
    return (answ, 0)

def get_user_by_login(username, pas):
    url = 'http://localhost:8001/api/login?username=' + username + '&pas=' + pas
    answ = getJSONdata(url, 'GET')
    if 'error' in answ:
        return (error_handler(answ), 1)
    session['sid'] = answ['sid']
    answ, error = get_user(session['sid']) 
    return (answ, error)


@app.route('/', methods=('GET', 'POST'))
def home():
    if 'sid' in session:
        data, error = get_user(session['sid'])
        if error:
            return render_template('msg.html', msg=data)
        return render_template('menu.html', user=data)
    return render_template('menu.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        pas = request.form.get('pas')
        data, error = get_user_by_login(username, pas)
        if error:
            return render_template('msg.html', msg=data)
        return render_template('menu.html', user=data)
    return render_template('login.html')


@app.route('/register', methods=('GET', 'POST'))
def reg_user():
    data = ''
    if 'sid' in session:
        data, error = get_user(session['sid'])
        if error:
            return render_template('msg.html', msg=data)

    if request.method == 'GET':
        return render_template('register.html', user=data)
    
    username = request.form.get('username')
    pas = request.form.get('pas')
    telnum = request.form.get('telnum')
    mail = request.form.get('mail')
    url = 'http://localhost:8001/api/rest_user?username=' + username + '&pas=' + pas + '&telnum=' + telnum + '&mail=' + mail
    data = getJSONdata(url, 'POST')
    if 'error' in data:
        return render_template('msg.html', msg=error_handler(data))
    data, error = get_user_by_login(username, pas)
    if error:
        return render_template('msg.html', msg=data)
    return render_template('register.html', user=data)
   
    
@app.route('/register_update', methods=('GET', 'POST'))
def update_user():
    telnum = request.form.get('telnum')
    mail = request.form.get('mail')
    url = 'http://localhost:8001/api/rest_user?sid=' + session['sid'] + '&mail=' + mail + '&telnum=' + telnum
    data = getJSONdata(url, 'PUT')
    if 'error' in data:
        return render_template('msg.html', msg=error_handler(data))
    return render_template('register.html', user=data)


@app.route('/register_delete', methods=('GET', 'POST'))
def delete_user():
    url = 'http://localhost:8001/api/rest_user?sid=' + session['sid']
    data = getJSONdata(url, 'DELETE')
    if 'error' in data:
        return render_template('msg.html', msg=error_handler(data))
    session.clear()
    return render_template('msg.html', msg=data['answer'])


@app.route('/guns', methods=('GET', 'POST'))
def guns():
    p = request.args.get('page','1')
    pp = request.args.get('perpage','10')
    data, error = get_guns(session['sid'], p, pp)
    if error:
        return render_template('msg.html', msg=data)
    array = []
    for i in range(1, int(data['max_page']) + 1):
        array.append(i)
    return render_template('guns.html', guns=data['elements'], page=p, perpage=pp, pages=array, gun_link=url_for('guns'))
    
@app.route('/guns/<int:gun_id>', methods=('GET', 'POST'))
def show_gun(gun_id):
    data, error = get_gun(gun_id, session['sid'])
    if error:
        return render_template('msg.html', msg=data)
    return render_template('gun.html', gun=data)

@app.route('/create_gun', methods=('GET', 'POST'))    
def create_gun():
    if request.method == 'GET':
        return render_template('gun.html')    
    name = request.form.get('name')
    type = request.form.get('type')
    cost = request.form.get('cost')
    url = 'http://localhost:8001/api/guns?sid=' + session['sid'] + '&name=' + name + '&type=' + str(type) + '&cost=' + str(cost)
    data = getJSONdata(url, 'POST')
    if 'error' in data:
        return render_template('msg.html', msg=error_handler(data))
    return render_template('gun.html', gun=data)

@app.route('/update_gun/<int:gun_id>', methods=('GET', 'POST'))
def update_gun(gun_id):
    name = request.form.get('name')
    type = request.form.get('type')
    cost = request.form.get('cost')
    url = 'http://localhost:8001/api/guns/' + str(gun_id) + '?sid=' + session['sid'] + '&name=' + name + '&type=' + str(type) + '&cost=' + str(cost)
    data = getJSONdata(url, 'PUT')
    if 'error' in data:
        return render_template('msg.html', msg=error_handler(data))
    return render_template('gun.html', gun=data)

@app.route('/delete_gun/<int:gun_id>', methods=('GET', 'POST'))
def delete_gun(gun_id):
    url = 'http://localhost:8001/api/guns/' + str(gun_id) + '?sid=' + session['sid']
    data = getJSONdata(url, 'DELETE')
    if 'error' in data:
        return render_template('msg.html', msg=error_handler(data))
    return render_template('msg.html', msg=data['answer'])


@app.route('/types', methods=('GET', 'POST'))
def types():
    p = request.args.get('page','1')
    pp = request.args.get('perpage','10')
    data, error = get_types(session['sid'], p, pp)
    if error:
        return render_template('msg.html', msg=data)
    array = []
    for i in range(1, int(data['max_page']) + 1):
        array.append(i)
    return render_template('types.html', types=data['elements'], pages=array, type_link=url_for('types'))
    
@app.route('/types/<int:type_id>', methods=('GET', 'POST'))
def show_type(type_id):
    data, error = get_type(type_id, session['sid'])
    if error:
        return render_template('msg.html', msg=data)
    return render_template('type.html', type=data)

@app.route('/create_type', methods=('GET', 'POST'))    
def create_type():
    if request.method == 'GET':
        return render_template('type.html')    
    name = request.form.get('name')
    url = 'http://localhost:8001/api/types?sid=' + session['sid'] + '&name=' + name
    data = getJSONdata(url, 'POST')
    if 'error' in data:
        return render_template('msg.html', msg=error_handler(data))
    return render_template('type.html', type=data)

@app.route('/update_type/<int:type_id>', methods=('GET', 'POST'))
def update_type(type_id):
    name = request.form.get('name')
    url = 'http://localhost:8001/api/types/' + str(type_id) + '?sid=' + session['sid'] + '&name=' + name
    data = getJSONdata(url, 'PUT')
    if 'error' in data:
        return render_template('msg.html', msg=error_handler(data))
    return render_template('type.html', type=data)

@app.route('/delete_type/<int:type_id>', methods=('GET', 'POST'))
def delete_type(type_id):
    url = 'http://localhost:8001/api/types/' + str(type_id) + '?sid=' + session['sid']
    data = getJSONdata(url, 'DELETE')
    if 'error' in data:
        return render_template('msg.html', msg=error_handler(data))
    return render_template('msg.html', msg=data['answer'])


@app.route('/favorites', methods=('GET', 'POST'))
def favorites():
    p = request.args.get('page','1')
    pp = request.args.get('perpage','10')
    data, error = get_favorites(session['sid'], p, pp)
    if error:
        return render_template('msg.html', msg=data)
    array = []
    for i in range(1, int(data['max_page']) + 1):
        array.append(i)
    return render_template('favorites.html', favorites=data['elements'], page=p, perpage=pp, pages=array, gun_link=url_for('guns'), favorite_link=url_for('favorites'))
    
@app.route('/delete_favorite/<int:fid>', methods=('GET', 'POST'))
def delete_favorite(fid):
    p = request.args.get('page','1')
    pp = request.args.get('perpage','10')
    url = 'http://localhost:8001/api/favorites/' + str(fid) + '?sid=' + session['sid']
    data = getJSONdata(url, 'DELETE')
    if 'error' in data:
        return render_template('msg.html', msg=error_handler(data))
    
    data, error = get_favorites(session['sid'], p, pp)
    if error:
        return render_template('msg.html', msg=data)
    array = []
    for i in range(1, int(data['max_page']) + 1):
        array.append(i)
    return render_template('favorites.html', favorites=data['elements'], page=p, perpage=pp, pages=array, gun_link=url_for('guns'), favorite_link=url_for('favorites'))


@app.route('/create_favorite/<int:gun_id>', methods=('GET', 'POST'))    
def create_favorite(gun_id):
    p = request.args.get('page','1')
    pp = request.args.get('perpage','10')
    url = 'http://localhost:8001/api/favorites?sid=' + session['sid'] + '&gun_id=' + str(gun_id)
    data = getJSONdata(url, 'POST')
    if 'error' in data:
        return render_template('msg.html', msg=error_handler(data))

    data, error = get_guns(session['sid'], p, pp)
    if error:
        return render_template('msg.html', msg=data)
    array = []
    for i in range(1, int(data['max_page']) + 1):
        array.append(i)
    return render_template('guns.html', guns=data['elements'], page=p, perpage=pp, pages=array, gun_link=url_for('guns'))
    

@app.route('/delete_favorite_gun/<int:gun_id>', methods=('GET', 'POST'))
def delete_favorite_gun(gun_id):
    p = request.args.get('page','1')
    pp = request.args.get('perpage','10')
    url = 'http://localhost:8001/api/favorites?sid=' + session['sid'] + '&gun_id=' + str(gun_id)
    data = getJSONdata(url, 'DELETE')
    if 'error' in data:
        return render_template('msg.html', msg=error_handler(data))
    
    data, error = get_guns(session['sid'], p, pp)
    if error:
        return render_template('msg.html', msg=data)
    array = []
    for i in range(1, int(data['max_page']) + 1):
        array.append(i)
    return render_template('guns.html', guns=data['elements'], page=p, perpage=pp, pages=array, gun_link=url_for('guns'))


@app.route('/exit')
def uexit():
    if 'sid' in session:
        delete_session(session['sid'])
        session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)