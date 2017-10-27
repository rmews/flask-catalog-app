import random
import string
import json
import os
import datetime
import httplib2
import requests
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

app = Flask(__name__)

# Connect to database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

################################
####    Helper Functions    ####
################################

def create_user(login_session):
    """Grab username, email and picture from login session"""
    new_user = User(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def get_user_id(user_id):
    """Grab users id from db and return it"""
    user = session.query(User).filter_by(id=user_id).one()
    return user

def get_user_email(email):
    """Grab users email from db and return it"""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


##################################
####          Routes          ####
##################################

@app.route('/')
@app.route('/catalog/')
def show_catalog():
    """Show one of two versions of the catalog based on login state"""
    # Pull all the categories
    categories = session.query(Category).order_by(asc(Category.name))
    # Pull the 10 most recent items
    items = session.query(Item).order_by(desc(Item.date)).limit(10)
    # If user is not logged-in then render template with no add item functionality
    if 'username' not in login_session:
        return render_template('publiccatalog.html',
                               categories=categories,
                               items=items)
    # If username is set, then render main template that allows user to add items
    else:
        # Pull the user info to show in nav
        user = get_user_id(login_session.get('user_id'))
        return render_template('catalog.html',
                               categories=categories,
                               items=items,
                               user=user)

@app.route('/login/')
def login():
    """Login route"""
    # Create token to prevent request forgery and store it
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    # Store it in session for later validation
    login_session['state'] = state
    # Render login template
    return render_template('login.html', state=state)

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Facebook Auth0 Route"""
    # Connect Facebook user if token is authenticated
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    # Exchange client token for long-lived server-side token with GET
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s \
           &client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    # Strip expire tag from access token
    token = result.split(',')[0].split(':')[1].replace('"', '')
    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200 \
           &width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # See if user exists
    user_id = get_user_email(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    # Output flash message
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("You are now logged in as %s" % login_session['username'])
    return output

@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Google Auth0 Route"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid sate parameter.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    # Obtain auth code
    code = request.data

    try:
        # Upgrade auth code into credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Abort if there is an error with access token
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        resonse.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store access token in session for later use
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # See if user exists, if not, make new one
    user_id = get_user_email(data['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    # Output flash message
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("You are now logged in as %s" % login_session['username'])
    return output

@app.route('/fbdisconnect')
def fbdisconnect():
    """Facebook Disconnect Route"""
    # Disconnect Facebook user, revoke token and reset login_session
    facebook_id = login_session['facebook_id']
    # The access token must be included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

@app.route('/gdisconnect')
def gdisconnect():
    """Google Disconnect Route"""
    # Disconnect Google user, revoke token and reset login_session
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET request to revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the token was invalid
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/disconnect')
def disconnect():
    """Disconnect based on provider"""
    # Check provider and then call function to log user out
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('show_catalog'))
    else:
        flash("You were not logged in to begin with!")
        return redirect(url_for('show_catalog'))

@app.route('/catalog/<path:category_name>/items/')
def show_items(category_name):
    """Show items belonging to a category"""
    # Pull all the categories
    categories = session.query(Category).order_by(asc(Category.name))
    # Identify which category user is in
    category = session.query(Category).filter_by(name=category_name).one()
    # Pull only the items that belong to the category
    items = session.query(Item).filter_by(category=category).all()
    # If user is not logged-in then render template with no add item functionality
    if 'username' not in login_session:
        return render_template('publicitems.html',
                               category=category,
                               categories=categories,
                               items=items)
    # If username is set, then render main template that allows user to add items
    else:
        user = get_user_id(login_session.get('user_id'))
        return render_template('items.html',
                               category=category,
                               categories=categories,
                               items=items,
                               user=user)

@app.route('/catalog/<path:category_name>/<path:item_name>/')
def show_item(category_name, item_name):
    """Show an individual item"""
    # Pull all the categories
    # categories = session.query(Category).order_by(asc(Category.name))
    # Pull only the item that belongs to the category on the GET request
    item = session.query(Item).filter_by(name=item_name).one()
    # Identify if item was created by user
    creator = get_user_id(item.user_id)
    # If user is logged-in and the creator then render template with editable functionality
    if 'username' in login_session and creator.id == login_session.get('user_id'):
        user = get_user_id(login_session.get('user_id'))
        return render_template('creatoritem.html',
                               category=category_name,
                               item=item,
                               user=user)
    # If user is logged-in but not the creator, then render template with no editable functionlity
    elif 'username' in login_session and creator.id != login_session.get('user_id'):
        # Pull in user info for header
        user = get_user_id(login_session.get('user_id'))
        return render_template('item.html',
                               category=category_name,
                               item=item,
                               user=user)
    # If user is not logged-in and not creator, render public template
    else:
        return render_template('publicitem.html',
                               category=category_name,
                               item=item,
                               creator=creator)

@app.route('/catalog/add/', methods=['GET', 'POST'])
def add_item():
    """Add a new item to Catagory"""
    # Check if user is logged-in, if not redirect them
    if 'username' not in login_session:
        return redirect(url_for('login'))
    # Logic for POST request
    if request.method == 'POST':
        # If form has name, description and category complete, then submit data
        if request.form['name'] and request.form['description'] and request.form['category']:
            newItem = Item(name=request.form['name'],
                           description=request.form['description'],
                           date=datetime.datetime.utcnow(),
                           category=session.query(Category).filter_by(name=request.form \
                           ['category']).one(),
                           user_id=login_session.get('user_id'))
            session.add(newItem)
            session.commit()
            flash("New Item %s Created Successfully" % (newItem.name))
            return redirect(url_for('show_catalog'))
        # If data is missing, return them to form with error message
        else:
            flash("Please check form again for empty fields")
            # Pull all the categories on GET request to generate dropdown menu
            categories = session.query(Category).all()
            user = get_user_id(login_session.get('user_id'))
            return render_template('additem.html',
                                   categories=categories,
                                   user=user)
    # Logic for GET request
    else:
        # Pull all the categories on GET request to generate dropdown menu
        categories = session.query(Category).all()
        user = get_user_id(login_session.get('user_id'))
        return render_template('additem.html',
                               categories=categories,
                               user=user)

@app.route('/catalog/<path:category_name>/<path:item_name>/edit/', methods=['GET', 'POST'])
def edit_item(category_name, item_name):
    """Edit an item"""
    # Check if user is logged-in, if not redirect them
    # Pull only the item that belongs to the category on the GET request
    editedItem = session.query(Item).filter_by(name=item_name).one()
    # Identify if item was created by user
    creator = get_user_id(editedItem.user_id)
    if 'username' not in login_session or login_session.get('user_id') != creator.id:
        return redirect(url_for('login'))
    # Logic for POST request
    if request.method == 'POST':
        # If form has name, description and category complete, then submit data
        if request.form['name'] and request.form['description'] and request.form['category']:
            # Grab form data and build object to update database
            if request.form['name']:
                editedItem.name = request.form['name']
            if request.form['description']:
                editedItem.description = request.form['description']
            if request.form['category']:
                category = session.query(Category).filter_by(name=request.form['category']).one()
                editedItem.category = category
            time = datetime.datetime.utcnow()
            editedItem.date = time
            session.add(editedItem)
            session.commit()
            flash("Item %s Successfully Updated" % (editedItem.name))
            return redirect(url_for('show_catalog'))
        # If data is missing, return them to form with error message
        else:
            flash("Please check form again for empty fields")
            # Pull all the categories on GET request to generate dropdown menu
            categories = session.query(Category).all()
            user = get_user_id(login_session.get('user_id'))
            return render_template('edititem.html',
                                   categories=categories,
                                   item=editedItem,
                                   user=user)
    # Logic for GET request
    else:
        # Pull all the categories on GET request to generate dropdown menu
        categories = session.query(Category).all()
        user = get_user_id(login_session.get('user_id'))
        return render_template('edititem.html',
                               categories=categories,
                               item=editedItem,
                               user=user)

@app.route('/catalog/<path:category_name>/<path:item_name>/delete/', methods=['GET', 'POST'])
def delete_item(category_name, item_name):
    """Delete an item"""
    # Check if user is logged-in, if not redirect them.
    # Pull only the item that belongs to the category on the GET request
    itemToDelete = session.query(Item).filter_by(name=item_name).one()
    # Identify if item was created by user
    creator = get_user_id(itemToDelete.user_id)
    if 'username' not in login_session or login_session.get('user_id') != creator.id:
        return redirect(url_for('login'))
    # Logic for POST request
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('show_catalog'))
    # Logic for GET request
    else:
        user = get_user_id(login_session.get('user_id'))
        return render_template('deleteitem.html',
                               item=itemToDelete,
                               user=user)

@app.route('/catalog/JSON')
def catalog_API():
    """APIs endpoint to view catalog information"""
    # Pull all the categories
    categories = session.query(Category).order_by(Category.name.asc()).all()
    # Create empty array
    categoryJSON = []
    # Loop through categories
    for category in categories:
        # serialize category data
        cat = category.serialize
        # Query item data
        items = session.query(Item).filter(Item.category_id == category.id).all()
        # Create empty array
        itemJSON = []
        # Loop through items
        for item in items:
            # Serialize item data and append to empty array
            itemJSON.append(item.serialize)
        cat['items'] = itemJSON
        categoryJSON.append(cat)
    return jsonify(Categories=[categoryJSON])

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(debug=True, host='0.0.0.0', port=5000)
