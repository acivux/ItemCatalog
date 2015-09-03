import os
import flask.ext.restless
from flask import Flask, redirect, url_for
from flaskext.uploads import UploadSet, configure_uploads, IMAGES
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database import Base, GlassType, WineStock, UserReview
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
api_endpoint_session = scoped_session(Session)

app = Flask(__name__)
app.config['db'] = Session()
app.config['UPLOADS_DEFAULT_DEST'] = os.path.join(app.root_path, 'image_uploads')
app.register_blueprint(temperature_api, url_prefix='/temperature')
app.register_blueprint(wine_color_api, url_prefix='/color')
app.register_blueprint(calories_api, url_prefix='/calories')
app.register_blueprint(abv_api, url_prefix='/abv')
app.register_blueprint(glass_api, url_prefix='/glass')
app.register_blueprint(character_api, url_prefix='/character')
app.register_blueprint(winetype_api, url_prefix='/winetype')
app.register_blueprint(winestock_api, url_prefix='/winestock')
app.register_blueprint(auth_api, url_prefix='/auth')

brandphotos = UploadSet('brandphotos', IMAGES)
glassphotos = UploadSet('glassphotos', IMAGES)
configure_uploads(app, (glassphotos, brandphotos))

api_manager = flask.ext.restless.APIManager(app, session=api_endpoint_session)
glass_blueprint = api_manager.create_api(GlassType)
winestock_blueprint = api_manager.create_api(
    WineStock,
    exclude_columns=['user', 'winetype_id'])
review_blueprint = api_manager.create_api(
    UserReview,
    exclude_columns=['user', 'winestock_id'])


@app.route('/')
def show_home():
    return redirect(url_for('winestock_api.show'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)


