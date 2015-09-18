import os
from flask import Flask, redirect, url_for, request, abort, render_template
from flask import session as login_session
from flaskext.uploads import UploadSet, configure_uploads, IMAGES
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database import Base, WineBrand, UserReview, WineType, GlassType
from database import Temperature, WineABV, WineCalories, WineColor
from wine_color_api.wine_color_api import wine_color_api
from temperature_api.temperature_api import temperature_api
from calories_api.calories_api import calories_api
from abv_api.abv_api import abv_api
from glass_api.glass_api import glass_api
from type_api.winetype_api import winetype_api
from winebrand_api.winebrand_api import winebrand_api
from auth_api.auth_api import auth_api, authenticate_api, generate_csrf_token
from auth_api.auth_api import login_required

from utils import get_single_postprocessor

# Database setup
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
api_endpoint_session = scoped_session(Session)

app = Flask(__name__)
app.config['db'] = Session()
app.config['UPLOADS_DEFAULT_DEST'] = os.path.join(app.root_path,
                                                  'image_uploads')
app.register_blueprint(temperature_api, url_prefix='/temperature')
app.register_blueprint(wine_color_api, url_prefix='/color')
app.register_blueprint(calories_api, url_prefix='/calories')
app.register_blueprint(abv_api, url_prefix='/abv')
app.register_blueprint(glass_api, url_prefix='/glass')
app.register_blueprint(winetype_api, url_prefix='/winetype')
app.register_blueprint(winebrand_api)
app.register_blueprint(auth_api, url_prefix='/auth')

brandphotos = UploadSet('brandphotos', IMAGES)
configure_uploads(app, (brandphotos,))


# set up CSRF token handling
@app.before_request
def csrf_protect():
    if request.method == "POST":
        # When signed in, the CSRF token is stored here
        server_token = login_session.pop('_csrf_token', None)

        # When first signing in, the CSRF token is found here
        form_token = request.form.get('_csrf_token', None)
        if not form_token:
            form_token = request.values.get('_csrf_token', None)

        if not server_token or server_token != form_token:
            abort(403)

app.jinja_env.globals['csrf_token'] = generate_csrf_token

# Setting up API endpoints
api_manager = restfull.APIManager(app, session=api_endpoint_session)

glass_api_manager = api_manager.create_api(
    GlassType,
    preprocessors=dict(GET_SINGLE=[authenticate_api],
                       GET_MANY=[authenticate_api]),
    collection_name='glass')

temp_api_manager = api_manager.create_api(
    Temperature,
    preprocessors=dict(GET_SINGLE=[authenticate_api],
                       GET_MANY=[authenticate_api]),
    collection_name='temperature')

abv_api_manager = api_manager.create_api(
    WineABV,
    preprocessors=dict(GET_SINGLE=[authenticate_api],
                       GET_MANY=[authenticate_api]),
    collection_name='abv')

calories_api_manager = api_manager.create_api(
    WineCalories,
    preprocessors=dict(GET_SINGLE=[authenticate_api],
                       GET_MANY=[authenticate_api]),
    collection_name='calories')

color_api_manager = api_manager.create_api(
    WineColor,
    preprocessors=dict(GET_SINGLE=[authenticate_api],
                       GET_MANY=[authenticate_api]),
    collection_name='color')

winebrand_api_manager = api_manager.create_api(
    WineBrand,
    preprocessors=dict(GET_SINGLE=[authenticate_api],
                       GET_MANY=[authenticate_api]),
    exclude_columns=['user', 'winetype_id'],
    collection_name='winebrand')

review_api_manager = api_manager.create_api(
    UserReview,
    preprocessors=dict(GET_SINGLE=[authenticate_api],
                       GET_MANY=[authenticate_api]),
    exclude_columns=['user', 'winebrand_id'],
    collection_name='review')

winetype_api_manager = api_manager.create_api(
    WineType,
    exclude_columns=['user', 'winebrand_id', 'winebrand'],
    preprocessors=dict(GET_SINGLE=[authenticate_api],
                       GET_MANY=[authenticate_api]),
    postprocessors={'GET_SINGLE': [get_single_postprocessor]},
    collection_name='winetype')


@app.route('/')
def show_home():
    return redirect(url_for('winebrand_api.show'))


@app.route('/help')
@login_required
def show_help():
    return render_template("help.html")

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
