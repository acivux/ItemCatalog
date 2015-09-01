from flask import current_app, Blueprint
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, desc, func
from database import WineStock, WineType, WineRating
from flask import session as login_session
import datetime

winestock_api = Blueprint('winestock_api', __name__)
template_prefix = "winestock/"


@winestock_api.route('/')
def show():
    session = current_app.config['db']
    wines = session.query(WineType, func.count(WineStock.id)).join(WineStock).group_by(WineType.name).order_by(asc(WineType.name))
    return render_template(template_prefix+'topview.html', wines=wines)


@winestock_api.route('/<int:winetype_id>/', methods=["GET"])
def show_brand(winetype_id):
    session = current_app.config['db']

    winetype = session.query(
        WineType
    ).filter_by(
        id=winetype_id
    ).one()

    wines = session.query(
        WineStock
    ).filter_by(
        winetype_id=winetype_id
    ).order_by(
        WineStock.brand_name,
        WineStock.vintage.asc()
    )
    return render_template(template_prefix+'brandview.html',
                           winetype=winetype,
                           wines=wines)


@winestock_api.route('/stockitem/<int:stockitem_id>/', methods=["GET"])
def show_stockitem(stockitem_id):
    session = current_app.config['db']
    item = session.query(WineStock).filter_by(id=stockitem_id).one()
    reviews = session.query(WineRating).filter_by(
        winestock_id=stockitem_id).order_by(
        WineRating.date_created.desc())
    return render_template(template_prefix+"stockview.html",
                           item=item,
                           reviews=reviews)


@winestock_api.route('/new', methods=["GET", "POST"])
def new():
    session = current_app.config['db']
    item = WineStock(brand_name="", vintage=1980)
    maxyear = datetime.date.today().year
    if request.method == "POST":
        item.brand_name = request.form['itemname']
        item.winetype_id = request.form.get('winetypevalue', None)
        item.vintage = request.form.get('vintagevalue', None)
        item.date_created = datetime.datetime.now()
        item.user_id = login_session.get('user_id', None)
        session.add(item)
        session.commit()
        session.flush()

        winetype = session.query(WineType.name).filter_by(
            id=item.winetype_id).one()

        flash("Successfully Added '%s (%s)'" % (winetype.name, item.brand_name),
              'success')
        return redirect(url_for('.show_stockitem', stockitem_id=item.id))
    else:
        winetypes = session.query(WineType).order_by(asc(WineType.name)).all()
        return render_template(template_prefix+'new_form.html',
                               item=item,
                               winetypes=winetypes,
                               maxyear=maxyear)


@winestock_api.route('/stockitem/<int:stockitem_id>/rating/new',
                     methods=["POST"])
def new_review(stockitem_id):
    session = current_app.config['db']
    if request.method == "POST":
        reviewitem = WineRating(
            winestock_id=stockitem_id,
            summary=request.form.get('summary', None),
            comment=request.form.get('reviewtext', None),
            rating=request.form.get('star', 1),
            date_created=datetime.datetime.now(),
            user_id=login_session.get('user_id', None)
        )
        session.add(reviewitem)
        session.commit()
        flash("Successfully added a review", 'success')
        return redirect(url_for('.show_stockitem', stockitem_id=stockitem_id))


@winestock_api.route('/reviews/<int:user_id>', methods=["GET"])
def list_user_reviews(user_id):
    session = current_app.config['db']
    reviews = session.query(WineRating).filter_by(user_id=user_id).order_by(WineRating.date_created.desc())
    return render_template(template_prefix+"user_reviews_list.html", reviews=reviews)

