import random
import string
import colorsys

from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
from flaskext.uploads import UploadSet, configure_uploads, IMAGES
from sqlalchemy import create_engine, asc, func
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
from database import Base, WineType
from wine_color_api.wine_color_api import wine_color_api
from temperature_api.temperature_api import temperature_api
from calories_api.calories_api import calories_api
from abv_api.abv_api import abv_api
from glass_api.glass_api import glass_api
from character_api.character_api import character_api
from type_api.winetype_api import winetype_api
from winestock_api.winestock_api import winestock_api
from auth_api.auth_api import auth_api

# Database setup
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)

app = Flask(__name__)
app.config['db'] = Session()
app.config['UPLOADS_DEFAULT_DEST'] = None
app.config['UPLOADS_DEFAULT_URL'] = None
app.register_blueprint(temperature_api, url_prefix='/temperature')
app.register_blueprint(wine_color_api, url_prefix='/color')
app.register_blueprint(calories_api, url_prefix='/calories')
app.register_blueprint(abv_api, url_prefix='/abv')
app.register_blueprint(glass_api, url_prefix='/glass')
app.register_blueprint(character_api, url_prefix='/character')
app.register_blueprint(winetype_api, url_prefix='/winetype')
app.register_blueprint(winestock_api, url_prefix='/winestock')
app.register_blueprint(auth_api, url_prefix='/auth')


# UPLOADED_PHOTOS_DEST = 'photolog'
# winetype_images = UploadSet('photos', IMAGES)
# configure_uploads(app, winetype_images)

@app.route('/')
def show_home():
    return redirect(url_for('winestock_api.show'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)


