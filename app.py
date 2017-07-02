from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash


from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import User, Category, Item, Base

from flask import session as login_session
import random
import string


# For gconnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import datetime

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogapp.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def getCategoryId(category_name):
    category = session.query(Category).filter_by(name=category_name).first()
    return category.id


def getItemId(item_name, category_id):
    item = session.query(Item).filter_by(name=item_name,
                                        category_id=category_id).first()
    if item:
        return item.id
    else:
        return 0


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    print "here" + login_session['username']
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


@app.route("/login")
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    # Render login template
    return render_template('login.html', STATE=state)


@app.route("/gconnect", methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade auth code to credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
                json.dumps('Failed to upgrade the authorization code to credentials'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
       % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # Abort if error in access token info
    if result.get('error') is not None:
        print '106'
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        print '114'
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Checking if the user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    return render_template('loginSuccess.html',
                            username=login_session['username'])


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Category Information
@app.route('/catalog/categories/JSON')
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


# JSON APIs to view Category's Item Information
@app.route('/catalog/<string:category_name>/JSON')
def categoryItemsJSON(category_name):
    category_id = getCategoryId(category_name)
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


# JSON APIs to view Category's Item Information
@app.route('/catalog/<string:category_name>/<string:item_name>/JSON')
def itemJSON(category_name, item_name):
    category_id = getCategoryId(category_name)
    item_id = getItemId(item_name, category_id)
    item = session.query(Item).filter_by(category_id=category_id).one()
    return jsonify(Item=item.serialize)


@app.route('/')
@app.route('/catalog')
def showCatalog():
    categories = session.query(Category)
    items = session.query(Item).order_by(desc(Item.created_on)).limit(10)
    # print login_session['credentials']
    print login_session.get('credentials')
    if login_session.get('credentials') != None:
        # print "here"
        return render_template('showCatalog.html',
                                categories=categories,
                                items=items)

    else:
        return render_template('publicShowCatalog.html',
                                categories=categories,
                                items=items)


@app.route('/catalog/<string:category_name>/items/')
def showCatalogItems(category_name):
    categories = session.query(Category)
    print "Category %s" % category_name
    category_id = getCategoryId(category_name)
    items = session.query(Item).filter_by(category_id=category_id).limit(10)
    if not login_session.get('credentials'):
        return render_template('showItems.html',
                                categories=categories,
                                items=items)
    else:
        return render_template('publicShowItems.html', categories=categories,
                                                        items=items)


@app.route('/catalog/items/new/', methods=['GET', 'POST'])
def addItem():
    if not login_session.get('credentials'):
        if request.method == 'GET':
            categories = session.query(Category).order_by(asc(Category.name))
            return render_template('newItem.html', categories=categories)
        elif request.method == 'POST':
            newItem = Item(
                user_id=1,
                name=request.form['title'],
                category_id=request.form['category'],
                created_on=datetime.datetime.now())
            session.add(newItem)
            session.commit()
            return redirect(url_for('showCatalog'))
    else:
        return redirect(url_for('showLogin'))


@app.route('/catalog/<string:category_name>/<string:item_name>/edit/',
            methods=['GET', 'POST'])
def editItem(category_name, item_name):
    if not login_session.get('credentials'):
        category_id = getCategoryId(category_name)
        categories = session.query(Category).order_by(asc(Category.name))
        item_id = getItemId(item_name, category_id)
        if request.method == 'GET':
            if item_id != 0:
                item = session.query(Item).filter_by(id=item_id).one()
                return render_template('editItem.html', item=item,
                                                category_name=category_name,
                                                categories=categories)
            else:
                return redirect(url_for('showCatalog'))
        elif request.method == 'POST':
            if item_id != 0:
                item = session.query(Item).filter_by(id=item_id).one()
                item.name = request.form['title']
                item.category_id = request.form['category']
                session.add(item)
                session.commit()
                return redirect(url_for('showCatalog'))
            else:
                return redirect(url_for('showCatalog'))
    else:
        return redirect(url_for('showCatalog'))


@app.route('/catalog/<string:category_name>/<string:item_name>',
            methods=['GET'])
def showItem(category_name, item_name):
    category_id = getCategoryId(category_name)
    item_id = getItemId(item_name, category_id)
    if not login_session.get('credentials'):
        if item_id != 0:
            item = session.query(Item).filter_by(id=item_id).one()
            return render_template('showItem.html',
                                    item=item,
                                    category_name=category_name)
        else:
            return redirect(url_for('showCatalog'))
    else:
        if item_id != 0:
            item = session.query(Item).filter_by(id=item_id).one()
            return render_template('publicShowItem.html',
                                    item=item,
                                    category_name=category_name)


@app.route('/catalog/<string:category_name>/<string:item_name>/delete/',
            methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    category_id = getCategoryId(category_name)
    categories = session.query(Category).order_by(asc(Category.name))
    item_id = getItemId(item_name, category_id)
    item = session.query(Item).filter_by(id=item_id).one()
    if not login_session.get('credentials'):
        if request.method == 'GET':
            return render_template('deleteItem.html',
                                item_name=item_name,
                                category_name=category_name)
        elif request.method == 'POST':
            session.delete(item)
            session.commit()
            return redirect(url_for('showCatalog'))
    else:
        return render_template(url_for('showCatalog'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=27016)
