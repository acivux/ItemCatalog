import random
import string
import json
from functools import wraps

from flask import current_app, Blueprint
from flask import render_template, request
from flask import redirect, url_for, flash
from flask import make_response
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests

from database import User

auth_api = Blueprint('auth_api', __name__)
template_prefix = "auth/"


@auth_api.route('/login', methods=["GET"])
def show_login():
    """
    Entry point for loggin into the app

    :return: HTML page
    """
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in
        xrange(32))
    login_session['state'] = state
    return render_template(template_prefix+'login.html', STATE=state)


@auth_api.route('/user', methods=["GET", "POST"])
def user_edit():
    """
    Edit an existing user.
    Existing user data found in the current session

    :return: HTML page
    """
    if login_session.get('user_id', None):
        if request.method == "POST":
            session = current_app.config['db']
            user = session\
                .query(User)\
                .filter_by(id=login_session['user_id'])\
                .one()
            user.nickname = request.form.get('usernickname')
            session.commit()
            flash("User nickname changed", 'success')
            return redirect(url_for('winebrand_api.show'))
        else:
            user = get_user_info(login_session['user_id'])
            return render_template(template_prefix+'user_edit.html', user=user)
    else:
        response = make_response(
            json.dumps('User mismatch.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response


@auth_api.route('/signout', methods=["GET"])
def signout():
    """
    Sign user out of the app, and disconnect from 3rd party authenticator
    """
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
        del login_session['isadmin']
        del login_session['provider']
        flash("You have successfully been logged out.", 'success')
        return redirect(url_for('winebrand_api.show'))
    else:
        flash("You were not logged in", 'danger')
        return redirect(url_for('winebrand_api.show'))


@auth_api.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Authenticate user through Google
    """
    google_client_secrets_file = './auth_api/google_client_secrets.json'

    with open(google_client_secrets_file, 'r') as gcsf:
        google_client_secrets_json = json.loads(gcsf.read())

    google_client_id = google_client_secrets_json['web']['client_id']

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.values.get('authresult', None)

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(google_client_secrets_file,
                                             scope='')
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

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != google_client_id:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
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

    # see if user exists, if it doesn't make a new one
    user_id = get_user_id(data["email"])
    if not user_id:
        user_id = create_user(login_session)
    else:
        update_user_profile(user_id, login_session)
    user = get_user_info(user_id)
    login_session['user_id'] = user_id
    login_session['isadmin'] = user.admin

    response = make_response(json.dumps('Please wait...'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


def gdisconnect():
    """
    Disconnect from Google
    """
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = json.loads(credentials).get('access_token')
    url = u'https://accounts.google.com/o/oauth2/revoke?token=%s' %\
          access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@auth_api.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
    Authenticate user through Facebook
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    with open('./auth_api/facebook_client_secrets.json', 'r') as jsfile:
        facebook_secrets = json.loads(jsfile.read())

    access_token = request.values.get('access_token', None)
    app_id = facebook_secrets['web']['app_id']
    app_secret = facebook_secrets['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id,
        app_secret,
        access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['access_token'] = token.split("=")[1]

    # Get user picture
    url = 'https://graph.facebook.com/v2.2/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    else:
        update_user_profile(user_id, login_session)
    user = get_user_info(user_id)
    login_session['user_id'] = user_id
    login_session['isadmin'] = user.admin

    response = make_response(json.dumps('Authenticated'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


def fbdisconnect():
    """
    Disconnect from Facebook
    """
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id,
        access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]


def get_user_id(email):
    """
    Retrieves a user ID for the specific email

    :param email: Email address to look up
    :return: user ID
    """
    try:
        user = current_app.config['db'].query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def create_user(login_session_obj):
    """
    Create a new user given the session object
    :param login_session_obj: Session object
    :return: user id
    """
    try:
        newuser = User(name=login_session_obj['username'],
                       email=login_session_obj['email'],
                       picture=login_session_obj['picture'])
        current_app.config['db'].add(newuser)
        current_app.config['db'].commit()
        return newuser.id
    except:
        return None


def get_user_info(user_id):
    """
    Retrieves the user data from the database given the user id
    :param user_id: User's ID
    :return: User object
    """
    try:
        user = current_app.config['db'].query(User).filter_by(id=user_id).one()
        return user
    except:
        return None


def update_user_profile(user_id, login_session_obj):
    """
    Updates a users profile data in the database.

    :param user_id: User's ID
    :param login_session_obj: Sesssion Object
    :return: None
    """
    try:
        user = current_app.config['db'].query(User).filter_by(id=user_id).one()
        user.name = login_session_obj['username']
        user.picture = login_session_obj['picture']
        current_app.config['db'].commit()
    except:
        return None


def login_required(f):
    """
    Function decorator to prevent public access

    :param f: function to protect
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in login_session:
            flash("You need to be signed in perform this task", "danger")
            return redirect(url_for('auth_api.show_login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Function decorator to prevent non-administrator access

    :param f: function to protect
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if login_session.get('isadmin', False):
            return f(*args, **kwargs)
        else:
            flash("Only administrators can perform this task", "danger")
            return redirect(url_for('auth_api.show_login'))
    return decorated_function


def authenticate_api(*args, **kwargs):
    """
    Flask-Restless uses this function to verify request was made by
    logged in user.
    """
    from flask.ext.restless import ProcessingException
    if 'user_id' not in login_session:
        raise ProcessingException(description='Not authenticated!')
    return None


def generate_csrf_token():
    """
    Generates a random string for use as CSRF token

    :return: a token
    """
    if '_csrf_token' not in login_session:
        token = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for x in
            xrange(64))
        login_session['_csrf_token'] = token
    return login_session['_csrf_token']


