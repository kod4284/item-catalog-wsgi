#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import make_response, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)

APPLICATION_NAME = "Catalog Application"
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    if access_token is None:
        print('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token='
    url += '%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        script = '''<script type='text/javascript'>
               document.write('Successfully disconnected.</br>Redirecting...')
               setTimeout("location.href='/'",2000);
               </script>'''
        response = make_response(script, 200)
        response.headers['Content-Type'] = 'text/html'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all catalogs
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(desc(Item.id))
    if 'username' not in login_session:
        return render_template('main.html', category=categories, item=items)
    else:
        return render_template(
            'private_main.html', category=categories, item=items)


@app.route('/catalog/<category_name>/items')
def showItems(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).join(Category).filter(
        Category.name == category_name).order_by(Category.name)
    return render_template('items.html', category=categories,
                           category_name=category_name, item=items)


@app.route('/catalog.json')
def catalogJSON():
    categories = []
    for i in session.query(Category).order_by(asc(Category.id)):
        items = session.query(Item).filter_by(category_id=i.id)
        category = {
            "id": i.id,
            "name": i.name,
            "Item": [j.serialize for j in items]
        }
        categories.append(category)

    return jsonify(Categories=categories)


@app.route('/catalog/<item_name>.json')
def itemJSON(item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    return jsonify(Item=item.serialize)


@app.route('/catalog/<category_name>/<item_name>')
def showDecription(category_name, item_name):
    item = session.query(Item).join(Category).filter(
        Category.name == category_name, Item.name == item_name).one()
    if 'username' not in login_session:
        return render_template('description.html', item=item)
    else:
        return render_template('private_description.html', item=item)


@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    if request.method == 'GET':
        if 'username' not in login_session:
            return redirect('/login')
        category = session.query(Category).order_by(Category.name)
        return render_template('add_item.html', category=category)
    if request.method == 'POST':
        category_name = request.form['category']
        category = session.query(Category).filter(
            Category.name == category_name).first()
        newItem = Item(name=request.form['title'],
                       description=request.form['description'],
                       category=category, user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Item (%s) Successfully Created' % (newItem.name))
        return redirect(url_for('showCatalog'))


@app.route('/catalog/<item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    if request.method == 'GET':
        editeditem = session.query(Item).filter_by(name=item_name).one()
        category = session.query(Category)
        if 'username' not in login_session:
            return redirect('/login')
        if editeditem.user_id != login_session['user_id']:
            result = "<script>function myAlert(){alert('You are not authorized"
            result += " to edit this item. You can only edit the items you"
            result += " created'); document.location.href='/'}"
            result += "</script><body onload='myAlert()''>"
            return result
        return render_template('edit_item.html',
                               edit_item=editeditem, category=category)
    if request.method == 'POST':
        editeditem = session.query(Item).filter_by(name=item_name).one()

        category_name = request.form['category']
        category = session.query(Category).filter(
            Category.name == category_name).first()

        editeditem.name = request.form['title']
        editeditem.description = request.form['description']
        editeditem.category = category
        return redirect(url_for('showCatalog'))


@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    if request.method == 'GET':
        deleteditem = session.query(Item).filter_by(name=item_name).one()
        if 'username' not in login_session:
            return redirect('/login')
        if deleteditem.user_id != login_session['user_id']:
            result = "<script>function myAlert(){alert('You are not authorized"
            result += " to delete this item. You can only delete the items you"
            result += " created');document.location.href='/'}"
            result += "</script><body onload='myAlert()''>"
            return result
        return render_template('delete_item.html', delete_item=deleteditem)
    if request.method == 'POST':
        deleteditem = session.query(Item).filter_by(name=item_name).one()
        session.delete(deleteditem)
        session.commit()
        return redirect(url_for('showCatalog'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)
