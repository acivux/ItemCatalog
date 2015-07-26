from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database import Base, User, Category, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)


@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/')
@app.route('/catalog/')
def show_home():
    session = Session()
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('home.html', categories=categories)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
