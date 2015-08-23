import random
import string
import colorsys

from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session

from database import Base, WineType
from wine_color_api.wine_color_api import wine_color_api
from temperature_api.temperature_api import temperature_api
from calories_api.calories_api import calories_api
from abv_api.abv_api import abv_api
from glass_api.glass_api import glass_api
from character_api.character_api import character_api


# Database setup
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)

app = Flask(__name__)
app.config['db'] = Session()
app.register_blueprint(temperature_api, url_prefix='/temperature')
app.register_blueprint(wine_color_api, url_prefix='/color')
app.register_blueprint(calories_api, url_prefix='/calories')
app.register_blueprint(abv_api, url_prefix='/abv')
app.register_blueprint(glass_api, url_prefix='/glass')
app.register_blueprint(character_api, url_prefix='/character')


def get_hsv(hexrgb):
    """
    Return sortable hue
    http://stackoverflow.com/questions/8915113/sort-hex-colors-to-match-rainbow
    """
    r, g, b = (int(hexrgb[i:i+2], 16) / 255.0 for i in xrange(0, 5, 2))
    return colorsys.rgb_to_hsv(r, g, b)


@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/')
@app.route('/winelist/')
def show_home():
    session = app.config['db']
    winetypes = session.query(WineType).order_by(asc(WineType.name))
    return render_template('home.html', winetypes=winetypes)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)


